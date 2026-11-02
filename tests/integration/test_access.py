import re
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import Client, override_settings

from apps.access.models import CompanyAccess, InformationGroup, Profile, ProfilePermission
from apps.accounts.views import LOGIN_ERROR

NEW_PASSWORD = "Clave-nueva-2026"


def _person(username, password, email="", companies=("1",), active=True):
    user = get_user_model().objects.create_user(username, email, password)
    user.is_active = active
    user.save()
    profile = Profile.objects.create(user=user)
    for group in InformationGroup.values:
        ProfilePermission.objects.create(profile=profile, group=group)
    for code in companies:
        CompanyAccess.objects.create(user=user, codigo_empresa=code)
    return user


def _enter(client, username, password, remember=False, keep=False, follow=False):
    return client.post(
        "/accounts/login/",
        {
            "username": username,
            "password": password,
            "remember": "on" if remember else "",
            "keep": "on" if keep else "",
        },
        follow=follow,
    )


@pytest.mark.django_db
def test_wrong_password_and_unknown_user_share_the_same_warning():
    _person("activa", "Clave-inicial-2026", email="activa@example.com")
    wrong = Client()
    unknown = Client()
    wrong_page = _enter(wrong, "activa", "no-es-la-clave")
    unknown_page = _enter(unknown, "nadie", "no-es-la-clave")
    assert wrong_page.status_code == 200
    assert LOGIN_ERROR in wrong_page.content.decode()
    assert LOGIN_ERROR in unknown_page.content.decode()
    assert "no existe" not in wrong_page.content.decode().casefold()
    assert "no existe" not in unknown_page.content.decode().casefold()
    assert wrong.session.get("_auth_user_id") is None


@pytest.mark.django_db
def test_inactive_account_does_not_enter():
    _person("parada", "Clave-inicial-2026", active=False)
    client = Client()
    page = _enter(client, "parada", "Clave-inicial-2026")
    assert LOGIN_ERROR in page.content.decode()
    assert client.session.get("_auth_user_id") is None


@pytest.mark.django_db
def test_remember_stores_the_username_and_not_the_password():
    _person("activa", "Clave-inicial-2026")
    client = Client()
    page = _enter(client, "activa", "Clave-inicial-2026", remember=True)
    assert page.cookies["okia_user"].value == "activa"
    assert "Clave-inicial-2026" not in page.cookies["okia_user"].value
    client = Client()
    client.cookies["okia_user"] = "activa"
    form = client.get("/accounts/login/")
    body = form.content.decode()
    assert 'value="activa"' in body
    assert "Clave-inicial-2026" not in body
    cleared = _enter(client, "activa", "Clave-inicial-2026", remember=False)
    assert cleared.cookies["okia_user"].value == ""


@pytest.mark.django_db
def test_session_lasts_thirty_days_only_when_asked():
    _person("activa", "Clave-inicial-2026")
    kept = Client()
    _enter(kept, "activa", "Clave-inicial-2026", keep=True)
    assert kept.session.get_expire_at_browser_close() is False
    assert 29 * 24 * 60 * 60 < kept.session.get_expiry_age() <= 30 * 24 * 60 * 60
    brief = Client()
    _enter(brief, "activa", "Clave-inicial-2026", keep=False)
    assert brief.session.get_expire_at_browser_close() is True


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_recovery_link_is_single_use_and_silent_without_mail():
    owner = _person("activa", "Clave-inicial-2026", email="activa@example.com")
    silent = _person("sin-correo", "Clave-inicial-2026", email="")
    known = Client()
    known.post("/accounts/recuperar/", {"username": owner.username})
    assert len(mail.outbox) == 1
    assert "60 minutos" in mail.outbox[0].body
    match = re.search(r"http://testserver(/accounts/recuperar/\S+)", mail.outbox[0].body)
    link = match.group(1)
    opened = known.get(link, follow=True)
    assert "Contraseña nueva" in opened.content.decode()
    saved = known.post(
        opened.request["PATH_INFO"],
        {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
    )
    assert saved.status_code == 302
    owner.refresh_from_db()
    assert owner.check_password(NEW_PASSWORD)
    used = known.get(link)
    assert "El enlace no sirve" in used.content.decode()
    assert not Client().login(username="activa", password="Clave-inicial-2026")
    assert Client().login(username="activa", password=NEW_PASSWORD)

    before = len(mail.outbox)
    missing = Client().post("/accounts/recuperar/", {"username": "nadie"}, follow=True)
    without = Client().post("/accounts/recuperar/", {"username": silent.username}, follow=True)
    assert missing.content == without.content
    assert "no existe" not in missing.content.decode().casefold()
    assert len(mail.outbox) == before


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_expired_recovery_link_does_not_change_the_password():
    owner = _person("activa", "Clave-inicial-2026", email="activa@example.com")
    client = Client()
    client.post("/accounts/recuperar/", {"username": owner.username})
    link = re.search(r"http://testserver(/accounts/recuperar/\S+)", mail.outbox[0].body).group(1)
    future = datetime.now() + timedelta(hours=2)
    with patch.object(PasswordResetTokenGenerator, "_now", return_value=future):
        page = client.get(link)
    assert "El enlace no sirve" in page.content.decode()
    owner.refresh_from_db()
    assert owner.check_password("Clave-inicial-2026")


@pytest.mark.django_db
def test_several_companies_hide_figures_until_one_is_chosen_and_switch_clears_the_previous():
    _person("varias", "Clave-inicial-2026", companies=("1", "2"))
    client = Client()
    entered = _enter(client, "varias", "Clave-inicial-2026", follow=True)
    body = entered.content.decode()
    assert "No hay cifras hasta elegir una empresa." in body
    assert "650,00 EUR" not in body
    assert "9.999,00 EUR" not in body
    first = client.post("/empresas/", {"codigo_empresa": "1"}, follow=True)
    first_body = first.content.decode()
    assert "Cuadro de mando" in first_body
    assert "1.190,00 EUR" not in first_body
    refreshed = client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2026", "next": "/"},
        follow=True,
    )
    refreshed_body = refreshed.content.decode()
    assert "1.190,00 EUR" in refreshed_body
    assert "9.999,00 EUR" not in refreshed_body
    second = client.post("/empresas/", {"codigo_empresa": "2"}, follow=True)
    second_body = second.content.decode()
    assert "9.999,00 EUR" not in second_body
    assert "1.190,00 EUR" not in second_body
    other = client.post(
        "/actualizar/",
        {"codigo_empresa": "2", "ejercicio": "2026", "next": "/"},
        follow=True,
    )
    other_body = other.content.decode()
    assert "9.999,00 EUR" in other_body
    assert "1.190,00 EUR" not in other_body


@pytest.mark.django_db
def test_one_company_is_selected_and_none_asks_for_an_administrator():
    _person("sola", "Clave-inicial-2026", companies=("1",))
    alone = Client()
    page = _enter(alone, "sola", "Clave-inicial-2026", follow=True)
    assert "Cuadro de mando" in page.content.decode()
    refreshed = alone.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2026", "next": "/"},
        follow=True,
    )
    assert "1.190,00 EUR" in refreshed.content.decode()
    _person("vacia", "Clave-inicial-2026", companies=())
    empty = Client()
    waiting = _enter(empty, "vacia", "Clave-inicial-2026", follow=True)
    assert "Solicite una empresa a quien administra." in waiting.content.decode()
    margin = empty.get("/margen/")
    assert margin.status_code == 302
    assert "/empresas/" in margin["Location"]


@pytest.mark.django_db
def test_logout_hides_the_previous_company():
    _person("activa", "Clave-inicial-2026")
    client = Client()
    _enter(client, "activa", "Clave-inicial-2026", follow=True)
    client.post("/accounts/logout/")
    page = client.get("/margen/")
    assert page.status_code == 302
    assert "/accounts/login/" in page["Location"]
    assert "650,00 EUR" not in page.content.decode()
