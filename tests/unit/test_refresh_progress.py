import json

import pytest
from django.test import Client

from apps.access.demo import ensure_demo
from apps.margins.snapshot import refresh_snapshot


@pytest.mark.django_db
def test_refresh_names_each_step_and_counts_the_project_fiches():
    events = []
    refresh_snapshot("1", 2026, progress=events.append)
    labels = [event["label"] for event in events]
    assert labels[:6] == [
        "Pedidos de venta",
        "Pedidos de compra",
        "Albaranes de venta",
        "Albaranes de compra",
        "Movimientos",
        "Cuadro de mando",
    ]
    fiches = [event for event in events if event["label"] == "Fichas de proyecto"]
    assert fiches[0]["done"] == 0
    assert "month" not in fiches[0]
    assert fiches[-1]["done"] == fiches[-1]["count"]
    assert fiches[-1]["count"] >= 1
    assert {event["month"] for event in fiches if event.get("month")} == {"febrero", "marzo", "mayo", "junio"}
    assert labels[-1] == "Listo"


@pytest.mark.django_db
def test_one_project_names_every_open_month_of_its_orders():
    from datetime import date
    from decimal import Decimal

    from apps.erp.sample import SaleOrder
    from apps.margins.project_life import refresh_project_lives

    seen = []
    refresh_project_lives(
        "1",
        2026,
        [
            SaleOrder("1", 2026, "T", "1", "C1", "P9", Decimal("10"), None, date(2026, 4, 2), "Pendiente"),
            SaleOrder("1", 2026, "T", "2", "C1", "P9", Decimal("20"), None, date(2026, 3, 10), "Pendiente"),
        ],
        [],
        [],
        [],
        [],
        on_project=lambda done, count, month="": seen.append(month),
    )
    assert seen == ["", "marzo, abril"]


@pytest.mark.django_db
def test_actualizar_streams_the_steps_and_the_page_keeps_the_notice(monkeypatch):
    ensure_demo()

    def fake(company, year, progress=None):
        progress({"step": 1, "total": 8, "label": "Pedidos de venta"})
        progress({"step": 7, "total": 8, "label": "Fichas de proyecto", "done": 1, "count": 2})
        progress({"step": 8, "total": 8, "label": "Listo"})

    monkeypatch.setattr("apps.margins.views.refresh_snapshot", fake)
    client = Client()
    client.login(username="demo", password="demo")
    page = client.get("/").content.decode()
    assert "No cierres esta página." in page
    assert 'title.textContent = year ? "Actualizando " + event.month + " de " + year' in page
    response = client.post(
        "/actualizar/",
        {"codigo_empresa": "1", "ejercicio": "2026", "next": "/proyecto/3001/"},
        HTTP_ACCEPT="application/x-ndjson",
    )
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/x-ndjson")
    lines = [json.loads(line) for line in b"".join(response.streaming_content).decode().splitlines()]
    assert lines[0]["label"] == "Pedidos de venta"
    assert lines[1]["done"] == 1
    assert lines[1]["count"] == 2
    assert lines[-1] == {"ok": True, "next": "/proyecto/3001/"}
