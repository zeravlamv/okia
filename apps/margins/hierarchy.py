from decimal import Decimal
from types import SimpleNamespace

from apps.erp.mapping import is_cancelled, is_expense_account, is_income_account
from apps.margins.services import (
    in_period,
    is_closing_entry,
    movement_in_period,
    sale_price,
)

FIGURES = ("sales", "income", "purchases", "expenses", "margin")


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


def _classify(company, year, orders):
    """El anulado no entra. El proyecto único cierra margen. El resto va al grupo aparte."""

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
    for group in by_project.values():
        if len(group) != 1:
            pending.extend(group)
            continue
        closed.append(group[0])
    return closed, pending


def _order_figures(order):
    """La venta sigue el pedido de venta. La compra sigue el pedido de compra."""

    sales, sales_missing = sale_price(order)
    return (
        {
            "sales": sales,
            "income": Decimal("0"),
            "purchases": Decimal("0"),
            "expenses": Decimal("0"),
            "margin": Decimal("0"),
        },
        sales_missing,
    )


def _blank():
    return {
        "incomplete": False,
        "kids": {},
        "children": [],
        "sales": Decimal("0"),
        "income": Decimal("0"),
        "purchases": Decimal("0"),
        "expenses": Decimal("0"),
        "margin": Decimal("0"),
    }


def _absorb(node, figures, incomplete):
    """Una pieza sin importe no se suma y el resultado queda incompleto."""

    if incomplete:
        node["incomplete"] = True
    for key in FIGURES:
        value = figures[key]
        if value is None:
            node["incomplete"] = True
            continue
        node[key] += value


def _place_codes(root, codes, dimensions, labels, figures, incomplete):
    node = root
    for (attribute, title, _group), code in zip(dimensions, codes):
        kids = node["kids"]
        if code not in kids:
            created = _blank()
            created["level"] = title
            created["label"] = _display(code, labels.get(attribute, {}))
            created["code"] = code
            kids[code] = created
        node = kids[code]
    _absorb(node, figures, incomplete)


def _place(root, order, dimensions, labels, figures, incomplete):
    codes = [_code(getattr(order, attribute, "")) for attribute, _title, _group in dimensions]
    _place_codes(root, codes, dimensions, labels, figures, incomplete)


def _portions(movement, amount):
    """Varias partes se reparten el importe del movimiento. Una sola parte se queda el importe entero."""

    slices = list(movement.slices)
    if len(slices) <= 1:
        return [(slices[0] if slices else None, amount)]
    if amount is None:
        return [(slices[0], None)]
    weights = [
        abs(Decimal(item.amount)) if item.amount is not None else Decimal("0") for item in slices
    ]
    weight_total = sum(weights, Decimal("0"))
    if weight_total == 0:
        share = (amount / len(slices)).quantize(Decimal("0.01"))
        portions = [(item, share) for item in slices[:-1]]
        portions.append((slices[-1], amount - share * (len(slices) - 1)))
        return portions
    portions = []
    used = Decimal("0")
    for item, weight in zip(slices[:-1], weights[:-1]):
        part = (amount * weight / weight_total).quantize(Decimal("0.01"))
        portions.append((item, part))
        used += part
    portions.append((slices[-1], amount - used))
    return portions


def _header_signed(movement, kind):
    if kind == "income":
        if movement.credit is None and movement.debit is None:
            return None
        return Decimal(movement.credit or 0) - Decimal(movement.debit or 0)
    if movement.debit is None and movement.credit is None:
        return None
    return Decimal(movement.debit or 0) - Decimal(movement.credit or 0)


def _line_amount(header_signed, line_amount):
    """El importe de AnaMovimientos ya está definido. No se vuelve a repartir."""

    if line_amount is None or header_signed is None:
        return None
    amount = Decimal(line_amount)
    if header_signed < 0 and amount > 0:
        return -amount
    return amount


def _line_codes(dimensions, analytic, project=None):
    codes = []
    for attribute, _title, _group in dimensions:
        if attribute == "project" and project is not None:
            codes.append(project)
            continue
        codes.append(_code(getattr(analytic, attribute, "")))
    return codes


def _unique_projects(orders, purchase_orders):
    """Un trío canal, delegación y departamento con un solo proyecto."""

    grouped = {}
    for document in list(orders) + list(purchase_orders or []):
        if is_cancelled(getattr(document, "status", "")):
            continue
        channel = _code(getattr(document, "channel", ""))
        delegation = _code(getattr(document, "delegation", ""))
        department = _code(getattr(document, "department", ""))
        project = _code(getattr(document, "project", ""))
        if not (channel and delegation and department and project):
            continue
        grouped.setdefault((channel, delegation, department), set()).add(project)
    return {key: next(iter(projects)) for key, projects in grouped.items() if len(projects) == 1}


def _resolved_project(analytic, unique):
    channel = _code(getattr(analytic, "channel", ""))
    delegation = _code(getattr(analytic, "delegation", ""))
    department = _code(getattr(analytic, "department", ""))
    project = _code(getattr(analytic, "project", ""))
    if project or not (channel and delegation and department):
        return project
    return unique.get((channel, delegation, department), "")


def _movement_figures(kind, amount):
    figures = {key: Decimal("0") for key in FIGURES}
    figures[kind] = amount
    if amount is None:
        figures["margin"] = None
    elif kind == "income":
        figures["margin"] = amount
    elif kind in ("expenses", "purchases"):
        figures["margin"] = -amount
    return figures


def _apply_analytical(root, company, year, movements, labels, dimensions, unique):
    """Cada fila de AnaMovimientos suma su importe en los niveles que ya trae."""

    for movement in movements:
        if movement.codigo_empresa != company or not movement_in_period(movement, year):
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        if is_income_account(movement.account_code, movement.account_name):
            kind = "income"
        elif is_expense_account(movement.account_code, movement.account_name):
            kind = "expenses"
        else:
            continue
        signed = _header_signed(movement, kind)
        lines = [analytic for analytic in movement.slices if any(_line_codes(dimensions, analytic))]
        if not lines and signed is not None:
            lines = [
                SimpleNamespace(
                    channel=getattr(movement, "channel", ""),
                    delegation=getattr(movement, "delegation", ""),
                    department=getattr(movement, "department", ""),
                    project=_code(movement.project),
                    section=getattr(movement, "section", ""),
                    amount=abs(signed),
                )
            ]
        for analytic in lines:
            project = _resolved_project(analytic, unique)
            codes = _line_codes(dimensions, analytic, project)
            if not any(codes):
                continue
            amount = _line_amount(signed, analytic.amount)
            _place_codes(
                root,
                codes,
                dimensions,
                labels,
                _movement_figures(kind, amount),
                amount is None,
            )


def _rollup(node):
    children = []
    ordered = sorted(node["kids"].values(), key=lambda item: item["label"].casefold())
    for child in ordered:
        _rollup(child)
        for key in FIGURES:
            node[key] += child[key]
        if child["incomplete"]:
            node["incomplete"] = True
        children.append(child)
    node["children"] = children
    node.pop("kids", None)


def _aside(order):
    price, incomplete = sale_price(order)
    return {
        "identity": f"{order.ejercicio} / {order.serie} / {order.numero}",
        "amount": price,
        "incomplete": incomplete,
    }


def _invoice_number(comment):
    """El comentario «Ntra.Fra.Num.: 260501» guarda el número de factura."""

    text = str(comment or "").strip()
    marker = "ntra.fra.num.:"
    folded = text.casefold()
    start = folded.find(marker)
    if start < 0:
        return ""
    return text[start + len(marker) :].strip()


def tree_income_entries(company, year, movements, dimensions, unique):
    """Cada ingreso que el árbol coloca, con los códigos del nivel donde cae."""

    company = str(company)
    year = int(year)
    found = []
    for movement in movements:
        if str(movement.codigo_empresa) != company or not movement_in_period(movement, year):
            continue
        if is_closing_entry(getattr(movement, "comment", "")):
            continue
        if not is_income_account(movement.account_code, movement.account_name):
            continue
        signed = _header_signed(movement, "income")
        lines = [analytic for analytic in movement.slices if any(_line_codes(dimensions, analytic))]
        if not lines and signed is not None:
            lines = [
                SimpleNamespace(
                    channel=getattr(movement, "channel", ""),
                    delegation=getattr(movement, "delegation", ""),
                    department=getattr(movement, "department", ""),
                    project=_code(movement.project),
                    section=getattr(movement, "section", ""),
                    amount=abs(signed),
                )
            ]
        for analytic in lines:
            project = _resolved_project(analytic, unique)
            codes = _line_codes(dimensions, analytic, project)
            if not any(codes):
                continue
            amount = _line_amount(signed, analytic.amount)
            if amount is None:
                continue
            found.append(
                {
                    "date": movement.movement_date,
                    "asiento": _code(getattr(movement, "asiento", "")),
                    "account_code": _code(movement.account_code),
                    "account_name": _code(movement.account_name),
                    "invoice": _invoice_number(getattr(movement, "comment", "")),
                    "amount": amount,
                    "codes": codes,
                }
            )
    return found


def build_hierarchy(
    company, year, orders, purchases, movements, labels, dimensions, purchase_orders=None
):
    """La venta sigue el pedido. El coste sigue AnaMovimientos. La línea de compra no entra."""

    del purchases
    closed, pending = _classify(company, year, orders)
    root = _blank()
    if dimensions:
        for order in closed:
            figures, incomplete = _order_figures(order)
            _place(root, order, dimensions, labels or {}, figures, incomplete)
        _apply_analytical(
            root,
            company,
            year,
            movements,
            labels or {},
            dimensions,
            _unique_projects(orders, purchase_orders),
        )
    _rollup(root)
    aside = sorted((_aside(order) for order in pending), key=lambda item: item["identity"])
    return {"nodes": root["children"], "totals": {key: root[key] for key in FIGURES}, "aside": aside}
