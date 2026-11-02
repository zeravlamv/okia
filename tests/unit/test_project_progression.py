from datetime import date
from decimal import Decimal

import pytest

from apps.erp.sample import (
    AnalyticSlice,
    Movement,
    SaleOrder,
    ValuedDocument,
    movements,
    orders,
    purchase_deliveries,
    purchase_orders,
    sales_deliveries,
)
from apps.margins.models import MonthLedger, ProjectExpense, ProjectLife, ProjectMilestone, ProjectPurchase
from apps.margins.project_life import (
    _document_amount,
    _purchase_invoice_pending,
    _purchase_order_pending,
    bar_end,
    load_project,
    progression_figures,
    refresh_project_lives,
)
from apps.margins.snapshot import evolution_chart, monthly_bars
from apps.access.models import InformationGroup


def _milestone(billing, amount):
    return (billing, amount)


def test_progression_is_half_when_half_the_order_is_delivered():
    figures = progression_figures(
        Decimal("1000"),
        [_milestone("invoiced", Decimal("400")), _milestone("open", Decimal("100"))],
    )
    assert figures["delivered"] == Decimal("500")
    assert figures["progression"] == Decimal("50")
    assert figures["pending"] == Decimal("500")
    assert figures["invoiced"] == Decimal("400")
    assert figures["open"] == Decimal("100")


def test_progression_passes_100_and_pending_is_zero():
    figures = progression_figures(Decimal("100"), [_milestone("invoiced", Decimal("150"))])
    assert figures["progression"] == Decimal("150")
    assert figures["pending"] == Decimal("0")


def test_progression_does_not_apply_when_the_order_base_is_zero():
    figures = progression_figures(Decimal("0"), [_milestone("invoiced", Decimal("10"))])
    assert figures["progression"] is None
    assert figures["pending"] == Decimal("0")


def test_a_credit_note_reduces_the_delivered_amount():
    document = type("Document", (), {"header_base": Decimal("40"), "lines": [], "credit": True})()
    amount, missing = _document_amount(document)
    assert missing is False
    assert amount == Decimal("-40")


def test_the_bar_ends_today_until_the_order_is_covered_and_on_the_last_milestone_after_that():
    today = date(2026, 10, 30)
    assert bar_end(date(2024, 3, 10), Decimal("1000"), Decimal("500"), [date(2026, 6, 2)], today) == today
    assert bar_end(date(2024, 1, 1), Decimal("100"), Decimal("100"), [date(2024, 6, 1)], today) == date(2024, 6, 1)
    assert bar_end(date(2027, 1, 1), Decimal("100"), Decimal("0"), [], today) == date(2027, 1, 1)


@pytest.mark.django_db
def test_the_closing_entry_is_not_stored_as_an_expense():
    refresh_project_lives(
        "1",
        2024,
        orders(),
        sales_deliveries(),
        purchase_orders(),
        purchase_deliveries(),
        movements(),
    )
    codes = set(ProjectExpense.objects.values_list("account_code", flat=True))
    assert "622" in codes
    assert "129" not in codes
    life = load_project("1", "3001", list(InformationGroup.values), date(2026, 10, 30))
    assert life["expenses"] == "40,00 EUR"
    assert "04/2024" not in [month["label"] for month in life["months"]]
    assert any(row["committed"] and row["identity"] == "2024 / P / 40" and row["status"] == "Comprometido" for row in life["purchase_orders"])
    assert life["order_count_text"] == "1 pedido"
    assert load_project("2", "3001", list(InformationGroup.values), date(2026, 10, 30)) is None


@pytest.mark.django_db
def test_the_breakdown_keeps_each_line_on_its_department_and_section():
    order = SaleOrder(
        codigo_empresa="1",
        ejercicio=2026,
        serie="A",
        numero="1",
        codigo_cliente="C1",
        project="P1",
        header_base=Decimal("100"),
        tax_included=None,
        order_date=date(2026, 1, 10),
        status="Pendiente",
        department="VENT",
        section="01",
    )
    delivery = ValuedDocument(
        "1",
        2026,
        "AV",
        "1",
        Decimal("80"),
        date(2026, 2, 1),
        "",
        project="P1",
        department="VENT",
        section="01",
    )
    purchase_order = ValuedDocument(
        "1",
        2026,
        "P",
        "9",
        Decimal("10"),
        date(2026, 1, 5),
        "Pendiente",
        project="P1",
        department="COMP",
        section="ALM",
    )
    purchase = ValuedDocument(
        "1",
        2026,
        "AC",
        "9",
        Decimal("10"),
        date(2026, 2, 5),
        "",
        project="P1",
        linked_ejercicio="2026",
        linked_serie="P",
        linked_numero="9",
    )
    movement = Movement(
        "1",
        "P1",
        "640",
        "Sueldos y salarios",
        Decimal("100"),
        Decimal("0"),
        ejercicio=2026,
        movement_date=date(2026, 2, 8),
        slices=[
            AnalyticSlice(project="P1", department="VENT", section="01", amount=Decimal("30")),
            AnalyticSlice(project="P1", department="PERS", section="02", amount=Decimal("20")),
        ],
    )
    labels = {
        "department": {"VENT": "Ventas", "COMP": "Compras", "PERS": "Personal"},
        "section": {"01": "Taller", "ALM": "Almacén", "02": "Oficina"},
    }
    refresh_project_lives(
        "1",
        2026,
        [order],
        [delivery],
        [purchase_order],
        [purchase],
        [movement],
        labels,
        {"C1": "Taller Norte"},
    )
    life = load_project("1", "P1", list(InformationGroup.values), date(2026, 10, 30))
    assert life["customer"] == "C1 — Taller Norte"
    assert life["expenses"] == "50,00 EUR"
    assert life["purchases"] == "10,00 EUR"
    assert any(
        row["identity"] == "2026 / P / 9" and row["status"] == "Pedido" and row["amount"] == "10,00 EUR"
        for row in life["purchase_orders"]
    )
    assert life["order_count_text"] == "1 pedido"
    assert life["order_total"] == "10,00 EUR"
    february = next(month for month in life["months"] if month["label"] == "02/2026")
    assert february["chart_delivered"] == Decimal("80")
    assert february["chart_margin"] == Decimal("30")
    assert february["delivered_up"] == 100
    assert february["margin_up"] > 0
    assert february["margin_down"] == 0
    february_life = next(month for month in life["evolution"] if month["label"] == "02/2026")
    assert [bar["name"] for bar in february_life["series"]] == ["Albaranado", "Gastos", "Margen"]
    assert february_life["series"][0]["width"] == 100
    assert february_life["series"][0]["negative"] is False
    assert february_life["margin"] == Decimal("30")
    assert february_life["series"][-1]["amount"] == "30,00 EUR"
    MonthLedger.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=2, income_amount=Decimal("80"), expense_amount=Decimal("50")
    )
    bars = monthly_bars("1", 2026, list(InformationGroup.values))
    february_bar = next(row for row in bars if row["label"] == "feb")
    assert february_bar["number"] == 2
    assert february_bar["sales"] == Decimal("80")
    assert february_bar["purchases"] == Decimal("0")
    assert february_bar["expenses"] == Decimal("50")
    assert february_bar["margin"] == Decimal("30")
    assert february_bar["sales_up"] == 100
    chart = evolution_chart(bars)
    assert [column["label"] for column in chart["columns"]] == ["ene", "feb"]
    february_column = chart["columns"][1]
    assert "Ingresos 80,00 EUR" in february_column["title"]
    assert "Gastos 50,00 EUR" in february_column["title"]
    assert february_column["margin_y"] == "16.0"
    assert february_column["sales_y"] == "16.0"
    assert february_column["sales_height"] == "230.0"
    assert february_column["purchase_height"] == "0.0"
    assert february_column["margin_height"] == "86.2"
    assert february_column["expense_height"] == "143.8"
    assert chart["peak_text"] == "80,00 EUR"
    assert life["deviation"] == "-20,00 EUR"
    assert life["net_margin"] == "30,00 EUR"
    rows = {row["department"]: row for row in life["slices"]}
    assert "COMP — Compras" not in rows
    assert rows["VENT — Ventas"]["expenses"] == "30,00 EUR"
    assert rows["PERS — Personal"]["expenses"] == "20,00 EUR"
    assert life["pending"] == "20,00 EUR"
    assert life["open"] == "0,00 EUR"
    assert life["purchase_pending"] == "0,00 EUR"
    assert life["purchase_invoice_pending"] == "0,00 EUR"
    vent_origins = rows["VENT — Ventas"]["origins"]
    assert vent_origins == [
        {"date": "08/02/2026", "origin": "640 — Sueldos y salarios", "amount": "30,00 EUR"},
    ]
    assert rows["PERS — Personal"]["origins"] == [
        {"date": "08/02/2026", "origin": "640 — Sueldos y salarios", "amount": "20,00 EUR"},
    ]


def test_purchase_pending_is_the_uncovered_order_and_blank_billing_stays_unknown():
    order = type("Row", (), {})()
    order.kind = "committed"
    order.ejercicio = 2026
    order.serie = "P"
    order.numero = "1"
    order.amount = Decimal("100")
    order.linked_ejercicio = ""
    order.linked_serie = ""
    order.linked_numero = ""
    delivery = type("Row", (), {})()
    delivery.kind = "delivery"
    delivery.ejercicio = 2026
    delivery.serie = "AC"
    delivery.numero = "9"
    delivery.amount = Decimal("40")
    delivery.linked_ejercicio = "2026"
    delivery.linked_serie = "P"
    delivery.linked_numero = "1"
    delivery.billing = ""
    assert _purchase_order_pending([order, delivery]) == Decimal("60")
    assert _purchase_invoice_pending([delivery]) is None
    delivery.billing = "open"
    assert _purchase_invoice_pending([delivery]) == Decimal("40")
    delivery.amount = Decimal("120")
    assert _purchase_order_pending([order, delivery]) == Decimal("0")
    delivery.billing = "invoiced"
    assert _purchase_invoice_pending([delivery]) == Decimal("0")


@pytest.mark.django_db
def test_a_covered_order_still_reaches_a_cost_in_a_later_exercise():
    life = ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto="CRUCE",
        order_date=date(2026, 1, 15),
        order_base=Decimal("100"),
    )
    ProjectMilestone.objects.create(
        life=life,
        ejercicio=2026,
        serie="A",
        numero="1",
        delivery_date=date(2026, 1, 20),
        amount=Decimal("100"),
        billing="invoiced",
    )
    ProjectPurchase.objects.create(
        life=life,
        kind="delivery",
        ejercicio=2027,
        serie="AC",
        numero="1",
        document_date=date(2027, 3, 4),
        amount=Decimal("30"),
    )
    ProjectExpense.objects.create(
        life=life,
        account_code="622",
        account_name="Reparaciones",
        movement_date=date(2027, 3, 18),
        amount=Decimal("5"),
    )
    shown = load_project("1", "CRUCE", list(InformationGroup.values), date(2026, 10, 31))
    labels = [month["label"] for month in shown["months"]]
    assert shown["start"] == "15/01/2026"
    assert shown["end"] == "18/03/2027"
    assert "01/2026" in labels
    assert "03/2027" in labels
    march = next(month for month in shown["months"] if month["label"] == "03/2027")
    assert march["chart_purchases"] == Decimal("0")
    assert march["chart_expenses"] == Decimal("5")
    evolution = {month["label"]: month for month in shown["evolution"]}
    assert evolution["01/2026"]["margin"] == Decimal("100")
    assert evolution["02/2026"]["margin"] == Decimal("100")
    assert evolution["03/2027"]["margin"] == Decimal("95")
    assert evolution["03/2027"]["series"][-1]["amount"] == "95,00 EUR"
    assert evolution["03/2027"]["series"][-1]["negative"] is False


@pytest.mark.django_db
def test_dashboard_expenses_are_the_book_minus_the_project_purchases():
    life = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P1", order_date=date(2026, 2, 1))
    ProjectMilestone.objects.create(
        life=life, ejercicio=2026, serie="AV", numero="1", delivery_date=date(2026, 2, 4), amount=Decimal("80"), billing=""
    )
    ProjectExpense.objects.create(
        life=life, account_code="602000", account_name="Compras", movement_date=date(2026, 2, 8), amount=Decimal("50")
    )
    MonthLedger.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        mes=2,
        income_count=1,
        income_amount=Decimal("110"),
        expense_count=2,
        expense_amount=Decimal("80"),
    )
    february = next(row for row in monthly_bars("1", 2026, list(InformationGroup.values)) if row["label"] == "feb")
    assert february["sales"] == Decimal("110")
    assert february["purchases"] == Decimal("50")
    assert february["expenses"] == Decimal("30")
    assert february["margin"] == Decimal("30")
    assert february["sales"] == february["purchases"] + february["expenses"] + february["margin"]
    assert february["cumulative_sales_text"] == "110,00 EUR"
    assert february["cumulative_margin_text"] == "30,00 EUR"


@pytest.mark.django_db
def test_each_month_carries_the_total_from_january():
    MonthLedger.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=1, income_amount=Decimal("10"), expense_amount=Decimal("4")
    )
    MonthLedger.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=2, income_amount=Decimal("3"), expense_amount=Decimal("1")
    )
    bars = {row["label"]: row for row in monthly_bars("1", 2026, list(InformationGroup.values))}
    assert bars["ene"]["cumulative_sales_text"] == "10,00 EUR"
    assert bars["ene"]["cumulative_expenses_text"] == "4,00 EUR"
    assert bars["ene"]["cumulative_margin_text"] == "6,00 EUR"
    assert bars["feb"]["cumulative_sales_text"] == "13,00 EUR"
    assert bars["feb"]["cumulative_purchases_text"] == "0,00 EUR"
    assert bars["feb"]["cumulative_expenses_text"] == "5,00 EUR"
    assert bars["feb"]["cumulative_margin_text"] == "8,00 EUR"
    assert bars["dic"]["cumulative_sales_text"] == "13,00 EUR"
    assert bars["dic"]["cumulative_margin_text"] == "8,00 EUR"
