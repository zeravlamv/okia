from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("empresas/", include("apps.access.urls")),
    path("", include("apps.margins.urls")),
]
