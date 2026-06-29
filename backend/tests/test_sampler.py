"""Testes do sampler e da retenção (Fatia 3)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from models.schema import SystemMetrics
from services.sampler import sample_once
from storage.db import get_connection
from storage.repositories import delete_samples_older_than, insert_metric_sample


def _count() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) AS c FROM metric_samples").fetchone()["c"]


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


def test_sample_once_inserts_one_row():
    before = _count()
    sample_once()
    assert _count() == before + 1


def test_retention_deletes_old_samples():
    old = datetime.now(timezone.utc) - timedelta(days=8)
    insert_metric_sample(_sample(), ts=old)
    insert_metric_sample(_sample())  # recente
    assert _count() == 2

    deleted = delete_samples_older_than(days=7)
    assert deleted == 1
    assert _count() == 1
