from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.access.models import InformationGroup
from apps.erp.sample import SaleOrder
from apps.margins.models import (
    AnalyticalSummary,
    DashboardSnapshot,
    MonthLedger,
    PeriodClosure,
    ProjectExerciseShare,
    ProjectExpense,
    ProjectLife,
)
from apps.margins.project_life import refresh_project_lives
from apps.margins.snapshot import load_dashboard, refresh_snapshot


def _order(project, number, month, amount):
    return SaleOrder(
        codigo_empresa="1",
        ejercicio=2026,
        serie="A",
        numero=number,
        codigo_cliente="C1",
        project=project,
        header_base=Decimal(amount),
        tax_included=None,
        order_date=date(2026, month, 1),
        status="Pendiente",
    )


@pytest.mark.django_db
def test_a_closed_month_keeps_its_fiche_and_an_open_month_is_refreshed():
    user = get_user_model().objects.create_user("cierra", "", "Clave-inicial-2026")
    march = _order("MAR", "1", 3, "100")
    february = _order("FEB", "2", 2, "50")
    refresh_project_lives("1", 2026, [march, february], [], [], [], [])
    kept = ProjectLife.objects.get(codigo_proyecto="MAR")
    stamp = kept.updated_at
    PeriodClosure.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=3, cerrado=True, changed_by=user
    )
    march.header_base = Decimal("999")
    february.header_base = Decimal("70")
    refresh_project_lives("1", 2026, [march, february], [], [], [], [])
    kept.refresh_from_db()
    assert kept.order_base == Decimal("100")
    assert kept.updated_at == stamp
    assert ProjectLife.objects.get(codigo_proyecto="FEB").order_base == Decimal("70")


@pytest.mark.django_db
def test_a_project_in_a_closed_month_and_an_open_month_is_not_refreshed():
    user = get_user_model().objects.create_user("cierra", "", "Clave-inicial-2026")
    march = _order("MIX", "1", 3, "10")
    february = _order("MIX", "2", 2, "20")
    refresh_project_lives("1", 2026, [march, february], [], [], [], [])
    life = ProjectLife.objects.get(codigo_proyecto="MIX")
    stamp = life.updated_at
    PeriodClosure.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=3, cerrado=True, changed_by=user
    )
    march.header_base = Decimal("99")
    february.header_base = Decimal("99")
    refresh_project_lives("1", 2026, [march, february], [], [], [], [])
    life.refresh_from_db()
    assert life.order_base == Decimal("30")
    assert life.updated_at == stamp


@pytest.mark.django_db
def test_a_month_outside_the_year_is_rejected():
    user = get_user_model().objects.create_user("cierra", "", "Clave-inicial-2026")
    closure = PeriodClosure(
        codigo_empresa="1", ejercicio=2026, mes=13, cerrado=True, changed_by=user
    )
    with pytest.raises(ValidationError):
        closure.full_clean()


@pytest.mark.django_db
def test_the_dashboard_keeps_the_saved_share_of_a_closed_month():
    user = get_user_model().objects.create_user("cierra", "", "Clave-inicial-2026")
    refresh_snapshot("1", 2024)
    original = DashboardSnapshot.objects.get(codigo_empresa="1", ejercicio=2024).sales_amount
    share = ProjectExerciseShare.objects.get(
        codigo_empresa="1", codigo_proyecto="3001", ejercicio=2024
    )
    share.sales_amount += 1
    share.save(update_fields=["sales_amount"])
    life = ProjectLife.objects.get(codigo_empresa="1", codigo_proyecto="3001")
    stamp = life.updated_at
    PeriodClosure.objects.create(
        codigo_empresa="1", ejercicio=2024, mes=3, cerrado=True, changed_by=user
    )
    refresh_snapshot("1", 2024)
    refreshed = DashboardSnapshot.objects.get(codigo_empresa="1", ejercicio=2024)
    life.refresh_from_db()
    assert refreshed.sales_amount == original + 1
    assert life.updated_at == stamp
    assert life.order_base == Decimal("1000")


@pytest.mark.django_db
def test_the_dashboard_sums_closed_months_and_lists_each_open_month():
    user = get_user_model().objects.create_user("cierra", "", "Clave-inicial-2026")
    DashboardSnapshot.objects.create(codigo_empresa="1", ejercicio=2026)
    ProjectLife.objects.create(
        codigo_empresa="1", codigo_proyecto="MAR", order_date=date(2026, 3, 1), order_base=Decimal("100")
    )
    ProjectLife.objects.create(
        codigo_empresa="1", codigo_proyecto="OCT", order_date=date(2026, 10, 1), order_base=Decimal("40")
    )
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="MAR",
        ejercicio=2026,
        sales_count=1,
        sales_amount=Decimal("100"),
        purchase_order_count=2,
        purchase_order_amount=Decimal("15"),
        income_count=1,
        income_amount=Decimal("100"),
        expense_count=1,
        expense_amount=Decimal("30"),
    )
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="OCT",
        ejercicio=2026,
        sales_count=1,
        sales_amount=Decimal("40"),
        purchase_order_count=1,
        purchase_order_amount=Decimal("9"),
    )
    PeriodClosure.objects.create(codigo_empresa="1", ejercicio=2026, mes=3, cerrado=True, changed_by=user)
    figures = load_dashboard("1", 2026, list(InformationGroup.values))
    assert figures["sales"] == {"count": 1, "amount": Decimal("100")}
    assert figures["purchase_orders"]["amount"] == Decimal("15")
    assert figures["accounted_purchases"] == {"count": 0, "amount": Decimal("0")}
    assert figures["expenses"]["amount"] == Decimal("30")
    assert figures["margin"] == Decimal("70")
    octubre = next(row for row in figures["pending_months"] if row["name"] == "octubre")
    assert octubre["amount"] == Decimal("40")
    assert octubre["count"] == 1
    assert "marzo" not in {row["name"] for row in figures["pending_months"]}
    assert len(figures["pending_months"]) == 11


@pytest.mark.django_db
def test_closed_income_follows_the_movement_month_and_the_tree_drops_open_paths():
    user = get_user_model().objects.create_user("cierra", "", "Clave-inicial-2026")
    snapshot = DashboardSnapshot.objects.create(codigo_empresa="1", ejercicio=2026, titulo_1="Canal")
    AnalyticalSummary.objects.create(
        snapshot=snapshot, nivel_1="Cerrado", sales=Decimal("100"), income=Decimal("80"), margin=Decimal("80")
    )
    AnalyticalSummary.objects.create(
        snapshot=snapshot, nivel_1="Abierto", sales=Decimal("40"), income=Decimal("1"), margin=Decimal("1")
    )
    ProjectLife.objects.create(
        codigo_empresa="1", codigo_proyecto="MAR", order_date=date(2026, 3, 1), order_base=Decimal("100")
    )
    ProjectLife.objects.create(
        codigo_empresa="1", codigo_proyecto="OCT", order_date=date(2026, 10, 1), order_base=Decimal("40")
    )
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="MAR",
        ejercicio=2026,
        nivel_1="Cerrado",
        sales_count=1,
        sales_amount=Decimal("100"),
        income_count=1,
        income_amount=Decimal("100"),
        expense_count=1,
        expense_amount=Decimal("30"),
    )
    ProjectExerciseShare.objects.create(
        codigo_empresa="1",
        codigo_proyecto="OCT",
        ejercicio=2026,
        nivel_1="Abierto",
        sales_count=1,
        sales_amount=Decimal("40"),
    )
    MonthLedger.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=3, income_count=2, income_amount=Decimal("200"), expense_count=1, expense_amount=Decimal("50")
    )
    MonthLedger.objects.create(
        codigo_empresa="1", ejercicio=2026, mes=10, income_count=1, income_amount=Decimal("9"), expense_count=1, expense_amount=Decimal("4")
    )
    PeriodClosure.objects.create(codigo_empresa="1", ejercicio=2026, mes=3, cerrado=True, changed_by=user)
    figures = load_dashboard("1", 2026, list(InformationGroup.values))
    assert figures["income"] == {"count": 2, "amount": Decimal("200")}
    assert figures["expenses"] == {"count": 1, "amount": Decimal("50")}
    assert figures["margin"] == Decimal("150")
    assert figures["sales"] == {"count": 1, "amount": Decimal("100")}
    labels = [node["label"] for node in figures["hierarchy"]]
    assert labels == ["Cerrado"]


@pytest.mark.django_db
def test_an_open_year_margins_income_minus_the_group_six_book():
    DashboardSnapshot.objects.create(
        codigo_empresa="1",
        ejercicio=2026,
        sales_delivery_count=1,
        sales_delivery_amount=Decimal("200"),
        expense_count=3,
        expense_amount=Decimal("100"),
        income_count=1,
        income_amount=Decimal("900"),
    )
    life = ProjectLife.objects.create(codigo_empresa="1", codigo_proyecto="P1", order_date=date(2026, 2, 1))
    ProjectExpense.objects.create(
        life=life, account_code="602", account_name="Compras", movement_date=date(2026, 2, 1), amount=Decimal("40")
    )
    figures = load_dashboard("1", 2026, list(InformationGroup.values))
    assert figures["accounted_purchases"] == {"count": 1, "amount": Decimal("40")}
    assert figures["expenses"] == {"count": 3, "amount": Decimal("60")}
    assert figures["margin"] == Decimal("800")
    assert figures["margin_percent"] == Decimal("800") / Decimal("900") * Decimal("100")

