from django.apps import AppConfig


class AccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.access"
    label = "access"
    verbose_name = "Permisos"

    def ready(self):
        from apps.access import admin  # noqa: F401
