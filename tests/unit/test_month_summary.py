from datetime import date
from decimal import Decimal

import pytest

from apps.access.models import InformationGroup
from apps.margins.models import (
    BookExpense,
    MonthLedger,
    ProjectDocumentLine,
    ProjectExpense,
    ProjectIncome,
    ProjectLife,
    ProjectMilestone,
    ProjectPurchase,
)
from apps.margins.month_summary import chosen_month, load_month_summary, month_board


def test_an_invalid_month_falls_back_to_today_or_january():
    today = date(2026, 10, 31)
    assert chosen_month("3", 2024, today) == 3
    assert chosen_month("99", 2026, today) == 10
    assert chosen_month(None, 2024, today) == 1


@pytest.mark.django_db
def test_march_sums_whole_fiches_and_leaves_april_out():
    _project("1", "MAR1", date(2026, 3, 2), Decimal("100"), delivered=Decimal("80"), expenses=Decimal("10"))
    _project("1", "MAR2", date(2026, 3, 18), Decimal("40"), delivered=Decimal("40"), expenses=Decimal("5"))
    _project("1", "ABR1", date(2026, 4, 4), Decimal("999"), delivered=Decimal("1"), expenses=Decimal("1"))
    _project("2", "OTRA", date(2026, 3, 2), Decimal("7"), delivered=Decimal("7"), expenses=Decimal("1"))

    march = load_month_summary("1", 2026, 3)

    assert [row["code"] for row in march["rows"]] == ["MAR1", "MAR2"]
    assert march["count"] == 2
    assert march["totals"]["order"] == Decimal("140")
    assert march["totals"]["deliveries"] == Decimal("120")
    assert march["totals"]["expenses"] == Decimal("15")
    assert march["margin"] == Decimal("105")
    assert march["sale_pending"] == Decimal("20")
    assert march["margin_percent"] == Decimal("87.5")


@pytest.mark.django_db
def test_a_fiche_in_two_months_is_counted_whole_in_each_and_named():
    life = _project(
        "1",
        "DOS",
        date(2026, 1, 10),
        Decimal("50"),
        delivered=Decimal("20"),
        expenses=Decimal("4"),
        orders=((date(2026, 1, 10), "2026 / T / 1"), (date(2026, 3, 10), "2026 / T / 2")),
    )
    assert life.order_base == Decimal("50")

    january = load_month_summary("1", 2026, 1)
    march = load_month_summary("1", 2026, 3)

    assert january["rows"][0]["order"] == march["rows"][0]["order"] == Decimal("50")
    assert january["rows"][0]["other_months"] == ["marzo"]
    assert march["rows"][0]["other_months"] == ["enero"]
    assert january["count"] == march["count"] == 1


@pytest.mark.django_db
def test_two_orders_in_the_same_month_make_one_row():
    _project(
        "1",
        "UNO",
        date(2026, 3, 1),
        Decimal("100"),
        orders=(
            (date(2026, 3, 1), "2026 / T / 1", Decimal("60")),
            (date(2026, 3, 20), "2026 / T / 2", Decimal("40")),
        ),
    )
    march = load_month_summary("1", 2026, 3)
    assert march["count"] == 1
    assert march["totals"]["order"] == Decimal("100")


@pytest.mark.django_db
def test_the_purchase_delivery_does_not_reduce_the_margin():
    life = _project("1", "COSTE", date(2026, 3, 1), Decimal("100"), delivered=Decimal("100"), expenses=Decimal("10"))
    ProjectPurchase.objects.create(
        life=life,
        kind="delivery",
        ejercicio=2026,
        serie="T",
        numero="9",
        amount=Decimal("50"),
        document_date=date(2026, 5, 1),
    )
    march = load_month_summary("1", 2026, 3)
    may = load_month_summary("1", 2026, 5)
    assert march["totals"]["purchase_deliveries"] == Decimal("0")
    assert may["totals"]["purchase_deliveries"] == Decimal("50")
    assert march["totals"]["expenses"] == Decimal("10")
    assert march["margin"] == Decimal("90")


@pytest.mark.django_db
def test_purchase_pending_is_what_each_order_still_lacks():
    life = _project("1", "COMP", date(2026, 3, 1), Decimal("10"))
    ProjectPurchase.objects.create(
        life=life,
        kind="order",
        ejercicio=2026,
        serie="T",
        numero="1",
        amount=Decimal("30"),
        document_date=date(2026, 3, 2),
    )
    ProjectPurchase.objects.create(
        life=life,
        kind="delivery",
        ejercicio=2026,
        serie="A",
        numero="1",
        amount=Decimal("10"),
        linked_ejercicio="2026",
        linked_serie="T",
        linked_numero="1",
    )
    ProjectPurchase.objects.create(
        life=life,
        kind="order",
        ejercicio=2026,
        serie="T",
        numero="2",
        amount=Decimal("10"),
        document_date=date(2026, 3, 3),
    )
    ProjectPurchase.objects.create(
        life=life,
        kind="delivery",
        ejercicio=2026,
        serie="A",
        numero="2",
        amount=Decimal("10"),
        linked_ejercicio="2026",
        linked_serie="T",
        linked_numero="2",
    )
    march = load_month_summary("1", 2026, 3)
    assert march["purchase_pending"] == Decimal("20")


@pytest.mark.django_db
def test_a_blank_amount_is_not_turned_into_zero():
    life = _project("1", "HUECO", date(2026, 3, 1), Decimal("80"), delivered=Decimal("80"))
    ProjectMilestone.objects.create(
        life=life, ejercicio=2026, serie="T", numero="2", amount=None, billing="unknown"
    )
    march = load_month_summary("1", 2026, 3)
    assert march["incomplete"] is True
    assert march["totals"]["deliveries"] == Decimal("80")


@pytest.mark.django_db
def test_a_delivery_created_in_march_of_a_february_order_enters_march():
    life = _project(
        "1",
        "FEB",
        date(2026, 2, 10),
        Decimal("100"),
        delivered=Decimal("40"),
        expenses=Decimal("10"),
    )
    ProjectMilestone.objects.filter(life=life).update(delivery_date=date(2026, 3, 4))

    february = load_month_summary("1", 2026, 2)
    march = load_month_summary("1", 2026, 3)

    assert february["totals"]["order"] == Decimal("100")
    assert february["totals"]["deliveries"] == Decimal("0")
    assert february["sale_pending"] == Decimal("60")
    assert february["totals"]["expenses"] == Decimal("10")
    assert march["count"] == 0
    assert march["totals"]["order"] == Decimal("0")
    assert march["totals"]["deliveries"] == Decimal("40")
    assert march["totals"]["expenses"] == Decimal("0")
    assert march["analytics"]["income_pending"] is False


@pytest.mark.django_db
def test_group_seven_stays_pending_until_it_is_stored():
    life = _project("1", "ANA", date(2026, 3, 1), Decimal("20"), expenses=Decimal("6"))
    march = load_month_summary("1", 2026, 3)
    assert march["analytics"]["expenses"] == Decimal("6")
    assert march["analytics"]["income_pending"] is True
    assert march["analytics"]["income"] is None

    life.income_stored = True
    life.save(update_fields=["income_stored"])
    ProjectIncome.objects.create(life=life, account_code="700", account_name="Ventas", amount=Decimal("12"))
    stored = load_month_summary("1", 2026, 3)
    assert stored["analytics"]["income"] == Decimal("12")
    assert stored["analytics"]["margin"] == Decimal("6")
    assert stored["analytics"]["income_pending"] is False


@pytest.mark.django_db
def test_group_seven_is_stored_from_the_analytical_line():
    from apps.erp.sample import AnalyticSlice, Movement
    from apps.margins.project_life import _store_project_income

    life = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="ANA", order_date=date(2026, 3, 1))
    income = Movement(
        "1",
        "",
        "700000",
        "Ventas",
        Decimal("0"),
        Decimal("30"),
        movement_date=date(2026, 4, 2),
        slices=[AnalyticSlice(project="ANA", amount=Decimal("30"))],
    )
    expense = Movement("1", "ANA", "600000", "Compras", Decimal("5"), Decimal("0"))
    closing = Movement(
        "1",
        "ANA",
        "700000",
        "Ventas",
        Decimal("0"),
        Decimal("9"),
        comment="Asiento de cierre ejercicio",
    )
    _store_project_income("1", {"ANA"}, [income, expense, closing], {})
    life.refresh_from_db()
    assert life.income_stored is True
    stored = ProjectIncome.objects.get()
    assert stored.amount == Decimal("30")
    assert stored.account_code == "700000"


@pytest.mark.django_db
def test_a_fiche_without_order_lines_uses_its_start_date():
    ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto="VIEJA",
        order_date=date(2026, 3, 8),
        order_base=Decimal("15"),
    )
    assert load_month_summary("1", 2026, 3)["rows"][0]["code"] == "VIEJA"
    assert load_month_summary("1", 2026, 4)["empty"] is True


@pytest.mark.django_db
def test_the_month_board_uses_group_seven_minus_group_six():
    life = ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto="ENE",
        order_date=date(2026, 1, 4),
        order_base=Decimal("100"),
    )
    ProjectExpense.objects.create(
        life=life,
        account_code="602000",
        movement_date=date(2026, 1, 8),
        amount=Decimal("20"),
    )
    ProjectExpense.objects.create(
        life=life,
        account_code="622000",
        movement_date=date(2026, 1, 9),
        amount=Decimal("7"),
    )
    BookExpense.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        account_code="480000",
        account_name="Gastos anticipados",
        movement_date=date(2026, 1, 10),
        amount=Decimal("-10"),
    )
    MonthLedger.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        mes=1,
        income_count=2,
        income_amount=Decimal("80"),
        expense_count=3,
        expense_amount=Decimal("50"),
    )

    board = month_board("1", 2026, 1, list(InformationGroup))

    assert board["cards"]["accounted_purchases"]["amount"] == Decimal("20")
    assert board["cards"]["expenses"]["amount"] == Decimal("40")
    assert board["cards"]["income"]["amount"] == Decimal("80")
    assert board["cards"]["margin"] == Decimal("20")
    assert month_board("1", 2026, 2, list(InformationGroup))["empty"] is True


def _project(company, code, when, order_base, delivered=None, expenses=None, orders=None):
    life = ProjectLife.objects.create(
        codigo_empresa=company,
        codigo_proyecto=code,
        order_date=when,
        order_base=order_base,
    )
    documents = orders or ((when, f"{when.year} / T / {code}", order_base),)
    for item in documents:
        moment, key, amount = item if len(item) == 3 else (item[0], item[1], order_base)
        ProjectDocumentLine.objects.create(
            life=life,
            kind="sale_order",
            document_key=key,
            position=0,
            amount=amount,
            line_date=moment,
        )
    if delivered is not None:
        ProjectMilestone.objects.create(
            life=life,
            ejercicio=when.year,
            serie="T",
            numero=code,
            delivery_date=when,
            amount=delivered,
            billing="invoiced",
        )
    if expenses is not None:
        ProjectExpense.objects.create(
            life=life,
            account_code="622",
            movement_date=when,
            amount=expenses,
        )
    return life
