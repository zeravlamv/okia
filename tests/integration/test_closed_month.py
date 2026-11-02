import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.access.demo import ensure_demo
from apps.margins.models import PeriodClosure, ProjectLife


@pytest.mark.django_db
def test_an_administrator_sees_the_closure_and_someone_else_does_not():
    ensure_demo()
    admin = Client()
    admin.login(username="demo", password="demo")
    opened = admin.get("/admin/margins/periodclosure/")
    assert opened.status_code == 200
    visitor = get_user_model().objects.create_user("visita", "", "Clave-inicial-2026")
    guest = Client()
    guest.login(username=visitor.username, password="Clave-inicial-2026")
    denied = guest.get("/admin/margins/periodclosure/")
    assert denied.status_code == 302


@pytest.mark.django_db
def test_an_administrator_can_close_and_reopen_a_whole_exercise():
    ensure_demo()
    admin = Client()
    admin.login(username="demo", password="demo")
    page = admin.get("/admin/margins/periodclosure/")
    assert "Cerrar ejercicio" in page.content.decode()
    assert "Abrir ejercicio" in page.content.decode()
    closed = admin.post(
        "/admin/margins/periodclosure/",
        {"codigo_empresa": "1", "ejercicio": "2016", "exercise_action": "close"},
    )
    assert closed.status_code == 302
    rows = PeriodClosure.objects.filter(codigo_empresa="1", ejercicio=2016)
    assert rows.count() == 12
    assert set(rows.values_list("cerrado", flat=True)) == {True}
    assert set(rows.values_list("changed_by__username", flat=True)) == {"demo"}
    opened = admin.post(
        "/admin/margins/periodclosure/",
        {"codigo_empresa": "1", "ejercicio": "2016", "exercise_action": "open"},
    )
    assert opened.status_code == 302
    rows = PeriodClosure.objects.filter(codigo_empresa="1", ejercicio=2016)
    assert rows.count() == 12
    assert set(rows.values_list("cerrado", flat=True)) == {False}
    refused = admin.post(
        "/admin/margins/periodclosure/",
        {"codigo_empresa": "1", "ejercicio": "1990", "exercise_action": "close"},
    )
    assert refused.status_code == 302
    assert not PeriodClosure.objects.filter(ejercicio=1990).exists()
    visitor = get_user_model().objects.create_user("visita", "", "Clave-inicial-2026")
    guest = Client()
    guest.login(username=visitor.username, password="Clave-inicial-2026")
    denied = guest.post(
        "/admin/margins/periodclosure/",
        {"codigo_empresa": "1", "ejercicio": "2016", "exercise_action": "close"},
    )
    assert denied.status_code == 302
    assert PeriodClosure.objects.filter(codigo_empresa="1", ejercicio=2016, cerrado=True).count() == 0



@pytest.mark.django_db
def test_actualizar_names_a_closed_month_and_leaves_that_fiche():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")
    client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2024", "next": "/proyecto/3001/"},
        follow=True,
    )
    life = ProjectLife.objects.get(codigo_empresa="1", codigo_proyecto="3001")
    stamp = life.updated_at
    PeriodClosure.objects.create(
        codigo_empresa="1",
        ejercicio=2024,
        mes=3,
        cerrado=True,
        changed_by=get_user_model().objects.get(username="demo"),
    )
    refreshed = client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2024", "next": "/proyecto/3001/"},
        follow=True,
    )
    body = refreshed.content.decode()
    assert "marzo" in body
    assert "No había ningún mes abierto" not in body
    life.refresh_from_db()
    assert life.updated_at == stamp


@pytest.mark.django_db
def test_twelve_closed_months_do_not_change_any_fiche():
    ensure_demo()
    client = Client()
    client.login(username="demo", password="demo")
    client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2024", "next": "/proyecto/3001/"},
        follow=True,
    )
    life = ProjectLife.objects.get(codigo_empresa="1", codigo_proyecto="3001")
    stamp = life.updated_at
    user = get_user_model().objects.get(username="demo")
    for month in range(1, 13):
        PeriodClosure.objects.create(
            codigo_empresa="1",
            ejercicio=2024,
            mes=month,
            cerrado=True,
            changed_by=user,
        )
    refreshed = client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2024", "next": "/proyecto/3001/"},
        follow=True,
    )
    assert "No había ningún mes abierto" in refreshed.content.decode()
    life.refresh_from_db()
    assert life.updated_at == stamp
