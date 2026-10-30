from django.conf import settings

from apps.erp.mapping import erp_cursor, list_columns
from apps.erp.sample import master_counts


def fetch_master_counts(codigo_empresa):
    if settings.SAMPLE_ERP:
        return master_counts().get(str(codigo_empresa), {"clientes": 0, "proveedores": 0, "articulos": 0})
    return {
        "clientes": _count("Clientes", codigo_empresa),
        "proveedores": _count("Proveedores", codigo_empresa),
        "articulos": _count("Articulos", codigo_empresa),
    }


def _count(table, codigo_empresa):
    columns = list_columns(table)
    company = next(name for name in columns if name.casefold() == "codigoempresa")
    cancelled = next((name for name in columns if name.casefold() == "fechabaja"), None)
    sql = f"SELECT COUNT(*) FROM [{table}] WHERE [{company}] = ?"
    if cancelled:
        sql += f" AND [{cancelled}] IS NULL"
    with erp_cursor() as cursor:
        cursor.execute(sql, codigo_empresa)
        return int(cursor.fetchone()[0])
