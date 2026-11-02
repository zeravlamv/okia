from decimal import Decimal

from apps.erp.mapping import (
    indicates_hours,
    is_cancelled,
    is_closing_entry,
    is_cost_account,
    is_expense_account,
    is_income_account,
)

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


def project_purchases(company, project, purchases):
    """Las compras de un pedido cerrado son la suma de las bases de todas sus líneas de compra, con cualquier fecha."""

    total = Decimal("0")
    incomplete = False
    for purchase in purchases:
        if purchase.codigo_empresa != company or purchase.project != project:
            continue
        if purchase.amount is None:
            incomplete = True
            continue
        total += Decimal(purchase.amount)
    return total, incomplete


def project_expenses(company, project, movements):
    """Los gastos son los apuntes de horas, mano de obra o personal de ese proyecto."""

    total = Decimal("0")
    incomplete = False
    for movement in movements:
        if movement.codigo_empresa != company or movement.project != project:
            continue
        if is_income_account(movement.account_code, movement.account_name):
            continue
        if not indicates_hours(movement.account_name):
            continue
        amount, missing = _side_amount(movement.debit, movement.credit, True)
        if missing:
            incomplete = True
            continue
        total += amount
    return total, incomplete


def project_cost(company, project, purchases, movements):
    """El coste son las compras contables y los gastos de ese proyecto. La línea de compra no se suma."""

    del purchases
    total = Decimal("0")
    incomplete = False
    for movement in movements:
        if movement.codigo_empresa != company or movement.project != project:
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        if not is_cost_account(movement.account_code, movement.account_name):
            continue
        amount, missing = _side_amount(movement.debit, movement.credit, True)
        if missing:
            incomplete = True
            continue
        total += amount
    return total, incomplete


def margin_ratio(income, margin):
    """El porcentaje es el margen sobre los ingresos. Sin ingresos, no aplica."""

    if income is None or margin is None or Decimal(income) == 0:
        return None
    return Decimal(margin) / Decimal(income) * Decimal("100")


def project_income(company, project, movements):
    """El margen del pedido es estos ingresos menos los gastos. No se mezcla con el precio."""

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


def in_period(document, year):
    """El periodo elige el documento por su fecha. Si no tiene fecha, entra por el ejercicio.

    No recorta el coste ni los ingresos del proyecto.
    """

    moment = getattr(document, "order_date", None)
    if moment is None:
        moment = getattr(document, "document_date", None)
    if moment is not None:
        return moment.year == year
    return document.ejercicio == year


def movement_in_period(movement, year):
    """La fecha del apunte manda. Si no tiene fecha, manda el ejercicio."""

    if movement.movement_date is not None:
        return movement.movement_date.year == year
    if movement.ejercicio is None:
        return False
    return int(movement.ejercicio) == year


def tree_movement(movement):
    """En el árbol, el gasto sigue siendo el apunte de horas y el ingreso la cuenta de ingreso."""

    if is_closing_entry(getattr(movement, "comment", "")):
        return None, None, False
    if is_income_account(movement.account_code, movement.account_name):
        amount, missing = _side_amount(movement.credit, movement.debit, True)
        return "income", amount, missing
    if indicates_hours(movement.account_name):
        amount, missing = _side_amount(movement.debit, movement.credit, True)
        return "expenses", amount, missing
    return None, None, False


def ledger_total(company, year, movements, kind):
    """Cada movimiento del ejercicio entra una vez. El reparto analítico no lo duplica."""

    total = Decimal("0")
    count = 0
    for movement in movements:
        if movement.codigo_empresa != company or not movement_in_period(movement, year):
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        if kind == "income":
            if not is_income_account(movement.account_code, movement.account_name):
                continue
            amount, missing = _side_amount(movement.credit, movement.debit, True)
        else:
            if not is_expense_account(movement.account_code, movement.account_name):
                continue
            amount, missing = _side_amount(movement.debit, movement.credit, True)
        if missing:
            continue
        total += amount
        count += 1
    return {"count": count, "amount": total}


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
        margin = None if income is None else income - cost
        percent = margin_ratio(income, margin)
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
