"""Testes do coletor de sistema (Fatia 1)."""

from __future__ import annotations

from collectors.system import collect_host_info, collect_system_metrics
from models.schema import CollectorMeta, SystemMetrics


def test_collect_returns_metrics_and_meta():
    metrics, meta = collect_system_metrics()
    assert isinstance(metrics, SystemMetrics)
    assert isinstance(meta, CollectorMeta)
    assert meta.source == "system"


def test_percentages_in_range():
    metrics, _ = collect_system_metrics()
    for pct in (metrics.cpu_pct, metrics.mem_pct, metrics.disk_pct):
        assert 0.0 <= pct <= 100.0


def test_meta_has_duration_and_timestamp():
    _, meta = collect_system_metrics()
    assert meta.duration_ms >= 0
    assert meta.collected_at is not None


def test_partial_on_disk_failure(monkeypatch):
    """Sem acesso ao disco, o coletor degrada para partial — não quebra."""
    import collectors.system as sysmod

    def boom(_path):
        raise OSError("acesso negado")

    monkeypatch.setattr(sysmod.psutil, "disk_usage", boom)
    metrics, meta = collect_system_metrics()
    assert meta.partial is True
    assert meta.reason is not None
    assert metrics.disk_pct == 0.0


def test_host_info():
    host = collect_host_info()
    assert host.hostname
    assert host.os
