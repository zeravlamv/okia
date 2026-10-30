from django.urls import path

from apps.access.views import choose_company

urlpatterns = [
    path("", choose_company, name="company-select"),
]
