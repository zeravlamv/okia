from datetime import date
from decimal import Decimal

import pytest
from django.test import Client

from apps.access.demo import ensure_demo
from apps.access.models import InformationGroup, ProfilePermission
from apps.erp.sample import AnalyticSlice, Movement
from apps.margins.models import (
    AccountGroup,
    BookExpense,
    BookIncome,
    DashboardSnapshot,
    MonthLedger,
    ProjectDocumentLine,
    ProjectExpense,
    ProjectLife,
)
from apps.margins.project_life import replace_book_expenses, replace_book_incomes
from apps.margins.snapshot import load_dashboard, monthly_bars


@pytest.mark.django_db
def test_a_month_amount_lists_its_stored_documents():
    ensure_demo()
    life = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P1", order_date=date(2026, 3, 1))
    DashboardSnapshot.objects.create(codigo_empresa="1", ejercicio=2026, income_stored=True)
    BookIncome.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        account_code="700000",
        account_name="Ventas",
        movement_date=date(2026, 3, 4),
        amount=Decimal("80"),
        project_code="P1",
        department_code="VENT",
        department_name="Ventas",
        section_code="01",
        section_name="Taller",
    )
    BookIncome.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        account_code="705000",
        account_name="Prestaciones",
        movement_date=date(2026, 4, 2),
        amount=Decimal("10"),
        project_code="P1",
    )
    ProjectExpense.objects.create(
        life=life,
        account_code="602000",
        account_name="Compras",
        movement_date=date(2026, 3, 8),
        amount=Decimal("15"),
        department_code="VENT",
        department_name="Ventas",
        section_code="01",
        section_name="Taller",
    )
    client = Client()
    client.login(username="demo", password="demo")
    session = client.session
    session["okia_year"] = 2026
    session["okia_company"] = "1"
    session.save()

    sale = client.get("/evolucion/?mes=3&tipo=ingreso")
    assert sale.status_code == 200
    body = sale.json()
    assert body["kind"] == "ingreso"
    assert body["title"] == "Ingresos de marzo de 2026"
    assert body["source"] == "Movimientos"
    assert body["total"] == "80,00 EUR"
    assert body["groups"] == [{
        "code": "700",
        "label": "700",
        "amount": "80,00 EUR",
        "lines": [[
            "04/03/2026",
            "P1",
            "700000 — Ventas",
            "VENT — Ventas",
            "01 — Taller",
            "80,00 EUR",
        ]],
    }]
    assert client.get("/evolucion/?mes=3&tipo=venta").status_code == 404

    spent = client.get("/evolucion/?mes=3&tipo=compra").json()
    assert spent["kind"] == "compra"
    assert spent["title"].startswith("Compras de")
    assert spent["source"] == "AnaMovimientos unida a Movimientos"
    assert spent["groups"] == [{
        "code": "602",
        "label": "602",
        "amount": "15,00 EUR",
        "lines": [[
            "08/03/2026",
            "P1",
            "602000 — Compras",
            "VENT — Ventas",
            "01 — Taller",
            "15,00 EUR",
        ]],
    }]
    assert spent["total"] == "15,00 EUR"
    assert client.get("/evolucion/?mes=3&tipo=margen").status_code == 404


@pytest.mark.django_db
def test_gasto_detail_requires_the_movements_group():
    user = ensure_demo()
    ProfilePermission.objects.filter(profile=user.profile, group=InformationGroup.MOVIMIENTOS).delete()
    client = Client()
    client.login(username="demo", password="demo")

    assert client.get("/evolucion/?mes=3&tipo=gasto").status_code == 403
    assert client.get("/evolucion/?mes=3&tipo=ingreso").status_code == 403


@pytest.mark.django_db
def test_expenses_group_by_the_first_three_digits_and_lines_open_from_the_document():
    ensure_demo()
    life = ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto="P9",
        order_date=date(2026, 1, 2),
        lines_stored=True,
    )
    ProjectExpense.objects.create(
        life=life, account_code="6020000021000", account_name="Elevación", movement_date=date(2026, 1, 4), amount=Decimal("10")
    )
    ProjectExpense.objects.create(
        life=life, account_code="6020000090000", account_name="Otra elevación", movement_date=date(2026, 1, 5), amount=Decimal("5")
    )
    ProjectExpense.objects.create(
        life=life, account_code="607001000001", account_name="Tarjeta", movement_date=date(2026, 1, 6), amount=Decimal("2")
    )
    ProjectDocumentLine.objects.create(
        life=life, kind="sale_delivery", document_key="2026 / T / 9", position=1, description="Tornillo", amount=Decimal("4")
    )
    ProjectDocumentLine.objects.create(
        life=life, kind="sale_delivery", document_key="2026 / T / 9", position=2, description="Tuerca", amount=Decimal("1")
    )
    client = Client()
    client.login(username="demo", password="demo")
    session = client.session
    session["okia_year"] = 2026
    session["okia_company"] = "1"
    session.save()

    groups = client.get("/evolucion/?mes=1&tipo=compra").json()["groups"]
    assert [group["code"] for group in groups] == ["602", "607"]
    assert groups[0]["amount"] == "15,00 EUR"
    assert len(groups[0]["lines"]) == 2
    lines = client.get("/evolucion/lineas/?proyecto=P9&albaran=2026 / T / 9").json()
    assert lines["rows"] == [["Tornillo", "4,00 EUR"], ["Tuerca", "1,00 EUR"]]
    assert lines["total"] == "5,00 EUR"
    assert lines["pending"] is False

    bare = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P8", order_date=date(2026, 1, 2))
    assert bare.lines_stored is False
    pending = client.get("/evolucion/lineas/?proyecto=P8&albaran=2026 / T / 1").json()
    assert pending["pending"] is True
    assert pending["rows"] == []


@pytest.mark.django_db
def test_book_expenses_stay_pending_until_actualizar_and_then_group():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")
    session = client.session
    session["okia_year"] = 2026
    session["okia_company"] = "1"
    session.save()

    pending = client.get("/evolucion/?mes=1&tipo=gasto").json()
    assert pending["pending"] is True
    assert pending["message"] == "Las líneas se guardan al pulsar Actualizar."
    assert pending["groups"] == []

    DashboardSnapshot.objects.create(codigo_empresa="1", ejercicio=2026, book_stored=True)
    BookExpense.objects.create(
        codigo_empresa="1", ejercicio=2026, account_code="640000", account_name="Sueldos",
        movement_date=date(2026, 1, 8), amount=Decimal("12"), project_code="",
    )
    BookExpense.objects.create(
        codigo_empresa="1", ejercicio=2026, account_code="642000", account_name="Seguridad Social",
        movement_date=date(2026, 1, 9), amount=Decimal("3"), project_code="",
    )
    body = client.get("/evolucion/?mes=1&tipo=gasto").json()
    assert body["pending"] is False
    assert body["source"] == "Movimientos"
    assert [group["code"] for group in body["groups"]] == ["640", "642"]
    assert body["total"] == "15,00 EUR"


@pytest.mark.django_db
def test_income_lines_group_by_the_first_three_digits():
    ensure_demo()
    DashboardSnapshot.objects.create(codigo_empresa="1", ejercicio=2026, income_stored=True)
    BookIncome.objects.create(
        codigo_empresa="1", ejercicio=2026, account_code="700000", account_name="Ventas",
        movement_date=date(2026, 1, 8), amount=Decimal("12"), project_code="",
    )
    BookIncome.objects.create(
        codigo_empresa="1", ejercicio=2026, account_code="705000", account_name="Prestaciones",
        movement_date=date(2026, 1, 9), amount=Decimal("3"), project_code="P1",
    )
    client = Client()
    client.login(username="demo", password="demo")
    session = client.session
    session["okia_year"] = 2026
    session["okia_company"] = "1"
    session.save()
    body = client.get("/evolucion/?mes=1&tipo=ingreso").json()
    assert body["pending"] is False
    assert [group["code"] for group in body["groups"]] == ["700", "705"]
    assert body["total"] == "15,00 EUR"


@pytest.mark.django_db
def test_book_incomes_keep_the_group_seven_header():
    kept = Movement("1", "P1", "700000", "Ventas", Decimal("0"), Decimal("40"), 2026, date(2026, 1, 31))
    expense = Movement("1", "", "640000", "Sueldos", Decimal("20"), Decimal("0"), 2026, date(2026, 1, 31))
    closing = Movement(
        "1", "", "700000", "Ventas", Decimal("0"), Decimal("40"), 2026, date(2026, 1, 31),
        comment="Asiento de cierre ejercicio",
    )
    replace_book_incomes("1", 2026, [kept, expense, closing])
    stored = list(BookIncome.objects.filter(codigo_empresa="1"))
    assert [(row.account_code, row.amount, row.project_code) for row in stored] == [("700000", Decimal("40"), "P1")]


@pytest.mark.django_db
def test_book_expenses_keep_only_the_part_not_placed_on_a_project():
    purchase = Movement("1", "P1", "602000", "Compras", Decimal("50"), Decimal("0"), 2026, date(2026, 3, 4))
    overhead = Movement("1", "", "640000", "Sueldos", Decimal("20"), Decimal("0"), 2026, date(2026, 3, 8))
    shared = Movement(
        "1", "P1", "621000", "Arrendamientos", Decimal("80"), Decimal("0"), 2026, date(2026, 3, 9),
        slices=[AnalyticSlice(project="P1", amount=Decimal("30")), AnalyticSlice(project="OTRO", amount=Decimal("50"))],
    )
    replace_book_expenses("1", 2026, [purchase, overhead, shared], ["P1"])
    stored = list(BookExpense.objects.filter(codigo_empresa="1").order_by("account_code"))
    assert [(row.account_code, row.amount) for row in stored] == [("621000", Decimal("50")), ("640000", Decimal("20"))]


@pytest.mark.django_db
def test_book_expenses_skip_a_line_already_kept_on_an_older_ficha():
    ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="VIEJO", order_date=date(2025, 9, 8))
    old = Movement("1", "VIEJO", "602000", "Compras", Decimal("40"), Decimal("0"), 2026, date(2026, 1, 31))
    fresh = Movement("1", "NUEVO", "602000", "Compras", Decimal("10"), Decimal("0"), 2026, date(2026, 1, 31))
    replace_book_expenses("1", 2026, [old, fresh], [])
    stored = list(BookExpense.objects.filter(codigo_empresa="1"))
    assert [(row.project_code, row.amount) for row in stored] == [("NUEVO", Decimal("10"))]


@pytest.mark.django_db
def test_a_three_digit_group_shows_its_saved_description():
    ensure_demo()
    AccountGroup.objects.create(
        codigo_empresa="1", code="602", description="Compras de otros aprovisionamientos"
    )
    life = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P1", order_date=date(2026, 1, 2))
    ProjectExpense.objects.create(
        life=life, account_code="602000", account_name="Elevación", movement_date=date(2026, 1, 4), amount=Decimal("10")
    )
    client = Client()
    client.login(username="demo", password="demo")
    session = client.session
    session["okia_year"] = 2026
    session["okia_company"] = "1"
    session.save()
    group = client.get("/evolucion/?mes=1&tipo=compra").json()["groups"][0]
    assert group["code"] == "602"
    assert group["label"] == "602 — Compras de otros aprovisionamientos"


@pytest.mark.django_db
def test_purchases_stay_in_group_sixty_and_other_groups_leave_expenses():
    ensure_demo()
    life = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P1", order_date=date(2026, 1, 2))
    ProjectExpense.objects.create(
        life=life, account_code="602000", account_name="Compras", movement_date=date(2026, 1, 4), amount=Decimal("50")
    )
    ProjectExpense.objects.create(
        life=life, account_code="629000", account_name="Otros servicios", movement_date=date(2026, 1, 5), amount=Decimal("10")
    )
    DashboardSnapshot.objects.create(
        codigo_empresa="1", ejercicio=2026, book_stored=True, income_amount=Decimal("110"), expense_amount=Decimal("55"), expense_count=4
    )
    BookExpense.objects.create(
        codigo_empresa="1", ejercicio=2026, account_code="480000", account_name="Gastos anticipados",
        movement_date=date(2026, 1, 6), amount=Decimal("-20"),
    )
    BookExpense.objects.create(
        codigo_empresa="1", ejercicio=2026, account_code="640000", account_name="Sueldos",
        movement_date=date(2026, 1, 7), amount=Decimal("15"),
    )
    MonthLedger.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=1, income_amount=Decimal("110"), expense_amount=Decimal("55")
    )
    january = next(row for row in monthly_bars("1", 2026, list(InformationGroup.values)) if row["label"] == "ene")
    assert january["purchases"] == Decimal("50")
    assert january["expenses"] == Decimal("25")
    assert january["margin"] == Decimal("35")
    figures = load_dashboard("1", 2026, list(InformationGroup.values))
    assert figures["accounted_purchases"]["amount"] == Decimal("50")
    assert figures["expenses"]["amount"] == Decimal("25")
    assert figures["margin"] == Decimal("35")

    client = Client()
    client.login(username="demo", password="demo")
    session = client.session
    session["okia_year"] = 2026
    session["okia_company"] = "1"
    session.save()
    purchases = client.get("/evolucion/?mes=1&tipo=compra").json()
    assert [group["code"] for group in purchases["groups"]] == ["602"]
    assert purchases["total"] == "50,00 EUR"
    expenses = client.get("/evolucion/?mes=1&tipo=gasto").json()
    assert [group["code"] for group in expenses["groups"]] == ["629", "640"]
    assert expenses["total"] == "25,00 EUR"
