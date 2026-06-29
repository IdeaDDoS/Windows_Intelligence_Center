"""Dataclasses canônicas — a espinha dorsal do pipeline.

Uma fonte canônica, múltiplos destinos: collectors devolvem `(payload, CollectorMeta)`;
a API serializa via modelos Pydantic próprios (ver `api/`), mantendo o contrato
interno desacoplado do contrato HTTP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CollectorMeta:
    """Metadados de uma coleta — honestidade sobre limitações.

    `partial=True` sinaliza coleta incompleta (ex.: falta de privilégio); `reason`
    explica o motivo. Nunca afirmar garantia que o coletor não pôde verificar.
    """

    source: str
    partial: bool = False
    reason: str | None = None
    collected_at: datetime = field(default_factory=_now_utc)
    duration_ms: int = 0


@dataclass
class SystemMetrics:
    """Snapshot de uso de recursos do sistema."""

    cpu_pct: float
    mem_pct: float
    mem_used_gb: float
    mem_total_gb: float
    disk_pct: float
    disk_used_gb: float
    disk_total_gb: float
    net_sent: int  # bytes acumulados desde o boot
    net_recv: int  # bytes acumulados desde o boot
    uptime_seconds: float


@dataclass
class HostInfo:
    """Identificação da máquina."""

    hostname: str
    os: str
    boot_time: datetime
