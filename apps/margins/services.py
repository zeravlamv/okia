from decimal import Decimal

from apps.erp.mapping import indicates_hours, is_cancelled, is_income_account

# Las reglas de cálculo están en negocio.md.


def sale_price(order):
    """El precio de venta es la base de la cabecera. Si no existe, es la suma de las bases de las líneas.

    El impuesto no entra en el precio ni en el margen.
    """

    if order.header_base is not None:
        return Decimal(order.header_base), False
    total = Decimal("0")
    found = False
    incomplete = False
    for line in order.lines:
        if line.base is None:
            incomplete = True
            continue
        total += Decimal(line.base)
        found = True
    if not found:
        return None, True
    return total, incomplete


def _side_amount(left, right, left_minus_right):
    if left is None and right is None:
        return None, True
    amount = Decimal(left or 0) - Decimal(right or 0)
    if not left_minus_right:
        amount = -amount
    return amount, False


def project_cost(company, project, purchases, movements):
    """Si la misma hora está en los dos sitios, entran las dos."""

    total = Decimal("0")
    incomplete = False
    for purchase in purchases:
        if purchase.codigo_empresa != company or purchase.project != project:
            continue
        if purchase.amount is None:
            incomplete = True
            continue
        total += Decimal(purchase.amount)
    for movement in movements:
        if movement.codigo_empresa != company or movement.project != project:
            continue
        if not indicates_hours(movement.account_name):
            continue
        amount, missing = _side_amount(movement.debit, movement.credit, True)
        if missing:
            incomplete = True
            continue
        total += amount
    return total, incomplete


def project_income(company, project, movements):
    """No se suma ni se resta al precio, al coste ni al margen."""

    total = Decimal("0")
    incomplete = False
    found = False
    for movement in movements:
        if movement.codigo_empresa != company or movement.project != project:
            continue
        if not is_income_account(movement.account_code, movement.account_name):
            continue
        amount, missing = _side_amount(movement.credit, movement.debit, True)
        if missing:
            incomplete = True
            continue
        total += amount
        found = True
    return total, incomplete or not found and False


def in_period(order, year):
    """El periodo elige el pedido. No recorta el coste ni los ingresos por la fecha de la imputación."""

    if order.order_date is not None:
        return order.order_date.year == year
    return order.ejercicio == year


def _by_project(rows, company):
    grouped = {}
    for row in rows:
        if row.codigo_empresa != company or not row.project:
            continue
        grouped.setdefault(row.project, []).append(row)
    return grouped


def build_report(company, year, orders, purchases, movements):
    """Si más de un pedido no anulado de la empresa comparte proyecto, el coste y los ingresos no se asignan a uno ni se duplican.

    Una pieza sin importe no se suma y el resultado queda incompleto.
    """

    purchases_by_project = _by_project(purchases, company)
    movements_by_project = _by_project(movements, company)
    active = [
        order
        for order in orders
        if order.codigo_empresa == company
        and in_period(order, year)
        and not is_cancelled(order.status)
    ]
    pending = []
    by_project = {}
    for order in active:
        if not order.project:
            pending.append(order)
            continue
        by_project.setdefault(order.project, []).append(order)

    closed = []
    for project, group in by_project.items():
        if len(group) != 1:
            pending.extend(group)
            continue
        order = group[0]
        price, price_incomplete = sale_price(order)
        cost, cost_incomplete = project_cost(
            company, project, purchases_by_project.get(project, []), movements_by_project.get(project, [])
        )
        income, income_incomplete = project_income(
            company, project, movements_by_project.get(project, [])
        )
        incomplete = price_incomplete or cost_incomplete or income_incomplete
        margin = None if price is None else price - cost
        percent = None
        if price not in (None, Decimal("0")) and margin is not None:
            percent = margin / price * Decimal("100")
        closed.append(
            {
                "ejercicio": order.ejercicio,
                "serie": order.serie,
                "numero": order.numero,
                "project": project,
                "price": price,
                "cost": cost,
                "margin": margin,
                "percent": percent,
                "income": income,
                "incomplete": incomplete,
            }
        )
    closed.sort(key=lambda row: (row["ejercicio"], row["serie"], row["numero"]))
    return {"closed": closed, "pending_count": len(pending)}
