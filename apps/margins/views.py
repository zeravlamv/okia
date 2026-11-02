import json
import logging
import threading
from queue import Queue

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.access.models import InformationGroup
from apps.access.services import has_groups, selected_company, set_company
from apps.margins.filters import filter_context, safe_next, selected_year, set_year
from apps.margins.format import format_money, format_percent
from apps.margins.models import MONTH_NAMES
from apps.margins.month_refresh import refresh_month
from apps.margins.month_summary import chosen_month, month_board, month_document_detail
from apps.margins.services import margin_ratio
from apps.margins.project_life import closed_months, load_project
from apps.margins.snapshot import (
    closure_notice,
    load_dashboard,
    load_orders,
    delivery_lines,
    evolution_chart,
    evolution_detail,
    month_hierarchy,
    monthly_bars,
    tree_income_detail,
    refresh_snapshot,
    snapshot_updated_at,
)


def _with_filters(request, company, extra):
    context = filter_context(request, company)
    context.update(extra)
    context["sample"] = settings.SAMPLE_ERP
    context["erp_name"] = settings.ERP_NAME
    context["updated_at"] = _format_updated_at(company, selected_year(request))
    return context


def _format_updated_at(company, year):
    moment = snapshot_updated_at(company, year)
    if moment is None:
        return ""
    return timezone.localtime(moment).strftime("%d/%m/%Y %H:%M")


@login_required
def apply_filters(request):
    if request.method != "POST":
        return redirect("dashboard")
    _remember_filters(request)
    return redirect(safe_next(request.POST.get("next", "/")))


def _remember_filters(request):
    company = request.POST.get("codigo_empresa", "").strip()
    if company:
        try:
            set_company(request, company)
        except PermissionError:
            pass
    raw_year = request.POST.get("ejercicio", "").strip()
    if raw_year.isdigit():
        set_year(request, int(raw_year))


logger = logging.getLogger(__name__)


@login_required
def refresh_dashboard(request):
    if request.method != "POST":
        return redirect("dashboard")
    _remember_filters(request)
    company = selected_company(request)
    if company is None:
        return redirect("company-select")
    year = selected_year(request)
    destination = safe_next(request.POST.get("next", "/"))
    if request.headers.get("Accept") != "application/x-ndjson":
        notice = closure_notice(refresh_snapshot(company, year))
        if notice:
            messages.info(request, notice)
        return redirect(destination)
    response = StreamingHttpResponse(
        _refresh_events(company, year, destination),
        content_type="application/x-ndjson",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@login_required
def refresh_month_view(request):
    """Recalcula un mes abierto. Un mes cerrado no lee el origen."""

    if request.method != "POST":
        return redirect("month-summary")
    _remember_filters(request)
    company = selected_company(request)
    if company is None:
        return redirect("company-select")
    raw_month = request.POST.get("mes", "")
    if not raw_month.isdigit() or not 1 <= int(raw_month) <= 12:
        return JsonResponse({"ok": False, "error": "Petición no válida"}, status=404)
    month = int(raw_month)
    year = selected_year(request)
    destination = safe_next(request.POST.get("next", f"/resumen/?mes={month}&listo=1"))
    response = StreamingHttpResponse(
        _month_events(company, year, month, destination),
        content_type="application/x-ndjson",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def _month_events(company, year, month, destination):
    events = Queue()

    def progress(event):
        events.put(event)

    def work():
        from django.db import close_old_connections

        close_old_connections()
        try:
            refresh_month(company, year, month, progress=progress)
            events.put({"ok": True, "next": destination})
        except Exception:
            logger.exception("No se ha podido recalcular el mes %s", month)
            events.put({"ok": False, "error": "No se ha podido actualizar."})
        finally:
            close_old_connections()
            events.put(None)

    threading.Thread(target=work, name="okia-month-refresh", daemon=True).start()
    while True:
        event = events.get()
        if event is None:
            break
        yield json.dumps(event, ensure_ascii=False) + "\n"


def _refresh_events(company, year, destination):
    """El hilo calcula y esta respuesta envía cada paso en cuanto ocurre."""

    events = Queue()

    def progress(event):
        events.put(event)

    def work():
        from django.db import close_old_connections

        close_old_connections()
        try:
            notice = closure_notice(refresh_snapshot(company, year, progress=progress))
            finished = {"ok": True, "next": destination}
            if notice:
                finished["notice"] = notice
            events.put(finished)
        except Exception:
            logger.exception("No se ha podido actualizar el ejercicio %s", year)
            events.put({"ok": False, "error": "No se ha podido actualizar."})
        finally:
            close_old_connections()
            events.put(None)

    threading.Thread(target=work, name="okia-refresh", daemon=True).start()
    while True:
        event = events.get()
        if event is None:
            break
        yield json.dumps(event, ensure_ascii=False) + "\n"


@login_required
def dashboard(request):
    company = selected_company(request)
    if company is None:
        return redirect("company-select")
    year = selected_year(request)
    groups = _visible_groups(request.user)
    figures = load_dashboard(company, year, groups)
    if figures is None:
        return render(
            request,
            "margins/dashboard.html",
            _with_filters(request, company, {"pending_refresh": True, "hierarchy": {"nodes": [], "aside": []}}),
        )
    breakdown = _format_hierarchy(figures.get("hierarchy", []))
    aside = [
        {
            "identity": row["identity"],
            "amount": format_money(row["amount"]),
            "incomplete": row["incomplete"],
        }
        for row in figures.get("aside", [])
    ]
    return render(
        request,
        "margins/dashboard.html",
        _with_filters(
            request,
            company,
            {
                "sales": _card(figures.get("sales")),
                "purchase_orders": _card(figures.get("purchase_orders")),
                "sales_deliveries": _card(figures.get("sales_deliveries")),
                "purchase_deliveries": _card(figures.get("purchase_deliveries")),
                "margin": format_money(figures["margin"]) if "margin" in figures else None,
                "margin_percent": format_percent(figures.get("margin_percent")) if "margin" in figures else None,
                "income": _card(figures.get("income")),
                "accounted_purchases": _card(figures.get("accounted_purchases")),
                "expenses": _card(figures.get("expenses")),
                "pending_refresh": False,
                "hierarchy": {"nodes": breakdown, "aside": aside},
                "show_margin": "margin" in figures,
                "months": (
                    months := monthly_bars(
                        company, year, groups, only_months=closed_months(company, year) or None
                    )
                ),
                "evolution": evolution_chart(months),
                "pending_months": [
                    {
                        "name": month["name"],
                        "count": month["count"],
                        "amount": format_money(month["amount"]),
                    }
                    for month in figures.get("pending_months", [])
                ],
            },
        ),
    )


def _format_node(node):
    item = {
        "level": node["level"],
        "label": node["label"],
        "incomplete": node["incomplete"],
        "code": node.get("code") or "",
        "children": [_format_node(child) for child in node["children"]],
    }
    if "margin" in node:
        item["margin_percent"] = format_percent(margin_ratio(node.get("income"), node["margin"]))
    for key in ("sales", "income", "purchases", "expenses", "margin"):
        if key in node:
            item[key] = format_money(node[key])
    return item


def _format_hierarchy(nodes):
    return [_format_node(node) for node in nodes]


def _card(value):
    if value is None:
        return None
    return {"count": value["count"], "amount": format_money(value["amount"])}


def _month_card(value, link=False):
    if value is None:
        return None
    amount = value["amount"]
    return {
        "count": value["count"],
        "amount": format_money(amount),
        "link": bool(link and amount not in (None, 0)),
    }


@login_required
def month_summary(request):
    company = selected_company(request)
    if company is None:
        return redirect("company-select")
    year = selected_year(request)
    month = chosen_month(request.GET.get("mes"), year, timezone.localdate())
    groups = _visible_groups(request.user)
    board = month_board(company, year, month, groups)
    bars = [row for row in monthly_bars(company, year, groups) if row["number"] == month]
    tree = month_hierarchy(company, year, month, groups)
    page = {
        "month_name": dict(MONTH_NAMES)[month],
        "year": year,
        "month": month,
        "empty": board["empty"],
        "sales": _month_card(board["cards"].get("sales"), link=True),
        "purchase_orders": _month_card(board["cards"].get("purchase_orders"), link=True),
        "sales_deliveries": _month_card(board["cards"].get("sales_deliveries"), link=True),
        "purchase_deliveries": _month_card(board["cards"].get("purchase_deliveries"), link=True),
        "income": _month_card(board["cards"].get("income"), link=True),
        "accounted_purchases": _month_card(board["cards"].get("accounted_purchases"), link=True),
        "expenses": _month_card(board["cards"].get("expenses"), link=True),
        "margin": format_money(board["cards"]["margin"]) if "margin" in board["cards"] else None,
        "margin_percent": (
            format_percent(board["cards"].get("margin_percent")) if "margin" in board["cards"] else None
        ),
        "show_margin": "margin" in board["cards"],
        "closed": (closed := month in closed_months(company, year)),
        "refresh_open": not closed and request.GET.get("listo") != "1",
        "months": [{"number": number, "name": name, "selected": number == month} for number, name in MONTH_NAMES],
        "evolution_months": bars,
        "evolution": evolution_chart(bars),
        "hierarchy": {
            "nodes": _format_hierarchy(tree["nodes"]),
            "aside": [],
            "projects": tree["projects"],
        },
    }
    return render(request, "margins/month.html", _with_filters(request, company, page))


@login_required
def project_life(request, codigo):
    company = selected_company(request)
    if company is None:
        return redirect("company-select")
    life = load_project(company, codigo, _visible_groups(request.user), timezone.localdate())
    context = _with_filters(request, company, {"life": life, "project_code": codigo, "pending_refresh": life is None})
    if life is not None:
        context["updated_at"] = timezone.localtime(life["updated_at"]).strftime("%d/%m/%Y %H:%M")
    return render(request, "margins/project.html", context)


def _visible_groups(user):
    return [group for group in InformationGroup.values if has_groups(user, [group])]


@login_required
def evolution_amount(request):
    """Detalle guardado del ingreso, la compra o el gasto de un mes. No lee SQL Server."""

    company = selected_company(request)
    if company is None:
        return JsonResponse({"error": "Sin empresa"}, status=403)
    raw_month = request.GET.get("mes", "")
    kind = request.GET.get("tipo", "")
    if kind not in ("ingreso", "compra", "gasto") or not raw_month.isdigit() or not 1 <= int(raw_month) <= 12:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    groups = _visible_groups(request.user)
    if InformationGroup.MOVIMIENTOS not in groups:
        return JsonResponse({"error": "Sin permiso"}, status=403)
    return JsonResponse(evolution_detail(company, selected_year(request), int(raw_month), kind, groups))


@login_required
def tree_income(request):
    """Apuntes guardados de un ingreso sin nivel. No lee SQL Server."""

    company = selected_company(request)
    if company is None:
        return JsonResponse({"error": "Sin empresa"}, status=403)
    if InformationGroup.MOVIMIENTOS not in _visible_groups(request.user):
        return JsonResponse({"error": "Sin permiso"}, status=403)
    try:
        path = json.loads(request.GET.get("ruta", ""))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    if not isinstance(path, list) or not 1 <= len(path) <= 4:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    cleaned = []
    seen = set()
    for item in path:
        if not isinstance(item, dict):
            return JsonResponse({"error": "Petición no válida"}, status=404)
        level = str(item.get("level", "")).strip()
        label = str(item.get("label", "")).strip()
        if not level or not label or len(level) > 40 or len(label) > 500 or level in seen:
            return JsonResponse({"error": "Petición no válida"}, status=404)
        seen.add(level)
        cleaned.append({"level": level, "label": label})
    raw_month = request.GET.get("mes", "")
    month = None
    if raw_month != "":
        if not raw_month.isdigit() or not 1 <= int(raw_month) <= 12:
            return JsonResponse({"error": "Petición no válida"}, status=404)
        month = int(raw_month)
    detail = tree_income_detail(company, selected_year(request), cleaned, month)
    if detail is None:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    return JsonResponse(detail)


@login_required
def evolution_lines(request):
    """Líneas guardadas de un albarán de cliente. No lee SQL Server."""

    company = selected_company(request)
    if company is None:
        return JsonResponse({"error": "Sin empresa"}, status=403)
    project = request.GET.get("proyecto", "").strip()
    document = request.GET.get("albaran", "").strip()
    kind = request.GET.get("tipo", "sale_delivery")
    needed = {
        "sale_order": InformationGroup.PEDIDOS_VENTA,
        "sale_delivery": InformationGroup.ALBARANES_VENTA,
        "purchase_order": InformationGroup.PEDIDOS_COMPRA,
        "purchase_delivery": InformationGroup.ALBARANES_COMPRA,
    }.get(kind)
    if needed is None or needed not in _visible_groups(request.user):
        return JsonResponse({"error": "Sin permiso"}, status=403)
    if not project or not document:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    payload = delivery_lines(company, project, document, kind)
    if payload is None:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    return JsonResponse(payload)


@login_required
def month_documents(request):
    """Pedidos o albaranes de un mes. No lee SQL Server."""

    company = selected_company(request)
    if company is None:
        return JsonResponse({"error": "Sin empresa"}, status=403)
    raw_month = request.GET.get("mes", "")
    kind = request.GET.get("tipo", "")
    if kind not in ("pedido", "pedido_compra", "albaran", "albaran_compra") or not raw_month.isdigit() or not 1 <= int(raw_month) <= 12:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    detail = month_document_detail(company, selected_year(request), int(raw_month), kind, _visible_groups(request.user))
    if detail is None:
        return JsonResponse({"error": "Petición no válida"}, status=404)
    if detail.get("forbidden"):
        return JsonResponse({"error": "Sin permiso"}, status=403)
    return JsonResponse(detail)


@login_required
def guide(request):
    """Explica el origen de cada cifra. No lee SQL Server ni el resumen guardado."""

    return render(request, "margins/guide.html")


@login_required
def order_margin(request):
    company = selected_company(request)
    if company is None:
        return redirect("company-select")
    required = [
        InformationGroup.PEDIDOS_VENTA,
        InformationGroup.PEDIDOS_COMPRA,
        InformationGroup.MOVIMIENTOS,
    ]
    context = _with_filters(
        request, company, {"forbidden": False, "rows": [], "pending_count": 0, "pending_refresh": False}
    )
    if not has_groups(request.user, required):
        context["forbidden"] = True
        return render(request, "margins/order.html", context)
    stored = load_orders(company, selected_year(request))
    if stored is None:
        context["pending_refresh"] = True
        return render(request, "margins/order.html", context)
    context["rows"] = [
        {
            "identity": row["identity"],
            "project": row["project"],
            "price": format_money(row["price"]),
            "cost": format_money(row["cost"]),
            "margin": format_money(row["margin"]),
            "percent": format_percent(row["percent"]),
            "income": format_money(row["income"]),
            "incomplete": row["incomplete"],
        }
        for row in stored["rows"]
    ]
    context["pending_count"] = stored["pending_count"]
    return render(request, "margins/order.html", context)
