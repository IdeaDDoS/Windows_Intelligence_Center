"""Dataclasses canônicas — a espinha dorsal do pipeline.

Uma fonte canônica, múltiplos destinos: collectors devolvem `(payload, CollectorMeta)`;
a API serializa via modelos Pydantic próprios (ver `api/`), mantendo o contrato
interno desacoplado do contrato HTTP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


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


@dataclass
class ProcessInfo:
    """Um processo em execução (snapshot)."""

    pid: int
    name: str
    cpu_pct: float
    rss_mb: float
    username: str
    exe: str | None = None


@dataclass
class ServiceInfo:
    """Um serviço do Windows."""

    name: str
    display_name: str
    status: str
    start_type: str


@dataclass
class SignatureInfo:
    """Resultado da verificação de assinatura digital de um executável.

    Honestidade sobre limitações: sem caminho do executável ou sem como verificar,
    `status` reflete o motivo (`unknown`/`error`) em vez de afirmar algo não checado.
    """

    is_signed: bool
    status: str
    signer: str | None = None


@dataclass
class ProcessDetail:
    """Detalhe de um processo: dados básicos + assinatura (sob demanda)."""

    process: ProcessInfo
    signature: SignatureInfo


@dataclass
class EventInfo:
    """Um evento do log de eventos do Windows (Event Viewer)."""

    ts: datetime
    log: str
    provider: str
    event_id: int
    level: str
    message: str


@dataclass
class AlertRule:
    """Regra de alerta por limiar sobre uma métrica."""

    id: int
    metric: str  # cpu_pct | mem_pct | disk_pct
    operator: str  # > | >= | < | <=
    threshold: float
    duration_s: int = 0
    enabled: bool = True


@dataclass
class Alert:
    """Um alerta disparado pela avaliação de uma regra."""

    rule_id: int
    ts: datetime
    value: float
    message: str


# ── Postura de segurança (Fatia 6) ───────────────────────────────────────────


class Severity(str, Enum):
    """Severidade de um achado. Herda de str para serializar como texto."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Peso de dedução no score por severidade (o score parte de 100 e desconta).
SEVERITY_WEIGHT: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.LOW: 3,
    Severity.MEDIUM: 8,
    Severity.HIGH: 15,
    Severity.CRITICAL: 25,
}


@dataclass
class PortInfo:
    """Uma porta em escuta (bind), com o processo dono."""

    port: int
    protocol: str  # TCP | UDP
    address: str
    status: str
    pid: int | None
    process: str | None
    service: str | None
    public: bool  # escuta em 0.0.0.0/:: → exposta na rede


@dataclass
class SecurityConfig:
    """Configuração de segurança do Windows (firewall, antivírus, hotfix)."""

    firewall: dict[str, bool] = field(default_factory=dict)  # perfil → ativo
    defender: dict[str, object] = field(default_factory=dict)  # flags do Defender
    antivirus: list[str] = field(default_factory=list)  # produtos de terceiros
    last_hotfix: str | None = None


@dataclass
class Finding:
    """Um achado da auditoria — sempre com motivo e recomendação."""

    id: str
    title: str
    severity: Severity
    category: str  # ports | firewall | defender | ...
    description: str
    recommendation: str = ""
    evidence: dict = field(default_factory=dict)


@dataclass
class ScoreLine:
    """Uma linha do detalhamento do score (para ele 'se explicar')."""

    label: str
    delta: int  # negativo = pontos perdidos


@dataclass
class AuditResult:
    """Resultado canônico de uma auditoria de postura de segurança."""

    ts: datetime
    score: int
    summary: str
    findings: list[Finding] = field(default_factory=list)
    ports: list[PortInfo] = field(default_factory=list)
    security: SecurityConfig | None = None
    score_breakdown: list[ScoreLine] = field(default_factory=list)
    partial: bool = False
    partial_reason: str | None = None
    id: int | None = None
