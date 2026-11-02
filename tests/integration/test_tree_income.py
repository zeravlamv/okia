import json
from datetime import date
from decimal import Decimal

import pytest
from django.test import Client

from apps.access.demo import ensure_demo
from apps.access.models import InformationGroup, ProfilePermission
from apps.erp.sample import Movement, SaleOrder
from apps.margins.dashboard import analytical_dimensions
from apps.margins.models import AnalyticalSummary, DashboardSnapshot, TreeIncome
from apps.margins.snapshot import month_hierarchy, replace_tree_incomes, tree_income_detail


def _titles():
    return [item[1] for item in list(analytical_dimensions())[:4]]


def _snapshot():
    titles = _titles()
    return DashboardSnapshot.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        tree_income_stored=True,
        titulo_1=titles[0],
        titulo_2=titles[1],
        titulo_3=titles[2],
        titulo_4=titles[3],
    )


def _blank_income():
    return Movement(
        codigo_empresa="1",
        project=None,
        account_code="705000015020",
        account_name="AUTOMATIZACION",
        debit=Decimal("0"),
        credit=Decimal("2148"),
        ejercicio=2026,
        movement_date=date(2026, 4, 30),
        comment="Ntra.Fra.Num.: 260501",
        channel="01",
        delegation="WAYN0030",
        asiento="3811",
    )


@pytest.mark.django_db
def test_a_blank_project_income_lists_the_posting():
    titles = _titles()
    _snapshot()
    placed = Movement(
        codigo_empresa="1",
        project="230309",
        account_code="705000015020",
        account_name="AUTOMATIZACION",
        debit=Decimal("0"),
        credit=Decimal("10"),
        ejercicio=2026,
        movement_date=date(2026, 5, 31),
        comment="Ntra.Fra.Num.: 999",
        channel="01",
        delegation="WAYN0030",
        department="2008",
        asiento="9",
    )
    labels = {
        "channel": {"01": "TECH"},
        "delegation": {"WAYN0030": "Headquarter DRAKE"},
        "department": {"2008": "COMERCIAL"},
        "project": {"230309": "PRUEBAS Y TEST BONAREA"},
    }
    order = SaleOrder(
        codigo_empresa="1",
        ejercicio=2026,
        serie="A",
        numero="1",
        codigo_cliente="C1",
        project="230309",
        header_base=Decimal("10"),
        tax_included=None,
        order_date=date(2026, 3, 23),
        status="Pendiente",
        channel="01",
        delegation="WAYN0030",
        department="2008",
    )
    replace_tree_incomes("1", 2026, [_blank_income(), placed], [order], [], labels)
    path = [
        {"level": titles[1], "label": "WAYN0030 — Headquarter DRAKE"},
        {"level": titles[2], "label": "Sin dato"},
        {"level": titles[3], "label": "Sin dato"},
    ]
    detail = tree_income_detail("1", 2026, path)
    assert detail["rows"] == [[
        "30/04/2026",
        "3811",
        "705000015020 — AUTOMATIZACION",
        "260501",
        "2.148,00 EUR",
    ]]
    assert detail["total"] == "2.148,00 EUR"
    assert detail["source"] == "Movimientos"
    assert TreeIncome.objects.filter(nivel_4="230309 — PRUEBAS Y TEST BONAREA").count() == 1


@pytest.mark.django_db
@pytest.mark.django_db
def test_a_month_keeps_its_own_income_lines():
    snapshot = _snapshot()
    titles = _titles()
    TreeIncome.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        movement_date=date(2026, 1, 15),
        amount=Decimal("10"),
        nivel_1="01 — TECH",
    )
    TreeIncome.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        movement_date=date(2026, 2, 2),
        amount=Decimal("100"),
        nivel_1="01 — TECH",
    )
    AnalyticalSummary.objects.create(snapshot=snapshot, **{f"nivel_{titles.index('Proyecto') + 1}": "230309 — PRUEBAS"})

    january = month_hierarchy("1", 2026, 1, list(InformationGroup))
    detail = tree_income_detail("1", 2026, [{"level": titles[0], "label": "01 — TECH"}], month=1)

    assert january["nodes"][0]["income"] == Decimal("10")
    assert january["nodes"][0]["label"] == "01 — TECH"
    assert "sales" not in january["nodes"][0]
    assert january["projects"] == [{"code": "230309", "label": "230309 — PRUEBAS"}]
    assert detail["total"] == "10,00 EUR"
    assert month_hierarchy("1", 2026, 2, list(InformationGroup))["nodes"][0]["income"] == Decimal("100")


@pytest.mark.django_db
def test_tree_income_waits_until_the_lines_are_stored():
    snapshot = _snapshot()
    snapshot.tree_income_stored = False
    snapshot.save(update_fields=["tree_income_stored"])
    titles = _titles()
    detail = tree_income_detail("1", 2026, [{"level": titles[3], "label": "Sin dato"}])
    assert detail["pending"] is True
    assert detail["rows"] == []


@pytest.mark.django_db
def test_tree_income_page_requires_movements_and_a_known_level():
    ensure_demo()
    titles = _titles()
    _snapshot()
    replace_tree_incomes(
        "1",
        2026,
        [_blank_income()],
        [],
        [],
        {"channel": {"01": "TECH"}, "delegation": {"WAYN0030": "Headquarter DRAKE"}},
    )
    client = Client()
    client.login(username="demo", password="demo")
    route = json.dumps([
        {"level": titles[1], "label": "WAYN0030 — Headquarter DRAKE"},
        {"level": titles[3], "label": "Sin dato"},
    ])
    opened = client.get("/arbol/ingresos/", {"ruta": route})
    assert opened.status_code == 200
    assert opened.json()["rows"][0][1] == "3811"
    assert client.get("/arbol/ingresos/", {"ruta": json.dumps([{"level": "Nada", "label": "Sin dato"}])}).status_code == 404
    user = ensure_demo()
    ProfilePermission.objects.filter(profile=user.profile, group=InformationGroup.MOVIMIENTOS).delete()
    client.login(username="demo", password="demo")
    assert client.get("/arbol/ingresos/", {"ruta": route}).status_code == 403
