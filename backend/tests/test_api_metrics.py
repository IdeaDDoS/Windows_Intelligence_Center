"""Testes de contrato do endpoint de métricas (Fatia 1)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_metrics_live_ok():
    with TestClient(app) as client:
        r = client.get("/api/metrics/live")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"metrics", "host", "meta"}
    assert set(body["metrics"].keys()) == {
        "cpu_pct",
        "mem_pct",
        "mem_used_gb",
        "mem_total_gb",
        "disk_pct",
        "disk_used_gb",
        "disk_total_gb",
        "net_sent",
        "net_recv",
        "uptime_seconds",
    }
    assert body["meta"]["source"] == "system"
    assert body["host"]["hostname"]
