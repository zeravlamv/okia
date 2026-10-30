import pytest
from django.test import Client

from apps.access.demo import DEMO_PASSWORD, DEMO_USERNAME, ensure_demo


@pytest.mark.django_db
def test_demo_user_sees_the_sample_margin_and_not_other_companies():
    ensure_demo()
    client = Client()
    assert client.login(username=DEMO_USERNAME, password=DEMO_PASSWORD)
    response = client.get("/margen/")
    assert response.status_code == 200
    body = response.content.decode()
    assert "650,00 EUR" in body
    assert "800,00 EUR" in body
    assert "9999,00 EUR" not in body
    assert "1002" not in body
    assert "No aplicable" in body
    assert "Incompleto" in body
