from datetime import date

from apps.access.services import allowed_companies
from apps.erp.companies import company_names

YEAR_SPAN = 11


def selected_year(request):
    raw = request.session.get("okia_year")
    try:
        year = int(raw)
    except (TypeError, ValueError):
        return date.today().year
    if year < 1990 or year > 2100:
        return date.today().year
    return year


def set_year(request, year):
    request.session["okia_year"] = int(year)
    return int(year)


def year_options():
    current = date.today().year
    return list(range(current, current - YEAR_SPAN, -1))


def filter_context(request, company):
    codes = allowed_companies(request.user)
    names = company_names(codes)
    return {
        "company": company,
        "year": selected_year(request),
        "company_options": [(code, names.get(code) or code) for code in codes],
        "year_options": year_options(),
    }


def safe_next(value):
    if not value or not value.startswith("/") or value.startswith("//"):
        return "/"
    return value
