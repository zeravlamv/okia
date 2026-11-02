from django.urls import path

from apps.margins.views import (
    apply_filters,
    dashboard,
    evolution_amount,
    evolution_lines,
    month_documents,
    tree_income,
    guide,
    month_summary,
    order_margin,
    project_life,
    refresh_dashboard,
    refresh_month_view,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("filtros/", apply_filters, name="apply-filters"),
    path("actualizar/", refresh_dashboard, name="refresh-dashboard"),
    path("margen/", order_margin, name="order-margin"),
    path("resumen/", month_summary, name="month-summary"),
    path("resumen/recalcular/", refresh_month_view, name="refresh-month"),
    path("resumen/documentos/", month_documents, name="month-documents"),
    path("guia/", guide, name="guide"),
    path("evolucion/", evolution_amount, name="evolution-detail"),
    path("evolucion/lineas/", evolution_lines, name="evolution-lines"),
    path("arbol/ingresos/", tree_income, name="tree-income"),
    path("proyecto/<str:codigo>/", project_life, name="project-life"),
]
