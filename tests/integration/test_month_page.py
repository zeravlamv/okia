from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.access.demo import ensure_demo
from apps.access.models import CompanyAccess, InformationGroup, Profile, ProfilePermission
from apps.margins.dashboard import analytical_dimensions
from apps.margins.models import (
    AnalyticalSummary,
    DashboardSnapshot,
    MonthLedger,
    PeriodClosure,
    ProjectDocumentLine,
    ProjectExpense,
    ProjectLife,
    ProjectPurchase,
    ProjectMilestone,
    TreeIncome,
)


@pytest.mark.django_db
def test_march_summary_lists_its_projects_and_opens_the_fiche():
    ensure_demo()
    _fiche("MAR1", date(2026, 3, 2), Decimal("100"), Decimal("80"), Decimal("10"))
    _fiche("MAR2", date(2026, 3, 18), Decimal("40"), Decimal("40"), Decimal("5"))
    _fiche("ABR1", date(2026, 4, 4), Decimal("999"), Decimal("1"), Decimal("1"))
    ProjectExpense.objects.create(
        life=ProjectLife.objects.get(codigo_proyecto="MAR1"),
        account_code="602000",
        movement_date=date(2026, 3, 5),
        amount=Decimal("12"),
    )
    MonthLedger.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        mes=3,
        income_count=1,
        income_amount=Decimal("200"),
        expense_count=2,
        expense_amount=Decimal("50"),
    )
    client = Client()
    client.login(username="demo", password="demo")

    body = client.get("/resumen/?mes=3").content.decode()

    assert "Resumen mes" in body
    assert "MAR1" not in body
    assert "ABR1" not in body
    assert "999,00 EUR" not in body
    assert "Pedidos de venta" in body
    assert "Albaranes de venta" in body
    assert "Pedidos de compra" in body
    assert "Albaranes de compra" in body
    assert "140,00 EUR" in body
    assert "120,00 EUR" in body
    assert "Ingresos" in body
    assert "200,00 EUR" in body
    assert "Compras" in body
    assert "12,00 EUR" in body
    assert "Gastos" in body
    assert "38,00 EUR" in body
    assert "<h2>Margen</h2>" in body
    assert "150,00 EUR" in body
    assert "75,00 %" in body
    assert "Grupo 7 menos el grupo 6." in body
    assert 'data-kind="pedido"' in body
    assert 'data-kind="albaran"' in body
    assert 'data-kind="pedido_compra"' not in body
    assert 'data-kind="albaran_compra"' not in body
    assert 'data-kind="ingreso"' in body
    assert 'data-kind="compra"' in body
    assert 'data-kind="gasto"' in body
    assert 'data-kind="margen"' in body
    assert 'data-month="3"' in body
    assert "Ficha de proyecto" in body
    assert "Mostrar gráfica" in body
    assert "acumulad" not in body
    assert 'id="hierarchy"' in body
    assert "Totales del mes" not in body
    assert "Resultado del mes" not in body
    assert "Analítica" not in body
    assert "month-projects" not in body


@pytest.mark.django_db
def test_a_profile_without_expenses_does_not_see_them_or_the_margin():
    user = get_user_model().objects.create_user("sin-gasto", "", "Clave-inicial-2026")
    profile = Profile.objects.create(user=user)
    for group in InformationGroup.values:
        if group == InformationGroup.MOVIMIENTOS:
            continue
        ProfilePermission.objects.create(profile=profile, group=group)
    CompanyAccess.objects.create(user=user, codigo_empresa="1")
    _fiche("MAR1", date(2026, 3, 2), Decimal("100"), Decimal("80"), Decimal("10"))
    client = Client()
    client.login(username="sin-gasto", password="Clave-inicial-2026")

    body = client.get("/resumen/?mes=3").content.decode()

    assert "100,00 EUR" in body
    assert "Ingresos" not in body
    assert "Compras" not in body
    assert "Gastos" not in body
    assert "Analítica" not in body
    assert "<h2>Margen</h2>" not in body
    assert "10,00 EUR" not in body
    assert "105,00 EUR" not in body


@pytest.mark.django_db
def test_an_empty_month_does_not_invent_zero_totals():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")

    body = client.get("/resumen/?mes=2").content.decode()

    assert "No hay proyectos calculados" in body
    assert "Actualizar" in body
    assert "0,00 EUR" not in body


@pytest.mark.django_db
def test_a_closed_month_stays_closed_when_it_is_opened():
    user = ensure_demo()
    PeriodClosure.objects.create(codigo_empresa="1", ejercicio=2026, mes=2, cerrado=True, changed_by=user)
    client = Client()
    client.login(username="demo", password="demo")

    body = client.get("/resumen/?mes=2").content.decode()

    assert "Este mes está cerrado" in body
    assert "última ficha guardada" in body
    assert "Este mes está abierto" not in body
    assert 'id="month-refresh"' not in body
    assert PeriodClosure.objects.get(codigo_empresa="1", ejercicio=2026, mes=2).cerrado is True


@pytest.mark.django_db
def test_an_open_month_says_so_and_offers_its_own_refresh():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")

    body = client.get("/resumen/?mes=3").content.decode()
    done = client.get("/resumen/?mes=3&listo=1").content.decode()

    assert "Este mes está abierto" in body
    assert "Se están recalculando sus cifras." in body
    assert 'id="month-refresh"' in body
    assert 'data-month="3"' in body
    assert "Este mes está abierto" in done
    assert 'id="month-refresh"' not in done


@pytest.mark.django_db
def test_refreshing_an_open_month_leaves_the_other_months_and_a_retained_project():
    from apps.margins.month_refresh import refresh_month

    user = ensure_demo()
    MonthLedger.objects.create(codigo_empresa="1", ejercicio=2026, mes=2, income_amount=Decimal("77"))
    kept = ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto="1001",
        order_date=date(2026, 2, 1),
        order_base=Decimal("15"),
        lines_stored=True,
    )
    ProjectDocumentLine.objects.create(
        life=kept,
        kind="sale_order",
        document_key="2026 / B / VIEJO",
        position=0,
        line_date=date(2026, 2, 1),
        amount=Decimal("15"),
    )
    ProjectMilestone.objects.create(
        life=kept,
        ejercicio=2026,
        serie="T",
        numero="9",
        delivery_date=date(2026, 3, 4),
        amount=Decimal("5"),
        billing="unknown",
    )
    PeriodClosure.objects.create(codigo_empresa="1", ejercicio=2026, mes=2, cerrado=True, changed_by=user)
    other = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="ZED", lines_stored=True)
    ProjectDocumentLine.objects.create(
        life=other,
        kind="sale_order",
        document_key="2026 / Z / 1",
        position=0,
        line_date=date(2026, 3, 8),
        amount=Decimal("4"),
    )

    refresh_month("1", 2026, 3)

    assert MonthLedger.objects.get(codigo_empresa="1", ejercicio=2026, mes=2).income_amount == Decimal("77")
    assert ProjectMilestone.objects.filter(life=kept, numero="9", amount=Decimal("5")).exists()
    assert ProjectDocumentLine.objects.filter(document_key="2026 / B / VIEJO").exists()
    assert not ProjectDocumentLine.objects.filter(document_key="2026 / A / 1001").exists()
    assert not ProjectDocumentLine.objects.filter(document_key="2026 / Z / 1").exists()
    assert not ProjectDocumentLine.objects.filter(document_key="2026 / B / 2001").exists()


@pytest.mark.django_db
def test_refreshing_a_closed_month_keeps_the_saved_figures():
    from apps.margins.month_refresh import refresh_month

    user = ensure_demo()
    MonthLedger.objects.create(codigo_empresa="1", ejercicio=2026, mes=3, income_amount=Decimal("8"))
    PeriodClosure.objects.create(codigo_empresa="1", ejercicio=2026, mes=3, cerrado=True, changed_by=user)

    refresh_month("1", 2026, 3)

    assert MonthLedger.objects.get(codigo_empresa="1", ejercicio=2026, mes=3).income_amount == Decimal("8")
    assert not ProjectDocumentLine.objects.filter(document_key="2026 / A / 1001").exists()


@pytest.mark.django_db
def test_an_open_month_stores_only_that_months_sale_order():
    from apps.margins.month_refresh import refresh_month

    ensure_demo()
    MonthLedger.objects.create(codigo_empresa="1", ejercicio=2026, mes=2, income_amount=Decimal("77"))

    refresh_month("1", 2026, 3)

    stored = ProjectDocumentLine.objects.get(kind="sale_order", document_key="2026 / A / 1001", position=0)
    assert stored.amount == Decimal("1000")
    assert stored.line_date == date(2026, 3, 1)
    assert ProjectDocumentLine.objects.filter(document_key="2026 / A / 1001", position=1, description="Servicio").exists()
    assert not ProjectDocumentLine.objects.filter(document_key="2026 / B / 2001").exists()
    assert MonthLedger.objects.get(codigo_empresa="1", ejercicio=2026, mes=2).income_amount == Decimal("77")


@pytest.mark.django_db
def test_february_keeps_the_running_total_and_that_months_tree():
    ensure_demo()
    MonthLedger.objects.create(codigo_empresa="1", ejercicio=2026, mes=1, income_count=1, income_amount=Decimal("10"))
    MonthLedger.objects.create(codigo_empresa="1", ejercicio=2026, mes=2, income_count=1, income_amount=Decimal("20"))
    titles = [item[1] for item in list(analytical_dimensions())[:4]]
    snapshot = DashboardSnapshot.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        tree_income_stored=True,
        titulo_1=titles[0],
        titulo_2=titles[1],
        titulo_3=titles[2],
        titulo_4=titles[3],
    )
    project_level = titles.index("Proyecto") + 1
    AnalyticalSummary.objects.create(
        snapshot=snapshot,
        **{f"nivel_{project_level}": "230309 — PRUEBAS"},
    )
    for moment, amount in ((date(2026, 1, 15), Decimal("7")), (date(2026, 2, 2), Decimal("9"))):
        TreeIncome.objects.create(
            codigo_empresa="1",
            ejercicio=2026,
            movement_date=moment,
            amount=amount,
            nivel_1="01 — TECH",
            nivel_2="WAYN",
            nivel_3="2008 — COMERCIAL",
            nivel_4="Sin dato",
        )
    client = Client()
    client.login(username="demo", password="demo")

    body = client.get("/resumen/?mes=2").content.decode()

    assert "20,00 EUR" in body
    assert "30,00 EUR" not in body
    assert "acumulad" not in body
    assert "9,00 EUR" in body
    assert "7,00 EUR" not in body
    assert "230309" in body
    assert 'data-income-month="2"' in body


@pytest.mark.django_db
def test_a_sale_order_amount_lists_the_order_and_its_lines():
    ensure_demo()
    life = _fiche("MAR1", date(2026, 3, 2), Decimal("100"), Decimal("80"), Decimal("10"))
    life.lines_stored = True
    life.customer_name = "Cliente Uno"
    life.save(update_fields=["lines_stored", "customer_name"])
    ProjectDocumentLine.objects.create(
        life=life,
        kind="sale_order",
        document_key="2026 / T / MAR1",
        position=1,
        description="Malla",
        amount=Decimal("100"),
    )
    ProjectPurchase.objects.create(
        life=life,
        kind="order",
        ejercicio=2026,
        serie="P",
        numero="9",
        document_date=date(2026, 3, 2),
        amount=Decimal("40"),
        supplier_name="Taller",
    )
    ProjectDocumentLine.objects.create(
        life=life,
        kind="purchase_order",
        document_key="2026 / P / 9",
        position=1,
        description="Tornillo",
        amount=Decimal("40"),
    )
    client = Client()
    client.login(username="demo", password="demo")

    detail = client.get("/resumen/documentos/", {"mes": "3", "tipo": "pedido"})
    lines = client.get("/evolucion/lineas/", {"proyecto": "MAR1", "albaran": "2026 / T / MAR1", "tipo": "sale_order"})
    purchase = client.get("/resumen/documentos/", {"mes": "3", "tipo": "pedido_compra"})
    purchase_lines = client.get(
        "/evolucion/lineas/",
        {"proyecto": "MAR1", "albaran": "2026 / P / 9", "tipo": "purchase_order"},
    )
    delivery = client.get("/resumen/documentos/", {"mes": "3", "tipo": "albaran"})

    assert detail.status_code == 200
    body = detail.json()
    assert body["title"] == "Pedidos de venta de marzo de 2026"
    assert body["source"] == "CabeceraPedidoCliente"
    assert body["total"] == "100,00 EUR"
    assert body["rows"][0]["document"] == "2026 / T / MAR1"
    assert body["rows"][0]["lineKind"] == "sale_order"
    assert body["rows"][0]["cells"][2] == "2026 / T / MAR1"
    assert lines.status_code == 200
    opened = lines.json()
    assert opened["rows"] == [["Malla", "100,00 EUR"]]
    assert opened["total"] == "100,00 EUR"
    assert purchase.json()["total"] == "40,00 EUR"
    assert purchase.json()["rows"][0]["lineKind"] == "purchase_order"
    assert purchase_lines.json()["rows"] == [["Tornillo", "40,00 EUR"]]
    assert delivery.json()["rows"][0]["document"] == "2026 / T / MAR1"
    assert delivery.json()["total"] == "80,00 EUR"
    assert client.get("/resumen/documentos/", {"mes": "3", "tipo": "margen"}).status_code == 404


def _fiche(code, when, order_base, delivered, expenses):
    life = ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto=code,
        order_date=when,
        order_base=order_base,
    )
    ProjectDocumentLine.objects.create(
        life=life,
        kind="sale_order",
        document_key=f"2026 / T / {code}",
        position=0,
        amount=order_base,
        line_date=when,
    )
    ProjectMilestone.objects.create(
        life=life,
        ejercicio=2026,
        serie="T",
        numero=code,
        delivery_date=when,
        amount=delivered,
        billing="invoiced",
    )
    ProjectExpense.objects.create(
        life=life,
        account_code="622",
        movement_date=when,
        amount=expenses,
    )
    return life
