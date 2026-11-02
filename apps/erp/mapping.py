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
    """Una cuenta del grupo 7 es ingreso aunque su nombre mencione horas.

    Esas horas son venta. El coste de personal sigue en las cuentas que no son de ingreso.
    """

    normalized = (code or "").strip()
    if normalized.startswith("7"):
        return True
    if indicates_hours(name):
        return False
    return "ingreso" in (name or "").casefold()


def is_closing_entry(comment):
    """El asiento de cierre anula las cuentas de ingreso y de gasto. No es ni lo uno ni lo otro."""

    return "cierre ejercicio" in (comment or "").casefold()


def is_expense_account(code, name):
    """Un gasto incluye el grupo 60: es el albarán de compra ya contabilizado.

    También entra el resto del grupo 6, o una cuenta cuyo nombre indique gasto, horas, mano de obra o personal.
    Una cuenta de ingreso no entra.
    """

    if is_income_account(code, name):
        return False
    if indicates_hours(name) or "gasto" in (name or "").casefold():
        return True
    return (code or "").strip().startswith("6")


def is_cost_account(code, name):
    """El coste de un proyecto son los gastos de AnaMovimientos, grupo 60 incluido."""

    return is_expense_account(code, name)


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


def month_window(year, month):
    """Primer instante del mes y el primero del mes siguiente."""

    from datetime import date

    year = int(year)
    month = int(month)
    start = date(year, month, 1)
    if month == 12:
        return start, date(year + 1, 1, 1)
    return start, date(year, month + 1, 1)


def read_columns(table, columns, company=None, optional=(), extra_where="", extra_params=()):
    """Lee columnas con su nombre real.

    Hace falta cuando la tabla tiene a la vez el ejercicio del documento y el del pedido relacionado.
    Las columnas opcionales se omiten si la tabla no las tiene.
    """

    available = {name.casefold(): name for name in list_columns(table)}
    selected = []
    output_names = []
    required = set(columns)
    for column in list(columns) + [name for name in optional if name not in required]:
        found = available.get(column.casefold())
        if not found:
            if column in required:
                raise MissingColumn(f"No está la columna {column} en {table}.")
            continue
        selected.append(found)
        output_names.append(column)
    column_list = ", ".join(f"[{column}]" for column in selected)
    sql = f"SELECT {column_list} FROM [{table}]"
    params = []
    if company is not None:
        company_column = available.get("codigoempresa")
        if not company_column:
            raise MissingColumn(f"No está CodigoEmpresa en {table}.")
        sql += f" WHERE [{company_column}] = ?"
        params.append(company)
    if extra_where:
        sql += (" AND " if params else " WHERE ") + extra_where
        params.extend(extra_params)
    with erp_cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    return [dict(zip(output_names, row)) for row in rows]


def read_table(table, logical_fields, company=None, extra_where="", extra_params=()):
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
    if extra_where:
        sql += (" AND " if params else " WHERE ") + extra_where
        params.extend(extra_params)
    with erp_cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    keys = list(selected)
    return [dict(zip(keys, row)) for row in rows]
