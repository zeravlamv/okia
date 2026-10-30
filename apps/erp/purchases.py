from datetime import datetime

from django.conf import settings

from apps.erp.mapping import read_table
from apps.erp.sample import PurchaseLine, for_company, purchases


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def fetch_purchases(codigo_empresa):
    if settings.SAMPLE_ERP:
        return for_company(purchases(), codigo_empresa)
    rows = read_table(
        "LineasPedidoProveedor",
        ["company", "project", "base", "article_name", "date", "exercise", "series", "number"],
        company=codigo_empresa,
    )
    return [
        PurchaseLine(
            codigo_empresa=_text(row["company"]),
            project=_text(row["project"]) or None,
            amount=row["base"],
            article_name=_text(row["article_name"]),
            line_date=_date(row["date"]),
            ejercicio=_text(row["exercise"]),
            serie=_text(row["series"]),
            numero=_text(row["number"]),
        )
        for row in rows
        if _text(row["company"]) == str(codigo_empresa)
    ]
