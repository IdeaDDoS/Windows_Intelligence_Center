"""Repositórios: acesso às tabelas de domínio do SQLite.

Mantém a regra de negócio fora do SQL e o SQL fora dos routers (camada storage).
Todas as queries são parametrizadas — nunca dado concatenado.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from models.schema import SystemMetrics
from storage.db import get_connection

# Janelas de histórico suportadas → segundos.
HISTORY_RANGES: dict[str, int] = {
    "1h": 3600,
    "6h": 6 * 3600,
    "24h": 24 * 3600,
}


def _iso(dt: datetime) -> str:
    """Normaliza para ISO-8601 em UTC (formato gravado na coluna ``ts``)."""
    return dt.astimezone(timezone.utc).isoformat()


def insert_metric_sample(metrics: SystemMetrics, ts: datetime | None = None) -> None:
    """Persiste uma amostra de métricas. ``ts`` permite injeção em testes."""
    moment = ts or datetime.now(timezone.utc)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO metric_samples "
            "(ts, cpu_pct, mem_pct, mem_used_gb, disk_pct, net_sent, net_recv) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                _iso(moment),
                metrics.cpu_pct,
                metrics.mem_pct,
                metrics.mem_used_gb,
                metrics.disk_pct,
                metrics.net_sent,
                metrics.net_recv,
            ),
        )
        conn.commit()


def _downsample(rows: list[dict], max_points: int) -> list[dict]:
    """Reduz a série para no máximo ``max_points`` pontos por passo uniforme."""
    if len(rows) <= max_points:
        return rows
    step = math.ceil(len(rows) / max_points)
    return rows[::step]


def query_history(
    range_key: str,
    max_points: int = 300,
    now: datetime | None = None,
) -> list[dict]:
    """Série temporal dentro da janela, já reduzida (downsample) para o gráfico."""
    if range_key not in HISTORY_RANGES:
        raise ValueError(f"janela inválida: {range_key!r}")
    moment = now or datetime.now(timezone.utc)
    cutoff = moment - timedelta(seconds=HISTORY_RANGES[range_key])
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT ts, cpu_pct, mem_pct, disk_pct, net_sent, net_recv "
            "FROM metric_samples WHERE ts >= ? ORDER BY ts",
            (_iso(cutoff),),
        ).fetchall()
    return _downsample([dict(r) for r in rows], max_points)


def delete_samples_older_than(days: int = 7, now: datetime | None = None) -> int:
    """Expurga amostras além da retenção (raw por 7 dias). Retorna quantas apagou."""
    moment = now or datetime.now(timezone.utc)
    cutoff = moment - timedelta(days=days)
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM metric_samples WHERE ts < ?", (_iso(cutoff),))
        conn.commit()
        return cur.rowcount
