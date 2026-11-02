import pytest
from django.test import Client

from apps.access.demo import ensure_demo


@pytest.mark.django_db
def test_the_guide_names_the_sql_server_tables():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")

    body = client.get("/guia/").content.decode()

    assert "De dónde salen los datos" in body
    assert "CabeceraPedidoCliente" in body
    assert "CabeceraAlbaranCliente" in body
    assert "CabeceraPedidoProveedor" in body
    assert "CabeceraAlbaranProveedor" in body
    assert "AnaMovimientos" in body
    assert "Movimientos" in body
    assert "PlanCuentas" in body
    assert "CabPosicion" in body


@pytest.mark.django_db
def test_the_menu_opens_the_guide():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")

    body = client.get("/").content.decode()

    assert 'href="/guia/"' in body
