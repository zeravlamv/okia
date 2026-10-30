import os
from contextlib import contextmanager

import pyodbc

HOUR_MARKERS = ("horas", "hora", "mano de obra", "personal")
CANCELLED_MARKERS = ("anulad", "cancelad")

CANDIDATES = {
    "company": ("CodigoEmpresa",),
    "customer": ("CodigoCliente",),
    "supplier": ("CodigoProveedor",),
    "exercise": ("EjercicioPedido", "Ejercicio", "Ejericicio"),
    "series": ("SeriePedido",),
    "number": ("NumeroPedido",),
    "article": ("CodigoArticulo",),
    "project": ("CodigoProyecto", "Proyecto"),
    "base": ("BaseImponible", "ImporteBase", "BaseImponibleLinea", "BaseLinea"),
    "tax_total": ("ImporteLiquido", "ImporteTotal", "TotalIvaIncluido"),
    "date": ("FechaPedido", "FechaDocumento", "Fecha"),
    "status": ("EstadoPedido", "Estado", "StatusPedido"),
    "channel": ("CodigoCanal", "Canal"),
    "delegation": ("IdDelegacion", "CodigoDelegacion", "Delegacion"),
    "department": ("CodigoDepartamento", "Departamento"),
    "section": ("CodigoSeccion", "Seccion"),
    "article_name": ("DescripcionArticulo", "Descripcion", "DescripcionLinea"),
    "account": ("CodigoCuenta",),
    "account_name": ("Cuenta", "NombreCuenta", "DescripcionCuenta", "Descripcion"),
    "debit": ("ImporteDebe", "Cargo", "Debe"),
    "credit": ("ImporteHaber", "Abono", "Haber"),
}


class MissingColumn(LookupError):
    pass


def indicates_hours(text):
    folded = (text or "").casefold()
    return any(marker in folded for marker in HOUR_MARKERS)


def is_cancelled(status):
    folded = (status or "").casefold()
    return any(marker in folded for marker in CANCELLED_MARKERS)


def is_income_account(code, name):
    if indicates_hours(name):
        return False
    normalized = (code or "").strip()
    if normalized.startswith("7"):
        return True
    return "ingreso" in (name or "").casefold()


def resolve(available, logical, required=True):
    lookup = {name.casefold(): name for name in available}
    for candidate in CANDIDATES[logical]:
        found = lookup.get(candidate.casefold())
        if found:
            return found
    if required:
        raise MissingColumn(
            f"No hay columna para '{logical}'. Se buscó: {', '.join(CANDIDATES[logical])}."
        )
    return None


def _without_secret(error):
    text = str(error)
    password = os.environ.get("ERP_PASSWORD", "")
    if password:
        text = text.replace(password, "***")
    return text


@contextmanager
def erp_cursor():
    driver = os.environ.get("ERP_ODBC_DRIVER", "ODBC Driver 18 for SQL Server")
    host = os.environ.get("ERP_HOST", "localhost")
    port = os.environ.get("ERP_PORT", "1433")
    name = os.environ.get("ERP_NAME", "")
    user = os.environ.get("ERP_USER", "")
    password = os.environ.get("ERP_PASSWORD", "")
    try:
        connection = pyodbc.connect(
            f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={name};"
            f"UID={user};PWD={password};TrustServerCertificate=yes;Encrypt=yes",
            timeout=20,
        )
    except pyodbc.Error as error:
        raise RuntimeError(f"No se pudo abrir el origen comercial. {_without_secret(error)}") from None
    try:
        yield connection.cursor()
    finally:
        connection.close()


def list_columns(table):
    with erp_cursor() as cursor:
        cursor.execute(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
            table,
        )
        return [row[0] for row in cursor.fetchall()]


def read_table(table, logical_fields, company=None):
    available = list_columns(table)
    selected = {
        logical: resolve(available, logical, required=True) for logical in logical_fields
    }
    column_list = ", ".join(f"[{column}]" for column in selected.values())
    sql = f"SELECT {column_list} FROM [{table}]"
    params = []
    if company is not None:
        sql += f" WHERE [{selected.get('company') or resolve(available, 'company')}] = ?"
        params.append(company)
    with erp_cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    keys = list(selected)
    return [dict(zip(keys, row)) for row in rows]
