import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client

from apps.access.demo import ensure_demo
from apps.margins.models import FinancialReport, FinancialReportLine, renumber_report_lines


def _line_form(index, text, accounts="", position="", line_id="", report_id="", total=False):
    data = {
        f"lines-{index}-id": line_id,
        f"lines-{index}-report": report_id,
        f"lines-{index}-position": position,
        f"lines-{index}-text": text,
        f"lines-{index}-accounts": accounts,
    }
    if total:
        data[f"lines-{index}-is_total"] = "on"
    return data


@pytest.mark.django_db
def test_an_administrator_creates_a_report_and_numbers_the_lines_by_tens():
    ensure_demo()
    admin = Client()
    admin.login(username="demo", password="demo")
    opened = admin.get("/admin/margins/financialreport/add/")
    assert opened.status_code == 200
    assert "lines-TOTAL_FORMS" in opened.content.decode()
    created = admin.post(
        "/admin/margins/financialreport/add/",
        {
            "code": "PYG",
            "description": "Cuenta de resultados",
            "lines-TOTAL_FORMS": "2",
            "lines-INITIAL_FORMS": "0",
            "lines-MIN_NUM_FORMS": "0",
            "lines-MAX_NUM_FORMS": "1000",
            **_line_form(0, "Ingresos", "7, 70"),
            **_line_form(1, "Gastos", "6"),
            "_save": "Grabar",
        },
    )
    assert created.status_code == 302
    report = FinancialReport.objects.get(code="PYG")
    assert [(line.position, line.text, line.accounts) for line in report.lines.all()] == [
        (10, "Ingresos", "7, 70"),
        (20, "Gastos", "6"),
    ]


@pytest.mark.django_db
def test_an_inserted_line_can_be_renumbered_from_the_report():
    ensure_demo()
    report = FinancialReport.objects.create(code="BAL", description="Balance")
    first = FinancialReportLine.objects.create(report=report, position=10, text="Activo", accounts="4")
    FinancialReportLine.objects.create(report=report, position=15, text="Pasivo", accounts="5")
    FinancialReportLine.objects.create(report=report, position=20, text="Total", accounts="", is_total=True)
    admin = Client()
    admin.login(username="demo", password="demo")
    page = admin.get(f"/admin/margins/financialreport/{report.pk}/change/")
    body = page.content.decode()
    assert page.status_code == 200
    assert "Renumerar de 10 en 10" in body
    posted = admin.post(
        f"/admin/margins/financialreport/{report.pk}/change/",
        {
            "code": "BAL",
            "description": "Balance",
            "lines-TOTAL_FORMS": "3",
            "lines-INITIAL_FORMS": "3",
            "lines-MIN_NUM_FORMS": "0",
            "lines-MAX_NUM_FORMS": "1000",
            **_line_form(0, "Activo", "4", "10", first.pk, report.pk),
            **_line_form(1, "Pasivo", "5", "15", report.lines.get(text="Pasivo").pk, report.pk),
            **_line_form(2, "Total", "", "20", report.lines.get(text="Total").pk, report.pk, total=True),
            "_renumber": "Renumerar de 10 en 10",
        },
    )
    assert posted.status_code == 302
    assert [line.position for line in report.lines.all()] == [10, 20, 30]
    assert report.lines.get(text="Total").is_total is True


@pytest.mark.django_db
def test_a_line_rejects_a_non_numeric_account_and_a_visitor_cannot_open_reports():
    report = FinancialReport.objects.create(code="XX", description="Prueba")
    line = FinancialReportLine(report=report, text="Mala", accounts="7, abc")
    with pytest.raises(ValidationError):
        line.full_clean()
    ensure_demo()
    visitor = get_user_model().objects.create_user("visita", "", "Clave-inicial-2026")
    guest = Client()
    guest.login(username=visitor.username, password="Clave-inicial-2026")
    assert guest.get("/admin/margins/financialreport/").status_code == 302
    renumber_report_lines(report)
