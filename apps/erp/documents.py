from datetime import datetime

from django.conf import settings

from apps.erp.mapping import erp_cursor, list_columns, month_window, read_columns
from apps.erp.sample import (
    SaleLine,
    ValuedDocument,
    for_company,
    purchase_deliveries,
    purchase_orders,
    sales_deliveries,
)

DOCUMENT_STATUS = {
    "0": "Pendiente",
    "1": "Bloqueado",
    "2": "Servido",
}

_OPTIONAL = {
        "purchase_order": (
            "CodigoProyecto",
            "CodigoProveedor",
            "CodigoCanal",
            "IdDelegacion",
            "CodigoDepartamento",
            "CodigoSeccion",
        ),
    "sales_delivery": (
        "CodigoProyecto",
        "CodigoDepartamento",
        "CodigoSeccion",
        "StatusFacturado",
        "StatusAbono",
    ),
    "purchase_delivery": (
        "CodigoProyecto",
        "CodigoProveedor",
        "CodigoDepartamento",
        "CodigoSeccion",
        "EjercicioPedido",
        "SeriePedido",
        "NumeroPedido",
        "StatusFacturado",
    ),
}


def _marked(value):
    text = _text(value)
    if text == "-1":
        return True
    if text == "0":
        return False
    return None


def _billing(value):
    mark = _marked(value)
    if mark is True:
        return "invoiced"
    if mark is False:
        return "open"
    return "unknown"


def fetch_supplier_names(codigo_empresa):
    """Nombre del proveedor de la misma empresa. Si la columna no está, queda el código."""

    if settings.SAMPLE_ERP:
        return {}
    available = {name.casefold(): name for name in list_columns("Proveedores")}
    code_column = available.get("codigoproveedor")
    name_column = available.get("razonsocial") or available.get("nombre")
    company_column = available.get("codigoempresa")
    if not code_column or not name_column or not company_column:
        return {}
    with erp_cursor() as cursor:
        cursor.execute(
            f"SELECT [{code_column}], [{name_column}] FROM [Proveedores] WHERE [{company_column}] = ?",
            codigo_empresa,
        )
        rows = cursor.fetchall()
    return {_text(code): _text(name) for code, name in rows if _text(code)}


def fetch_customer_names(codigo_empresa):
    """Nombre del cliente de la misma empresa. Si la columna no está, queda el código."""

    if settings.SAMPLE_ERP:
        return {}
    available = {name.casefold(): name for name in list_columns("Clientes")}
    code_column = available.get("codigocliente")
    name_column = available.get("razonsocial") or available.get("nombre")
    company_column = available.get("codigoempresa")
    if not code_column or not name_column or not company_column:
        return {}
    with erp_cursor() as cursor:
        cursor.execute(
            f"SELECT [{code_column}], [{name_column}] FROM [Clientes] WHERE [{company_column}] = ?",
            codigo_empresa,
        )
        rows = cursor.fetchall()
    return {_text(code): _text(name) for code, name in rows if _text(code)}


_KINDS = {
    "purchase_order": {
        "header": "CabeceraPedidoProveedor",
        "line": "LineasPedidoProveedor",
        "exercise": "EjercicioPedido",
        "series": "SeriePedido",
        "number": "NumeroPedido",
        "date": "FechaPedido",
        "status": "Estado",
        "sample": purchase_orders,
    },
    "sales_delivery": {
        "header": "CabeceraAlbaranCliente",
        "line": "LineasAlbaranCliente",
        "exercise": "EjercicioAlbaran",
        "series": "SerieAlbaran",
        "number": "NumeroAlbaran",
        "date": "FechaAlbaran",
        "status": None,
        "sample": sales_deliveries,
    },
    "purchase_delivery": {
        "header": "CabeceraAlbaranProveedor",
        "line": "LineasAlbaranProveedor",
        "exercise": "EjercicioAlbaran",
        "series": "SerieAlbaran",
        "number": "NumeroAlbaran",
        "date": "FechaAlbaran",
        "status": None,
        "sample": purchase_deliveries,
    },
}


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def _status(value):
    text = _text(value)
    return DOCUMENT_STATUS.get(text, text)


def _article(row):
    code = _text(row.get("CodigoArticulo"))
    name = _text(row.get("DescripcionArticulo")) or _text(row.get("DescripcionLinea"))
    if code and name:
        return f"{code} — {name}"
    return name or code


def _in_month(moment, year, month):
    return moment is not None and moment.year == int(year) and moment.month == int(month)


def _lines_in_span(spec, year, month):
    start, end = month_window(year, month)
    line = spec["line"]
    header = spec["header"]
    where = (
        f"EXISTS (SELECT 1 FROM [{header}] h WHERE "
        f"h.[CodigoEmpresa] = [{line}].[CodigoEmpresa] AND "
        f"h.[{spec['exercise']}] = [{line}].[{spec['exercise']}] AND "
        f"h.[{spec['series']}] = [{line}].[{spec['series']}] AND "
        f"h.[{spec['number']}] = [{line}].[{spec['number']}] AND "
        f"h.[{spec['date']}] >= ? AND h.[{spec['date']}] < ?)"
    )
    return where, (start, end)


def _fetch(kind, codigo_empresa, year=None, month=None):
    spec = _KINDS[kind]
    if settings.SAMPLE_ERP:
        rows = for_company(spec["sample"](), codigo_empresa)
        if year is None or month is None:
            return rows
        return [row for row in rows if _in_month(row.document_date, year, month)]
    header_where, header_params = ("", ())
    line_where, line_params = ("", ())
    if year is not None and month is not None:
        start, end = month_window(year, month)
        header_where = f"[{spec['date']}] >= ? AND [{spec['date']}] < ?"
        header_params = (start, end)
        line_where, line_params = _lines_in_span(spec, year, month)
    header_columns = [
        "CodigoEmpresa",
        spec["exercise"],
        spec["series"],
        spec["number"],
        "BaseImponible",
        spec["date"],
    ]
    if spec["status"]:
        header_columns.append(spec["status"])
    headers = read_columns(
        spec["header"],
        header_columns,
        company=codigo_empresa,
        optional=_OPTIONAL[kind],
        extra_where=header_where,
        extra_params=header_params,
    )
    lines = read_columns(
        spec["line"],
        ["CodigoEmpresa", spec["exercise"], spec["series"], spec["number"], "BaseImponible"],
        company=codigo_empresa,
        optional=("CodigoArticulo", "DescripcionArticulo", "DescripcionLinea"),
        extra_where=line_where,
        extra_params=line_params,
    )
    grouped = {}
    for row in lines:
        key = (
            _text(row["CodigoEmpresa"]),
            _text(row[spec["exercise"]]),
            _text(row[spec["series"]]),
            _text(row[spec["number"]]),
        )
        grouped.setdefault(key, []).append(row)
    result = []
    for row in headers:
        if _text(row["CodigoEmpresa"]) != str(codigo_empresa):
            continue
        key = (
            _text(row["CodigoEmpresa"]),
            _text(row[spec["exercise"]]),
            _text(row[spec["series"]]),
            _text(row[spec["number"]]),
        )
        result.append(
            ValuedDocument(
                codigo_empresa=_text(row["CodigoEmpresa"]),
                ejercicio=int(row[spec["exercise"]]),
                serie=_text(row[spec["series"]]),
                numero=_text(row[spec["number"]]),
                header_base=row["BaseImponible"],
                document_date=_date(row[spec["date"]]),
                status=_status(row[spec["status"]]) if spec["status"] else "",
                lines=[
                    SaleLine(base=line["BaseImponible"], article=_article(line))
                    for line in grouped.get(key, [])
                ],
                project=_text(row.get("CodigoProyecto")),
                channel=_text(row.get("CodigoCanal")),
                delegation=_text(row.get("IdDelegacion")),
                department=_text(row.get("CodigoDepartamento")),
                section=_text(row.get("CodigoSeccion")),
                supplier_code=_text(row.get("CodigoProveedor")),
                billing=_billing(row.get("StatusFacturado")) if "StatusFacturado" in row else "",
                credit=_marked(row.get("StatusAbono")) is True,
                linked_ejercicio=_text(row.get("EjercicioPedido")),
                linked_serie=_text(row.get("SeriePedido")),
                linked_numero=_text(row.get("NumeroPedido")),
            )
        )
    return result


def fetch_purchase_orders(codigo_empresa, year=None, month=None):
    return _fetch("purchase_order", codigo_empresa, year, month)


def fetch_sales_deliveries(codigo_empresa, year=None, month=None):
    return _fetch("sales_delivery", codigo_empresa, year, month)


def fetch_purchase_deliveries(codigo_empresa, year=None, month=None):
    return _fetch("purchase_delivery", codigo_empresa, year, month)
