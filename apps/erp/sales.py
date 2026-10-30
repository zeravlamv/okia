from datetime import datetime

from django.conf import settings

from apps.erp.mapping import read_table
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


def fetch_orders(codigo_empresa):
    if settings.SAMPLE_ERP:
        return for_company(orders(), codigo_empresa)
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
    )
    lines = read_table(
        "LineasPedidoCliente",
        ["company", "exercise", "series", "number", "article", "base"],
        company=codigo_empresa,
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
