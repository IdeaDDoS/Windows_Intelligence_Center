"""Repositórios: acesso às tabelas de domínio do SQLite.

Mantém a regra de negócio fora do SQL e o SQL fora dos routers (camada storage).
Todas as queries são parametrizadas — nunca dado concatenado.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from models.schema import AlertRule, SystemMetrics
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


# ── Alertas (Fatia 4) ────────────────────────────────────────────────────────

# Colunas editáveis de uma regra (whitelist — protege o UPDATE dinâmico de injeção).
_RULE_FIELDS = ("metric", "operator", "threshold", "duration_s", "enabled")


def list_alert_rules(enabled_only: bool = False) -> list[dict]:
    """Lista as regras de alerta (todas, ou só as ativas)."""
    sql = "SELECT id, metric, operator, threshold, duration_s, enabled FROM alert_rules"
    if enabled_only:
        sql += " WHERE enabled = 1"
    sql += " ORDER BY id"
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql).fetchall()]


def list_enabled_rules() -> list[AlertRule]:
    """Regras ativas já como dataclasses canônicas (consumidas pelo motor)."""
    return [
        AlertRule(
            id=r["id"],
            metric=r["metric"],
            operator=r["operator"],
            threshold=r["threshold"],
            duration_s=r["duration_s"],
            enabled=bool(r["enabled"]),
        )
        for r in list_alert_rules(enabled_only=True)
    ]


def get_alert_rule(rule_id: int) -> dict | None:
    """Uma regra pelo id, ou ``None`` se não existir."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, metric, operator, threshold, duration_s, enabled "
            "FROM alert_rules WHERE id = ?",
            (rule_id,),
        ).fetchone()
    return dict(row) if row else None


def create_alert_rule(
    metric: str,
    operator: str,
    threshold: float,
    duration_s: int,
    enabled: bool,
) -> int:
    """Cria uma regra e devolve o id gerado."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO alert_rules (metric, operator, threshold, duration_s, enabled) "
            "VALUES (?, ?, ?, ?, ?)",
            (metric, operator, threshold, duration_s, int(enabled)),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_alert_rule(rule_id: int, fields: dict) -> bool:
    """Atualiza campos de uma regra (só os da whitelist). True se algo mudou."""
    updates = {k: v for k, v in fields.items() if k in _RULE_FIELDS and v is not None}
    if not updates:
        return False
    if "enabled" in updates:
        updates["enabled"] = int(updates["enabled"])
    # As chaves vêm da whitelist `_RULE_FIELDS` — seguro interpolar no SET.
    set_clause = ", ".join(f"{col} = ?" for col in updates)
    params = [*updates.values(), rule_id]
    with get_connection() as conn:
        cur = conn.execute(
            f"UPDATE alert_rules SET {set_clause} WHERE id = ?", params
        )
        conn.commit()
        return cur.rowcount > 0


def insert_alert(rule_id: int, ts: datetime, value: float, message: str) -> int:
    """Registra um alerta disparado e devolve o id gerado."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO alerts (rule_id, ts, value, message) VALUES (?, ?, ?, ?)",
            (rule_id, _iso(ts), value, message),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_alerts(limit: int = 100) -> list[dict]:
    """Alertas mais recentes primeiro."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, rule_id, ts, value, message, acknowledged "
            "FROM alerts ORDER BY ts DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def count_unacknowledged_alerts() -> int:
    """Quantidade de alertas ainda não reconhecidos."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM alerts WHERE acknowledged = 0"
        ).fetchone()
    return int(row["c"])


def ack_alert(alert_id: int) -> bool:
    """Marca um alerta como reconhecido. True se o alerta existia."""
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,)
        )
        conn.commit()
        return cur.rowcount > 0
