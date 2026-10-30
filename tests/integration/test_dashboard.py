from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.access.admin import CompanyAccessForm
from apps.access.demo import ensure_demo
from apps.access.models import (
    AnalyticalLevel,
    CompanyAccess,
    ErpConnection,
    InformationGroup,
    Profile,
    ProfilePermission,
)
from apps.erp.sample import SaleOrder, master_counts, movements, orders, purchases
from apps.margins.dashboard import build_dashboard
from apps.margins.services import build_report


@pytest.mark.django_db
def test_dashboard_uses_full_project_cost_and_period_purchases():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        master_counts()["1"],
        groups,
    )
    assert panel["sales"] == {"count": 5, "amount": Decimal("1190")}
    assert panel["purchases"] == {"count": 5, "amount": Decimal("1164")}
    assert panel["margin"] == Decimal("620")
    assert panel["income"] == Decimal("800")
    assert panel["clientes"] == 2
    report = build_report("1", 2026, orders(), purchases(), movements())
    order = next(row for row in report["closed"] if row["numero"] == "1001")
    assert order["cost"] == Decimal("350")
    previous = build_dashboard(
        "1",
        2025,
        orders(),
        purchases(),
        movements(),
        master_counts()["1"],
        groups,
    )
    assert previous["sales"] == {"count": 1, "amount": Decimal("300")}
    assert previous["purchases"]["amount"] == Decimal("200")


@pytest.mark.django_db
def test_missing_group_is_omitted_and_channel_breakdown_uses_the_sale_price():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        master_counts()["1"],
        groups,
    )
    channel = next(section for section in panel["breakdown"] if section["title"] == "Canal")
    amounts = {row["label"]: row["amount"] for row in channel["rows"]}
    assert amounts["Tienda"] == Decimal("1000")
    limited = [group for group in groups if group != InformationGroup.CANALES]
    without_channel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        master_counts()["1"],
        limited,
    )
    assert all(section["title"] != "Canal" for section in without_channel["breakdown"])
    only_customers = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        master_counts()["1"],
        [InformationGroup.CLIENTES],
    )
    assert list(only_customers) == ["clientes"]


def _priced_order(numero, **extra):
    values = {
        "codigo_empresa": "1",
        "ejercicio": 2026,
        "serie": "A",
        "numero": numero,
        "codigo_cliente": "C1",
        "project": numero,
        "header_base": Decimal("10"),
        "tax_included": None,
        "order_date": date(2026, 1, 1),
        "status": "Pendiente",
    }
    values.update(extra)
    return SaleOrder(**values)


@pytest.mark.django_db
def test_breakdown_shows_each_description_and_keeps_separate_codes():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        [
            _priced_order("01", channel="01", header_base=Decimal("10")),
            _priced_order("02", channel="02", header_base=Decimal("20")),
            _priced_order("03", channel="03", header_base=Decimal("5")),
            _priced_order("04", channel="  ", header_base=Decimal("7")),
        ],
        [],
        [],
        master_counts()["1"],
        groups,
        {
            "channel": {"01": "TECH", "02": "TECH", "03": "   "},
        },
    )
    channel = next(section for section in panel["breakdown"] if section["title"] == "Canal")
    rows = [(row["label"], row["amount"]) for row in channel["rows"]]
    assert ("01 — TECH", Decimal("10")) in rows
    assert ("02 — TECH", Decimal("20")) in rows
    assert ("03", Decimal("5")) in rows
    assert ("Sin dato", Decimal("7")) in rows


def _with_groups(username, groups, companies=("1",)):
    user = get_user_model().objects.create_user(username, "", "Clave-inicial-2026")
    profile = Profile.objects.create(user=user)
    for group in groups:
        ProfilePermission.objects.create(profile=profile, group=group)
    for code in companies:
        CompanyAccess.objects.create(user=user, codigo_empresa=code)
    return user


@pytest.mark.django_db
def test_dashboard_is_home_and_the_exercise_filter_changes_the_figures():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")
    page = client.get("/")
    body = page.content.decode()
    assert page.status_code == 200
    assert "Cuadro de mando" in body
    assert "1190,00 EUR" in body
    assert "Menú" in body
    assert "Margen de pedidos" in body
    assert "Administración" in body
    changed = client.post(
        "/filtros/",
        {"codigo_empresa": "1", "ejercicio": "2025", "next": "/"},
        follow=True,
    )
    changed_body = changed.content.decode()
    assert "300,00 EUR" in changed_body
    assert "1190,00 EUR" not in changed_body
    margin = client.get("/margen/").content.decode()
    assert "A / 1005" in margin
    assert "300,00 EUR" in margin
    assert "1000,00 EUR" not in margin


@pytest.mark.django_db
def test_a_profile_without_sales_does_not_see_that_indicator():
    _with_groups("solo-clientes", [InformationGroup.CLIENTES])
    client = Client()
    client.login(username="solo-clientes", password="Clave-inicial-2026")
    body = client.get("/").content.decode()
    assert "Clientes" in body
    assert "Pedidos de venta" not in body
    assert "Administración" not in body


@pytest.mark.django_db
def test_admin_hides_other_companies_and_does_not_show_the_secret_again():
    admin_user = ensure_demo()
    other = get_user_model().objects.create_user("ajena", "ajena@example.com", "Clave-inicial-2026")
    CompanyAccess.objects.create(user=other, codigo_empresa="2")
    connection = ErpConnection.objects.create(
        name="principal",
        host="localhost",
        database="TECSO",
        username="logic",
        password="secreto-origen",
    )
    client = Client()
    client.force_login(admin_user)
    assert client.get("/admin/").status_code == 200
    users = client.get("/admin/auth/user/").content.decode()
    assert "demo" in users
    assert "ajena" not in users
    form = client.get(f"/admin/access/erpconnection/{connection.pk}/change/")
    assert form.status_code == 200
    assert "secreto-origen" not in form.content.decode()
    rejected = CompanyAccessForm(
        data={"user": other.pk, "codigo_empresa": "2"},
        request=type("Request", (), {"user": admin_user})(),
    )
    assert rejected.is_valid() is False


@pytest.mark.django_db
def test_the_analytical_tree_sets_the_report_order():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        master_counts()["1"],
        groups,
    )
    titles = [section["title"] for section in panel["breakdown"]]
    assert titles == ["Canal", "Delegación", "Departamento", "Proyecto", "Sección"]

    admin_user = ensure_demo()
    client = Client()
    client.force_login(admin_user)
    page = client.get("/admin/access/analyticallevel/")
    body = page.content.decode()
    assert page.status_code == 200
    assert body.index("Canal") < body.index("Delegación")
    assert body.index("Delegación") < body.index("Departamento")
    assert body.index("Departamento") < body.index("Proyecto")
    assert body.index("Proyecto") < body.index("Sección")
    assert client.get("/admin/access/analyticallevel/add/").status_code == 403

    levels = list(AnalyticalLevel.objects.order_by("position", "code"))
    posted = {
        "form-TOTAL_FORMS": str(len(levels)),
        "form-INITIAL_FORMS": str(len(levels)),
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
        "_save": "Guardar",
    }
    for index, level in enumerate(levels):
        posted[f"form-{index}-id"] = str(level.pk)
        posted[f"form-{index}-position"] = "1"
    rejected = client.post("/admin/access/analyticallevel/", posted)
    assert rejected.status_code == 200
    assert "Cada nivel ha de tener una posición distinta." in rejected.content.decode()
    assert list(AnalyticalLevel.objects.order_by("position").values_list("position", flat=True)) == [
        1,
        2,
        3,
        4,
        5,
    ]

    section = AnalyticalLevel.objects.get(code=AnalyticalLevel.Level.SECCION)
    section.position = 1
    canal = AnalyticalLevel.objects.get(code=AnalyticalLevel.Level.CANAL)
    canal.position = 6
    section.save()
    canal.save()
    reordered = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        master_counts()["1"],
        groups,
    )
    assert [section["title"] for section in reordered["breakdown"]] == [
        "Sección",
        "Delegación",
        "Departamento",
        "Proyecto",
        "Canal",
    ]
