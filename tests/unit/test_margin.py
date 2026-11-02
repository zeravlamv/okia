from datetime import date
from decimal import Decimal

from apps.erp.sample import Movement, PurchaseLine, SaleLine, SaleOrder, movements, orders, purchases
from apps.margins.services import build_report, ledger_total, sale_price


def test_header_base_ignores_tax_and_lines():
    order = orders()[0]
    price, incomplete = sale_price(order)
    assert price == Decimal("1000")
    assert incomplete is False
    assert order.tax_included == Decimal("1210")


def test_company_margin_uses_the_accounting_cost():
    report = build_report("1", 2026, orders(), purchases(), movements())
    closed = {row["numero"]: row for row in report["closed"]}
    row = closed["1001"]
    assert row["price"] == Decimal("1000")
    assert row["cost"] == Decimal("50")
    assert row["margin"] == Decimal("750")
    assert row["income"] == Decimal("800")
    assert row["percent"] == Decimal("93.75")
    assert "1002" not in closed
    assert "9999" not in {item["price"] for item in report["closed"]}


def test_a_purchase_line_from_another_year_does_not_enter_the_cost():
    report = build_report("1", 2026, orders(), purchases(), movements())
    row = next(item for item in report["closed"] if item["numero"] == "1001")
    assert row["cost"] == Decimal("50")


def test_zero_price_has_no_percentage():
    report = build_report("1", 2026, orders(), purchases(), movements())
    row = next(item for item in report["closed"] if item["numero"] == "1003")
    assert row["price"] == Decimal("0")
    assert row["margin"] == Decimal("0")
    assert row["percent"] is None


def test_missing_line_amount_marks_the_result_incomplete():
    report = build_report("1", 2026, orders(), purchases(), movements())
    row = next(item for item in report["closed"] if item["numero"] == "1004")
    assert row["price"] == Decimal("10")
    assert row["incomplete"] is True


def test_shared_project_is_not_a_closed_margin():
    report = build_report("1", 2026, orders(), purchases(), movements())
    numbers = {row["numero"] for row in report["closed"]}
    assert "2001" not in numbers
    assert "2002" not in numbers
    assert report["pending_count"] == 2


def test_order_dated_outside_the_year_is_excluded_but_its_project_cost_rule_holds():
    report = build_report("1", 2026, orders(), purchases(), movements())
    assert "1005" not in {row["numero"] for row in report["closed"]}


def test_other_company_does_not_change_the_margin():
    own = build_report("1", 2026, orders(), purchases(), movements())
    other = build_report("2", 2026, orders(), purchases(), movements())
    own_row = next(row for row in own["closed"] if row["numero"] == "1001")
    other_row = next(row for row in other["closed"] if row["numero"] == "1001")
    assert own_row["price"] == Decimal("1000")
    assert other_row["price"] == Decimal("9999")
    assert other_row["income"] == Decimal("9999")


def test_unassigned_purchase_is_not_added_to_a_closed_order():
    extra = purchases() + [
        PurchaseLine("1", "1001", None, "Sin precio", date(2026, 3, 3)),
    ]
    report = build_report("1", 2026, orders(), extra, movements())
    row = next(item for item in report["closed"] if item["numero"] == "1001")
    assert row["incomplete"] is False
    assert row["cost"] == Decimal("50")


def test_vat_account_is_neither_cost_nor_income():
    extra = movements() + [
        Movement("1", "1003", "472", "IVA soportado", Decimal("99"), Decimal("0")),
    ]
    report = build_report("1", 2026, orders(), purchases(), extra)
    row = next(item for item in report["closed"] if item["numero"] == "1003")
    assert row["cost"] == Decimal("0")
    assert row["income"] == Decimal("0")


def test_sale_without_header_uses_line_bases_only():
    order = SaleOrder(
        codigo_empresa="1",
        ejercicio=2026,
        serie="Z",
        numero="1",
        codigo_cliente="C",
        project="1",
        header_base=None,
        tax_included=Decimal("99"),
        order_date=date(2026, 1, 1),
        status="Pendiente",
        lines=[SaleLine(Decimal("5"), "A"), SaleLine(Decimal("7"), "B")],
    )
    price, incomplete = sale_price(order)
    assert price == Decimal("12")
    assert incomplete is False


def test_the_closing_entry_is_neither_income_nor_expense():
    rows = [
        Movement("1", None, "700", "Ventas", Decimal("0"), Decimal("100"), ejercicio=2026),
        Movement(
            "1",
            None,
            "700",
            "Ventas",
            Decimal("0"),
            Decimal("500"),
            ejercicio=2026,
            comment="CIERRE EJERCICIO",
        ),
        Movement("1", None, "640", "Sueldos y salarios personal", Decimal("40"), Decimal("0"), ejercicio=2026),
        Movement(
            "1",
            None,
            "640",
            "Sueldos y salarios personal",
            Decimal("0"),
            Decimal("40"),
            ejercicio=2026,
            comment="CIERRE EJERCICIO",
        ),
    ]
    assert ledger_total("1", 2026, rows, "income") == {"count": 1, "amount": Decimal("100")}
    assert ledger_total("1", 2026, rows, "expense") == {"count": 1, "amount": Decimal("40")}
