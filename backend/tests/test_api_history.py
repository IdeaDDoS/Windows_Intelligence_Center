"""Testes de contrato do endpoint de histórico (Fatia 3)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from models.schema import SystemMetrics
from storage.repositories import insert_metric_sample, query_history


def _sample() -> SystemMetrics:
    return SystemMetrics(
        cpu_pct=10.0,
        mem_pct=40.0,
        mem_used_gb=6.4,
        mem_total_gb=16.0,
        disk_pct=55.0,
        disk_used_gb=250.0,
        disk_total_gb=500.0,
        net_sent=1024,
        net_recv=2048,
        uptime_seconds=3600.0,
    )


def test_history_range_ok():
    for _ in range(5):
        insert_metric_sample(_sample())
    with TestClient(app) as client:
        r = client.get("/api/metrics/history?range=1h")
    assert r.status_code == 200
    body = r.json()
    assert body["range"] == "1h"
    assert len(body["points"]) == 5
    assert set(body["points"][0].keys()) == {
        "ts",
        "cpu_pct",
        "mem_pct",
        "disk_pct",
        "net_sent",
        "net_recv",
    }


def test_history_downsample_limits_points():
    for _ in range(50):
        insert_metric_sample(_sample())
    points = query_history("24h", max_points=10)
    assert len(points) <= 10


def test_history_invalid_range_422():
    with TestClient(app) as client:
        r = client.get("/api/metrics/history?range=99x")
    assert r.status_code == 422
