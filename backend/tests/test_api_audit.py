"""Testes de contrato dos endpoints de auditoria (Fatia 6) — collectors mockados."""

from __future__ import annotations

from fastapi.testclient import TestClient

import services.audit as audit_svc
from main import app
from models.schema import CollectorMeta, PortInfo, SecurityConfig


def _fake_ports():
    port = PortInfo(
        port=3389,
        protocol="TCP",
        address="0.0.0.0",
        status="LISTEN",
        pid=1,
        process="svc",
        service="rdp",
        public=True,
    )
    return [port], CollectorMeta(source="ports")


def _fake_security():
    cfg = SecurityConfig(
        firewall={"Domain": False},
        defender={"antivirus_enabled": False, "realtime_enabled": True},
        antivirus=[],
        last_hotfix="2026-06-01",
    )
    return cfg, CollectorMeta(source="security_config")


def _mock_collectors(monkeypatch):
    monkeypatch.setattr(audit_svc, "collect_ports", _fake_ports)
    monkeypatch.setattr(audit_svc, "collect_security_config", _fake_security)


def test_run_audit_scores_and_finds(monkeypatch):
    _mock_collectors(monkeypatch)
    with TestClient(app) as client:
        r = client.post("/api/audit/run")
    assert r.status_code == 200
    body = r.json()
    assert body["score"] < 100
    cats = {f["category"] for f in body["findings"]}
    assert {"ports", "firewall", "defender"} <= cats
    assert body["ports"][0]["port"] == 3389
    assert body["security"]["firewall"] == {"Domain": False}


def test_latest_reflects_run(monkeypatch):
    _mock_collectors(monkeypatch)
    with TestClient(app) as client:
        run = client.post("/api/audit/run").json()
        latest = client.get("/api/audit/latest").json()
    assert latest["audit"]["id"] == run["id"]
    assert latest["audit"]["score"] == run["score"]
    assert len(latest["findings"]) >= 1


def test_latest_empty_when_no_audit():
    with TestClient(app) as client:
        r = client.get("/api/audit/latest")
    assert r.status_code == 200
    assert r.json()["audit"] is None


def test_history_lists_audits(monkeypatch):
    _mock_collectors(monkeypatch)
    with TestClient(app) as client:
        client.post("/api/audit/run")
        r = client.get("/api/audit")
    assert r.status_code == 200
    assert len(r.json()["audits"]) >= 1


def test_audit_detail_404():
    with TestClient(app) as client:
        r = client.get("/api/audit/999999")
    assert r.status_code == 404
