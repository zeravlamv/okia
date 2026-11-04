"""Proyectos del ejercicio cuya ficha ya guardada no cuadra. No lee el origen."""

from decimal import Decimal

from apps.access.models import InformationGroup
from apps.margins.models import REVIEW_DONE, REVIEW_PENDING, ProjectDocumentLine, ProjectLife
from apps.margins.project_life import KIND_COMMITTED, KIND_DELIVERY, KIND_ORDER

SALE_ORDER = "sale_order"
PAIR_SALE = "Pedido de venta y albaranado"
PAIR_PURCHASE = "Pedido de compra y albaranado"


def pending_projects(company, year, groups):
    """Proyectos en Pdte. Revisar con alguna pareja visible distinta."""

    return _projects(company, year, groups, REVIEW_PENDING)


def reviewed_projects(company, year, groups):
    """Proyectos en Revisado que siguen con alguna pareja visible distinta."""

    return _projects(company, year, groups, REVIEW_DONE)


def _projects(company, year, groups, status):
    company = str(company)
    year = int(year)
    allowed = set(groups)
    show_sale = (
        InformationGroup.PEDIDOS_VENTA in allowed and InformationGroup.ALBARANES_VENTA in allowed
    )
    show_purchase = (
        InformationGroup.PEDIDOS_COMPRA in allowed and InformationGroup.ALBARANES_COMPRA in allowed
    )
    found = []
    for life in _lives_in_year(company, year):
        if life.review_status != status:
            continue
        pairs = _pairs(life, show_sale, show_purchase)
        if not pairs:
            continue
        found.append(
            {
                "code": life.codigo_proyecto,
                "customer": life.customer_name or "",
                "pairs": pairs,
            }
        )
    found.sort(key=lambda item: item["code"].casefold())
    return found


def _lives_in_year(company, year):
    lined = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=SALE_ORDER,
        position=0,
        line_date__year=year,
    ).values_list("life_id", flat=True)
    any_lines = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=SALE_ORDER,
        position=0,
    ).values_list("life_id", flat=True)
    chosen = set(lined)
    chosen.update(
        ProjectLife.objects.filter(codigo_empresa=company, order_date__year=year)
        .exclude(pk__in=any_lines)
        .values_list("pk", flat=True)
    )
    return ProjectLife.objects.filter(pk__in=chosen).prefetch_related("milestones", "purchases")


def _sum(rows):
    total = Decimal("0")
    for row in rows:
        if row.amount is None:
            return None
        total += Decimal(row.amount)
    return total


def _gap(left, right, name, left_label, right_label):
    if left is None or right is None or left == right:
        return None
    return {
        "name": name,
        "left_label": left_label,
        "right_label": right_label,
        "left": left,
        "right": right,
    }


def _pairs(life, show_sale, show_purchase):
    delivered = _sum(list(life.milestones.all()))
    pairs = []
    if show_sale:
        order_base = None if life.order_base is None else Decimal(life.order_base)
        gap = _gap(order_base, delivered, PAIR_SALE, "Pedido de venta", "Albaranado")
        if gap:
            pairs.append(gap)
    if show_purchase:
        purchases = list(life.purchases.all())
        ordered = _sum(row for row in purchases if row.kind in (KIND_ORDER, KIND_COMMITTED))
        bought = _sum(row for row in purchases if row.kind == KIND_DELIVERY)
        gap = _gap(ordered, bought, PAIR_PURCHASE, "Pedido de compra", "Albaranado")
        if gap:
            pairs.append(gap)
    return pairs
