import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client

from apps.access.demo import ensure_demo
from apps.access.models import InformationGroup, ProfilePermission
from apps.erp.sample import Movement
from apps.margins.dashboard import analytical_dimensions, tree_dimensions
from apps.margins.models import DashboardSnapshot, OrderSummary, ProjectExerciseShare, ProjectLife, TreeExpense, TreeIncome
from apps.margins.snapshot import (
    replace_tree_expenses,
    tree_expense_detail,
    tree_margin_detail,
    tree_sales_detail,
)


def _titles():
    return [item[1] for item in list(analytical_dimensions())[:4]]


def _snapshot(**flags):
    titles = _titles()
    return DashboardSnapshot.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        tree_income_stored=True,
        titulo_1=titles[0],
        titulo_2=titles[1],
        titulo_3=titles[2],
        titulo_4=titles[3],
        **flags,
    )


def _commercial_path():
    titles = _titles()
    return [
        {"level": titles[0], "label": "01 — TECH"},
        {"level": titles[1], "label": "ABRE0019 — Centro logístico Abrera"},
        {"level": titles[2], "label": "2008 — COMERCIAL"},
    ]


def _labels():
    return {
        "channel": {"01": "TECH"},
        "delegation": {"ABRE0019": "Centro logístico Abrera"},
        "department": {"2008": "COMERCIAL", "2009": "OBRA"},
        "project": {"P1": "OBRA ABRERA"},
    }


def test_every_amount_of_every_group_can_open_its_origin():
    script = Path(settings.BASE_DIR, "static", "js", "breakdown.js").read_text(encoding="utf-8")
    assert 'node.label === "Sin dato"' not in script
    assert "arbol-origen" in script
    assert "ventas" in script
    assert "gastos" in script
    assert "margen" in script


@pytest.mark.django_db
def test_commercial_department_lists_its_sale_orders():
    snapshot = _snapshot()
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="P1",
        ejercicio=2026,
        sales=Decimal("22515.05"),
        nivel_1="01 — TECH",
        nivel_2="ABRE0019 — Centro logístico Abrera",
        nivel_3="2008 — COMERCIAL",
        nivel_4="P1 — OBRA ABRERA",
    )
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="P0",
        ejercicio=2026,
        sales=Decimal("0"),
        nivel_1="01 — TECH",
        nivel_2="ABRE0019 — Centro logístico Abrera",
        nivel_3="2008 — COMERCIAL",
        nivel_4="Sin dato",
    )
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="P9",
        ejercicio=2026,
        sales=Decimal("100"),
        nivel_1="01 — TECH",
        nivel_2="ABRE0019 — Centro logístico Abrera",
        nivel_3="Sin dato",
        nivel_4="Sin dato",
    )
    OrderSummary.objects.create(snapshot=snapshot, identity="2026 / A / 19", project="P1", price=Decimal("22515.05"))
    ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P1", order_date=date(2026, 2, 2))

    detail = tree_sales_detail("1", 2026, _commercial_path())

    assert detail["source"] == "CabeceraPedidoCliente"
    assert detail["headers"] == ["Pedido", "Fecha", "Proyecto", "Importe"]
    assert detail["rows"] == [["2026 / A / 19", "02/02/2026", "P1 — OBRA ABRERA", "22.515,05 EUR"]]
    assert detail["total"] == "22.515,05 EUR"


@pytest.mark.django_db
def test_commercial_department_lists_its_expenses_and_skips_income():
    titles = [item[1] for item in tree_dimensions()]
    DashboardSnapshot.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        tree_income_stored=True,
        tree_expense_stored=True,
        **{f"titulo_{index}": title for index, title in enumerate(titles, start=1)},
    )
    expense = Movement(
        codigo_empresa="1",
        project="",
        account_code="629000",
        account_name="SUMINISTROS",
        debit=Decimal("15.50"),
        credit=Decimal("0"),
        ejercicio=2026,
        movement_date=date(2026, 3, 15),
        asiento="44",
        channel="01",
        delegation="ABRE0019",
        department="2008",
    )
    other = Movement(
        codigo_empresa="1",
        project="",
        account_code="629000",
        account_name="SUMINISTROS",
        debit=Decimal("3"),
        credit=Decimal("0"),
        ejercicio=2026,
        movement_date=date(2026, 3, 16),
        asiento="45",
        channel="01",
        delegation="ABRE0019",
        department="2009",
    )
    income = Movement(
        codigo_empresa="1",
        project="",
        account_code="705000",
        account_name="VENTAS",
        debit=Decimal("0"),
        credit=Decimal("9"),
        ejercicio=2026,
        movement_date=date(2026, 3, 17),
        asiento="46",
        channel="01",
        delegation="ABRE0019",
        department="2008",
    )
    replace_tree_expenses("1", 2026, [expense, other, income], [], [], _labels())

    detail = tree_expense_detail(
        "1",
        2026,
        [
            {"level": titles[0], "label": "01 — TECH"},
            {"level": titles[1], "label": "Sin dato"},
            {"level": titles[2], "label": "ABRE0019 — Centro logístico Abrera"},
            {"level": titles[3], "label": "2008 — COMERCIAL"},
        ],
    )

    assert detail["headers"] == ["Fecha", "Asiento", "Cuenta", "Importe"]
    assert detail["rows"] == [["15/03/2026", "44", "629000 — SUMINISTROS", "15,50 EUR"]]
    assert detail["total"] == "15,50 EUR"
    assert TreeExpense.objects.count() == 2
    assert tree_expense_detail("1", 2026, [{"level": "Nada", "label": "2008 — COMERCIAL"}]) is None


@pytest.mark.django_db
def test_margin_of_a_branch_shows_income_and_expenses():
    _snapshot(tree_expense_stored=True)
    common = {
        "codigo_empresa": "1",
        "ejercicio": 2026,
        "nivel_1": "01 — TECH",
        "nivel_2": "ABRE0019 — Centro logístico Abrera",
        "nivel_3": "2008 — COMERCIAL",
    }
    TreeIncome.objects.create(movement_date=date(2026, 4, 1), asiento="1", account_code="705000", amount=Decimal("10"), **common)
    TreeExpense.objects.create(movement_date=date(2026, 4, 2), asiento="2", account_code="629000", amount=Decimal("4"), **common)

    detail = tree_margin_detail("1", 2026, _commercial_path())

    assert [section["title"] for section in detail["sections"]] == ["Ingresos", "Gastos"]
    assert detail["sections"][0]["rows"][0][-1] == "10,00 EUR"
    assert detail["sections"][1]["rows"][0][-1] == "4,00 EUR"
    assert detail["total"] == "6,00 EUR"
    assert detail["source"] == "Movimientos"


@pytest.mark.django_db
def test_expenses_wait_until_the_lines_are_stored():
    _snapshot()
    detail = tree_expense_detail("1", 2026, _commercial_path())
    assert detail["pending"] is True
    assert detail["rows"] == []


@pytest.mark.django_db
def test_origin_page_serves_each_kind_and_its_permission():
    ensure_demo()
    snapshot = _snapshot(tree_expense_stored=True)
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="P1",
        ejercicio=2026,
        sales=Decimal("10"),
        nivel_1="01 — TECH",
        nivel_2="ABRE0019 — Centro logístico Abrera",
        nivel_3="2008 — COMERCIAL",
        nivel_4="P1 — OBRA ABRERA",
    )
    OrderSummary.objects.create(snapshot=snapshot, identity="2026 / A / 19", project="P1", price=Decimal("10"))
    ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P1", order_date=date(2026, 2, 2))
    TreeIncome.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        movement_date=date(2026, 4, 1),
        amount=Decimal("10"),
        nivel_1="01 — TECH",
        nivel_2="ABRE0019 — Centro logístico Abrera",
        nivel_3="2008 — COMERCIAL",
    )
    client = Client()
    client.login(username="demo", password="demo")
    route = json.dumps(_commercial_path())

    sales = client.get("/arbol/ingresos/", {"ruta": route, "tipo": "ventas"})
    income = client.get("/arbol/ingresos/", {"ruta": route, "tipo": "ingresos"})
    margin = client.get("/arbol/ingresos/", {"ruta": route, "tipo": "margen"})
    guide = client.get("/guia/")

    assert sales.status_code == 200
    assert sales.json()["rows"][0][0] == "2026 / A / 19"
    assert income.status_code == 200
    assert income.json()["rows"][0][-1] == "10,00 EUR"
    assert margin.status_code == 200
    assert margin.json()["sections"][1]["message"] == "No hay apuntes en esta rama."
    assert "Cualquier importe del árbol" in guide.content.decode()
    assert client.get("/arbol/ingresos/", {"ruta": route, "tipo": "nada"}).status_code == 404

    user = ensure_demo()
    ProfilePermission.objects.filter(profile=user.profile, group=InformationGroup.PEDIDOS_VENTA).delete()
    client.login(username="demo", password="demo")
    assert client.get("/arbol/ingresos/", {"ruta": route, "tipo": "ventas"}).status_code == 403
    assert client.get("/arbol/ingresos/", {"ruta": route, "tipo": "ingresos"}).status_code == 200
