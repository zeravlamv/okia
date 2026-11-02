import pytest
from django.test import Client
from django.utils import timezone

from apps.access.demo import ensure_demo
from apps.access.models import CompanyAccess, InformationGroup, Profile, ProfilePermission
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_the_project_fiche_waits_for_refresh_and_then_shows_its_whole_life():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")
    waiting = client.get("/proyecto/3001/")
    waiting_body = waiting.content.decode()
    assert waiting.status_code == 200
    assert "Pulse Actualizar" in waiting_body
    assert "50,00 %" not in waiting_body
    refreshed = client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2024", "next": "/proyecto/3001/"},
        follow=True,
    )
    body = refreshed.content.decode()
    assert "50,00 %" in body
    assert "400,00 EUR" in body
    assert "100,00 EUR" in body
    assert "Pendiente de albaranar" in body
    assert "Pendiente de facturar" in body
    assert "500,00 EUR" in body
    assert "1.000,00 EUR" in body
    assert "80,00 EUR" in body
    assert "40,00 EUR" in body
    assert "2024 / P / 40" in body
    assert "Comprometido" in body
    assert "25,00 EUR" in body
    assert "Desviación" in body
    assert "-500,00 EUR" in body
    assert "Margen neto" not in body
    assert "El pedido, los albaranes" not in body
    assert "460,00 EUR" in body
    assert "Analítica costes" in body
    assert "Evolución proyecto" in body
    assert "PR1 — Suministros Norte" in body
    assert "622 — Reparaciones y conservación" in body
    assert "129" not in body
    assert "Pedido del 10/03/2024" in body
    assert 'class="fiche-customer">C6</p>' in body
    assert "2024, 2025, 2026" in body
    assert timezone.localdate().strftime("%d/%m/%Y") in body
    again = client.get("/proyecto/3001/").content.decode()
    assert "50,00 %" in again
    board = client.get("/").content.decode()
    assert '"code": "3001"' in board
    assert 'id="project-query"' in board


@pytest.mark.django_db
def test_a_profile_without_sales_deliveries_does_not_see_the_progression():
    ensure_demo()
    user = get_user_model().objects.create_user("sin-albaran", "", "Clave-inicial-2026")
    profile = Profile.objects.create(user=user)
    for group in InformationGroup.values:
        if group == InformationGroup.ALBARANES_VENTA:
            continue
        ProfilePermission.objects.create(profile=profile, group=group)
    CompanyAccess.objects.create(user=user, codigo_empresa="1")
    client = Client()
    client.login(username="sin-albaran", password="Clave-inicial-2026")
    client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2024", "next": "/proyecto/3001/"},
        follow=True,
    )
    body = client.get("/proyecto/3001/").content.decode()
    assert "Progresión" not in body
    assert "Desviación" not in body
    assert "Margen neto" not in body
    assert "50,00 %" not in body
    assert "1.000,00 EUR" in body
