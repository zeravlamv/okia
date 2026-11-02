from decimal import Decimal

from apps.access.models import AnalyticalLevel, InformationGroup
from apps.erp.mapping import is_cancelled
from apps.margins.hierarchy import FIGURES, build_hierarchy
from apps.margins.services import in_period, ledger_total, margin_ratio, sale_price

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


def level_group(title):
    for name, group in _LEVELS.values():
        if name == title:
            return group
    return None


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


def _documents_value(company, year, documents):
    """Número e importe sin impuestos. Manda la base de la cabecera."""

    active = [
        document
        for document in documents
        if document.codigo_empresa == company
        and in_period(document, year)
        and not is_cancelled(document.status)
    ]
    return {"count": len(active), "amount": _prices(active)}


def _visible_figures(allowed):
    keys = []
    if InformationGroup.PEDIDOS_VENTA in allowed:
        keys.append("sales")
    if InformationGroup.MOVIMIENTOS in allowed:
        keys.append("income")
        keys.append("expenses")
        keys.append("margin")
    return [key for key in FIGURES if key in keys]


def _strip(nodes, keys):
    visible = []
    for node in nodes:
        item = {
            "level": node["level"],
            "label": node["label"],
            "incomplete": node["incomplete"],
            "children": _strip(node["children"], keys),
        }
        for key in keys:
            item[key] = node[key]
        visible.append(item)
    return visible


def build_dashboard(
    company,
    year,
    orders,
    purchases,
    movements,
    groups,
    labels=None,
    purchase_orders=None,
    sales_deliveries=None,
    purchase_deliveries=None,
    ledger=None,
):
    """Un grupo no permitido no ocupa un hueco con valor cero."""

    allowed = set(groups)
    active = _active_orders(company, year, orders)
    dimensions = [item for item in analytical_dimensions() if item[2] in allowed][:4]
    tree = build_hierarchy(
        company,
        year,
        orders,
        purchases,
        movements,
        labels or {},
        dimensions,
        purchase_orders=purchase_orders,
    )
    result = {}
    if dimensions:
        result["hierarchy"] = _strip(tree["nodes"], _visible_figures(allowed))
    if InformationGroup.PEDIDOS_VENTA in allowed and tree["aside"]:
        result["aside"] = tree["aside"]
    if InformationGroup.PEDIDOS_VENTA in allowed:
        result["sales"] = {"count": len(active), "amount": _prices(active)}
    if purchase_orders is not None and InformationGroup.PEDIDOS_COMPRA in allowed:
        result["purchase_orders"] = _documents_value(company, year, purchase_orders)
    if sales_deliveries is not None and InformationGroup.ALBARANES_VENTA in allowed:
        result["sales_deliveries"] = _documents_value(company, year, sales_deliveries)
    if purchase_deliveries is not None and InformationGroup.ALBARANES_COMPRA in allowed:
        result["purchase_deliveries"] = _documents_value(company, year, purchase_deliveries)
    if InformationGroup.MOVIMIENTOS in allowed:
        source = movements if ledger is None else ledger
        result["income"] = ledger_total(company, year, source, "income")
        result["expenses"] = ledger_total(company, year, source, "expense")
        result["margin"] = result["income"]["amount"] - result["expenses"]["amount"]
        result["margin_percent"] = margin_ratio(result["income"]["amount"], result["margin"])
    return result
