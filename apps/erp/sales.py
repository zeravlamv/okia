from datetime import datetime

from django.conf import settings

from apps.erp.mapping import list_columns, month_window, read_table, resolve
from apps.erp.sample import SaleLine, SaleOrder, for_company, orders

ORDER_STATUS = {
    "0": "Pendiente",
    "1": "Bloqueado",
    "2": "Servido",
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
    return ORDER_STATUS.get(text, text)


def _project(value):
    text = _text(value)
    return text or None


def _in_month(moment, year, month):
    return moment is not None and moment.year == int(year) and moment.month == int(month)


def _header_span(table, year, month):
    column = resolve(list_columns(table), "date")
    start, end = month_window(year, month)
    return f"[{column}] >= ? AND [{column}] < ?", (start, end)


def _lines_in_span(line_table, header_table, year, month):
    header_columns = list_columns(header_table)
    line_columns = list_columns(line_table)
    links = []
    for logical in ("company", "exercise", "series", "number"):
        links.append(
            f"h.[{resolve(header_columns, logical)}] = [{line_table}].[{resolve(line_columns, logical)}]"
        )
    start, end = month_window(year, month)
    date_column = resolve(header_columns, "date")
    where = (
        f"EXISTS (SELECT 1 FROM [{header_table}] h WHERE "
        + " AND ".join(links)
        + f" AND h.[{date_column}] >= ? AND h.[{date_column}] < ?)"
    )
    return where, (start, end)


def fetch_orders(codigo_empresa, year=None, month=None):
    if settings.SAMPLE_ERP:
        rows = for_company(orders(), codigo_empresa)
        if year is None or month is None:
            return rows
        return [row for row in rows if _in_month(row.order_date, year, month)]
    header_where, header_params = ("", ())
    line_where, line_params = ("", ())
    if year is not None and month is not None:
        header_where, header_params = _header_span("CabeceraPedidoCliente", year, month)
        line_where, line_params = _lines_in_span("LineasPedidoCliente", "CabeceraPedidoCliente", year, month)
    headers = read_table(
        "CabeceraPedidoCliente",
        [
            "company",
            "customer",
            "exercise",
            "series",
            "number",
            "project",
            "base",
            "tax_total",
            "date",
            "status",
            "channel",
            "delegation",
            "department",
            "section",
        ],
        company=codigo_empresa,
        extra_where=header_where,
        extra_params=header_params,
    )
    lines = read_table(
        "LineasPedidoCliente",
        ["company", "exercise", "series", "number", "article", "base"],
        company=codigo_empresa,
        extra_where=line_where,
        extra_params=line_params,
    )
    grouped = {}
    for row in lines:
        key = (_text(row["company"]), _text(row["exercise"]), _text(row["series"]), _text(row["number"]))
        grouped.setdefault(key, []).append(row)
    result = []
    for row in headers:
        if _text(row["company"]) != str(codigo_empresa):
            continue
        key = (_text(row["company"]), _text(row["exercise"]), _text(row["series"]), _text(row["number"]))
        result.append(
            SaleOrder(
                codigo_empresa=_text(row["company"]),
                ejercicio=int(row["exercise"]),
                serie=_text(row["series"]),
                numero=_text(row["number"]),
                codigo_cliente=_text(row["customer"]),
                project=_project(row["project"]),
                header_base=row["base"],
                tax_included=row["tax_total"],
                order_date=_date(row["date"]),
                status=_status(row["status"]),
                channel=_text(row["channel"]),
                delegation=_text(row["delegation"]),
                department=_text(row["department"]),
                section=_text(row["section"]),
                lines=[
                    SaleLine(base=line["base"], article=_text(line["article"]))
                    for line in grouped.get(key, [])
                ],
            )
        )
    return result
