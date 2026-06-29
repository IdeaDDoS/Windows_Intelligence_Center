"""Testes de contrato dos endpoints de processos e serviços (Fatia 2)."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

from main import app
from models.schema import SignatureInfo


def test_list_processes_ok():
    with TestClient(app) as client:
        r = client.get("/api/processes?top_n=5")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"processes", "meta"}
    assert len(body["processes"]) <= 5
    if body["processes"]:
        assert set(body["processes"][0].keys()) == {
            "pid",
            "name",
            "cpu_pct",
            "rss_mb",
            "username",
            "exe",
        }
    assert body["meta"]["source"] == "processes"


def test_process_detail_ok(monkeypatch):
    """Detalhe do próprio processo de teste, com assinatura mockada (sem PowerShell)."""
    import api.processes as processes_api

    monkeypatch.setattr(
        processes_api,
        "get_signature",
        lambda _exe: SignatureInfo(is_signed=True, status="Valid", signer="CN=Test"),
    )
    with TestClient(app) as client:
        r = client.get(f"/api/processes/{os.getpid()}")
    assert r.status_code == 200
    body = r.json()
    assert body["process"]["pid"] == os.getpid()
    assert set(body["signature"].keys()) == {"is_signed", "status", "signer"}
    assert body["signature"]["status"] == "Valid"


def test_process_detail_404():
    with TestClient(app) as client:
        r = client.get("/api/processes/99999999")
    assert r.status_code == 404


def test_list_services_ok():
    with TestClient(app) as client:
        r = client.get("/api/services")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"services", "meta"}
    assert body["meta"]["source"] == "services"
