"""Testes de contrato dos endpoints de alertas e regras (Fatia 4)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from main import app
from storage.repositories import insert_alert, list_alert_rules


def test_rules_seeded():
    with TestClient(app) as client:
        r = client.get("/api/alert_rules")
    assert r.status_code == 200
    rules = r.json()["rules"]
    assert len(rules) >= 3
    assert {"cpu_pct", "mem_pct", "disk_pct"} <= {rule["metric"] for rule in rules}


def test_create_rule():
    with TestClient(app) as client:
        r = client.post(
            "/api/alert_rules",
            json={"metric": "cpu_pct", "operator": ">", "threshold": 50, "duration_s": 0},
        )
    assert r.status_code == 201
    body = r.json()
    assert body["metric"] == "cpu_pct"
    assert body["threshold"] == 50
    assert body["id"] > 0


def test_update_rule():
    with TestClient(app) as client:
        rule_id = client.get("/api/alert_rules").json()["rules"][0]["id"]
        r = client.put(f"/api/alert_rules/{rule_id}", json={"enabled": False})
    assert r.status_code == 200
    assert r.json()["enabled"] is False


def test_update_missing_rule_404():
    with TestClient(app) as client:
        r = client.put("/api/alert_rules/999999", json={"enabled": False})
    assert r.status_code == 404


def test_list_alerts_empty():
    with TestClient(app) as client:
        r = client.get("/api/alerts")
    assert r.status_code == 200
    assert r.json()["alerts"] == []


def test_ack_alert():
    rule_id = list_alert_rules()[0]["id"]
    alert_id = insert_alert(rule_id, datetime.now(timezone.utc), 99.0, "teste")
    with TestClient(app) as client:
        ack = client.post(f"/api/alerts/{alert_id}/ack")
        assert ack.status_code == 200
        assert ack.json()["acknowledged"] is True
        alerts = client.get("/api/alerts").json()["alerts"]
    assert any(a["id"] == alert_id and a["acknowledged"] for a in alerts)


def test_ack_missing_alert_404():
    with TestClient(app) as client:
        r = client.post("/api/alerts/999999/ack")
    assert r.status_code == 404
