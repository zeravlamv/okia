from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from apps.access.models import InformationGroup
from apps.erp.documents import fetch_customer_names, fetch_supplier_names
from apps.erp.mapping import is_cancelled, is_closing_entry, is_cost_account, is_expense_account, is_income_account
from apps.margins.format import format_money, format_percent
from apps.margins.hierarchy import _line_amount
from apps.margins.models import (
    MONTH_NAMES,
    PeriodClosure,
    BookExpense,
    BookIncome,
    ProjectDocumentLine,
    ProjectExpense,
    ProjectIncome,
    ProjectLife,
    ProjectMilestone,
    ProjectOrderShare,
    ProjectPurchase,
)
from apps.margins.services import _side_amount, in_period, movement_in_period, sale_price

BILLING_INVOICED = "invoiced"
BILLING_OPEN = "open"
BILLING_UNKNOWN = "unknown"
KIND_DELIVERY = "delivery"
KIND_COMMITTED = "committed"
KIND_ORDER = "order"
_BILLING_LABELS = {
    BILLING_INVOICED: "Facturado",
    BILLING_OPEN: "No facturado",
    BILLING_UNKNOWN: "Sin dato de facturación",
}


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def _billing_of(document):
    billing = _text(getattr(document, "billing", ""))
    if billing in _BILLING_LABELS:
        return billing
    return BILLING_UNKNOWN


def _document_amount(document):
    amount, incomplete = sale_price(document)
    if amount is None:
        return None, True
    if getattr(document, "credit", False):
        amount = -Decimal(amount)
    return Decimal(amount), incomplete


def progression_figures(order_base, milestones):
    """Albaranado, progresión y pendiente a partir de la base del pedido y los hitos.

    Un importe vacío no se convierte en cero. Si la base es cero o falta, el porcentaje no aplica.
    """

    delivered = Decimal("0")
    parts = {BILLING_INVOICED: Decimal("0"), BILLING_OPEN: Decimal("0"), BILLING_UNKNOWN: Decimal("0")}
    incomplete = False
    for billing, amount in milestones:
        if amount is None:
            incomplete = True
            continue
        value = Decimal(amount)
        delivered += value
        parts[billing] += value
    if order_base is None:
        percent = None
        pending = None
        incomplete = True
    else:
        base = Decimal(order_base)
        percent = None if base == 0 else delivered / base * Decimal("100")
        pending = Decimal("0") if delivered >= base else base - delivered
    return {
        "delivered": delivered,
        "invoiced": parts[BILLING_INVOICED],
        "open": parts[BILLING_OPEN],
        "unknown": parts[BILLING_UNKNOWN],
        "progression": percent,
        "part_percents": {
            key: (None if order_base is None or Decimal(order_base) == 0 else value / Decimal(order_base) * Decimal("100"))
            for key, value in parts.items()
        },
        "pending": pending,
        "incomplete": incomplete,
    }


def _purchase_order_pending(purchases):
    """Lo que falta por albaranar en cada pedido. Si el albarán lo cubre, el pendiente es cero."""

    covered = {}
    for row in purchases:
        if row.kind != KIND_DELIVERY or not _text(row.linked_numero) or row.amount is None:
            continue
        key = (_text(row.linked_ejercicio), _text(row.linked_serie), _text(row.linked_numero))
        covered[key] = covered.get(key, Decimal("0")) + Decimal(row.amount)
    pending = Decimal("0")
    for row in purchases:
        if row.kind not in (KIND_ORDER, KIND_COMMITTED) or row.amount is None:
            continue
        gap = Decimal(row.amount) - covered.get(
            (_text(row.ejercicio), _text(row.serie), _text(row.numero)),
            Decimal("0"),
        )
        if gap > 0:
            pending += gap
    return pending


def _purchase_invoice_pending(purchases):
    """Albaranes de compra no facturados. Vacío si esa marca aún no se ha guardado."""

    rows = [row for row in purchases if row.kind == KIND_DELIVERY]
    if any(not _text(getattr(row, "billing", "")) for row in rows):
        return None
    total = Decimal("0")
    for row in rows:
        if row.billing == BILLING_OPEN and row.amount is not None:
            total += Decimal(row.amount)
    return total


def bar_end(order_date, order_base, delivered, dated_marks, today):
    """El final de la barra es el último hito si el pedido ya está cubierto. Si no, es hoy."""

    covered = (
        order_base is not None
        and delivered is not None
        and Decimal(delivered) >= Decimal(order_base)
        and bool(dated_marks)
    )
    if covered:
        return max(dated_marks)
    if order_date is not None and order_date > today:
        return order_date
    return today


def life_end(order_date, order_base, delivered, dated_marks, other_dates, today):
    """La vida llega al último documento, aunque caiga en otro ejercicio.

    Si el pedido sigue abierto, también llega hasta hoy.
    """

    moments = [bar_end(order_date, order_base, delivered, dated_marks, today)]
    moments.extend(moment for moment in other_dates if moment is not None)
    moments = [moment for moment in moments if moment is not None]
    if not moments:
        return None
    return max(moments)


def _month_totals(rows, date_name):
    totals = defaultdict(lambda: Decimal("0"))
    for row in rows:
        moment = getattr(row, date_name, None)
        amount = getattr(row, "amount", None)
        if moment is None or amount is None:
            continue
        totals[_month_start(moment)] += Decimal(amount)
    return totals


def _evolution(order_date, end, deliveries, purchases, expenses, show_deliveries, show_purchases, show_expenses):
    """Cada mes arrastra lo acumulado desde el pedido. El margen es ese albaranado menos el gasto."""

    if order_date is None or end is None:
        return []
    delivered = _month_totals(deliveries, "delivery_date")
    bought = _month_totals(purchases, "movement_date")
    spent = _month_totals(expenses, "movement_date")
    show_margin = show_deliveries and show_expenses
    running_delivered = Decimal("0")
    running_purchases = Decimal("0")
    running_expenses = Decimal("0")
    raw = []
    started = False
    for start in month_span(order_date, end):
        running_delivered += delivered.get(start, Decimal("0"))
        running_purchases += bought.get(start, Decimal("0"))
        running_expenses += spent.get(start, Decimal("0"))
        if not started and running_delivered == 0 and running_purchases == 0 and running_expenses == 0:
            continue
        started = True
        raw.append(
            (
                start,
                running_delivered,
                running_purchases,
                running_expenses,
                running_delivered - running_purchases - running_expenses,
            )
        )
    peak = Decimal("0")
    for _start, cum_delivered, cum_purchases, cum_expenses, margin in raw:
        if show_deliveries:
            peak = max(peak, abs(cum_delivered))
        if show_purchases:
            peak = max(peak, abs(cum_purchases))
        if show_expenses:
            peak = max(peak, abs(cum_expenses))
        if show_margin:
            peak = max(peak, abs(margin))

    def bar(name, tone, value):
        width = 0
        if value and peak:
            width = max(round(abs(float(value)) / float(peak) * 100), 4)
        return {"name": name, "tone": tone, "width": width, "negative": value < 0, "amount": format_money(value)}

    months = []
    for start, cum_delivered, cum_purchases, cum_expenses, margin in raw:
        series = []
        if show_deliveries:
            series.append(bar("Albaranado", "venta", cum_delivered))
        if show_expenses:
            series.append(bar("Gastos", "gasto", cum_expenses))
        if show_margin:
            series.append(bar("Margen", "margen", margin))
        months.append({"label": start.strftime("%m/%Y"), "margin": margin, "series": series})
    return months


def _month_start(moment):
    return date(moment.year, moment.month, 1)


def _next_month(moment):
    if moment.month == 12:
        return date(moment.year + 1, 1, 1)
    return date(moment.year, moment.month + 1, 1)


def _month_last(moment):
    return date(moment.year, moment.month, monthrange(moment.year, moment.month)[1])


def month_span(start, end):
    if start is None or end is None:
        return []
    cursor = _month_start(start)
    last = _month_start(end)
    months = []
    while cursor <= last:
        months.append(cursor)
        cursor = _next_month(cursor)
    return months


def _customer_of(orders, customers):
    codes = []
    for order in orders:
        code = _text(getattr(order, "codigo_cliente", ""))
        if code and code not in codes:
            codes.append(code)
    if not codes:
        return "", ""
    if len(codes) == 1:
        code = codes[0]
        return code, _text((customers or {}).get(code, ""))
    return ", ".join(codes), ""


def _lookup(code, names):
    code = _text(code)
    if not code:
        return "", ""
    return code, _text((names or {}).get(code, ""))


def _level_fields(department, section, labels):
    labels = labels or {}
    department_code, department_name = _lookup(department, labels.get("department"))
    section_code, section_name = _lookup(section, labels.get("section"))
    return {
        "department_code": department_code,
        "department_name": department_name,
        "section_code": section_code,
        "section_name": section_name,
    }


def _store_project_income(company, project_codes, movements, labels):
    """Guarda el grupo 7 de AnaMovimientos en los proyectos que se acaban de actualizar."""

    lives = {
        life.codigo_proyecto: life
        for life in ProjectLife.objects.filter(codigo_empresa=company, codigo_proyecto__in=project_codes)
    }
    if not lives:
        return
    ProjectIncome.objects.filter(life__in=list(lives.values())).delete()
    rows = []
    for movement in movements:
        if str(getattr(movement, "codigo_empresa", "")) != company:
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        if not str(getattr(movement, "account_code", "") or "").strip().startswith("7"):
            continue
        for code, department, section, part in _income_placements(movement):
            life = lives.get(code)
            if life is None:
                continue
            rows.append(
                ProjectIncome(
                    life=life,
                    account_code=_text(movement.account_code),
                    account_name=_text(movement.account_name),
                    movement_date=movement.movement_date,
                    amount=part,
                    **_level_fields(department, section, labels),
                )
            )
    ProjectIncome.objects.bulk_create(rows)
    ProjectLife.objects.filter(pk__in=[life.pk for life in lives.values()]).update(income_stored=True)


def replace_book_expenses(company, year, movements, chosen, labels=None):
    """Guarda el grupo 6 del libro que no quedó en las compras de una ficha.

    La ficha puede ser de otro ejercicio: su compra sigue en la gráfica del mes
    del apunte y no debe repetirse en el detalle de gastos.
    """

    company = str(company)
    year = int(year)
    kept = {_text(code) for code in chosen}
    kept.update(
        ProjectLife.objects.filter(codigo_empresa=company).values_list("codigo_proyecto", flat=True)
    )
    rows = []
    for movement in movements:
        if str(getattr(movement, "codigo_empresa", "")) != company:
            continue
        if not movement_in_period(movement, year) or is_closing_entry(getattr(movement, "comment", "")):
            continue
        moment = getattr(movement, "movement_date", None)
        if moment is None or not is_expense_account(movement.account_code, movement.account_name):
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
        rows.append(
            BookExpense(
                codigo_empresa=company,
                ejercicio=year,
                account_code=_text(movement.account_code),
                account_name=_text(movement.account_name),
                movement_date=moment,
                amount=remainder,
                project_code=_text(getattr(movement, "project", "")),
                **_level_fields(
                    getattr(movement, "department", ""),
                    getattr(movement, "section", ""),
                    labels,
                ),
            )
        )
    BookExpense.objects.filter(codigo_empresa=company, ejercicio=year).delete()
    BookExpense.objects.bulk_create(rows)


def replace_book_incomes(company, year, movements, labels=None):
    """Guarda el grupo 7 del libro, por la fecha del apunte.

    El importe es el de la cabecera, el mismo que suma el mes: abono menos cargo.
    """

    company = str(company)
    year = int(year)
    rows = []
    for movement in movements:
        if str(getattr(movement, "codigo_empresa", "")) != company:
            continue
        if not movement_in_period(movement, year) or is_closing_entry(getattr(movement, "comment", "")):
            continue
        moment = getattr(movement, "movement_date", None)
        if moment is None or not is_income_account(movement.account_code, movement.account_name):
            continue
        amount, missing = _side_amount(movement.credit, movement.debit, True)
        if missing:
            continue
        rows.append(
            BookIncome(
                codigo_empresa=company,
                ejercicio=year,
                account_code=_text(movement.account_code),
                account_name=_text(movement.account_name),
                movement_date=moment,
                amount=amount,
                project_code=_text(getattr(movement, "project", "")),
                **_level_fields(
                    getattr(movement, "department", ""),
                    getattr(movement, "section", ""),
                    labels,
                ),
            )
        )
    BookIncome.objects.filter(codigo_empresa=company, ejercicio=year).delete()
    BookIncome.objects.bulk_create(rows, batch_size=500)


def _income_placements(movement):
    if movement.debit is None and movement.credit is None:
        signed = None
    else:
        signed = Decimal(movement.credit or 0) - Decimal(movement.debit or 0)
    return _placements(movement, signed)


def _expense_placements(movement):
    """Cada fila analítica conserva su importe. Sin filas, vale el apunte entero."""

    if movement.debit is None and movement.credit is None:
        signed = None
    else:
        signed = Decimal(movement.debit or 0) - Decimal(movement.credit or 0)
    return _placements(movement, signed)


def _placements(movement, signed):
    coded = [
        item
        for item in movement.slices
        if any(
            _text(getattr(item, name, ""))
            for name in ("channel", "delegation", "department", "project", "section")
        )
    ]
    if not coded:
        return [
            (
                _text(movement.project),
                _text(getattr(movement, "department", "")),
                _text(getattr(movement, "section", "")),
                signed,
            )
        ]
    rows = []
    for item in coded:
        rows.append(
            (
                _text(getattr(item, "project", "")) or _text(movement.project),
                _text(getattr(item, "department", "")),
                _text(getattr(item, "section", "")),
                _line_amount(signed, item.amount),
            )
        )
    return rows


def _label(code, name, show_name):
    code = _text(code)
    name = _text(name)
    if not show_name or not name or name == code:
        return code or "Sin dato"
    return f"{code} — {name}"


def _sum_known(rows):
    total = Decimal("0")
    incomplete = False
    for amount in rows:
        if amount is None:
            incomplete = True
            continue
        total += Decimal(amount)
    return total, incomplete


def closed_months(company, year):
    """Meses cerrados de una empresa y un ejercicio. Sin fila, el mes está abierto."""

    return set(
        PeriodClosure.objects.filter(
            codigo_empresa=str(company),
            ejercicio=year,
            cerrado=True,
        ).values_list("mes", flat=True)
    )


def set_exercise_closure(company, year, closed, user):
    """Marca los doce meses de un ejercicio. No lee el origen ni actualiza fichas."""

    for month in range(1, 13):
        PeriodClosure.objects.update_or_create(
            codigo_empresa=str(company),
            ejercicio=int(year),
            mes=month,
            defaults={"cerrado": closed, "changed_by": user},
        )


def retained_projects(company, year, orders, closed=None):
    """Un proyecto queda retenido entero si algún pedido vigente del ejercicio cae en un mes cerrado.

    Un pedido anulado no cuenta. Sin fecha de pedido, ese pedido no retiene.
    """

    if closed is None:
        closed = closed_months(company, year)
    if not closed:
        return set()
    retained = set()
    company = str(company)
    for order in orders:
        if order.codigo_empresa != company or is_cancelled(order.status) or not in_period(order, year):
            continue
        project = _text(order.project)
        if not project or order.order_date is None:
            continue
        if order.order_date.month in closed:
            retained.add(project)
    return retained


def refresh_project_lives(
    company,
    year,
    orders,
    sales_deliveries,
    purchase_orders,
    purchase_deliveries,
    movements,
    labels=None,
    customers=None,
    on_project=None,
    period_movements=None,
):
    """Sustituye la vida de los proyectos cuyo pedido entra en el ejercicio. El resto de fechas se conserva."""

    retained = retained_projects(company, year, orders)
    chosen = {}
    for order in orders:
        if order.codigo_empresa != str(company) or is_cancelled(order.status) or not in_period(order, year):
            continue
        project = _text(order.project)
        if not project or project in retained:
            continue
        chosen.setdefault(project, []).append(order)
    names = {}
    for document in list(purchase_orders) + list(purchase_deliveries):
        code = _text(getattr(document, "supplier_code", ""))
        label = _text(getattr(document, "supplier_name", ""))
        if code and label:
            names[code] = label
    if not settings.SAMPLE_ERP:
        names.update(fetch_supplier_names(company))
    client_names = dict(customers or {})
    if not settings.SAMPLE_ERP:
        client_names.update(fetch_customer_names(company))
    with transaction.atomic():
        ProjectLife.objects.filter(codigo_empresa=str(company), codigo_proyecto__in=list(chosen)).delete()
        if on_project is not None:
            on_project(0, len(chosen), "")
        for index, (project, project_orders) in enumerate(chosen.items(), start=1):
            _store_life(
                str(company),
                project,
                project_orders,
                sales_deliveries,
                purchase_orders,
                purchase_deliveries,
                movements,
                names,
                labels or {},
                client_names,
            )
            if on_project is not None:
                on_project(index, len(chosen), _months_label(project_orders))
        if period_movements is not None:
            _store_project_income(str(company), set(chosen), period_movements, labels or {})


def _months_label(orders):
    names = dict(MONTH_NAMES)
    months = sorted({order.order_date.month for order in orders if getattr(order, "order_date", None)})
    return ", ".join(names[month] for month in months if month in names)


def _document_lines(life, kind, document_key, header_amount, header_date, lines, credit=False):
    stored = [
        ProjectDocumentLine(
            life=life,
            kind=kind,
            document_key=document_key,
            position=0,
            description="",
            amount=header_amount,
            line_date=header_date,
        )
    ]
    for index, line in enumerate(lines or [], start=1):
        amount = getattr(line, "base", None)
        if amount is not None:
            amount = Decimal(amount)
            if credit:
                amount = -amount
        label = _text(getattr(line, "article", "")) or f"Línea {index}"
        stored.append(
            ProjectDocumentLine(
                life=life,
                kind=kind,
                document_key=document_key,
                position=index,
                description=label[:160],
                amount=amount,
            )
        )
    return stored


def _store_life(
    company, project, orders, sales_deliveries, purchase_orders, purchase_deliveries, movements, names, labels, customers
):
    dates = [order.order_date for order in orders if order.order_date is not None]
    bases = []
    incomplete = False
    for order in orders:
        amount, missing = sale_price(order)
        if missing or amount is None:
            incomplete = True
        if amount is not None:
            bases.append(Decimal(amount))
    order_base = sum(bases, Decimal("0")) if bases else None
    if incomplete and not bases:
        order_base = None
    customer_code, customer_name = _customer_of(orders, customers)
    life = ProjectLife.objects.create(
        codigo_empresa=company,
        codigo_proyecto=project,
        order_date=min(dates) if dates else None,
        order_base=order_base,
        customer_code=customer_code,
        customer_name=customer_name,
        incomplete=incomplete,
        levels_stored=True,
        lines_stored=True,
    )
    document_lines = []
    order_shares = []
    for order in orders:
        amount, _missing = sale_price(order)
        order_shares.append(
            ProjectOrderShare(
                life=life,
                amount=None if amount is None else Decimal(amount),
                **_level_fields(getattr(order, "department", ""), getattr(order, "section", ""), labels),
            )
        )
        document_lines.extend(
            _document_lines(
                life,
                "sale_order",
                f"{order.ejercicio} / {order.serie} / {order.numero}",
                None if amount is None else Decimal(amount),
                order.order_date,
                order.lines,
            )
        )
    purchase_headers = {}
    for document in purchase_orders:
        if document.codigo_empresa != company or is_cancelled(document.status):
            continue
        purchase_headers[(_text(document.ejercicio), _text(document.serie), _text(document.numero))] = document
    milestones = []
    for document in sales_deliveries:
        if document.codigo_empresa != company or _text(getattr(document, "project", "")) != project:
            continue
        if is_cancelled(document.status):
            continue
        amount, missing = _document_amount(document)
        if missing:
            life.incomplete = True
        milestones.append(
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
        document_lines.extend(
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
    purchases = []
    linked = set()
    for document in purchase_deliveries:
        if document.codigo_empresa != company or _text(getattr(document, "project", "")) != project:
            continue
        if is_cancelled(document.status):
            continue
        amount, missing = _document_amount(document)
        if missing:
            life.incomplete = True
        link = (
            _text(getattr(document, "linked_ejercicio", "")),
            _text(getattr(document, "linked_serie", "")),
            _text(getattr(document, "linked_numero", "")),
        )
        if link[2]:
            linked.add(link)
        header = purchase_headers.get(link) if link[2] else None
        department = _text(getattr(document, "department", ""))
        section = _text(getattr(document, "section", ""))
        if header is not None:
            if not department:
                department = _text(getattr(header, "department", ""))
            if not section:
                section = _text(getattr(header, "section", ""))
        code = _text(getattr(document, "supplier_code", ""))
        purchases.append(
            ProjectPurchase(
                life=life,
                kind=KIND_DELIVERY,
                ejercicio=document.ejercicio,
                serie=document.serie,
                numero=document.numero,
                supplier_code=code,
                supplier_name=names.get(code, _text(getattr(document, "supplier_name", ""))),
                document_date=document.document_date,
                amount=amount,
                billing=_billing_of(document),
                linked_ejercicio=link[0],
                linked_serie=link[1],
                linked_numero=link[2],
                **_level_fields(department, section, labels),
            )
        )
        document_lines.extend(
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
    for document in purchase_orders:
        if document.codigo_empresa != company or _text(getattr(document, "project", "")) != project:
            continue
        if is_cancelled(document.status):
            continue
        key = (_text(document.ejercicio), _text(document.serie), _text(document.numero))
        amount, missing = _document_amount(document)
        if missing:
            life.incomplete = True
        code = _text(getattr(document, "supplier_code", ""))
        purchases.append(
            ProjectPurchase(
                life=life,
                kind=KIND_COMMITTED if key not in linked else KIND_ORDER,
                ejercicio=document.ejercicio,
                serie=document.serie,
                numero=document.numero,
                supplier_code=code,
                supplier_name=names.get(code, _text(getattr(document, "supplier_name", ""))),
                document_date=document.document_date,
                amount=amount,
                **_level_fields(getattr(document, "department", ""), getattr(document, "section", ""), labels),
            )
        )
        document_lines.extend(
            _document_lines(
                life,
                "purchase_order",
                f"{document.ejercicio} / {document.serie} / {document.numero}",
                amount,
                document.document_date,
                getattr(document, "lines", ()),
            )
        )
    expenses = []
    for movement in movements:
        if movement.codigo_empresa != company or is_closing_entry(movement.comment):
            continue
        if not is_cost_account(movement.account_code, movement.account_name):
            continue
        for code, department, section, part in _expense_placements(movement):
            if code != project:
                continue
            if part is None:
                life.incomplete = True
            expenses.append(
                ProjectExpense(
                    life=life,
                    account_code=_text(movement.account_code),
                    account_name=_text(movement.account_name),
                    movement_date=movement.movement_date,
                    amount=part,
                    **_level_fields(department, section, labels),
                )
            )
    if life.incomplete:
        life.save(update_fields=["incomplete"])
    ProjectOrderShare.objects.bulk_create(order_shares)
    ProjectMilestone.objects.bulk_create(milestones)
    ProjectPurchase.objects.bulk_create(purchases)
    ProjectExpense.objects.bulk_create(expenses)
    ProjectDocumentLine.objects.bulk_create(document_lines)
    return life


def _money(value):
    if value is None:
        return "—"
    return format_money(value)


def _lines_of(stored, kind, document_key):
    return [
        {"description": line.description or "Línea", "amount": _money(line.amount)}
        for line in stored
        if line.kind == kind and line.document_key == document_key and line.position > 0
    ]


def _sale_order_documents(life, stored, show_clients):
    party = _label(life.customer_code, life.customer_name, show_clients) if life.customer_code else ""
    if life.lines_stored:
        headers = [line for line in stored if line.kind == "sale_order" and line.position == 0]
        headers.sort(key=lambda line: (line.line_date or date.min, line.document_key))
        return [
            {
                "date": _date_text(line.line_date),
                "identity": line.document_key,
                "party": party,
                "amount": _money(line.amount),
                "status": "Pedido",
                "lines": _lines_of(stored, "sale_order", line.document_key),
            }
            for line in headers
        ]
    if life.order_base is None and life.order_date is None:
        return []
    return [
        {
            "date": _date_text(life.order_date),
            "identity": "Pedido",
            "party": party,
            "amount": _money(life.order_base),
            "status": "Pedido",
            "lines": [],
        }
    ]


def _delivery_documents(rows, kind, stored, party):
    documents = []
    for row in rows:
        key = f"{row.ejercicio} / {row.serie} / {row.numero}"
        moment = getattr(row, "delivery_date", None) or getattr(row, "document_date", None)
        documents.append(
            {
                "date": _date_text(moment),
                "identity": key,
                "party": party(row),
                "amount": _money(row.amount),
                "status": "",
                "lines": _lines_of(stored, kind, key),
                "sort": moment or date.min,
            }
        )
    documents.sort(key=lambda item: (item["sort"], item["identity"]))
    for item in documents:
        del item["sort"]
    return documents


def _donut(order_base, purchases, expenses, margin, show_purchases, show_expenses, show_margin):
    parts = []
    if show_purchases and purchases and purchases > 0:
        parts.append(("Compras", purchases, "#2f6b45"))
    if show_expenses and expenses and expenses > 0:
        parts.append(("Gastos", expenses, "#8a5a00"))
    if show_margin and margin is not None and margin > 0:
        parts.append(("Margen", margin, "#1c1c1c"))
    used = sum((amount for _label, amount, _color in parts), Decimal("0"))
    whole = Decimal(order_base) if order_base not in (None, 0) else used
    if used > whole and used:
        whole = used
    ring = 490.088
    gap = 4.0
    offset = 0.0
    slices = []
    for label, amount, color in parts:
        length = float(amount / whole) * ring if whole else 0.0
        paint = length
        shift = 0.0
        if length > gap * 2:
            paint = length - gap
            shift = gap / 2
        slices.append(
            {
                "label": label,
                "amount": format_money(amount),
                "percent": format_percent(_ratio(amount, whole)),
                "color": color,
                "length": f"{paint:.2f}",
                "rest": f"{ring - paint:.2f}",
                "offset": f"{-(offset + shift):.2f}",
            }
        )
        offset += length
    return slices


def _progression_width(percent):
    if percent is None:
        return ""
    value = Decimal(percent)
    if value < 0:
        value = Decimal("0")
    elif value > Decimal("100"):
        value = Decimal("100")
    return f"{value:.2f}"


def _date_text(moment):
    if moment is None:
        return ""
    return moment.strftime("%d/%m/%Y")


def _grouped(rows, show_name):
    grouped = {}
    for code, name, amount in rows:
        bucket = grouped.setdefault(code or "", {"name": name, "amount": Decimal("0"), "incomplete": False})
        if name:
            bucket["name"] = name
        if amount is None:
            bucket["incomplete"] = True
            continue
        bucket["amount"] += Decimal(amount)
    result = [
        {
            "label": _label(code, bucket["name"], show_name),
            "amount": bucket["amount"],
            "amount_text": format_money(bucket["amount"]),
            "incomplete": bucket["incomplete"],
        }
        for code, bucket in grouped.items()
    ]
    result.sort(key=lambda item: (-item["amount"], item["label"].casefold()))
    return result


def _ratio(part, whole):
    if part is None or whole is None or Decimal(whole) == 0:
        return None
    return Decimal(part) / Decimal(whole) * Decimal("100")


def _cost_origins(department, section, rows):
    """Fecha, cuenta e importe de las filas de AnaMovimientos de ese departamento y esa sección."""

    origins = []
    for row in rows:
        if _text(row.department_code) != department or _text(row.section_code) != section:
            continue
        origins.append(
            {
                "date": _date_text(row.movement_date),
                "origin": _label(row.account_code, row.account_name, True),
                "amount": _money(row.amount),
                "sort": row.movement_date or date.min,
            }
        )
    origins.sort(key=lambda item: (item["sort"], item["origin"].casefold()))
    for item in origins:
        del item["sort"]
    return origins


def _breakdown(expenses, show_departments, show_sections):
    """La analítica de costes solo agrupa los gastos de AnaMovimientos."""

    buckets = {}

    def add(row):
        key = (_text(row.department_code), _text(row.section_code))
        bucket = buckets.setdefault(
            key,
            {"department_name": "", "section_name": "", "expenses": Decimal("0")},
        )
        if row.department_name:
            bucket["department_name"] = row.department_name
        if row.section_name:
            bucket["section_name"] = row.section_name
        if row.amount is None:
            return
        bucket["expenses"] += Decimal(row.amount)

    for row in expenses:
        add(row)
    result = []
    for (department, section), bucket in sorted(buckets.items(), key=lambda item: (item[0][0].casefold(), item[0][1].casefold())):
        if bucket["expenses"] == 0:
            continue
        result.append(
            {
                "department": _label(department, bucket["department_name"], show_departments),
                "section": _label(section, bucket["section_name"], show_sections),
                "expenses": _money(bucket["expenses"]),
                "origins": _cost_origins(department, section, expenses),
            }
        )
    return result


def load_project(company, code, groups, today):
    """Presenta la vida guardada. Si no existe, no la calcula."""

    life = (
        ProjectLife.objects.filter(codigo_empresa=str(company), codigo_proyecto=str(code))
        .prefetch_related("milestones", "purchases", "expenses", "order_shares", "lines")
        .first()
    )
    if life is None:
        return None
    allowed = set(groups)
    show_order = InformationGroup.PEDIDOS_VENTA in allowed
    show_deliveries = InformationGroup.ALBARANES_VENTA in allowed
    show_purchase_orders = InformationGroup.PEDIDOS_COMPRA in allowed
    show_purchase_deliveries = InformationGroup.ALBARANES_COMPRA in allowed
    show_expenses = InformationGroup.MOVIMIENTOS in allowed
    show_supplier_name = InformationGroup.PROVEEDORES in allowed
    show_clients = InformationGroup.CLIENTES in allowed
    show_departments = InformationGroup.DEPARTAMENTOS in allowed
    show_sections = InformationGroup.SECCIONES in allowed
    milestones = list(life.milestones.all())
    purchases = list(life.purchases.all())
    expenses = list(life.expenses.all())
    figures = progression_figures(
        life.order_base,
        [(row.billing, row.amount) for row in milestones],
    )
    delivered_dates = [row.delivery_date for row in milestones if row.delivery_date is not None]
    other_dates = [
        row.document_date
        for row in purchases
        if row.kind == KIND_DELIVERY and row.document_date is not None
    ]
    other_dates.extend(row.movement_date for row in expenses if row.movement_date is not None)
    end = life_end(
        life.order_date,
        life.order_base,
        figures["delivered"],
        delivered_dates,
        other_dates,
        today,
    )
    dated = sorted((row for row in milestones if row.delivery_date is not None), key=lambda row: (row.delivery_date, row.numero))
    running = Decimal("0")
    milestone_rows = []
    for row in dated:
        if row.amount is not None:
            running += Decimal(row.amount)
        percent = None
        if life.order_base not in (None, 0) and row.amount is not None:
            percent = running / Decimal(life.order_base) * Decimal("100")
        milestone_rows.append(
            {
                "date": _date_text(row.delivery_date),
                "amount": _money(row.amount),
                "billing": _BILLING_LABELS.get(row.billing, _BILLING_LABELS[BILLING_UNKNOWN]),
                "percent": format_percent(percent),
            }
        )
    months = []
    for start in month_span(life.order_date, end):
        last = _month_last(start)
        cumulative = progression_figures(
            life.order_base,
            [(row.billing, row.amount) for row in dated if row.delivery_date <= last],
        )
        month_delivered = [
            row.amount
            for row in dated
            if _month_start(row.delivery_date) == start
        ]
        month_expenses = [
            row.amount
            for row in expenses
            if row.movement_date is not None and _month_start(row.movement_date) == start
        ]
        delivered_total, _delivered_missing = _sum_known(month_delivered)
        expense_total_month, _expense_missing = _sum_known(month_expenses)
        visible = []
        if show_deliveries:
            visible.extend([cumulative["delivered"], cumulative["invoiced"], cumulative["open"]])
        if show_expenses:
            visible.append(expense_total_month)
        if not visible or all(value == 0 for value in visible):
            continue
        months.append(
            {
                "label": start.strftime("%m/%Y"),
                "cumulative": format_money(cumulative["delivered"]),
                "invoiced": format_money(cumulative["invoiced"]),
                "open": format_money(cumulative["open"]),
                "percent": format_percent(cumulative["progression"]),
                "purchases": format_money(Decimal("0")),
                "expenses": format_money(expense_total_month),
                "chart_delivered": delivered_total,
                "chart_purchases": Decimal("0"),
                "chart_expenses": expense_total_month,
            }
        )
    show_chart_margin = show_deliveries and show_expenses
    for month in months:
        month["chart_margin"] = month["chart_delivered"] - month["chart_purchases"] - month["chart_expenses"]
    peak = Decimal("0")
    for month in months:
        if show_deliveries:
            peak = max(peak, abs(month["chart_delivered"]))
        if show_expenses:
            peak = max(peak, abs(month["chart_purchases"]), abs(month["chart_expenses"]))
        if show_chart_margin:
            peak = max(peak, abs(month["chart_margin"]))

    def _parts(value):
        if not value or not peak:
            return 0, 0
        height = max(round(abs(float(value)) / float(peak) * 100), 8)
        if value > 0:
            return height, 0
        return 0, height

    for month in months:
        delivered_up, delivered_down = _parts(month["chart_delivered"])
        purchase_up, purchase_down = _parts(month["chart_purchases"])
        expense_up, expense_down = _parts(month["chart_expenses"])
        margin_up, margin_down = _parts(month["chart_margin"])
        month["delivered_up"] = delivered_up if show_deliveries else 0
        month["delivered_down"] = delivered_down if show_deliveries else 0
        month["purchase_up"] = purchase_up if show_expenses else 0
        month["purchase_down"] = purchase_down if show_expenses else 0
        month["expense_up"] = expense_up if show_expenses else 0
        month["expense_down"] = expense_down if show_expenses else 0
        month["margin_up"] = margin_up if show_chart_margin else 0
        month["margin_down"] = margin_down if show_chart_margin else 0
        month["delivered_text"] = format_money(month["chart_delivered"])
        month["purchase_text"] = month["purchases"]
        month["expense_text"] = month["expenses"]
        month["margin_text"] = format_money(month["chart_margin"])
    deliveries = [row for row in purchases if row.kind == KIND_DELIVERY]
    committed = [row for row in purchases if row.kind == KIND_COMMITTED]
    order_documents = [row for row in purchases if row.kind in (KIND_ORDER, KIND_COMMITTED)]
    order_total, _order_missing = _sum_known(row.amount for row in order_documents)
    order_count = len(order_documents)
    purchase_total, purchase_missing = _sum_known(row.amount for row in deliveries)
    expense_total, expense_missing = _sum_known(row.amount for row in expenses)
    years = set()
    if life.order_date is not None:
        years.add(life.order_date.year)
    for row in milestones + purchases + expenses:
        moment = getattr(row, "delivery_date", None) or getattr(row, "document_date", None) or getattr(row, "movement_date", None)
        if moment is not None:
            years.add(moment.year)
        elif getattr(row, "ejercicio", None):
            years.add(int(row.ejercicio))
    undated = []
    if show_deliveries:
        undated.extend(
            f"Albarán de venta {row.ejercicio} / {row.serie} / {row.numero}"
            for row in milestones
            if row.delivery_date is None
        )
    if show_purchase_deliveries:
        undated.extend(
            f"Albarán de compra {row.ejercicio} / {row.serie} / {row.numero}"
            for row in deliveries
            if row.document_date is None
        )
    if show_expenses:
        undated.extend(
            f"Gasto {row.account_code}"
            for row in expenses
            if row.movement_date is None
        )
    marks = []
    if show_deliveries:
        for row, shown in zip(dated, milestone_rows):
            marks.append(
                {
                    "sort": row.delivery_date,
                    "date": shown["date"],
                    "kind": "venta",
                    "detail": shown["billing"],
                    "amount": shown["amount"],
                    "percent": shown["percent"],
                }
            )
    if show_purchase_deliveries:
        for row in deliveries:
            if row.document_date is None:
                continue
            marks.append(
                {
                    "sort": row.document_date,
                    "date": _date_text(row.document_date),
                    "kind": "compra",
                    "detail": _label(row.supplier_code, row.supplier_name, show_supplier_name),
                    "amount": _money(row.amount),
                    "percent": "",
                }
            )
    marks.sort(key=lambda item: (item["sort"], 0 if item["kind"] == "venta" else 1))
    for item in marks:
        del item["sort"]
    committed_sum, _committed_missing = _sum_known(row.amount for row in committed)
    purchase_pending = _purchase_order_pending(purchases)
    purchase_invoice_pending = _purchase_invoice_pending(purchases)
    show_deviation = show_order and show_deliveries
    deviation = None
    if show_deviation and life.order_base is not None:
        deviation = figures["delivered"] - Decimal(life.order_base)
    show_net_margin = show_deliveries and show_expenses
    net_margin = None
    if show_net_margin:
        net_margin = figures["delivered"] - expense_total
    slices = []
    if life.levels_stored and show_expenses:
        slices = _breakdown(expenses, show_departments, show_sections)
    stored_lines = list(life.lines.all()) if life.lines_stored else []
    sale_order_docs = _sale_order_documents(life, stored_lines, show_clients) if show_order else []
    sale_delivery_docs = (
        _delivery_documents(
            milestones,
            "sale_delivery",
            stored_lines,
            lambda row: _BILLING_LABELS.get(row.billing, ""),
        )
        if show_deliveries
        else []
    )
    purchase_delivery_docs = (
        _delivery_documents(
            deliveries,
            "purchase_delivery",
            stored_lines,
            lambda row: _label(row.supplier_code, row.supplier_name, show_supplier_name),
        )
        if show_purchase_deliveries
        else []
    )
    donut = _donut(
        life.order_base,
        Decimal("0"),
        expense_total,
        net_margin,
        False,
        show_expenses,
        show_net_margin,
    )
    evolution = _evolution(
        life.order_date,
        end,
        dated,
        [],
        expenses,
        show_deliveries,
        False,
        show_expenses,
    )
    return {
        "code": life.codigo_proyecto,
        "updated_at": life.updated_at,
        "incomplete": life.incomplete or figures["incomplete"] or purchase_missing or expense_missing,
        "show_order": show_order,
        "show_deliveries": show_deliveries,
        "show_purchases": show_purchase_deliveries,
        "show_committed": show_purchase_orders,
        "show_sale_pending": show_order and show_deliveries,
        "show_purchase_pending": show_purchase_orders and show_purchase_deliveries,
        "show_expenses": show_expenses,
        "show_deviation": show_deviation,
        "show_net_margin": show_net_margin,
        "show_slice_committed": show_purchase_orders and bool(committed),
        "levels_stored": life.levels_stored,
        "lines_stored": life.lines_stored,
        "sale_orders": sale_order_docs,
        "sale_deliveries": sale_delivery_docs,
        "purchase_deliveries": purchase_delivery_docs,
        "donut": donut,
        "negative_margin": format_money(net_margin) if show_net_margin and net_margin is not None and net_margin < 0 else "",
        "customer": _label(life.customer_code, life.customer_name, show_clients) if life.customer_code and show_order else "",
        "start": _date_text(life.order_date),
        "end": _date_text(end) if life.order_date is not None else "",
        "years": ", ".join(str(year) for year in sorted(years)),
        "order_base": _money(life.order_base),
        "delivered": _money(figures["delivered"]),
        "progression": format_percent(figures["progression"]),
        "invoiced": _money(figures["invoiced"]),
        "invoiced_percent": format_percent(figures["part_percents"][BILLING_INVOICED]),
        "open": _money(figures["open"]),
        "open_percent": format_percent(figures["part_percents"][BILLING_OPEN]),
        "unknown": _money(figures["unknown"]),
        "unknown_percent": format_percent(figures["part_percents"][BILLING_UNKNOWN]),
        "show_unknown": figures["unknown"] != 0,
        "pending": _money(figures["pending"]),
        "purchase_pending": _money(purchase_pending),
        "purchase_invoice_pending": "Sin dato" if purchase_invoice_pending is None else _money(purchase_invoice_pending),
        "purchases": _money(purchase_total),
        "cost": _money(expense_total),
        "order_count_text": f"{order_count} pedido" if order_count == 1 else f"{order_count} pedidos",
        "order_total": _money(order_total),
        "expenses": _money(expense_total),
        "deviation": _money(deviation),
        "deviation_percent": format_percent(_ratio(deviation, life.order_base)),
        "net_margin": _money(net_margin),
        "net_margin_percent": format_percent(_ratio(net_margin, figures["delivered"])),
        "slices": slices,
        "committed_total": _money(committed_sum),
        "progression_width": _progression_width(figures["progression"]) if show_deliveries else "",
        "marks": marks,
        "milestones": milestone_rows,
        "months": months,
        "evolution": evolution,
        "delivery_marks": [
            {
                "date": _date_text(row.delivery_date),
                "amount": _money(row.amount),
                "billing": _BILLING_LABELS.get(row.billing, _BILLING_LABELS[BILLING_UNKNOWN]),
            }
            for row in dated
        ],
        "purchase_marks": [
            {
                "date": _date_text(row.document_date),
                "amount": _money(row.amount),
                "supplier": _label(row.supplier_code, row.supplier_name, show_supplier_name),
            }
            for row in deliveries
            if row.document_date is not None
        ],
        "committed": [
            {
                "date": _date_text(row.document_date),
                "amount": _money(row.amount),
                "supplier": _label(row.supplier_code, row.supplier_name, show_supplier_name),
            }
            for row in committed
        ],
        "purchase_orders": [
            {
                "date": _date_text(row.document_date),
                "identity": f"{row.ejercicio} / {row.serie} / {row.numero}",
                "supplier": _label(row.supplier_code, row.supplier_name, show_supplier_name),
                "party": _label(row.supplier_code, row.supplier_name, show_supplier_name),
                "amount": _money(row.amount),
                "committed": row.kind == KIND_COMMITTED,
                "status": "Comprometido" if row.kind == KIND_COMMITTED else "Pedido",
                "lines": _lines_of(stored_lines, "purchase_order", f"{row.ejercicio} / {row.serie} / {row.numero}"),
            }
            for row in sorted(
                (row for row in purchases if row.kind in (KIND_ORDER, KIND_COMMITTED)),
                key=lambda row: (row.document_date or date.min, _text(row.numero)),
            )
        ] if show_purchase_orders else [],
        "suppliers": _grouped(
            ((row.supplier_code, row.supplier_name, row.amount) for row in deliveries),
            show_supplier_name,
        ),
        "accounts": _grouped(
            ((row.account_code, row.account_name, row.amount) for row in expenses),
            True,
        ),
        "undated": undated,
    }
