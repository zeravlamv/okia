from django.db import connections


class ErpRouter:
    """La conexión erp solo se lee. Django no crea ni migra esas tablas."""

    erp_label = "erp"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.erp_label and "erp" in connections.databases:
            return "erp"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.erp_label:
            raise RuntimeError("El origen comercial es de solo lectura.")
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.erp_label or db == "erp":
            return False
        return None
