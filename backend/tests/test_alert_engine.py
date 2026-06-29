"""Testes do motor de alertas (Fatia 4)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from analyzers.alerts import AlertEngine
from models.schema import AlertRule, SystemMetrics

_T0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _metrics(cpu: float = 0.0, mem: float = 0.0, disk: float = 0.0) -> SystemMetrics:
    return SystemMetrics(
        cpu_pct=cpu,
        mem_pct=mem,
        mem_used_gb=1.0,
        mem_total_gb=16.0,
        disk_pct=disk,
        disk_used_gb=1.0,
        disk_total_gb=500.0,
        net_sent=0,
        net_recv=0,
        uptime_seconds=0.0,
    )


def _rule(duration_s: int = 0) -> AlertRule:
    return AlertRule(
        id=1, metric="cpu_pct", operator=">", threshold=90.0, duration_s=duration_s
    )


def test_fires_on_violation():
    engine = AlertEngine()
    alerts = engine.evaluate(_metrics(cpu=95), [_rule()], _T0)
    assert len(alerts) == 1
    assert alerts[0].rule_id == 1
    assert alerts[0].value == 95


def test_no_fire_below_threshold():
    engine = AlertEngine()
    assert engine.evaluate(_metrics(cpu=50), [_rule()], _T0) == []


def test_respects_duration():
    engine = AlertEngine()
    rule = _rule(duration_s=60)
    # Viola, mas ainda não pelo tempo exigido → não dispara.
    assert engine.evaluate(_metrics(cpu=95), [rule], _T0) == []
    # Após a duração, com a violação contínua → dispara.
    later = _T0 + timedelta(seconds=61)
    alerts = engine.evaluate(_metrics(cpu=95), [rule], later)
    assert len(alerts) == 1


def test_no_duplicate_while_violating():
    engine = AlertEngine()
    rule = _rule()
    first = engine.evaluate(_metrics(cpu=95), [rule], _T0)
    second = engine.evaluate(_metrics(cpu=95), [rule], _T0 + timedelta(seconds=5))
    assert len(first) == 1
    assert second == []


def test_refires_after_recovery():
    engine = AlertEngine()
    rule = _rule()
    assert len(engine.evaluate(_metrics(cpu=95), [rule], _T0)) == 1
    # Voltou ao normal: limpa o estado.
    assert engine.evaluate(_metrics(cpu=10), [rule], _T0 + timedelta(seconds=5)) == []
    # Viola de novo: dispara novamente.
    again = engine.evaluate(_metrics(cpu=95), [rule], _T0 + timedelta(seconds=10))
    assert len(again) == 1


def test_disabled_rule_never_fires():
    engine = AlertEngine()
    rule = AlertRule(
        id=2, metric="cpu_pct", operator=">", threshold=90.0, enabled=False
    )
    assert engine.evaluate(_metrics(cpu=99), [rule], _T0) == []
