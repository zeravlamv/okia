from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.access.models import InformationGroup
from apps.access.services import has_groups, selected_company, set_company
from apps.erp.analytics import fetch_dimension_labels
from apps.erp.ledger import fetch_movements
from apps.erp.masters import fetch_master_counts
from apps.erp.purchases import fetch_purchases
from apps.erp.sales import fetch_orders
from apps.margins.dashboard import build_dashboard
from apps.margins.filters import filter_context, safe_next, selected_year, set_year
from apps.margins.format import format_money, format_percent
from apps.margins.services import build_report


def _with_filters(request, company, extra):
    context = filter_context(request, company)
    context.update(extra)
    context["sample"] = settings.SAMPLE_ERP
    context["erp_name"] = settings.ERP_NAME
    return context


@login_required
def apply_filters(request):
    if request.method != "POST":
        return redirect("dashboard")
    company = request.POST.get("codigo_empresa", "").strip()
    if company:
        try:
            set_company(request, company)
        except PermissionError:
            pass
    raw_year = request.POST.get("ejercicio", "").strip()
    if raw_year.isdigit():
        set_year(request, int(raw_year))
    return redirect(safe_next(request.POST.get("next", "/")))


@login_required
def dashboard(request):
    company = selected_company(request)
    if company is None:
        return redirect("company-select")
    year = selected_year(request)
    groups = _visible_groups(request.user)
    figures = build_dashboard(
        company,
        year,
        fetch_orders(company),
        fetch_purchases(company),
        fetch_movements(company),
        fetch_master_counts(company),
        groups,
        fetch_dimension_labels(company),
    )
    breakdown = [
        {
            "title": section["title"],
            "rows": [
                {"label": row["label"], "amount": format_money(row["amount"])}
                for row in section["rows"]
            ],
        }
        for section in figures.get("breakdown", [])
    ]
    return render(
        request,
        "margins/dashboard.html",
        _with_filters(
            request,
            company,
            {
                "sales": _card(figures.get("sales")),
                "purchases": _card(figures.get("purchases")),
                "margin": format_money(figures["margin"]) if "margin" in figures else None,
                "income": format_money(figures["income"]) if "income" in figures else None,
                "clientes": figures.get("clientes"),
                "proveedores": figures.get("proveedores"),
                "articulos": figures.get("articulos"),
                "breakdown": breakdown,
                "show_margin": "margin" in figures,
                "show_income": "income" in figures,
            },
        ),
    )


def _card(value):
    if value is None:
        return None
    return {"count": value["count"], "amount": format_money(value["amount"])}


def _visible_groups(user):
    return [group for group in InformationGroup.values if has_groups(user, [group])]


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
    context = _with_filters(request, company, {"forbidden": False, "rows": [], "pending_count": 0})
    if not has_groups(request.user, required):
        context["forbidden"] = True
        return render(request, "margins/order.html", context)
    year = selected_year(request)
    report = build_report(
        company,
        year,
        fetch_orders(company),
        fetch_purchases(company),
        fetch_movements(company),
    )
    context["rows"] = [
        {
            "identity": f"{row['ejercicio']} / {row['serie']} / {row['numero']}",
            "project": row["project"],
            "price": format_money(row["price"]),
            "cost": format_money(row["cost"]),
            "margin": format_money(row["margin"]),
            "percent": format_percent(row["percent"]),
            "income": format_money(row["income"]),
            "incomplete": row["incomplete"],
        }
        for row in report["closed"]
    ]
    context["pending_count"] = report["pending_count"]
    return render(request, "margins/order.html", context)
