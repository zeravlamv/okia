"""Recalcula un mes abierto. No reescribe los demás ni un proyecto retenido."""

from decimal import Decimal

from django.conf import settings
from django.db import transaction

from apps.erp.analytics import fetch_dimension_labels
from apps.erp.documents import (
    fetch_customer_names,
    fetch_purchase_deliveries,
    fetch_purchase_orders,
    fetch_sales_deliveries,
    fetch_supplier_names,
)
from apps.erp.ledger import fetch_period_movements
from apps.erp.mapping import (
    is_cancelled,
    is_closing_entry,
    is_cost_account,
    is_expense_account,
    is_income_account,
)
from apps.erp.sales import fetch_orders
from apps.margins.dashboard import analytical_dimensions
from apps.margins.hierarchy import _display, _unique_projects, tree_income_entries
from apps.margins.models import (
    MONTH_NAMES,
    BookExpense,
    BookIncome,
    DashboardSnapshot,
    MonthLedger,
    ProjectDocumentLine,
    ProjectExpense,
    ProjectLife,
    ProjectMilestone,
    ProjectPurchase,
    TreeIncome,
)
from apps.margins.project_life import (
    KIND_DELIVERY,
    KIND_ORDER,
    KIND_COMMITTED,
    _billing_of,
    _document_amount,
    _document_lines,
    _expense_placements,
    _level_fields,
    _text,
    closed_months,
)
from apps.margins.services import _side_amount


def refresh_month(company, year, month, progress=None):
    """Lee el origen de un mes abierto y sustituye solo lo guardado de ese mes.

    Un mes cerrado no se lee. Un proyecto con un pedido en un mes cerrado no se toca.
    """

    company = str(company)
    year = int(year)
    month = int(month)
    name = dict(MONTH_NAMES).get(month, "")

    def tell(step, label):
        if progress is not None:
            progress({"step": step, "total": 6, "label": label, "month": name})

    if month in closed_months(company, year):
        tell(6, "Listo")
        return
    tell(1, "Pedidos de venta")
    orders = fetch_orders(company, year, month)
    tell(2, "Pedidos de compra")
    purchase_orders = fetch_purchase_orders(company, year, month)
    tell(3, "Albaranes de venta")
    sales_deliveries = fetch_sales_deliveries(company, year, month)
    tell(4, "Albaranes de compra")
    purchase_deliveries = fetch_purchase_deliveries(company, year, month)
    tell(5, "Movimientos")
    movements = fetch_period_movements(company, year, month)
    labels = fetch_dimension_labels(company)
    customers = {} if settings.SAMPLE_ERP else fetch_customer_names(company)
    suppliers = {} if settings.SAMPLE_ERP else fetch_supplier_names(company)
    tell(6, "Guardando el mes")
    retained = _retained_codes(company, year)
    with transaction.atomic():
        _replace_commercial(
            company,
            year,
            month,
            orders,
            sales_deliveries,
            purchase_orders,
            purchase_deliveries,
            retained,
            labels,
            customers,
            suppliers,
        )
        _replace_expenses(company, year, month, movements, retained, labels)
        _replace_ledger(company, year, month, movements)
        _replace_books(company, year, month, movements, labels)
        _replace_tree(company, year, month, movements, orders, purchase_orders, labels)


def _retained_codes(company, year):
    """Proyectos cuyo pedido de venta ya guardado cae en un mes cerrado."""

    closed = closed_months(company, year)
    if not closed:
        return set()
    codes = set(
        ProjectDocumentLine.objects.filter(
            life__codigo_empresa=company,
            kind="sale_order",
            position=0,
            line_date__year=year,
            line_date__month__in=closed,
        ).values_list("life__codigo_proyecto", flat=True)
    )
    codes.update(
        ProjectLife.objects.filter(
            codigo_empresa=company,
            order_date__year=year,
            order_date__month__in=closed,
        ).values_list("codigo_proyecto", flat=True)
    )
    return {code for code in codes if code}


def _in_month(moment, year, month):
    return moment is not None and moment.year == year and moment.month == month


def _replace_commercial(
    company,
    year,
    month,
    orders,
    sales_deliveries,
    purchase_orders,
    purchase_deliveries,
    retained,
    labels,
    customers,
    suppliers,
):
    sale_orders = _open_orders(company, orders, year, month, retained)
    deliveries = _open_documents(company, sales_deliveries, year, month, retained)
    bought_orders = _open_documents(company, purchase_orders, year, month, retained)
    bought_deliveries = _open_documents(company, purchase_deliveries, year, month, retained)
    linked = _links_outside_month(company, year, month)
    for document in bought_deliveries:
        link = (
            _text(getattr(document, "linked_ejercicio", "")),
            _text(getattr(document, "linked_serie", "")),
            _text(getattr(document, "linked_numero", "")),
        )
        if link[2]:
            linked.add(link)
    for kind in ("sale_order", "sale_delivery", "purchase_order", "purchase_delivery"):
        _drop_month_lines(company, kind, year, month, retained)
    milestones = ProjectMilestone.objects.filter(
        life__codigo_empresa=company,
        delivery_date__year=year,
        delivery_date__month=month,
    )
    purchases = ProjectPurchase.objects.filter(
        life__codigo_empresa=company,
        document_date__year=year,
        document_date__month=month,
    )
    if retained:
        milestones = milestones.exclude(life__codigo_proyecto__in=retained)
        purchases = purchases.exclude(life__codigo_proyecto__in=retained)
    milestones.delete()
    purchases.delete()
    lines = []
    new_milestones = []
    new_purchases = []
    for order in sale_orders:
        amount, _missing = _document_amount(order)
        life = _life_for(
            company,
            _text(order.project),
            _text(getattr(order, "codigo_cliente", "")),
            _text(customers.get(_text(getattr(order, "codigo_cliente", "")), "")),
            order.order_date,
            amount,
        )
        lines.extend(
            _document_lines(
                life,
                "sale_order",
                f"{order.ejercicio} / {order.serie} / {order.numero}",
                amount,
                order.order_date,
                order.lines,
            )
        )
    tracked = _projects_with_sale_orders(company)
    for document in deliveries:
        life = _existing_life(company, _text(document.project), tracked)
        if life is None:
            continue
        amount, _missing = _document_amount(document)
        new_milestones.append(
            ProjectMilestone(
                life=life,
                ejercicio=document.ejercicio,
                serie=document.serie,
                numero=document.numero,
                delivery_date=document.document_date,
                amount=amount,
                billing=_billing_of(document),
                **_level_fields(getattr(document, "department", ""), getattr(document, "section", ""), labels),
            )
        )
        lines.extend(
            _document_lines(
                life,
                "sale_delivery",
                f"{document.ejercicio} / {document.serie} / {document.numero}",
                amount,
                document.document_date,
                getattr(document, "lines", ()),
                credit=bool(getattr(document, "credit", False)),
            )
        )
    for document in bought_deliveries:
        life = _existing_life(company, _text(document.project), tracked)
        if life is None:
            continue
        amount, _missing = _document_amount(document)
        code = _text(getattr(document, "supplier_code", ""))
        link = (
            _text(getattr(document, "linked_ejercicio", "")),
            _text(getattr(document, "linked_serie", "")),
            _text(getattr(document, "linked_numero", "")),
        )
        new_purchases.append(
            ProjectPurchase(
                life=life,
                kind=KIND_DELIVERY,
                ejercicio=document.ejercicio,
                serie=document.serie,
                numero=document.numero,
                supplier_code=code,
                supplier_name=suppliers.get(code, _text(getattr(document, "supplier_name", ""))),
                document_date=document.document_date,
                amount=amount,
                billing=_billing_of(document),
                linked_ejercicio=link[0],
                linked_serie=link[1],
                linked_numero=link[2],
                **_level_fields(getattr(document, "department", ""), getattr(document, "section", ""), labels),
            )
        )
        lines.extend(
            _document_lines(
                life,
                "purchase_delivery",
                f"{document.ejercicio} / {document.serie} / {document.numero}",
                amount,
                document.document_date,
                getattr(document, "lines", ()),
                credit=bool(getattr(document, "credit", False)),
            )
        )
    for document in bought_orders:
        life = _existing_life(company, _text(document.project), tracked)
        if life is None:
            continue
        amount, _missing = _document_amount(document)
        code = _text(getattr(document, "supplier_code", ""))
        key = (_text(document.ejercicio), _text(document.serie), _text(document.numero))
        new_purchases.append(
            ProjectPurchase(
                life=life,
                kind=KIND_COMMITTED if key not in linked else KIND_ORDER,
                ejercicio=document.ejercicio,
                serie=document.serie,
                numero=document.numero,
                supplier_code=code,
                supplier_name=suppliers.get(code, _text(getattr(document, "supplier_name", ""))),
                document_date=document.document_date,
                amount=amount,
                **_level_fields(getattr(document, "department", ""), getattr(document, "section", ""), labels),
            )
        )
        lines.extend(
            _document_lines(
                life,
                "purchase_order",
                f"{document.ejercicio} / {document.serie} / {document.numero}",
                amount,
                document.document_date,
                getattr(document, "lines", ()),
            )
        )
    ProjectMilestone.objects.bulk_create(new_milestones)
    ProjectPurchase.objects.bulk_create(new_purchases)
    ProjectDocumentLine.objects.bulk_create(lines)
    _clear_stale_orders(company, year, month, retained)
    ProjectLife.objects.filter(
        codigo_empresa=company,
        order_date=None,
        lines__isnull=True,
        milestones__isnull=True,
        purchases__isnull=True,
        expenses__isnull=True,
        incomes__isnull=True,
    ).delete()


def _open_orders(company, orders, year, month, retained):
    chosen = []
    for order in orders:
        if str(order.codigo_empresa) != company or is_cancelled(order.status):
            continue
        if not _in_month(order.order_date, year, month):
            continue
        project = _text(order.project)
        if not project or project in retained:
            continue
        chosen.append(order)
    return chosen


def _open_documents(company, documents, year, month, retained):
    chosen = []
    for document in documents:
        if str(document.codigo_empresa) != company or is_cancelled(document.status):
            continue
        if not _in_month(document.document_date, year, month):
            continue
        project = _text(getattr(document, "project", ""))
        if not project or project in retained:
            continue
        chosen.append(document)
    return chosen


def _links_outside_month(company, year, month):
    linked = set()
    stored = ProjectPurchase.objects.filter(life__codigo_empresa=company, kind=KIND_DELIVERY)
    for row in stored:
        if _in_month(row.document_date, year, month) or not _text(row.linked_numero):
            continue
        linked.add((_text(row.linked_ejercicio), _text(row.linked_serie), _text(row.linked_numero)))
    return linked


def _drop_month_lines(company, kind, year, month, retained):
    headers = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=kind,
        position=0,
        line_date__year=year,
        line_date__month=month,
    )
    if retained:
        headers = headers.exclude(life__codigo_proyecto__in=retained)
    keys = list(headers.values_list("life_id", "document_key"))
    headers.delete()
    for life_id, key in keys:
        ProjectDocumentLine.objects.filter(life_id=life_id, kind=kind, document_key=key).delete()


def _projects_with_sale_orders(company):
    """Proyectos que ya tienen pedido de venta. Un albarán no crea un proyecto."""

    codes = set(
        ProjectDocumentLine.objects.filter(
            life__codigo_empresa=company,
            kind="sale_order",
            position=0,
        ).values_list("life__codigo_proyecto", flat=True)
    )
    codes.update(
        ProjectLife.objects.filter(codigo_empresa=company)
        .exclude(order_date=None)
        .values_list("codigo_proyecto", flat=True)
    )
    return {code for code in codes if code}


def _existing_life(company, project, tracked):
    if project not in tracked:
        return None
    return ProjectLife.objects.filter(codigo_empresa=company, codigo_proyecto=project).first()


def _life_for(company, project, customer_code="", customer_name="", order_date=None, order_base=None):
    life = ProjectLife.objects.filter(codigo_empresa=company, codigo_proyecto=project).first()
    if life is None:
        return ProjectLife.objects.create(
            codigo_empresa=company,
            codigo_proyecto=project,
            order_date=order_date,
            order_base=order_base,
            customer_code=customer_code,
            customer_name=customer_name,
            lines_stored=True,
            levels_stored=True,
        )
    if not life.lines_stored:
        life.lines_stored = True
        life.save(update_fields=["lines_stored"])
    return life


def _clear_stale_orders(company, year, month, retained):
    lives = ProjectLife.objects.filter(
        codigo_empresa=company,
        order_date__year=year,
        order_date__month=month,
    )
    if retained:
        lives = lives.exclude(codigo_proyecto__in=retained)
    for life in lives:
        if ProjectDocumentLine.objects.filter(life=life, kind="sale_order", position=0).exists():
            continue
        life.order_date = None
        life.order_base = None
        life.save(update_fields=["order_date", "order_base"])


def _replace_expenses(company, year, month, movements, retained, labels):
    stored = ProjectExpense.objects.filter(
        life__codigo_empresa=company,
        movement_date__year=year,
        movement_date__month=month,
    )
    if retained:
        stored = stored.exclude(life__codigo_proyecto__in=retained)
    stored.delete()
    lives = {
        life.codigo_proyecto: life
        for life in ProjectLife.objects.filter(codigo_empresa=company)
    }
    rows = []
    for movement in movements:
        if str(getattr(movement, "codigo_empresa", "")) != company:
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        if not _in_month(getattr(movement, "movement_date", None), year, month):
            continue
        if not is_cost_account(movement.account_code, movement.account_name):
            continue
        for code, department, section, part in _expense_placements(movement):
            if not code or code in retained or code not in lives:
                continue
            rows.append(
                ProjectExpense(
                    life=lives[code],
                    account_code=_text(movement.account_code),
                    account_name=_text(movement.account_name),
                    movement_date=movement.movement_date,
                    amount=part,
                    **_level_fields(department, section, labels),
                )
            )
    ProjectExpense.objects.bulk_create(rows)


def _replace_ledger(company, year, month, movements):
    bucket = {
        "income_count": 0,
        "income_amount": Decimal("0"),
        "expense_count": 0,
        "expense_amount": Decimal("0"),
        "purchase_count": 0,
        "purchase_amount": Decimal("0"),
    }
    counted = False
    for movement in movements:
        if str(getattr(movement, "codigo_empresa", "")) != company:
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        moment = getattr(movement, "movement_date", None)
        if not _in_month(moment, year, month):
            continue
        if is_income_account(movement.account_code, movement.account_name):
            amount, missing = _side_amount(movement.credit, movement.debit, True)
            kind = "income"
        elif is_expense_account(movement.account_code, movement.account_name):
            amount, missing = _side_amount(movement.debit, movement.credit, True)
            kind = "expense"
        else:
            continue
        if missing:
            continue
        counted = True
        bucket[f"{kind}_count"] += 1
        bucket[f"{kind}_amount"] += amount
    existing = MonthLedger.objects.filter(codigo_empresa=company, ejercicio=year, mes=month)
    if not counted and not existing.exists():
        return
    MonthLedger.objects.update_or_create(
        codigo_empresa=company,
        ejercicio=year,
        mes=month,
        defaults=bucket,
    )


def _replace_books(company, year, month, movements, labels):
    kept = set(ProjectLife.objects.filter(codigo_empresa=company).values_list("codigo_proyecto", flat=True))
    expenses = []
    incomes = []
    for movement in movements:
        if str(getattr(movement, "codigo_empresa", "")) != company:
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        moment = getattr(movement, "movement_date", None)
        if not _in_month(moment, year, month):
            continue
        if is_income_account(movement.account_code, movement.account_name):
            amount, missing = _side_amount(movement.credit, movement.debit, True)
            if not missing:
                incomes.append(
                    BookIncome(
                        codigo_empresa=company,
                        ejercicio=year,
                        account_code=_text(movement.account_code),
                        account_name=_text(movement.account_name),
                        movement_date=moment,
                        amount=amount,
                        project_code=_text(getattr(movement, "project", "")),
                        **_level_fields(getattr(movement, "department", ""), getattr(movement, "section", ""), labels),
                    )
                )
        if not is_expense_account(movement.account_code, movement.account_name):
            continue
        if movement.debit is None and movement.credit is None:
            continue
        header = Decimal(movement.debit or 0) - Decimal(movement.credit or 0)
        placed = Decimal("0")
        if _text(getattr(movement, "project", "")):
            for code, _department, _section, part in _expense_placements(movement):
                if code in kept and part is not None:
                    placed += Decimal(part)
        remainder = header - placed
        if remainder == 0:
            continue
        expenses.append(
            BookExpense(
                codigo_empresa=company,
                ejercicio=year,
                account_code=_text(movement.account_code),
                account_name=_text(movement.account_name),
                movement_date=moment,
                amount=remainder,
                project_code=_text(getattr(movement, "project", "")),
                **_level_fields(getattr(movement, "department", ""), getattr(movement, "section", ""), labels),
            )
        )
    BookExpense.objects.filter(
        codigo_empresa=company,
        ejercicio=year,
        movement_date__year=year,
        movement_date__month=month,
    ).delete()
    BookIncome.objects.filter(
        codigo_empresa=company,
        ejercicio=year,
        movement_date__year=year,
        movement_date__month=month,
    ).delete()
    BookExpense.objects.bulk_create(expenses)
    BookIncome.objects.bulk_create(incomes)


def _replace_tree(company, year, month, movements, orders, purchase_orders, labels):
    dimensions = list(analytical_dimensions())[:4]
    entries = [
        entry
        for entry in tree_income_entries(
            company,
            year,
            movements,
            dimensions,
            _unique_projects(orders or [], purchase_orders or []),
        )
        if _in_month(entry["date"], year, month)
    ]
    names = labels or {}
    rows = []
    for entry in entries:
        path = [
            _display(code, names.get(attribute, {}))
            for (attribute, _title, _group), code in zip(dimensions, entry["codes"])
        ]
        while len(path) < 4:
            path.append("")
        rows.append(
            TreeIncome(
                codigo_empresa=company,
                ejercicio=year,
                movement_date=entry["date"],
                asiento=entry["asiento"][:20],
                account_code=entry["account_code"][:20],
                account_name=entry["account_name"][:120],
                invoice=entry["invoice"][:40],
                amount=entry["amount"],
                nivel_1=path[0][:500],
                nivel_2=path[1][:500],
                nivel_3=path[2][:500],
                nivel_4=path[3][:500],
            )
        )
    TreeIncome.objects.filter(
        codigo_empresa=company,
        ejercicio=year,
        movement_date__year=year,
        movement_date__month=month,
    ).delete()
    TreeIncome.objects.bulk_create(rows, batch_size=500)
    if not rows:
        return
    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=company, ejercicio=year).first()
    if snapshot is not None and not snapshot.tree_income_stored:
        snapshot.tree_income_stored = True
        snapshot.save(update_fields=["tree_income_stored"])
