from django.urls import path

from apps.margins.views import apply_filters, dashboard, order_margin

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("filtros/", apply_filters, name="apply-filters"),
    path("margen/", order_margin, name="order-margin"),
]
