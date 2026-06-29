"""Endpoints de métricas do sistema."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from collectors.system import collect_host_info, collect_system_metrics

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


class MetaPayload(BaseModel):
    source: str
    partial: bool
    reason: str | None
    collected_at: datetime
    duration_ms: int


class MetricsLiveResponse(BaseModel):
    metrics: MetricsPayload
    host: HostPayload
    meta: MetaPayload


@router.get("/metrics/live", response_model=MetricsLiveResponse)
async def metrics_live() -> MetricsLiveResponse:
    """Snapshot atual de CPU, memória, disco e rede."""
    metrics, meta = collect_system_metrics()
    host = collect_host_info()
    return MetricsLiveResponse(
        metrics=MetricsPayload(**vars(metrics)),
        host=HostPayload(**vars(host)),
        meta=MetaPayload(**vars(meta)),
    )
