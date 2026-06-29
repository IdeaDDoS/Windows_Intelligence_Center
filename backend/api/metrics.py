"""Endpoints de métricas do sistema."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from api.common import MetaPayload, meta_payload
from collectors.system import collect_host_info, collect_system_metrics
from storage.repositories import query_history

router = APIRouter()


class MetricsPayload(BaseModel):
    cpu_pct: float
    mem_pct: float
    mem_used_gb: float
    mem_total_gb: float
    disk_pct: float
    disk_used_gb: float
    disk_total_gb: float
    net_sent: int
    net_recv: int
    uptime_seconds: float


class HostPayload(BaseModel):
    hostname: str
    os: str
    boot_time: datetime


class MetricsLiveResponse(BaseModel):
    metrics: MetricsPayload
    host: HostPayload
    meta: MetaPayload


class HistoryPoint(BaseModel):
    ts: datetime
    cpu_pct: float
    mem_pct: float
    disk_pct: float
    net_sent: int
    net_recv: int


class MetricsHistoryResponse(BaseModel):
    range: str
    points: list[HistoryPoint]


@router.get("/metrics/live", response_model=MetricsLiveResponse)
async def metrics_live() -> MetricsLiveResponse:
    """Snapshot atual de CPU, memória, disco e rede."""
    metrics, meta = collect_system_metrics()
    host = collect_host_info()
    return MetricsLiveResponse(
        metrics=MetricsPayload(**vars(metrics)),
        host=HostPayload(**vars(host)),
        meta=meta_payload(meta),
    )


# Síncrono de propósito: lê o SQLite (I/O bloqueante); o FastAPI roda funções
# `def` em threadpool, sem travar o event loop.
@router.get("/metrics/history", response_model=MetricsHistoryResponse)
def metrics_history(
    range: Literal["1h", "6h", "24h"] = "1h",
) -> MetricsHistoryResponse:
    """Série temporal de CPU/mem/disco/rede na janela escolhida (downsampled)."""
    points = query_history(range)
    return MetricsHistoryResponse(
        range=range,
        points=[HistoryPoint(**p) for p in points],
    )
