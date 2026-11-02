from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth

from apps.access.models import InformationGroup
from apps.erp.analytics import fetch_dimension_labels
from apps.erp.mapping import is_cancelled, is_closing_entry, is_expense_account, is_income_account
from apps.erp.documents import (
    fetch_purchase_deliveries,
    fetch_purchase_orders,
    fetch_sales_deliveries,
)
from apps.erp.ledger import fetch_account_groups, fetch_movements, fetch_period_movements
from apps.erp.purchases import fetch_purchases
from apps.erp.sales import fetch_orders
from apps.margins.dashboard import (
    _documents_value,
    _visible_figures,
    analytical_dimensions,
    build_dashboard,
    level_group,
)
from apps.margins.format import format_money
from apps.margins.hierarchy import _display, _unique_projects, tree_income_entries
from apps.margins.models import (
    MONTH_NAMES,
    AnalyticalSummary,
    AsideSummary,
    AccountGroup,
    BookExpense,
    BookIncome,
    DashboardSnapshot,
    TreeIncome,
    MonthLedger,
    OrderSummary,
    ProjectDocumentLine,
    ProjectExerciseShare,
    ProjectExpense,
    ProjectLife,
)
from apps.margins.project_life import (
    closed_months,
    refresh_project_lives,
    replace_book_expenses,
    replace_book_incomes,
    retained_projects,
)
from apps.margins.services import (
    _side_amount,
    build_report,
    in_period,
    ledger_total,
    margin_ratio,
    movement_in_period,
    sale_price,
)


def _leaves(nodes, path, found):
    for node in nodes:
        step = path + [node["label"]]
        if node["children"]:
            _leaves(node["children"], step, found)
        else:
            found.append((step, node))
    return found


def _amount(value):
    if value is None:
        return Decimal("0")
    return value


def _pad(values):
    row = list(values[:4])
    while len(row) < 4:
        row.append("")
    return row


def _card(source, prefix):
    if source is None:
        return {f"{prefix}_count": 0, f"{prefix}_amount": Decimal("0")}
    return {f"{prefix}_count": source["count"], f"{prefix}_amount": source["amount"]}


def _tell(progress, step, label, done=None, count=None, month=""):
    if progress is None:
        return
    event = {"step": step, "total": 8, "label": label}
    if count is not None:
        event["done"] = done
        event["count"] = count
    if month:
        event["month"] = month
    progress(event)


def closure_notice(months):
    """Texto para la persona. Vacío si no hay ningún mes cerrado."""

    chosen = sorted({int(month) for month in months or []})
    if not chosen:
        return ""
    if chosen == list(range(1, 13)):
        return "No había ningún mes abierto. No se ha actualizado ningún proyecto."
    labels = dict(MONTH_NAMES)
    names = ", ".join(labels[month] for month in chosen)
    return f"No se han actualizado los meses cerrados: {names}."


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def _by_project(documents):
    grouped = defaultdict(list)
    for document in documents:
        grouped[_text(getattr(document, "project", ""))].append(document)
    return grouped


def _without(documents, retained):
    if not retained:
        return documents
    return [document for document in documents if _text(getattr(document, "project", "")) not in retained]


def _card_pair(company, year, documents):
    if not documents:
        return 0, Decimal("0")
    valued = _documents_value(str(company), year, documents)
    return valued["count"], valued["amount"]


def _path_labels(order, labels):
    names = []
    for attribute, _title, _group in list(analytical_dimensions())[:4]:
        code = _text(getattr(order, attribute, ""))
        names.append(_display(code, (labels or {}).get(attribute, {})))
    while len(names) < 4:
        names.append("")
    return names


def _share_for(company, year, project, buckets, labels):
    orders = buckets["orders"].get(project, [])
    purchase_orders = buckets["purchase_orders"].get(project, [])
    sales_deliveries = buckets["sales_deliveries"].get(project, [])
    purchase_deliveries = buckets["purchase_deliveries"].get(project, [])
    movements = buckets["movements"].get(project, [])
    active_orders = [
        order
        for order in orders
        if not is_cancelled(order.status) and in_period(order, year)
    ]
    sales_count, sales_amount = _card_pair(company, year, active_orders)
    purchase_count, purchase_amount = _card_pair(company, year, purchase_orders)
    delivery_count, delivery_amount = _card_pair(company, year, sales_deliveries)
    bought_count, bought_amount = _card_pair(company, year, purchase_deliveries)
    income = ledger_total(str(company), year, movements, "income")
    expense = ledger_total(str(company), year, movements, "expense")
    path_sales = Decimal("0")
    if len(active_orders) == 1:
        price, _missing = sale_price(active_orders[0])
        path_sales = Decimal("0") if price is None else Decimal(price)
    path = _path_labels(active_orders[0], labels) if active_orders else ["", "", "", ""]
    return ProjectExerciseShare(
        codigo_empresa=str(company),
        codigo_proyecto=project,
        ejercicio=year,
        sales_count=sales_count,
        sales_amount=sales_amount,
        purchase_order_count=purchase_count,
        purchase_order_amount=purchase_amount,
        sales_delivery_count=delivery_count,
        sales_delivery_amount=delivery_amount,
        purchase_delivery_count=bought_count,
        purchase_delivery_amount=bought_amount,
        income_count=income["count"],
        income_amount=income["amount"],
        expense_count=expense["count"],
        expense_amount=expense["amount"],
        nivel_1=path[0],
        nivel_2=path[1],
        nivel_3=path[2],
        nivel_4=path[3],
        sales=path_sales,
        income=income["amount"],
        purchases=Decimal("0"),
        expenses=expense["amount"],
        margin=income["amount"] - expense["amount"],
    )


def _add_card(figures, key, count, amount):
    card = figures.get(key)
    if card is None:
        return
    card["count"] += count
    card["amount"] += Decimal(amount)


def _absorb_share(leaves, share):
    path = [share.nivel_1, share.nivel_2, share.nivel_3, share.nivel_4]
    if not any(path):
        return
    for found, node in leaves:
        if list(found) == path:
            node["sales"] = _amount(node.get("sales")) + share.sales
            node["income"] = _amount(node.get("income")) + share.income
            node["purchases"] = _amount(node.get("purchases")) + share.purchases
            node["expenses"] = _amount(node.get("expenses")) + share.expenses
            node["margin"] = _amount(node.get("margin")) + share.margin
            node["incomplete"] = node.get("incomplete") or share.incomplete
            return
    leaves.append(
        (
            path,
            {
                "sales": share.sales,
                "income": share.income,
                "purchases": share.purchases,
                "expenses": share.expenses,
                "margin": share.margin,
                "incomplete": share.incomplete,
            },
        )
    )


def replace_month_ledgers(company, year, movements):
    """Guarda el ingreso y el gasto de cada mes según la fecha del apunte.

    Un apunte sin fecha no pertenece a ningún mes. El cierre no lo suma.
    """

    buckets = {
        month: {
            "income_count": 0,
            "income_amount": Decimal("0"),
            "expense_count": 0,
            "expense_amount": Decimal("0"),
            "purchase_count": 0,
            "purchase_amount": Decimal("0"),
        }
        for month in range(1, 13)
    }
    for movement in movements:
        if str(getattr(movement, "codigo_empresa", "")) != str(company):
            continue
        if not movement_in_period(movement, year):
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        moment = getattr(movement, "movement_date", None)
        if moment is None or moment.month not in buckets:
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
        bucket = buckets[moment.month]
        bucket[f"{kind}_count"] += 1
        bucket[f"{kind}_amount"] += amount
    MonthLedger.objects.filter(codigo_empresa=str(company), ejercicio=year).delete()
    MonthLedger.objects.bulk_create(
        [
            MonthLedger(codigo_empresa=str(company), ejercicio=year, mes=month, **bucket)
            for month, bucket in buckets.items()
        ]
    )


def _open_only_paths(shares, lives, year, closed):
    """Rutas analíticas que solo tienen proyectos de meses abiertos."""

    path_months = defaultdict(set)
    for share in shares:
        month = _month_of(lives.get(share.codigo_proyecto), year)
        path = (share.nivel_1, share.nivel_2, share.nivel_3, share.nivel_4)
        if month is None or not any(path):
            continue
        path_months[path].add(month)
    return {path for path, months in path_months.items() if months.isdisjoint(closed)}


def refresh_snapshot(company, year, progress=None):
    """Lee el origen comercial y sustituye el resumen de esa empresa y ese ejercicio.

    Los meses cerrados no se recalculan. Devuelve esos meses.
    """

    closed = sorted(closed_months(company, year))
    if set(closed) >= set(range(1, 13)):
        _tell(progress, 8, "Listo")
        return closed
    groups = list(InformationGroup.values)
    _tell(progress, 1, "Pedidos de venta")
    orders = fetch_orders(company)
    _tell(progress, 2, "Pedidos de compra")
    purchase_orders = fetch_purchase_orders(company)
    purchases = fetch_purchases(company)
    _tell(progress, 3, "Albaranes de venta")
    sales_deliveries = fetch_sales_deliveries(company)
    _tell(progress, 4, "Albaranes de compra")
    purchase_deliveries = fetch_purchase_deliveries(company)
    _tell(progress, 5, "Movimientos")
    movements = fetch_movements(company)
    period_movements = fetch_period_movements(company, year)
    account_groups = fetch_account_groups(company)
    _tell(progress, 6, "Cuadro de mando")
    labels = fetch_dimension_labels(company)
    retained = retained_projects(company, year, orders, closed)
    orders_open = _without(orders, retained)
    purchases_open = _without(purchases, retained)
    purchase_orders_open = _without(purchase_orders, retained)
    sales_open = _without(sales_deliveries, retained)
    purchase_deliveries_open = _without(purchase_deliveries, retained)
    movements_open = _without(movements, retained)
    period_open = _without(period_movements, retained)
    figures = build_dashboard(
        company,
        year,
        orders_open,
        purchases_open,
        period_open,
        groups,
        labels,
        purchase_orders=purchase_orders_open,
        sales_deliveries=sales_open,
        purchase_deliveries=purchase_deliveries_open,
        ledger=period_open,
    )
    report = build_report(company, year, orders_open, purchases_open, movements_open)
    buckets = {
        "orders": _by_project(orders),
        "purchase_orders": _by_project(purchase_orders),
        "sales_deliveries": _by_project(sales_deliveries),
        "purchase_deliveries": _by_project(purchase_deliveries),
        "movements": _by_project(period_movements),
    }
    open_projects = set()
    by_project = defaultdict(list)
    for order in orders:
        if str(getattr(order, "codigo_empresa", "")) != str(company):
            continue
        if is_cancelled(order.status) or not in_period(order, year):
            continue
        project = _text(order.project)
        if not project:
            continue
        by_project[project].append(order)
        if project not in retained:
            open_projects.add(project)
    retained_pending = 0
    kept_identities = set()
    for project, group in by_project.items():
        if project not in retained or len(group) == 1:
            continue
        retained_pending += len(group)
        for order in group:
            kept_identities.add(f"{order.ejercicio} / {order.serie} / {order.numero}")
    titles = _pad([item[1] for item in list(analytical_dimensions())[:4]])
    leaves = _leaves(figures.get("hierarchy", []), [], [])
    with transaction.atomic():
        replace_month_ledgers(company, year, period_movements)
        previous = DashboardSnapshot.objects.filter(codigo_empresa=company, ejercicio=year).first()
        old_orders = list(previous.orders.all()) if previous else []
        old_aside = list(previous.aside_rows.all()) if previous else []
        kept_shares = list(
            ProjectExerciseShare.objects.filter(
                codigo_empresa=str(company),
                ejercicio=year,
                codigo_proyecto__in=retained,
            )
        ) if retained else []
        for share in kept_shares:
            _add_card(figures, "sales", share.sales_count, share.sales_amount)
            _add_card(figures, "purchase_orders", share.purchase_order_count, share.purchase_order_amount)
            _add_card(figures, "sales_deliveries", share.sales_delivery_count, share.sales_delivery_amount)
            _add_card(figures, "purchase_deliveries", share.purchase_delivery_count, share.purchase_delivery_amount)
            _add_card(figures, "income", share.income_count, share.income_amount)
            _add_card(figures, "expenses", share.expense_count, share.expense_amount)
            _absorb_share(leaves, share)
        ProjectExerciseShare.objects.filter(
            codigo_empresa=str(company),
            ejercicio=year,
            codigo_proyecto__in=open_projects,
        ).delete()
        ProjectExerciseShare.objects.bulk_create(
            [_share_for(company, year, project, buckets, labels) for project in sorted(open_projects)]
        )
        aside_rows = []
        seen_aside = set()
        for row in figures.get("aside", []):
            aside_rows.append(row)
            seen_aside.add(row["identity"])
        for row in old_aside:
            if row.identity in kept_identities and row.identity not in seen_aside:
                aside_rows.append(
                    {"identity": row.identity, "amount": row.amount, "incomplete": row.incomplete}
                )
                seen_aside.add(row.identity)
        order_rows = [row for row in report["closed"] if row["project"] not in retained]
        for row in old_orders:
            if row.project in retained:
                order_rows.append(row)
        DashboardSnapshot.objects.filter(codigo_empresa=company, ejercicio=year).delete()
        snapshot = DashboardSnapshot.objects.create(
            codigo_empresa=company,
            ejercicio=year,
            titulo_1=titles[0],
            titulo_2=titles[1],
            titulo_3=titles[2],
            titulo_4=titles[3],
            pending_count=report["pending_count"] + retained_pending,
            **_card(figures.get("sales"), "sales"),
            **_card(figures.get("purchase_orders"), "purchase_order"),
            **_card(figures.get("sales_deliveries"), "sales_delivery"),
            **_card(figures.get("purchase_deliveries"), "purchase_delivery"),
            **_card(figures.get("income"), "income"),
            **_card(figures.get("expenses"), "expense"),
        )
        AnalyticalSummary.objects.bulk_create(
            [
                AnalyticalSummary(
                    snapshot=snapshot,
                    nivel_1=path[0],
                    nivel_2=path[1],
                    nivel_3=path[2],
                    nivel_4=path[3],
                    sales=_amount(node.get("sales")),
                    income=_amount(node.get("income")),
                    purchases=_amount(node.get("purchases")),
                    expenses=_amount(node.get("expenses")),
                    margin=_amount(node.get("margin")),
                    incomplete=node["incomplete"],
                )
                for path, node in (( _pad(path), node) for path, node in leaves)
            ]
        )
        AsideSummary.objects.bulk_create(
            [
                AsideSummary(
                    snapshot=snapshot,
                    identity=row["identity"],
                    amount=row["amount"],
                    incomplete=row["incomplete"],
                )
                for row in aside_rows
            ]
        )
        refresh_project_lives(
            company,
            year,
            orders,
            sales_deliveries,
            purchase_orders,
            purchase_deliveries,
            movements,
            labels,
            on_project=lambda done, count, month="": _tell(progress, 7, "Fichas de proyecto", done, count, month),
            period_movements=period_movements,
        )
        replace_account_groups(company, account_groups)
        replace_book_expenses(company, year, period_movements, open_projects, labels)
        replace_book_incomes(company, year, period_movements, labels)
        replace_tree_incomes(company, year, period_open, orders_open, purchase_orders_open, labels)
        snapshot.book_stored = True
        snapshot.income_stored = True
        snapshot.tree_income_stored = True
        snapshot.save(update_fields=["book_stored", "income_stored", "tree_income_stored"])
        OrderSummary.objects.bulk_create(_order_summaries(snapshot, order_rows))
    _tell(progress, 8, "Listo")
    return closed


def _order_summaries(snapshot, rows):
    summaries = []
    for row in rows:
        if isinstance(row, OrderSummary):
            identity = row.identity
            project = row.project
            price = row.price
            cost = row.cost
            margin = row.margin
            income = row.income
            incomplete = row.incomplete
        else:
            identity = f"{row['ejercicio']} / {row['serie']} / {row['numero']}"
            project = row["project"]
            price = row["price"]
            cost = row["cost"]
            margin = row["margin"]
            income = row["income"]
            incomplete = row["incomplete"]
        summaries.append(
            OrderSummary(
                snapshot=snapshot,
                identity=identity,
                project=project,
                price=price,
                cost=cost,
                margin=margin,
                income=income,
                incomplete=incomplete,
            )
        )
    return summaries


def _project_code(level, label):
    """El resumen guarda «código — descripción». La ficha necesita solo el código."""

    if level != "Proyecto" or not label or label == "Sin dato":
        return ""
    code, separator, _description = str(label).partition(" — ")
    return code if separator else str(label)


def _nest(rows, indexes, titles, depth, keys):
    if depth >= len(indexes):
        return []
    position = indexes[depth]
    field = f"nivel_{position + 1}"
    grouped = {}
    for row in rows:
        grouped.setdefault(getattr(row, field) or "Sin dato", []).append(row)
    nodes = []
    for label in sorted(grouped, key=str.casefold):
        group = grouped[label]
        node = {
            "level": titles[position],
            "label": label,
            "code": _project_code(titles[position], label),
            "incomplete": any(item.incomplete for item in group),
            "children": _nest(group, indexes, titles, depth + 1, keys),
        }
        for key in keys:
            node[key] = sum((getattr(item, key) for item in group), Decimal("0"))
        nodes.append(node)
    return nodes


_MONTHS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")


def _parts(value, peak):
    if not value or not peak:
        return 0, 0
    height = max(round(abs(float(value)) / float(peak) * 100), 8)
    if value > 0:
        return height, 0
    return 0, height


def _purchase_by_month(company, year, months=None):
    """Grupo 60 ya guardado en el proyecto. Esas son las compras del cuadro."""

    query = ProjectExpense.objects.filter(
        life__codigo_empresa=str(company),
        movement_date__year=year,
        account_code__startswith="60",
    )
    if months is not None:
        query = query.filter(movement_date__month__in=list(months))
    amounts = {}
    counts = {}
    for row in (
        query.annotate(month=ExtractMonth("movement_date"))
        .values("month")
        .annotate(total=Sum("amount"), rows=Count("id"))
    ):
        amounts[row["month"]] = row["total"] or Decimal("0")
        counts[row["month"]] = row["rows"] or 0
    return amounts, counts


def _outside_group_six(company, year, months=None):
    """Apuntes guardados que no empiezan por 6. No son gasto del cuadro."""

    query = BookExpense.objects.filter(codigo_empresa=str(company), ejercicio=year).exclude(
        account_code__startswith="6"
    )
    if months is not None:
        query = query.filter(movement_date__month__in=list(months))
    amounts = {}
    for row in (
        query.annotate(month=ExtractMonth("movement_date"))
        .values("month")
        .annotate(total=Sum("amount"))
    ):
        amounts[row["month"]] = row["total"] or Decimal("0")
    return amounts


def _split_book(company, year, book_amount, book_count, months=None):
    """Gastos es el grupo 6 del libro menos las compras del grupo 60."""

    amounts, counts = _purchase_by_month(company, year, months)
    bought = sum(amounts.values(), Decimal("0"))
    outside = sum(_outside_group_six(company, year, months).values(), Decimal("0"))
    group_six = Decimal(book_amount) - outside
    return (
        {"count": sum(counts.values(), 0), "amount": bought},
        {"count": book_count, "amount": group_six - bought},
    )


def monthly_bars(company, year, groups, only_months=None):
    """Ingresos del grupo 7, compras de proyecto y el resto del grupo 6, por mes."""

    allowed = set(groups)
    show_expenses = InformationGroup.MOVIMIENTOS in allowed
    show_sales = show_expenses
    show_purchases = show_expenses
    show_margin = show_expenses
    if not show_sales and not show_purchases and not show_expenses:
        return []
    purchases = {}
    expenses = {}
    incomes = {}
    if show_expenses:
        purchases = _purchase_by_month(company, year, only_months)[0]
        outside = _outside_group_six(company, year, only_months)
        for row in MonthLedger.objects.filter(codigo_empresa=str(company), ejercicio=year):
            incomes[row.mes] = Decimal(row.income_amount)
            group_six = Decimal(row.expense_amount) - outside.get(row.mes, Decimal("0"))
            expenses[row.mes] = group_six - purchases.get(row.mes, Decimal("0"))
    if not any(purchases.values()) and not any(expenses.values()) and not any(incomes.values()):
        return []
    rows = []
    for number, label in enumerate(_MONTHS, start=1):
        if only_months is not None and number not in only_months:
            continue
        sold = incomes.get(number, Decimal("0"))
        bought = purchases.get(number, Decimal("0"))
        spent = expenses.get(number, Decimal("0"))
        margin = incomes[number] - bought - spent if number in incomes else Decimal("0")
        rows.append((number, label, sold, bought, spent, margin))
    carried_sales = Decimal("0")
    carried_purchases = Decimal("0")
    carried_expenses = Decimal("0")
    carried_margin = Decimal("0")
    cumulative = {}
    for number in range(1, 13):
        sold = incomes.get(number, Decimal("0"))
        bought = purchases.get(number, Decimal("0"))
        spent = expenses.get(number, Decimal("0"))
        margin = incomes[number] - bought - spent if number in incomes else Decimal("0")
        carried_sales += sold
        carried_purchases += bought
        carried_expenses += spent
        carried_margin += margin
        cumulative[number] = (carried_sales, carried_purchases, carried_expenses, carried_margin)
    peak = Decimal("0")
    for _number, _label, sold, bought, spent, margin in rows:
        if show_sales:
            peak = max(peak, abs(sold))
        if show_purchases:
            peak = max(peak, abs(bought))
        if show_expenses:
            peak = max(peak, abs(spent))
        if show_margin:
            peak = max(peak, abs(margin))
    months = []
    for number, label, sold, bought, spent, margin in rows:
        sales_up, sales_down = _parts(sold, peak)
        purchase_up, purchase_down = _parts(bought, peak)
        expense_up, expense_down = _parts(spent, peak)
        margin_up, margin_down = _parts(margin, peak)
        carried_sales, carried_purchases, carried_expenses, carried_margin = cumulative[number]
        months.append(
            {
                "number": number,
                "label": label,
                "sales": sold,
                "purchases": bought,
                "expenses": spent,
                "margin": margin,
                "sales_text": format_money(sold) if show_sales else "",
                "purchases_text": format_money(bought) if show_purchases else "",
                "expenses_text": format_money(spent) if show_expenses else "",
                "margin_text": format_money(margin) if show_margin else "",
                "cumulative_sales_text": format_money(carried_sales) if show_sales else "",
                "cumulative_purchases_text": format_money(carried_purchases) if show_purchases else "",
                "cumulative_expenses_text": format_money(carried_expenses) if show_expenses else "",
                "cumulative_margin_text": format_money(carried_margin) if show_margin else "",
                "sales_up": sales_up if show_sales else 0,
                "sales_down": sales_down if show_sales else 0,
                "purchase_up": purchase_up if show_purchases else 0,
                "purchase_down": purchase_down if show_purchases else 0,
                "expense_up": expense_up if show_expenses else 0,
                "expense_down": expense_down if show_expenses else 0,
                "margin_up": margin_up if show_margin else 0,
                "margin_down": margin_down if show_margin else 0,
                "show_sales": show_sales,
                "show_purchases": show_purchases,
                "show_expenses": show_expenses,
                "show_margin": show_margin,
            }
        )
    return months


def evolution_chart(months):
    """Columna de ingresos y, al lado, compras, gastos y margen apilados."""

    if not months:
        return None
    last = None
    for index, month in enumerate(months):
        if month["sales"] or month["purchases"] or month["expenses"] or month["margin"]:
            last = index
    if last is None:
        return None
    shown = months[: last + 1]
    show_sales = shown[0]["show_sales"]
    show_purchases = shown[0]["show_purchases"]
    show_expenses = shown[0]["show_expenses"]
    show_margin = shown[0]["show_margin"]
    left, right, top, bottom = 16, 984, 16, 246
    plot = bottom - top
    count = len(shown)
    slot = (right - left) / count
    gap = min(8.0, slot * 0.08)
    pair = slot * 0.72
    width = (pair - gap) / 2 if show_sales else pair
    totals = []
    for month in shown:
        sold = month["sales"] if show_sales and month["sales"] > 0 else Decimal("0")
        bought = month["purchases"] if show_purchases and month["purchases"] > 0 else Decimal("0")
        spent = month["expenses"] if show_expenses and month["expenses"] > 0 else Decimal("0")
        kept = month["margin"] if show_margin and month["margin"] > 0 else Decimal("0")
        totals.append(max(sold, bought + spent + kept))
    peak = max(totals)
    if peak == 0:
        peak = Decimal("1")

    def height(amount):
        return float(plot) * float(Decimal(amount) / peak)

    columns = []
    for index, month in enumerate(shown):
        sold = month["sales"] if show_sales and month["sales"] > 0 else Decimal("0")
        bought = month["purchases"] if show_purchases and month["purchases"] > 0 else Decimal("0")
        spent = month["expenses"] if show_expenses and month["expenses"] > 0 else Decimal("0")
        kept = month["margin"] if show_margin and month["margin"] > 0 else Decimal("0")
        sales_height = height(sold)
        purchase_height = height(bought)
        expense_height = height(spent)
        margin_height = height(kept)
        origin = left + slot * index + (slot - (width * (2 if show_sales else 1) + (gap if show_sales else 0))) / 2
        columns.append(
            {
                "number": month["number"],
                "label": month["label"],
                "sales_x": f"{origin:.1f}",
                "x": f"{origin + (width + gap if show_sales else 0):.1f}",
                "width": f"{width:.1f}",
                "sales_y": f"{bottom - sales_height:.1f}",
                "sales_height": f"{sales_height:.1f}",
                "purchase_y": f"{bottom - purchase_height:.1f}",
                "purchase_height": f"{purchase_height:.1f}",
                "expense_y": f"{bottom - purchase_height - expense_height:.1f}",
                "expense_height": f"{expense_height:.1f}",
                "margin_y": f"{bottom - purchase_height - expense_height - margin_height:.1f}",
                "margin_height": f"{margin_height:.1f}",
                "tick_x": f"{left + slot * index + slot / 2:.1f}",
                "title": (
                    f"{month['label']}. Ingresos {month['sales_text']}. "
                    f"Compras {month['purchases_text']}. Gastos {month['expenses_text']}. "
                    f"Margen {month['margin_text']}."
                ),
            }
        )
    return {
        "columns": columns,
        "zero_y": f"{bottom:.1f}",
        "left": f"{left:.1f}",
        "right": f"{right:.1f}",
        "peak_text": format_money(peak),
        "show_sales": show_sales,
        "show_purchases": show_purchases,
        "show_expenses": show_expenses,
        "show_margin": show_margin,
    }


def _book_expense_detail(company, year, month, names, allowed):
    """Apuntes del libro que no entraron en compras. No lee el origen."""

    title = f"Gastos de {names[month]} de {year}"
    headers = ["Fecha", "Proyecto", "Origen"]
    show_department = InformationGroup.DEPARTAMENTOS in allowed
    show_section = InformationGroup.SECCIONES in allowed
    if show_department:
        headers.append("Departamento")
    if show_section:
        headers.append("Sección")
    headers.append("Importe")
    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=str(company), ejercicio=year).first()
    if snapshot is None or not snapshot.book_stored:
        return {
            "kind": "gasto",
            "title": title,
            "source": "Movimientos",
            "pending": True,
            "message": "Las líneas se guardan al pulsar Actualizar.",
            "headers": headers,
            "groups": [],
            "total": "",
        }
    stored = list(
        BookExpense.objects.filter(
            codigo_empresa=str(company),
            ejercicio=year,
            movement_date__month=month,
            account_code__startswith="6",
        ).order_by("movement_date", "project_code", "account_code")
    )
    stored.extend(
        ProjectExpense.objects.filter(
            life__codigo_empresa=str(company),
            movement_date__year=year,
            movement_date__month=month,
            account_code__startswith="6",
        )
        .exclude(account_code__startswith="60")
        .select_related("life")
        .order_by("movement_date", "life__codigo_proyecto", "account_code")
    )
    grouped = {}
    total = Decimal("0")
    for row in stored:
        code = str(row.account_code or "").strip()
        prefix = code[:3] or "Sin dato"
        bucket = grouped.setdefault(prefix, {"amount": Decimal("0"), "lines": []})
        total += Decimal(row.amount)
        project = getattr(row, "project_code", None)
        if project is None:
            project = row.life.codigo_proyecto
        line = [
            row.movement_date.strftime("%d/%m/%Y"),
            project or "Sin dato",
            _named(row.account_code, row.account_name),
        ]
        if show_department:
            line.append(_named(row.department_code, row.department_name))
        if show_section:
            line.append(_named(row.section_code, row.section_name))
        line.append(format_money(row.amount))
        bucket["amount"] += Decimal(row.amount)
        bucket["lines"].append(line)
    return {
        "kind": "gasto",
        "title": title,
        "source": "Movimientos",
        "pending": False,
        "message": "",
        "headers": headers,
        "groups": _present_groups(company, grouped),
        "total": format_money(total),
    }


def _book_income_detail(company, year, month, names, allowed):
    """Apuntes de ingreso del grupo 7. No lee el origen."""

    title = f"Ingresos de {names[month]} de {year}"
    headers = ["Fecha", "Proyecto", "Origen"]
    show_department = InformationGroup.DEPARTAMENTOS in allowed
    show_section = InformationGroup.SECCIONES in allowed
    if show_department:
        headers.append("Departamento")
    if show_section:
        headers.append("Sección")
    headers.append("Importe")
    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=str(company), ejercicio=year).first()
    if snapshot is None or not snapshot.income_stored:
        return {
            "kind": "ingreso",
            "title": title,
            "source": "Movimientos",
            "pending": True,
            "message": "Las líneas se guardan al pulsar Actualizar.",
            "headers": headers,
            "groups": [],
            "total": "",
        }
    stored = BookIncome.objects.filter(
        codigo_empresa=str(company),
        ejercicio=year,
        movement_date__month=month,
    ).order_by("movement_date", "project_code", "account_code")
    grouped = {}
    total = Decimal("0")
    for row in stored:
        code = str(row.account_code or "").strip()
        prefix = code[:3] or "Sin dato"
        bucket = grouped.setdefault(prefix, {"amount": Decimal("0"), "lines": []})
        total += Decimal(row.amount)
        line = [
            row.movement_date.strftime("%d/%m/%Y"),
            row.project_code or "Sin dato",
            _named(row.account_code, row.account_name),
        ]
        if show_department:
            line.append(_named(row.department_code, row.department_name))
        if show_section:
            line.append(_named(row.section_code, row.section_name))
        line.append(format_money(row.amount))
        bucket["amount"] += Decimal(row.amount)
        bucket["lines"].append(line)
    return {
        "kind": "ingreso",
        "title": title,
        "source": "Movimientos",
        "pending": False,
        "message": "",
        "headers": headers,
        "groups": _present_groups(company, grouped),
        "total": format_money(total),
    }


def evolution_detail(company, year, month, kind, groups):
    """Líneas ya guardadas que suman el ingreso, la compra o el gasto de un mes. No lee el origen."""

    allowed = set(groups)
    names = dict(MONTH_NAMES)
    if kind == "gasto":
        return _book_expense_detail(company, year, month, names, allowed)
    if kind == "ingreso":
        return _book_income_detail(company, year, month, names, allowed)
    title = f"Compras de {names[month]} de {year}"
    show_department = InformationGroup.DEPARTAMENTOS in allowed
    show_section = InformationGroup.SECCIONES in allowed
    stored = (
        ProjectExpense.objects.filter(
            life__codigo_empresa=str(company),
            movement_date__year=year,
            movement_date__month=month,
            account_code__startswith="60",
        )
        .select_related("life")
        .order_by("movement_date", "life__codigo_proyecto", "account_code")
    )
    headers = ["Fecha", "Proyecto", "Origen"]
    if show_department:
        headers.append("Departamento")
    if show_section:
        headers.append("Sección")
    headers.append("Importe")
    grouped = {}
    total = Decimal("0")
    for row in stored:
        code = str(row.account_code or "").strip()
        prefix = code[:3] or "Sin dato"
        bucket = grouped.setdefault(prefix, {"amount": Decimal("0"), "lines": []})
        if row.amount is not None:
            amount = Decimal(row.amount)
            bucket["amount"] += amount
            total += amount
        line = [
            row.movement_date.strftime("%d/%m/%Y"),
            row.life.codigo_proyecto,
            _named(row.account_code, row.account_name),
        ]
        if show_department:
            line.append(_named(row.department_code, row.department_name))
        if show_section:
            line.append(_named(row.section_code, row.section_name))
        line.append(format_money(row.amount))
        bucket["lines"].append(line)
    return {
        "kind": "compra",
        "title": title,
        "source": "AnaMovimientos unida a Movimientos",
        "headers": headers,
        "groups": _present_groups(company, grouped),
        "total": format_money(total),
    }


def delivery_lines(company, project, document_key, kind="sale_delivery"):
    """Líneas guardadas de un pedido o un albarán. No lee el origen."""

    stored_kind = {
        "sale_order": "sale_order",
        "sale_delivery": "sale_delivery",
        "purchase_order": "purchase_order",
        "purchase_delivery": "purchase_delivery",
    }.get(kind)
    if stored_kind is None:
        return None
    noun = "pedido" if stored_kind.endswith("order") else "albarán"
    title = f"Líneas del {noun} {document_key}".strip()
    life = ProjectLife.objects.filter(codigo_empresa=str(company), codigo_proyecto=project).first()
    if life is None or not life.lines_stored:
        return {
            "title": title,
            "pending": True,
            "message": "Las líneas se guardan al pulsar Actualizar.",
            "headers": ["Artículo", "Importe"],
            "rows": [],
            "total": "",
        }
    stored = ProjectDocumentLine.objects.filter(
        life=life,
        kind=stored_kind,
        document_key=document_key,
        position__gt=0,
    ).order_by("position")
    rows = []
    total = Decimal("0")
    for line in stored:
        if line.amount is not None:
            total += Decimal(line.amount)
        rows.append([line.description or "Línea", format_money(line.amount)])
    if not rows:
        return {
            "title": title,
            "pending": False,
            "message": f"Este {noun} no tiene líneas guardadas.",
            "headers": ["Artículo", "Importe"],
            "rows": [],
            "total": "",
        }
    return {
        "title": title,
        "pending": False,
        "message": "",
        "headers": ["Artículo", "Importe"],
        "rows": rows,
        "total": format_money(total),
    }


def replace_account_groups(company, rows):
    """Sustituye las descripciones de grupo guardadas para la empresa."""

    company = str(company)
    AccountGroup.objects.filter(codigo_empresa=company).delete()
    AccountGroup.objects.bulk_create(
        [
            AccountGroup(codigo_empresa=company, code=str(code).strip()[:4], description=str(name or "").strip()[:160])
            for code, name in rows
            if str(code or "").strip()
        ],
        batch_size=500,
    )


def replace_tree_incomes(company, year, movements, orders, purchase_orders, labels):
    """Sustituye los ingresos del árbol. Cada fila guarda el nivel donde cayó."""

    company = str(company)
    year = int(year)
    dimensions = list(analytical_dimensions())[:4]
    entries = tree_income_entries(
        company,
        year,
        movements,
        dimensions,
        _unique_projects(orders or [], purchase_orders or []),
    )
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
    TreeIncome.objects.filter(codigo_empresa=company, ejercicio=year).delete()
    TreeIncome.objects.bulk_create(rows, batch_size=500)


def store_tree_incomes(company, year):
    """Lee los apuntes del ejercicio y guarda el ingreso del árbol. No rehace las fichas."""

    replace_tree_incomes(
        company,
        year,
        fetch_period_movements(company, year),
        fetch_orders(company),
        fetch_purchase_orders(company),
        fetch_dimension_labels(company),
    )
    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=str(company), ejercicio=int(year)).first()
    if snapshot is None:
        return
    snapshot.tree_income_stored = True
    snapshot.save(update_fields=["tree_income_stored"])


class _IncomePath:
    """Ingreso ya guardado con los cuatro niveles. No es una fila del año."""

    def __init__(self, levels, amount):
        self.nivel_1, self.nivel_2, self.nivel_3, self.nivel_4 = levels
        self.income = amount
        self.incomplete = False


def month_hierarchy(company, year, month, groups):
    """Árbol del mes con los ingresos que tienen fecha y nivel. No lee SQL Server."""

    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=str(company), ejercicio=int(year)).first()
    projects = _finder_projects(snapshot)
    allowed = set(groups)
    if (
        snapshot is None
        or not snapshot.tree_income_stored
        or InformationGroup.MOVIMIENTOS not in allowed
    ):
        return {"nodes": [], "projects": projects}
    titles = [snapshot.titulo_1, snapshot.titulo_2, snapshot.titulo_3, snapshot.titulo_4]
    indexes = [index for index, title in enumerate(titles) if title and level_group(title) in allowed]
    rows = [
        _IncomePath(
            (line.nivel_1, line.nivel_2, line.nivel_3, line.nivel_4),
            Decimal(line.amount),
        )
        for line in TreeIncome.objects.filter(
            codigo_empresa=str(company),
            ejercicio=int(year),
            movement_date__year=int(year),
            movement_date__month=int(month),
        )
    ]
    nodes = _nest(rows, indexes, titles, 0, ["income"]) if indexes and rows else []
    return {"nodes": nodes, "projects": projects}


def _finder_projects(snapshot):
    """Proyectos del árbol del ejercicio, para abrir la ficha."""

    if snapshot is None:
        return []
    titles = [snapshot.titulo_1, snapshot.titulo_2, snapshot.titulo_3, snapshot.titulo_4]
    if "Proyecto" not in titles:
        return []
    field = f"nivel_{titles.index('Proyecto') + 1}"
    found = {}
    for row in snapshot.rows.all():
        label = getattr(row, field) or ""
        code = _project_code("Proyecto", label)
        if code and code not in found:
            found[code] = label
    return [{"code": code, "label": found[code]} for code in sorted(found, key=str.casefold)]


def tree_income_detail(company, year, path, month=None):
    """Apuntes de ingreso de una rama del árbol. No lee SQL Server."""

    labels = [item["label"] for item in path]
    title = "Ingresos de " + " / ".join(labels)
    headers = ["Fecha", "Asiento", "Cuenta", "Factura", "Importe"]
    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=str(company), ejercicio=year).first()
    if snapshot is None or not snapshot.tree_income_stored:
        return {
            "title": title,
            "source": "Movimientos",
            "pending": True,
            "message": "Las líneas se guardan al pulsar Actualizar.",
            "headers": headers,
            "rows": [],
            "total": "",
        }
    titles = [snapshot.titulo_1, snapshot.titulo_2, snapshot.titulo_3, snapshot.titulo_4]
    query = TreeIncome.objects.filter(codigo_empresa=str(company), ejercicio=year)
    for item in path:
        if item["level"] not in titles:
            return None
        query = query.filter(**{f"nivel_{titles.index(item['level']) + 1}": item["label"]})
    if month is not None:
        query = query.filter(movement_date__month=int(month))
    stored = list(query.order_by("movement_date", "asiento", "account_code"))
    total = sum((Decimal(row.amount) for row in stored), Decimal("0"))
    return {
        "title": title,
        "source": "Movimientos",
        "pending": False,
        "message": "",
        "headers": headers,
        "rows": [
            [
                row.movement_date.strftime("%d/%m/%Y") if row.movement_date else "—",
                row.asiento or "—",
                _named(row.account_code, row.account_name),
                row.invoice or "—",
                format_money(row.amount),
            ]
            for row in stored
        ],
        "total": format_money(total),
    }


def _present_groups(company, grouped):
    names = {
        row.code: row.description
        for row in AccountGroup.objects.filter(codigo_empresa=str(company))
    }
    return [
        {
            "code": code,
            "label": _named(code, names.get(code, "")),
            "amount": format_money(bucket["amount"]),
            "lines": bucket["lines"],
        }
        for code, bucket in sorted(grouped.items())
    ]


def _named(code, name):
    code = str(code or "").strip()
    name = str(name or "").strip()
    if name and name != code:
        return f"{code} — {name}" if code else name
    return code or "Sin dato"


def snapshot_updated_at(company, year):
    """Momento en que se guardó el resumen. None si todavía no existe."""

    snapshot = (
        DashboardSnapshot.objects.filter(codigo_empresa=company, ejercicio=year)
        .only("updated_at")
        .first()
    )
    if snapshot is None:
        return None
    return snapshot.updated_at


def _month_of(life, year):
    if life is None or life.order_date is None or life.order_date.year != int(year):
        return None
    return life.order_date.month


def _sum_attr(rows, name):
    return sum((Decimal(getattr(row, name)) for row in rows), Decimal("0"))


def _closed_figures(company, year, groups, snapshot):
    """Tarjetas y árbol de los meses cerrados, y el pendiente de cada mes abierto."""

    closed = closed_months(company, year)
    if not closed:
        return None
    lives = {
        life.codigo_proyecto: life
        for life in ProjectLife.objects.filter(codigo_empresa=str(company))
    }
    shares = list(
        ProjectExerciseShare.objects.filter(codigo_empresa=str(company), ejercicio=year)
    )
    seen = set()
    closed_shares = []
    pending = {
        month: {"count": 0, "amount": Decimal("0")}
        for month in range(1, 13)
        if month not in closed
    }
    for share in shares:
        seen.add(share.codigo_proyecto)
        month = _month_of(lives.get(share.codigo_proyecto), year)
        if month in closed:
            closed_shares.append(share)
        elif month in pending:
            pending[month]["count"] += share.sales_count
            pending[month]["amount"] += Decimal(share.sales_amount)
    for project, life in lives.items():
        if project in seen:
            continue
        month = _month_of(life, year)
        amount = Decimal(life.order_base or 0)
        if month in closed and amount:
            closed_shares.append(
                ProjectExerciseShare(
                    codigo_proyecto=project,
                    sales_count=1,
                    sales_amount=amount,
                    nivel_1="",
                    nivel_2="",
                    nivel_3="",
                    nivel_4="",
                )
            )
        elif month in pending and amount:
            pending[month]["count"] += 1
            pending[month]["amount"] += amount
    names = dict(MONTH_NAMES)
    allowed = set(groups)
    titles = [snapshot.titulo_1, snapshot.titulo_2, snapshot.titulo_3, snapshot.titulo_4]
    indexes = [index for index, title in enumerate(titles) if title and level_group(title) in allowed]
    keys = _visible_figures(allowed)
    result = {
        "pending_months": [
            {"name": names[month], "count": bucket["count"], "amount": bucket["amount"]}
            for month, bucket in pending.items()
        ]
    }
    open_only = _open_only_paths(shares, lives, year, closed)
    stored = [
        row
        for row in snapshot.rows.all()
        if (row.nivel_1, row.nivel_2, row.nivel_3, row.nivel_4) not in open_only
    ]
    if indexes and keys and stored:
        result["hierarchy"] = _nest(stored, indexes, titles, 0, keys)
    elif indexes and keys:
        result["hierarchy"] = _nest(
            [share for share in closed_shares if share.nivel_1 or share.nivel_2 or share.nivel_3 or share.nivel_4],
            indexes,
            titles,
            0,
            keys,
        )
    if InformationGroup.PEDIDOS_VENTA in allowed:
        result["sales"] = {
            "count": sum(share.sales_count for share in closed_shares),
            "amount": _sum_attr(closed_shares, "sales_amount"),
        }
    if InformationGroup.PEDIDOS_COMPRA in allowed:
        result["purchase_orders"] = {
            "count": sum(share.purchase_order_count for share in closed_shares),
            "amount": _sum_attr(closed_shares, "purchase_order_amount"),
        }
    if InformationGroup.ALBARANES_VENTA in allowed:
        result["sales_deliveries"] = {
            "count": sum(share.sales_delivery_count for share in closed_shares),
            "amount": _sum_attr(closed_shares, "sales_delivery_amount"),
        }
    if InformationGroup.ALBARANES_COMPRA in allowed:
        result["purchase_deliveries"] = {
            "count": sum(share.purchase_delivery_count for share in closed_shares),
            "amount": _sum_attr(closed_shares, "purchase_delivery_amount"),
        }
    if InformationGroup.MOVIMIENTOS in allowed:
        ledgers = list(MonthLedger.objects.filter(codigo_empresa=str(company), ejercicio=year))
        if ledgers:
            chosen = [row for row in ledgers if row.mes in closed]
            income = _sum_attr(chosen, "income_amount")
            expenses = _sum_attr(chosen, "expense_amount")
            income_count = sum(row.income_count for row in chosen)
            expense_count = sum(row.expense_count for row in chosen)
        else:
            income = _sum_attr(closed_shares, "income_amount")
            expenses = _sum_attr(closed_shares, "expense_amount")
            income_count = sum(share.income_count for share in closed_shares)
            expense_count = sum(share.expense_count for share in closed_shares)
        result["income"] = {"count": income_count, "amount": income}
        result["accounted_purchases"], result["expenses"] = _split_book(
            company, year, expenses, expense_count, closed
        )
        result["margin"] = income - result["accounted_purchases"]["amount"] - result["expenses"]["amount"]
        result["margin_percent"] = margin_ratio(income, result["margin"])
    return result


def load_dashboard(company, year, groups):
    """Devuelve el resumen guardado. Si no existe, no consulta el origen comercial."""

    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=company, ejercicio=year).first()
    if snapshot is None:
        return None
    closed_view = _closed_figures(company, year, groups, snapshot)
    if closed_view is not None:
        return closed_view
    allowed = set(groups)
    titles = [snapshot.titulo_1, snapshot.titulo_2, snapshot.titulo_3, snapshot.titulo_4]
    indexes = [index for index, title in enumerate(titles) if title and level_group(title) in allowed]
    keys = _visible_figures(allowed)
    result = {}
    if indexes and keys:
        result["hierarchy"] = _nest(list(snapshot.rows.all()), indexes, titles, 0, keys)
    if InformationGroup.PEDIDOS_VENTA in allowed:
        result["sales"] = {"count": snapshot.sales_count, "amount": snapshot.sales_amount}
        aside = [
            {"identity": row.identity, "amount": row.amount, "incomplete": row.incomplete}
            for row in snapshot.aside_rows.all()
        ]
        if aside:
            result["aside"] = aside
    if InformationGroup.PEDIDOS_COMPRA in allowed:
        result["purchase_orders"] = {
            "count": snapshot.purchase_order_count,
            "amount": snapshot.purchase_order_amount,
        }
    if InformationGroup.ALBARANES_VENTA in allowed:
        result["sales_deliveries"] = {
            "count": snapshot.sales_delivery_count,
            "amount": snapshot.sales_delivery_amount,
        }
    if InformationGroup.ALBARANES_COMPRA in allowed:
        result["purchase_deliveries"] = {
            "count": snapshot.purchase_delivery_count,
            "amount": snapshot.purchase_delivery_amount,
        }
    if InformationGroup.MOVIMIENTOS in allowed:
        result["income"] = {"count": snapshot.income_count, "amount": snapshot.income_amount}
        result["accounted_purchases"], result["expenses"] = _split_book(
            company, year, snapshot.expense_amount, snapshot.expense_count
        )
        result["margin"] = (
            snapshot.income_amount
            - result["accounted_purchases"]["amount"]
            - result["expenses"]["amount"]
        )
        result["margin_percent"] = margin_ratio(snapshot.income_amount, result["margin"])
    return result


def load_orders(company, year):
    snapshot = DashboardSnapshot.objects.filter(codigo_empresa=company, ejercicio=year).first()
    if snapshot is None:
        return None
    rows = [
        {
            "identity": row.identity,
            "project": row.project,
            "price": row.price,
            "cost": row.cost,
            "margin": row.margin,
            "percent": margin_ratio(row.income, row.margin),
            "income": row.income,
            "incomplete": row.incomplete,
        }
        for row in snapshot.orders.all()
    ]
    return {"rows": rows, "pending_count": snapshot.pending_count}
