from datetime import date
from decimal import Decimal

import pytest

from apps.access.models import InformationGroup
from apps.erp.sample import SaleOrder
from apps.margins.discrepancies import pending_projects, reviewed_projects
from apps.margins.models import (
    REVIEW_DONE,
    REVIEW_PENDING,
    ProjectIncome,
    ProjectLife,
    ProjectMilestone,
    ProjectPurchase,
)
from apps.margins.project_life import KIND_COMMITTED, refresh_project_lives


def _life(company, code, when, order_base, delivered=None, income=None, review=REVIEW_PENDING, customer=""):
    life = ProjectLife.objects.create(
        codigo_empresa=company,
        codigo_proyecto=code,
        order_date=when,
        order_base=order_base,
        customer_name=customer,
        review_status=review,
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
    if income is not None:
        ProjectIncome.objects.create(
            life=life,
            account_code="700",
            movement_date=when,
            amount=income,
        )
    return life


@pytest.mark.django_db
def test_only_the_open_mismatch_is_pending():
    _life("1", "PEND", date(2026, 3, 2), Decimal("100"), delivered=Decimal("40"), customer="Taller Norte")
    _life("1", "CUADRA", date(2026, 3, 3), Decimal("10"), delivered=Decimal("10"), income=Decimal("10"))
    _life("1", "VISTO", date(2026, 3, 4), Decimal("80"), delivered=Decimal("10"), review=REVIEW_DONE)
    _life("2", "OTRA", date(2026, 3, 2), Decimal("100"), delivered=Decimal("0"))
    _life("1", "OTRO", date(2025, 3, 2), Decimal("100"), delivered=Decimal("0"))

    rows = pending_projects("1", 2026, list(InformationGroup.values))

    assert [row["code"] for row in rows] == ["PEND"]
    assert rows[0]["customer"] == "Taller Norte"
    assert rows[0]["pairs"][0]["left"] == Decimal("100")
    assert rows[0]["pairs"][0]["right"] == Decimal("40")
    assert [row["code"] for row in reviewed_projects("1", 2026, list(InformationGroup.values))] == ["VISTO"]


@pytest.mark.django_db
def test_zero_matches_zero_and_a_larger_delivery_does_not():
    _life("1", "CERO", date(2026, 1, 1), Decimal("0"))
    _life("1", "MAS", date(2026, 1, 2), Decimal("10"), delivered=Decimal("15"))

    rows = pending_projects("1", 2026, list(InformationGroup.values))

    assert [row["code"] for row in rows] == ["MAS"]


@pytest.mark.django_db
def test_a_committed_purchase_without_a_delivery_is_pending():
    life = _life("1", "COMP", date(2026, 2, 2), Decimal("0"))
    ProjectPurchase.objects.create(
        life=life,
        kind=KIND_COMMITTED,
        ejercicio=2026,
        serie="P",
        numero="1",
        document_date=date(2026, 2, 2),
        amount=Decimal("20"),
    )

    rows = pending_projects("1", 2026, list(InformationGroup.values))

    assert rows[0]["pairs"][0]["name"] == "Pedido de compra y albaranado"
    assert rows[0]["pairs"][0]["left"] == Decimal("20")
    assert rows[0]["pairs"][0]["right"] == Decimal("0")


@pytest.mark.django_db
def test_unbooked_income_does_not_open_a_matched_project():
    _life("1", "ING", date(2026, 4, 1), Decimal("50"), delivered=Decimal("50"), income=Decimal("0"))

    assert pending_projects("1", 2026, list(InformationGroup.values)) == []


@pytest.mark.django_db
def test_a_missing_amount_does_not_invent_a_difference():
    life = _life("1", "HUECO", date(2026, 5, 1), Decimal("100"))
    ProjectMilestone.objects.create(
        life=life,
        ejercicio=2026,
        serie="T",
        numero="1",
        delivery_date=date(2026, 5, 1),
        amount=None,
        billing="invoiced",
    )

    assert pending_projects("1", 2026, list(InformationGroup.values)) == []


@pytest.mark.django_db
def test_review_comes_back_only_when_it_is_pending_again():
    life = _life("1", "PEND", date(2026, 3, 2), Decimal("100"), delivered=Decimal("40"))
    life.review_status = REVIEW_DONE
    life.save(update_fields=["review_status"])
    assert pending_projects("1", 2026, list(InformationGroup.values)) == []
    life.review_status = REVIEW_PENDING
    life.save(update_fields=["review_status"])
    assert [row["code"] for row in pending_projects("1", 2026, list(InformationGroup.values))] == ["PEND"]


@pytest.mark.django_db
def test_refresh_keeps_the_review():
    ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto="1001",
        order_date=date(2026, 3, 1),
        order_base=Decimal("10"),
        review_status=REVIEW_DONE,
    )
    refresh_project_lives(
        "1",
        2026,
        [
            SaleOrder(
                codigo_empresa="1",
                ejercicio=2026,
                serie="A",
                numero="1",
                codigo_cliente="C1",
                project="1001",
                header_base=Decimal("10"),
                tax_included=None,
                order_date=date(2026, 3, 1),
                status="Pendiente",
            )
        ],
        [],
        [],
        [],
        [],
    )

    stored = ProjectLife.objects.get(codigo_empresa="1", codigo_proyecto="1001")
    assert stored.review_status == REVIEW_DONE
    assert stored.order_base == Decimal("10")
