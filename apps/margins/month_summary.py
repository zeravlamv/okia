"""Agrupa las fichas ya guardadas de un mes. No lee el origen ni escribe."""

from decimal import Decimal

from apps.access.models import InformationGroup
from apps.margins.format import format_money, format_percent
from apps.margins.models import (
    MONTH_NAMES,
    MonthLedger,
    ProjectDocumentLine,
    ProjectLife,
    ProjectMilestone,
    ProjectPurchase,
)
from apps.margins.snapshot import _split_book
from apps.margins.project_life import (
    KIND_COMMITTED,
    KIND_DELIVERY,
    KIND_ORDER,
    _label,
    _purchase_order_pending,
)
from apps.margins.services import margin_ratio

SALE_ORDER = "sale_order"
_MONTH_NAMES = dict(MONTH_NAMES)
_COLUMNS = (
    ("order", "Pedido de cliente", "venta"),
    ("deliveries", "Albaranes de cliente", "venta"),
    ("purchase_orders", "Pedidos de compra", "compra"),
    ("purchase_deliveries", "Albaranes de compra", "compra"),
    ("expenses", "Gastos", "gasto"),
)


def chosen_month(raw, year, today):
    """Mes pedido, o el de hoy si el ejercicio es el año en curso, o enero."""

    try:
        month = int(raw)
    except (TypeError, ValueError):
        month = 0
    if 1 <= month <= 12:
        return month
    if int(year) == today.year:
        return today.month
    return 1


def load_month_summary(company, year, month):
    """Fichas cuyo pedido de venta cae en el mes, cada una una sola vez y entera."""

    company = str(company)
    year = int(year)
    month = int(month)
    lines = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=SALE_ORDER,
        position=0,
        line_date__year=year,
    )
    selected = set()
    months_of = {}
    for line in lines:
        if line.line_date is None:
            continue
        months_of.setdefault(line.life_id, set()).add(line.line_date.month)
        if line.line_date.month == month:
            selected.add(line.life_id)
    stored_orders = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=SALE_ORDER,
        position=0,
    ).values_list("life_id", flat=True)
    fallbacks = ProjectLife.objects.filter(
        codigo_empresa=company,
        order_date__year=year,
        order_date__month=month,
    ).exclude(pk__in=stored_orders)
    for life in fallbacks:
        selected.add(life.pk)
    lives = list(
        ProjectLife.objects.filter(codigo_empresa=company, pk__in=selected)
        .prefetch_related("milestones", "purchases", "expenses", "incomes")
        .order_by("codigo_proyecto")
    )
    rows = [_row(life, months_of.get(life.pk, set()), month) for life in lives]
    commercial = _commercial(company, year, month)
    analytics = _analytics(lives)
    return _assemble(year, month, rows, commercial, analytics)


def month_board(company, year, month, groups):
    """Las mismas cifras que una columna del cuadro, más el comercial de ese mes."""

    company = str(company)
    year = int(year)
    month = int(month)
    allowed = set(groups)
    commercial = _commercial(company, year, month)
    counts = _commercial_counts(company, year, month)
    cards = {}
    if InformationGroup.PEDIDOS_VENTA in allowed:
        cards["sales"] = {"count": counts["order"], "amount": commercial["order"]}
    if InformationGroup.PEDIDOS_COMPRA in allowed:
        cards["purchase_orders"] = {"count": counts["purchase_orders"], "amount": commercial["purchase_orders"]}
    if InformationGroup.ALBARANES_VENTA in allowed:
        cards["sales_deliveries"] = {"count": counts["deliveries"], "amount": commercial["deliveries"]}
    if InformationGroup.ALBARANES_COMPRA in allowed:
        cards["purchase_deliveries"] = {
            "count": counts["purchase_deliveries"],
            "amount": commercial["purchase_deliveries"],
        }
    ledger = MonthLedger.objects.filter(codigo_empresa=company, ejercicio=year, mes=month).first()
    if InformationGroup.MOVIMIENTOS in allowed and ledger is not None:
        purchases, expenses = _split_book(
            company,
            year,
            ledger.expense_amount,
            ledger.expense_count,
            [month],
        )
        income = Decimal(ledger.income_amount)
        margin = income - purchases["amount"] - expenses["amount"]
        cards["income"] = {"count": ledger.income_count, "amount": income}
        cards["accounted_purchases"] = purchases
        cards["expenses"] = expenses
        cards["margin"] = margin
        cards["margin_percent"] = margin_ratio(income, margin)
    stored = any(value["amount"] not in (None, Decimal("0")) for value in cards.values() if isinstance(value, dict))
    if ledger is not None and InformationGroup.MOVIMIENTOS in allowed:
        stored = True
    return {"cards": cards, "empty": not stored}


def _commercial_counts(company, year, month):
    """Cuenta documentos con fecha en el mes. No lee el origen."""

    order_lines = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=SALE_ORDER,
        position=0,
        line_date__year=year,
        line_date__month=month,
    )
    known_lives = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=SALE_ORDER,
        position=0,
    ).values("life_id")
    fallbacks = ProjectLife.objects.filter(
        codigo_empresa=company,
        order_date__year=year,
        order_date__month=month,
    ).exclude(pk__in=known_lives)
    return {
        "order": order_lines.count() + fallbacks.count(),
        "deliveries": ProjectMilestone.objects.filter(
            life__codigo_empresa=company,
            delivery_date__year=year,
            delivery_date__month=month,
        ).count(),
        "purchase_orders": ProjectPurchase.objects.filter(
            life__codigo_empresa=company,
            kind__in=(KIND_ORDER, KIND_COMMITTED),
            document_date__year=year,
            document_date__month=month,
        ).count(),
        "purchase_deliveries": ProjectPurchase.objects.filter(
            life__codigo_empresa=company,
            kind=KIND_DELIVERY,
            document_date__year=year,
            document_date__month=month,
        ).count(),
    }


_DOCUMENT_KINDS = {
    "pedido": {
        "permission": InformationGroup.PEDIDOS_VENTA,
        "title": "Pedidos de venta",
        "source": "CabeceraPedidoCliente",
        "party": "Cliente",
        "line_kind": "sale_order",
    },
    "pedido_compra": {
        "permission": InformationGroup.PEDIDOS_COMPRA,
        "title": "Pedidos de compra",
        "source": "CabeceraPedidoProveedor",
        "party": "Proveedor",
        "line_kind": "purchase_order",
    },
    "albaran": {
        "permission": InformationGroup.ALBARANES_VENTA,
        "title": "Albaranes de venta",
        "source": "CabeceraAlbaranCliente",
        "party": "Cliente",
        "line_kind": "sale_delivery",
    },
    "albaran_compra": {
        "permission": InformationGroup.ALBARANES_COMPRA,
        "title": "Albaranes de compra",
        "source": "CabeceraAlbaranProveedor",
        "party": "Proveedor",
        "line_kind": "purchase_delivery",
    },
}


def month_document_detail(company, year, month, kind, groups):
    """Documentos del mes y el acceso a sus líneas. No lee el origen."""

    spec = _DOCUMENT_KINDS.get(kind)
    if spec is None:
        return None
    allowed = set(groups)
    if spec["permission"] not in allowed:
        return {"forbidden": True}
    company = str(company)
    year = int(year)
    month = int(month)
    show_clients = InformationGroup.CLIENTES in allowed
    show_suppliers = InformationGroup.PROVEEDORES in allowed
    if kind == "pedido":
        rows, total = _sale_order_documents(company, year, month, show_clients)
    elif kind == "pedido_compra":
        rows, total = _purchase_documents(company, year, month, (KIND_ORDER, KIND_COMMITTED), show_suppliers, "purchase_order")
    elif kind == "albaran":
        rows, total = _sale_delivery_documents(company, year, month, show_clients)
    else:
        rows, total = _purchase_documents(company, year, month, (KIND_DELIVERY,), show_suppliers, "purchase_delivery")
    names = dict(MONTH_NAMES)
    document_header = "Pedido" if kind.startswith("pedido") else "Albarán"
    return {
        "kind": kind,
        "title": f"{spec['title']} de {names[month]} de {year}",
        "source": spec["source"],
        "pending": False,
        "message": "",
        "headers": ["Fecha", "Proyecto", document_header, spec["party"], "Importe"],
        "rows": rows,
        "total": format_money(total),
    }


def _document_row(when, project, document, party, amount, line_kind):
    return {
        "cells": [
            when.strftime("%d/%m/%Y") if when else "—",
            project or "Sin dato",
            document or "Pedido",
            party or "Sin dato",
            format_money(amount),
        ],
        "project": project or "",
        "document": document or "",
        "lineKind": line_kind,
    }


def _sale_order_documents(company, year, month, show_clients):
    rows = []
    total = Decimal("0")
    headers = (
        ProjectDocumentLine.objects.filter(
            life__codigo_empresa=company,
            kind="sale_order",
            position=0,
            line_date__year=year,
            line_date__month=month,
        )
        .select_related("life")
        .order_by("line_date", "document_key")
    )
    for line in headers:
        if line.amount is not None:
            total += Decimal(line.amount)
        life = line.life
        rows.append(
            _document_row(
                line.line_date,
                life.codigo_proyecto,
                line.document_key,
                _label(life.customer_code, life.customer_name, show_clients),
                line.amount,
                "sale_order",
            )
        )
    known = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind="sale_order",
        position=0,
    ).values("life_id")
    fallbacks = ProjectLife.objects.filter(
        codigo_empresa=company,
        order_date__year=year,
        order_date__month=month,
    ).exclude(pk__in=known).order_by("order_date", "codigo_proyecto")
    for life in fallbacks:
        if life.order_base is not None:
            total += Decimal(life.order_base)
        rows.append(
            _document_row(
                life.order_date,
                life.codigo_proyecto,
                "",
                _label(life.customer_code, life.customer_name, show_clients),
                life.order_base,
                "sale_order",
            )
        )
    return rows, total


def _sale_delivery_documents(company, year, month, show_clients):
    rows = []
    total = Decimal("0")
    stored = (
        ProjectMilestone.objects.filter(
            life__codigo_empresa=company,
            delivery_date__year=year,
            delivery_date__month=month,
        )
        .select_related("life")
        .order_by("delivery_date", "ejercicio", "serie", "numero")
    )
    for row in stored:
        if row.amount is not None:
            total += Decimal(row.amount)
        life = row.life
        rows.append(
            _document_row(
                row.delivery_date,
                life.codigo_proyecto,
                f"{row.ejercicio} / {row.serie} / {row.numero}",
                _label(life.customer_code, life.customer_name, show_clients),
                row.amount,
                "sale_delivery",
            )
        )
    return rows, total


def _purchase_documents(company, year, month, kinds, show_suppliers, line_kind):
    rows = []
    total = Decimal("0")
    stored = (
        ProjectPurchase.objects.filter(
            life__codigo_empresa=company,
            kind__in=kinds,
            document_date__year=year,
            document_date__month=month,
        )
        .select_related("life")
        .order_by("document_date", "ejercicio", "serie", "numero")
    )
    for row in stored:
        if row.amount is not None:
            total += Decimal(row.amount)
        rows.append(
            _document_row(
                row.document_date,
                row.life.codigo_proyecto,
                f"{row.ejercicio} / {row.serie} / {row.numero}",
                _label(row.supplier_code, row.supplier_name, show_suppliers),
                row.amount,
                line_kind,
            )
        )
    return rows, total


def present_month(summary, visible):
    """Prepara la ficha del mes con las cifras que el perfil puede ver."""

    show = {
        "order": bool(visible.get("order")),
        "deliveries": bool(visible.get("deliveries")),
        "purchase_orders": bool(visible.get("purchase_orders")),
        "purchase_deliveries": bool(visible.get("purchase_deliveries")),
        "expenses": bool(visible.get("expenses")),
    }
    show["margin"] = show["deliveries"] and show["expenses"]
    show["sale_pending"] = show["order"] and show["deliveries"]
    show["purchase_pending"] = show["purchase_orders"] and show["purchase_deliveries"]
    page = {
        "month_name": summary["month_name"],
        "year": summary["year"],
        "empty": summary["empty"],
        "incomplete": summary["incomplete"],
        "count": summary["count"],
        "show": show,
        "rows": [],
        "totals": {},
        "margin": "",
        "margin_percent": "",
        "served_percent": "",
        "sale_pending": "",
        "purchase_pending": "",
        "analytics": None,
        "composition": None,
        "total_bars": [],
        "project_rows": [],
    }
    if summary["empty"]:
        return page
    page["rows"] = [_present_row(row, show) for row in summary["rows"]]
    for key, _label, _tone in _COLUMNS:
        if show[key]:
            page["totals"][key] = _text(summary["totals"][key])
    if show["margin"]:
        page["margin"] = _text(summary["margin"])
        if summary["margin_percent"] is not None:
            page["margin_percent"] = format_percent(summary["margin_percent"])
    if show["sale_pending"]:
        page["sale_pending"] = _text(summary["sale_pending"])
        served = margin_ratio(summary["totals"].get("order"), summary.get("served"))
        if served is not None:
            page["served_percent"] = format_percent(served)
    if show["purchase_pending"]:
        page["purchase_pending"] = _text(summary["purchase_pending"])
    if show["expenses"] and summary.get("analytics"):
        page["analytics"] = _present_analytics(summary["analytics"])
    page["composition"] = _composition(summary, show)
    page["total_bars"] = _total_bars(summary, show)
    page["project_rows"] = _project_rows(summary, show)
    return page


def _assemble(year, month, rows, commercial, analytics):
    totals = {
        "order": commercial["order"],
        "deliveries": commercial["deliveries"],
        "purchase_orders": commercial["purchase_orders"],
        "purchase_deliveries": commercial["purchase_deliveries"],
        "expenses": analytics["expenses"],
    }
    has_amount = any(totals[key] not in (None, Decimal("0")) for key in totals)
    if not rows and not has_amount and not commercial["incomplete"] and not analytics["incomplete"]:
        return {
            "year": year,
            "month": month,
            "month_name": _MONTH_NAMES[month],
            "empty": True,
            "incomplete": False,
            "count": 0,
            "rows": [],
            "totals": {},
            "margin": None,
            "margin_percent": None,
            "served": None,
            "sale_pending": None,
            "purchase_pending": None,
            "analytics": None,
        }
    margin = None
    if totals["deliveries"] is not None and totals["expenses"] is not None:
        margin = totals["deliveries"] - totals["expenses"]
    return {
        "year": year,
        "month": month,
        "month_name": _MONTH_NAMES[month],
        "empty": False,
        "incomplete": commercial["incomplete"] or analytics["incomplete"] or any(row["incomplete"] for row in rows),
        "count": len(rows),
        "rows": rows,
        "totals": totals,
        "margin": margin,
        "margin_percent": margin_ratio(totals["deliveries"], margin),
        "served": commercial["served"],
        "sale_pending": commercial["sale_pending"],
        "purchase_pending": commercial["purchase_pending"],
        "analytics": analytics,
    }


def _commercial(company, year, month):
    """Pedidos y albaranes por la fecha del documento, aunque el pedido sea de otro mes."""

    ordered, sale_pending, served, sale_gap = _sale_flow(company, year, month)
    deliveries, delivery_gap = _fold(
        ProjectMilestone.objects.filter(
            life__codigo_empresa=company,
            delivery_date__year=year,
            delivery_date__month=month,
        ).values_list("amount", flat=True)
    )
    purchase_orders, order_gap = _fold(
        ProjectPurchase.objects.filter(
            life__codigo_empresa=company,
            kind__in=(KIND_ORDER, KIND_COMMITTED),
            document_date__year=year,
            document_date__month=month,
        ).values_list("amount", flat=True)
    )
    purchase_deliveries, note_gap = _fold(
        ProjectPurchase.objects.filter(
            life__codigo_empresa=company,
            kind=KIND_DELIVERY,
            document_date__year=year,
            document_date__month=month,
        ).values_list("amount", flat=True)
    )
    purchase_pending, pending_gap = _purchase_pending(company, year, month)
    return {
        "order": ordered,
        "deliveries": deliveries,
        "purchase_orders": purchase_orders,
        "purchase_deliveries": purchase_deliveries,
        "sale_pending": sale_pending,
        "served": served,
        "purchase_pending": purchase_pending,
        "incomplete": sale_gap or delivery_gap or order_gap or note_gap or pending_gap,
    }


def _sale_flow(company, year, month):
    """Los albaranes de cualquier fecha cubren primero el pedido más antiguo."""

    orders = {}
    incomplete = False
    lives_with_lines = set()
    lines = ProjectDocumentLine.objects.filter(
        life__codigo_empresa=company,
        kind=SALE_ORDER,
        position=0,
        line_date__year=year,
    )
    for line in lines:
        lives_with_lines.add(line.life_id)
        if line.line_date is None:
            continue
        bucket = orders.setdefault(line.life_id, {})
        if line.amount is None:
            incomplete = True
            bucket.setdefault(line.line_date.month, Decimal("0"))
            continue
        bucket[line.line_date.month] = bucket.get(line.line_date.month, Decimal("0")) + Decimal(line.amount)
    fallbacks = ProjectLife.objects.filter(codigo_empresa=company, order_date__year=year).exclude(pk__in=lives_with_lines)
    for life in fallbacks:
        if life.order_base is None:
            incomplete = True
            continue
        orders.setdefault(life.pk, {})[life.order_date.month] = Decimal(life.order_base)
    delivered = {}
    if orders:
        for row in ProjectMilestone.objects.filter(life_id__in=list(orders)):
            if row.amount is None:
                incomplete = True
                continue
            delivered[row.life_id] = delivered.get(row.life_id, Decimal("0")) + Decimal(row.amount)
    ordered = Decimal("0")
    pending = Decimal("0")
    served = Decimal("0")
    for life_id, by_month in orders.items():
        pool = delivered.get(life_id, Decimal("0"))
        for current in sorted(by_month):
            amount = by_month[current]
            used = min(pool, amount) if pool > 0 else Decimal("0")
            pool -= used
            if current == month:
                ordered += amount
                served += used
                pending += amount - used
    return ordered, pending, served, incomplete


def _purchase_pending(company, year, month):
    grouped = {}
    for row in ProjectPurchase.objects.filter(life__codigo_empresa=company):
        grouped.setdefault(row.life_id, []).append(row)
    pending = Decimal("0")
    incomplete = False
    for group in grouped.values():
        month_orders = [
            row
            for row in group
            if row.kind in (KIND_ORDER, KIND_COMMITTED)
            and row.document_date is not None
            and row.document_date.year == year
            and row.document_date.month == month
        ]
        if not month_orders:
            continue
        covered = {}
        for row in group:
            if row.kind != KIND_DELIVERY or not str(row.linked_numero or "").strip():
                continue
            if row.amount is None:
                incomplete = True
                continue
            key = (str(row.linked_ejercicio), str(row.linked_serie), str(row.linked_numero))
            covered[key] = covered.get(key, Decimal("0")) + Decimal(row.amount)
        for row in month_orders:
            if row.amount is None:
                incomplete = True
                continue
            gap = Decimal(row.amount) - covered.get((str(row.ejercicio), str(row.serie), str(row.numero)), Decimal("0"))
            if gap > 0:
                pending += gap
    return pending, incomplete


def _analytics(lives):
    """Grupo 6 y grupo 7 de los proyectos del mes, con cualquier fecha de asiento."""

    expenses, expense_gap = _fold(
        row.amount
        for life in lives
        for row in life.expenses.all()
        if str(row.account_code or "").strip().startswith("6")
    )
    pending = bool(lives) and any(not life.income_stored for life in lives)
    income_gap = False
    if not lives:
        income = Decimal("0")
    elif pending:
        income = None
    else:
        income, income_gap = _fold(row.amount for life in lives for row in life.incomes.all())
    margin = None
    if income is not None and expenses is not None:
        margin = income - expenses
    return {
        "expenses": expenses,
        "income": income,
        "income_pending": bool(lives) and pending,
        "margin": margin,
        "margin_percent": margin_ratio(income, margin),
        "incomplete": expense_gap or income_gap,
    }


def _present_analytics(analytics):
    presented = {
        "expenses": _text(analytics["expenses"]),
        "income": "" if analytics["income_pending"] else _text(analytics["income"]),
        "income_pending": analytics["income_pending"],
        "margin": "",
        "margin_percent": "",
    }
    if analytics["margin"] is not None and not analytics["income_pending"]:
        presented["margin"] = _text(analytics["margin"])
        if analytics["margin_percent"] is not None:
            presented["margin_percent"] = format_percent(analytics["margin_percent"])
    return presented


def _row(life, months, month):
    order = None if life.order_base is None else Decimal(life.order_base)
    deliveries, delivery_gap = _fold_stored(life.milestones.all())
    purchase_orders, order_gap = _fold_stored(
        row for row in life.purchases.all() if row.kind in (KIND_ORDER, KIND_COMMITTED)
    )
    purchase_deliveries, delivery_note_gap = _fold_stored(
        row for row in life.purchases.all() if row.kind == KIND_DELIVERY
    )
    expenses, expense_gap = _fold_stored(life.expenses.all())
    others = sorted(item for item in months if item != month)
    return {
        "code": life.codigo_proyecto,
        "order": order,
        "deliveries": deliveries,
        "purchase_orders": purchase_orders,
        "purchase_deliveries": purchase_deliveries,
        "expenses": expenses,
        "purchase_pending": _purchase_order_pending(list(life.purchases.all())),
        "other_months": [_MONTH_NAMES[item] for item in others],
        "incomplete": life.incomplete or order is None or delivery_gap or order_gap or delivery_note_gap or expense_gap,
    }


def _fold_stored(rows):
    return _fold(row.amount for row in rows)


def _fold(amounts):
    total = Decimal("0")
    incomplete = False
    known = False
    for amount in amounts:
        if amount is None:
            incomplete = True
            continue
        known = True
        total += Decimal(amount)
    if not known:
        return (None if incomplete else Decimal("0")), incomplete
    return total, incomplete


def _present_row(row, show):
    presented = {
        "code": row["code"],
        "other_months": _join_months(row["other_months"]),
        "incomplete": row["incomplete"],
    }
    for key, _label, _tone in _COLUMNS:
        if show[key]:
            presented[key] = _text(row[key])
    return presented


def _join_months(names):
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " y " + names[-1]


def _text(value):
    if value is None:
        return "—"
    return format_money(value)


def _bar(name, tone, value, peak):
    width = 0
    if value and peak:
        width = max(round(abs(float(value)) / float(peak) * 100), 4)
    return {
        "name": name,
        "tone": tone,
        "width": width,
        "negative": value < 0,
        "amount": format_money(value),
    }


def _total_bars(summary, show):
    items = []
    for key, label, tone in _COLUMNS:
        amount = summary["totals"].get(key)
        if show[key] and amount is not None:
            items.append((label, tone, amount))
    return _scaled(items)


def _project_rows(summary, show):
    if not show["deliveries"] and not show["expenses"]:
        return []
    pending = []
    peak = Decimal("0")
    for row in summary["rows"]:
        series = []
        if show["deliveries"] and row["deliveries"] is not None:
            series.append(("Albaranado", "venta", row["deliveries"]))
            peak = max(peak, abs(row["deliveries"]))
        if show["expenses"] and row["expenses"] is not None:
            series.append(("Gastos", "gasto", row["expenses"]))
            peak = max(peak, abs(row["expenses"]))
        if series:
            pending.append((row["code"], series))
    return [{"label": code, "series": [_bar(name, tone, value, peak) for name, tone, value in series]} for code, series in pending]


def _scaled(items):
    peak = Decimal("0")
    for _label, _tone, amount in items:
        peak = max(peak, abs(amount))
    return [_bar(label, tone, amount, peak) for label, tone, amount in items]


def _composition(summary, show):
    parts = []
    if show["deliveries"] and summary["totals"].get("deliveries") and summary["totals"]["deliveries"] > 0:
        parts.append(("Albaranes", summary["totals"]["deliveries"], "#0b4f6c"))
    if show["expenses"] and summary["totals"].get("expenses") and summary["totals"]["expenses"] > 0:
        parts.append(("Gastos", summary["totals"]["expenses"], "#8a5a00"))
    margin = summary["margin"]
    if show["margin"] and margin is not None and margin > 0:
        parts.append(("Margen", margin, "#1c1c1c"))
    center = ""
    if show["order"]:
        center = _text(summary["totals"].get("order"))
    if not parts and not center:
        return None
    used = sum((amount for _label, amount, _color in parts), Decimal("0"))
    whole = summary["totals"].get("order") if show["order"] else None
    if whole in (None, 0):
        whole = used
    elif used > whole:
        whole = used
    return {
        "center": center,
        "slices": _ring(parts, whole),
        "negative_margin": format_money(margin) if show["margin"] and margin is not None and margin < 0 else "",
    }


def _ring(parts, whole):
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
                "percent": format_percent(Decimal(amount) / Decimal(whole) * Decimal("100") if whole else None),
                "color": color,
                "length": f"{paint:.2f}",
                "rest": f"{ring - paint:.2f}",
                "offset": f"{-(offset + shift):.2f}",
            }
        )
        offset += length
    return slices
