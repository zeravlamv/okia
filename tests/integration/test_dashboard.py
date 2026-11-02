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
from apps.erp.sample import (
    AnalyticSlice,
    Movement,
    PurchaseLine,
    SaleOrder,
    ValuedDocument,
    movements,
    orders,
    purchase_deliveries,
    purchase_orders,
    purchases,
    sales_deliveries,
)
from apps.margins.dashboard import build_dashboard
from apps.margins.services import build_report


@pytest.mark.django_db
def test_dashboard_values_documents_and_keeps_the_order_margin():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        groups,
        purchase_orders=purchase_orders(),
        sales_deliveries=sales_deliveries(),
        purchase_deliveries=purchase_deliveries(),
    )
    assert panel["sales"] == {"count": 5, "amount": Decimal("1190")}
    assert panel["purchase_orders"] == {"count": 1, "amount": Decimal("400")}
    assert panel["sales_deliveries"] == {"count": 3, "amount": Decimal("850")}
    assert panel["purchase_deliveries"] == {"count": 2, "amount": Decimal("330")}
    assert panel["income"] == {"count": 2, "amount": Decimal("900")}
    assert panel["expenses"] == {"count": 2, "amount": Decimal("75")}
    assert panel["margin"] == Decimal("825")
    assert panel["margin_percent"] == Decimal("825") / Decimal("900") * Decimal("100")
    assert "clientes" not in panel
    assert "proveedores" not in panel
    assert "articulos" not in panel
    report = build_report("1", 2026, orders(), purchases(), movements())
    order = next(row for row in report["closed"] if row["numero"] == "1001")
    assert order["cost"] == Decimal("50")
    previous = build_dashboard(
        "1",
        2025,
        orders(),
        purchases(),
        movements(),
        groups,
        purchase_orders=purchase_orders(),
        sales_deliveries=sales_deliveries(),
        purchase_deliveries=purchase_deliveries(),
    )
    assert previous["sales"] == {"count": 1, "amount": Decimal("300")}
    assert previous["purchase_orders"] == {"count": 1, "amount": Decimal("200")}
    assert previous["sales_deliveries"]["amount"] == Decimal("415")
    assert previous["income"] == {"count": 0, "amount": Decimal("0")}


@pytest.mark.django_db
def test_missing_group_is_omitted_and_channel_breakdown_uses_the_sale_price():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        groups,
    )
    canal = next(node for node in panel["hierarchy"] if node["label"] == "Tienda")
    assert canal["sales"] == Decimal("1000")
    limited = [group for group in groups if group != InformationGroup.CANALES]
    without_channel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        limited,
    )

    def levels(nodes, found):
        for node in nodes:
            found.append(node["level"])
            levels(node["children"], found)
        return found

    assert "Canal" not in levels(without_channel["hierarchy"], [])
    without_expenses = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        [group for group in groups if group != InformationGroup.MOVIMIENTOS],
    )
    assert "expenses" not in without_expenses["hierarchy"][0]
    assert "margin" not in without_expenses["hierarchy"][0]
    only_customers = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        [InformationGroup.CLIENTES],
    )
    assert only_customers == {}


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
        groups,
        {
            "channel": {"01": "TECH", "02": "TECH", "03": "   "},
        },
    )
    rows = [(node["label"], node["sales"]) for node in panel["hierarchy"]]
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
    assert "Pulse Actualizar" in body
    assert "Actualizado el" not in body
    assert "1.190,00 EUR" not in body
    assert "Menú" in body
    assert "Margen de pedidos" in body
    assert "Administración" in body
    refreshed = client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2026", "next": "/"},
        follow=True,
    )
    refreshed_body = refreshed.content.decode()
    assert "1.190,00 EUR" in refreshed_body
    assert "Tienda" in refreshed_body
    assert "825,00 EUR" in refreshed_body
    assert "91,67 %" in refreshed_body
    assert "Actualizado el" in refreshed_body
    changed = client.post(
        "/filtros/",
        {"codigo_empresa": "1", "ejercicio": "2025", "next": "/"},
        follow=True,
    )
    changed_body = changed.content.decode()
    assert "300,00 EUR" not in changed_body
    assert "1.190,00 EUR" not in changed_body
    assert "Pulse Actualizar" in changed_body
    assert "Actualizado el" not in changed_body
    client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2025", "next": "/margen/"},
        follow=True,
    )
    margin = client.get("/margen/").content.decode()
    assert "A / 1005" in margin
    assert "300,00 EUR" in margin
    assert "1.000,00 EUR" not in margin


@pytest.mark.django_db
def test_a_profile_without_sales_does_not_see_that_indicator():
    _with_groups("solo-clientes", [InformationGroup.CLIENTES])
    client = Client()
    client.login(username="solo-clientes", password="Clave-inicial-2026")
    body = client.get("/").content.decode()
    assert "Clientes" not in body
    assert "Proveedores" not in body
    assert "Artículos" not in body
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
def test_a_movement_without_lines_uses_the_levels_written_on_it():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        [],
        [],
        [
            Movement(
                "1",
                None,
                "705",
                "Ventas",
                Decimal("0"),
                Decimal("500"),
                ejercicio=2026,
                channel="01",
                delegation="ALGE1424",
            )
        ],
        groups,
    )
    canal = next(node for node in panel["hierarchy"] if node["label"] == "01")
    assert canal["income"] == Decimal("500")
    delegation = canal["children"][0]
    assert delegation["label"] == "ALGE1424"
    assert delegation["income"] == Decimal("500")


def _project_node(nodes, label):
    for node in nodes:
        if node["level"] == "Proyecto" and node["label"] == label:
            return node
        found = _project_node(node["children"], label)
        if found is not None:
            return found
    return None


@pytest.mark.django_db
def test_the_three_levels_take_the_only_order_project():
    groups = list(InformationGroup.values)
    sale = SaleOrder(
        codigo_empresa="1",
        ejercicio=2026,
        serie="A",
        numero="1",
        codigo_cliente="C1",
        project="26005",
        header_base=Decimal("10"),
        tax_included=None,
        order_date=date(2026, 1, 1),
        status="Pendiente",
        channel="01",
        delegation="CENT1247",
        department="2008",
    )
    movement = Movement(
        "1",
        None,
        "642",
        "Sueldos",
        Decimal("80"),
        Decimal("0"),
        ejercicio=2026,
        channel="01",
        delegation="CENT1247",
        department="2008",
    )
    panel = build_dashboard("1", 2026, [sale], [], [movement], groups)
    project = _project_node(panel["hierarchy"], "26005")
    assert project["expenses"] == Decimal("80")
    assert _project_node(panel["hierarchy"], "Sin dato") is None


@pytest.mark.django_db
def test_several_projects_for_the_same_three_levels_stay_without_project():
    groups = list(InformationGroup.values)

    def sale(numero, project):
        return SaleOrder(
            codigo_empresa="1",
            ejercicio=2026,
            serie="A",
            numero=numero,
            codigo_cliente="C1",
            project=project,
            header_base=Decimal("10"),
            tax_included=None,
            order_date=date(2026, 1, 1),
            status="Pendiente",
            channel="01",
            delegation="CENT1247",
            department="2008",
        )

    movement = Movement(
        "1",
        None,
        "642",
        "Sueldos",
        Decimal("80"),
        Decimal("0"),
        ejercicio=2026,
        channel="01",
        delegation="CENT1247",
        department="2008",
    )
    panel = build_dashboard(
        "1",
        2026,
        [sale("1", "26005"), sale("2", "26006")],
        [],
        [movement],
        groups,
    )
    missing = _project_node(panel["hierarchy"], "Sin dato")
    assert missing["expenses"] == Decimal("80")


@pytest.mark.django_db
def test_a_purchase_line_does_not_enter_the_analytical_cost():
    groups = list(InformationGroup.values)
    sale = SaleOrder(
        codigo_empresa="1",
        ejercicio=2026,
        serie="A",
        numero="1",
        codigo_cliente="C1",
        project="26019",
        header_base=Decimal("10"),
        tax_included=None,
        order_date=date(2026, 1, 1),
        status="Pendiente",
        channel="Obra",
    )
    line = PurchaseLine(
        "1",
        "26019",
        Decimal("40"),
        "Tornillo",
        date(2026, 1, 2),
        ejercicio="2026",
        serie="P",
        numero="9",
    )
    header = ValuedDocument(
        "1",
        2026,
        "P",
        "9",
        Decimal("40"),
        date(2026, 1, 2),
        "Pendiente",
        project="26019",
        channel="01",
        delegation="CENT1247",
        department="2006",
    )
    movement = Movement(
        "1",
        "26019",
        "600",
        "Compras de mercaderías",
        Decimal("12"),
        Decimal("0"),
        ejercicio=2026,
        channel="01",
        delegation="CENT1247",
        department="2006",
    )
    panel = build_dashboard(
        "1",
        2026,
        [sale],
        [line],
        [movement],
        groups,
        purchase_orders=[header],
    )
    project = _project_node(panel["hierarchy"], "26019")
    assert project["expenses"] == Decimal("12")
    assert project["sales"] == Decimal("0")
    assert "purchases" not in project
    sale_node = _project_node(
        [node for node in panel["hierarchy"] if node["label"] == "Obra"],
        "26019",
    )
    assert sale_node["sales"] == Decimal("10")
    assert sale_node["expenses"] == Decimal("0")


@pytest.mark.django_db
def test_each_analytical_line_keeps_its_own_amount():
    groups = list(InformationGroup.values)
    spent = Movement(
        "1",
        "1001",
        "640",
        "Sueldos y salarios personal",
        Decimal("100"),
        Decimal("0"),
        ejercicio=2026,
        slices=[
            AnalyticSlice(channel="Tienda", amount=Decimal("30")),
            AnalyticSlice(channel="Web", amount=Decimal("20")),
        ],
    )
    income = Movement(
        "1",
        "1001",
        "700",
        "Ventas",
        Decimal("0"),
        Decimal("800"),
        ejercicio=2026,
        slices=[AnalyticSlice(channel="Tienda", amount=Decimal("800"))],
    )
    panel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        [spent, income],
        groups,
    )
    rows = {node["label"]: node for node in panel["hierarchy"]}
    assert rows["Tienda"]["expenses"] == Decimal("30")
    assert rows["Web"]["expenses"] == Decimal("20")
    assert rows["Tienda"]["sales"] == Decimal("1000")
    assert sum((node["expenses"] for node in panel["hierarchy"]), Decimal("0")) == Decimal("50")
    assert sum((node["margin"] for node in panel["hierarchy"]), Decimal("0")) == Decimal("750")


@pytest.mark.django_db
def test_the_analytical_tree_sets_the_report_order():
    groups = list(InformationGroup.values)
    panel = build_dashboard(
        "1",
        2026,
        orders(),
        purchases(),
        movements(),
        groups,
    )
    def path_levels(nodes):
        if not nodes:
            return []
        return [nodes[0]["level"]] + path_levels(nodes[0]["children"])

    def total(nodes, key):
        return sum((node[key] for node in nodes), Decimal("0"))

    assert path_levels(panel["hierarchy"]) == [
        "Canal",
        "Delegación",
        "Departamento",
        "Proyecto",
    ]
    assert total(panel["hierarchy"], "sales") == Decimal("1010")
    assert total(panel["hierarchy"], "expenses") == Decimal("50")
    assert total(panel["hierarchy"], "margin") == Decimal("750")
    assert total(panel["hierarchy"], "income") == Decimal("800")
    aside = {row["identity"]: row["amount"] for row in panel["aside"]}
    assert aside["2026 / B / 2001"] == Decimal("100")
    assert aside["2026 / B / 2002"] == Decimal("80")

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
        groups,
    )
    assert path_levels(reordered["hierarchy"]) == [
        "Sección",
        "Delegación",
        "Departamento",
        "Proyecto",
    ]
    assert total(reordered["hierarchy"], "sales") == Decimal("1010")
    assert total(reordered["hierarchy"], "margin") == Decimal("750")
