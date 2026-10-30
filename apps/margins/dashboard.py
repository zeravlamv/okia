from decimal import Decimal

from apps.access.models import AnalyticalLevel, InformationGroup
from apps.erp.mapping import is_cancelled
from apps.margins.services import build_report, in_period, sale_price

_LEVELS = {
    AnalyticalLevel.Level.CANAL: ("Canal", InformationGroup.CANALES),
    AnalyticalLevel.Level.DELEGACION: ("Delegación", InformationGroup.DELEGACIONES),
    AnalyticalLevel.Level.DEPARTAMENTO: ("Departamento", InformationGroup.DEPARTAMENTOS),
    AnalyticalLevel.Level.PROYECTO: ("Proyecto", InformationGroup.PROYECTOS),
    AnalyticalLevel.Level.SECCION: ("Sección", InformationGroup.SECCIONES),
}
_DEFAULT_ORDER = (
    AnalyticalLevel.Level.CANAL,
    AnalyticalLevel.Level.DELEGACION,
    AnalyticalLevel.Level.DEPARTAMENTO,
    AnalyticalLevel.Level.PROYECTO,
    AnalyticalLevel.Level.SECCION,
)


def analytical_dimensions():
    """El árbol analítico guardado fija el orden. Si falta algún nivel, se usa el orden inicial."""

    stored = [
        row.code
        for row in AnalyticalLevel.objects.order_by("position", "code")
        if row.code in _LEVELS
    ]
    if len(stored) != len(_DEFAULT_ORDER) or len(set(stored)) != len(_DEFAULT_ORDER):
        stored = list(_DEFAULT_ORDER)
    return tuple((code, *_LEVELS[code]) for code in stored)


def _sum(values):
    total = Decimal("0")
    for value in values:
        if value is not None:
            total += Decimal(value)
    return total


def _active_orders(company, year, orders):
    return [
        order
        for order in orders
        if order.codigo_empresa == company
        and in_period(order, year)
        and not is_cancelled(order.status)
    ]


def _prices(orders):
    total = Decimal("0")
    for order in orders:
        price, _incomplete = sale_price(order)
        if price is not None:
            total += price
    return total


def period_purchases(company, year, purchases):
    """El número y el importe son las compras fechadas en el ejercicio.

    No son el coste del pedido: una compra de otro año sigue en el margen.
    """

    amount = Decimal("0")
    documents = set()
    for line in purchases:
        if line.codigo_empresa != company or line.line_date is None:
            continue
        if line.line_date.year != year:
            continue
        if line.amount is None:
            continue
        amount += Decimal(line.amount)
        if line.numero:
            documents.add((line.ejercicio, line.serie, line.numero))
        else:
            documents.add(("linea", id(line)))
    return {"count": len(documents), "amount": amount}


def _code(value):
    if value is None:
        return ""
    return str(value).strip()


def _display(code, names):
    if not code:
        return "Sin dato"
    description = _code(names.get(code))
    if not description or description == code:
        return code
    return f"{code} — {description}"


def _breakdown(orders, labels):
    sections = []
    for attribute, title, _group in analytical_dimensions():
        names = labels.get(attribute, {})
        grouped = {}
        for order in orders:
            price, _incomplete = sale_price(order)
            if price is None:
                continue
            code = _code(getattr(order, attribute, ""))
            grouped[code] = grouped.get(code, Decimal("0")) + price
        if not grouped:
            continue
        rows = [
            {"label": _display(code, names), "amount": amount}
            for code, amount in grouped.items()
        ]
        rows.sort(key=lambda row: row["label"].casefold())
        sections.append({"title": title, "group": _group, "rows": rows})
    return sections


def build_dashboard(company, year, orders, purchases, movements, masters, groups, labels=None):
    """Un grupo no permitido no ocupa un hueco con valor cero."""

    allowed = set(groups)
    active = _active_orders(company, year, orders)
    report = build_report(company, year, orders, purchases, movements)
    result = {}
    if InformationGroup.PEDIDOS_VENTA in allowed:
        result["sales"] = {"count": len(active), "amount": _prices(active)}
        result["breakdown"] = [
            section
            for section in _breakdown(active, labels or {})
            if section["group"] in allowed
        ]
    if InformationGroup.PEDIDOS_COMPRA in allowed:
        result["purchases"] = period_purchases(company, year, purchases)
    margin_groups = {
        InformationGroup.PEDIDOS_VENTA,
        InformationGroup.PEDIDOS_COMPRA,
        InformationGroup.MOVIMIENTOS,
    }
    if margin_groups.issubset(allowed):
        result["margin"] = _sum(row["margin"] for row in report["closed"])
    if {InformationGroup.PEDIDOS_VENTA, InformationGroup.MOVIMIENTOS}.issubset(allowed):
        result["income"] = _sum(row["income"] for row in report["closed"])
    for key, group in (
        ("clientes", InformationGroup.CLIENTES),
        ("proveedores", InformationGroup.PROVEEDORES),
        ("articulos", InformationGroup.ARTICULOS),
    ):
        if group in allowed:
            result[key] = masters.get(key, 0)
    return result
