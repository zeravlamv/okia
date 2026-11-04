from datetime import date
from decimal import Decimal

import pytest
from django.test import Client

from apps.access.demo import ensure_demo
from apps.margins.models import ProjectIncome, ProjectLife, ProjectMilestone


def _life(code, order_base, delivered, income=None, review="Pdte. Revisar", customer=""):
    life = ProjectLife.objects.create(
        codigo_empresa="1",
        codigo_proyecto=code,
        order_date=date(2026, 3, 2),
        order_base=order_base,
        customer_name=customer,
        review_status=review,
    )
    ProjectMilestone.objects.create(
        life=life,
        ejercicio=2026,
        serie="T",
        numero=code,
        delivery_date=date(2026, 3, 2),
        amount=delivered,
        billing="invoiced",
    )
    if income is not None:
        ProjectIncome.objects.create(
            life=life,
            account_code="700",
            movement_date=date(2026, 3, 2),
            amount=income,
        )
    return life


@pytest.mark.django_db
def test_the_bell_lists_only_the_open_mismatch_and_the_review_toggles_it():
    ensure_demo()
    _life("PEND", Decimal("100"), Decimal("40"), customer="Taller Norte")
    _life("CUADRA", Decimal("10"), Decimal("10"), income=Decimal("10"))
    _life("VISTO", Decimal("80"), Decimal("10"), review="Revisado")
    client = Client()
    client.login(username="demo", password="demo")
    client.post("/filtros/", {"codigo_empresa": "1", "ejercicio": "2026", "next": "/"})

    page = client.get("/")
    body = page.content.decode()

    assert page.status_code == 200
    assert 'id="discrepancy-bell"' in body
    assert 'id="reviewed-bell"' in body
    assert 'aria-label="1 proyectos pendientes de revisar"' in body
    assert 'aria-label="1 proyectos revisados"' in body
    assert "PEND" in body
    assert "Taller Norte" in body
    assert "100,00 EUR" in body
    assert "40,00 EUR" in body
    assert "CUADRA" not in body
    assert "VISTO" in body
    assert "/proyecto/PEND/" in body
    assert "/proyecto/VISTO/" in body

    saved = client.post("/proyecto/PEND/", {"revision": "Revisado"}, follow=True)
    assert "Revisado" in saved.content.decode()
    assert ProjectLife.objects.get(codigo_proyecto="PEND").order_base == Decimal("100")
    quiet = client.get("/").content.decode()
    assert 'aria-label="0 proyectos pendientes de revisar"' in quiet
    assert 'aria-label="2 proyectos revisados"' in quiet
    assert "No hay proyectos pendientes de revisar." in quiet
    assert "/proyecto/PEND/" in quiet

    client.post("/proyecto/PEND/", {"revision": "Pdte. Revisar"})
    again = client.get("/").content.decode()
    assert 'aria-label="1 proyectos pendientes de revisar"' in again
    assert 'aria-label="1 proyectos revisados"' in again


@pytest.mark.django_db
def test_a_matched_project_with_no_income_stays_off_the_bell():
    ensure_demo()
    _life("ALIN", Decimal("50"), Decimal("50"), income=Decimal("0"))
    client = Client()
    client.login(username="demo", password="demo")
    client.post("/filtros/", {"codigo_empresa": "1", "ejercicio": "2026", "next": "/"})

    body = client.get("/").content.decode()

    assert "Ventas e ingresos" not in body
    assert "ALIN" not in body
    assert "No hay proyectos pendientes de revisar." in body
