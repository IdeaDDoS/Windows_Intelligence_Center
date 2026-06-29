"""Testes de contrato do endpoint de eventos (Fatia 5) — coletor mockado."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

import api.events as events_api
from main import app
from models.schema import CollectorMeta, EventInfo


def _fake_collect(**kwargs):
    event = EventInfo(
        ts=datetime(2026, 6, 29, 12, 0, 0, tzinfo=timezone.utc),
        log="System",
        provider="Service Control Manager",
        event_id=42,
        level="Error",
        message="boom",
    )
    return [event], CollectorMeta(source="events")


def test_events_endpoint_ok(monkeypatch):
    monkeypatch.setattr(events_api, "collect_events", _fake_collect)
    with TestClient(app) as client:
        r = client.get("/api/events?log=System&level=error&since=24h&limit=10")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"events", "meta"}
    assert body["events"][0]["event_id"] == 42
    assert set(body["events"][0].keys()) == {
        "ts",
        "log",
        "provider",
        "event_id",
        "level",
        "message",
    }
    assert body["meta"]["source"] == "events"


def test_events_invalid_log_422():
    with TestClient(app) as client:
        r = client.get("/api/events?log=Nope")
    assert r.status_code == 422


def test_events_invalid_level_422():
    with TestClient(app) as client:
        r = client.get("/api/events?level=fatal")
    assert r.status_code == 422
