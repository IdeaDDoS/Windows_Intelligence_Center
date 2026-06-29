"""Endpoint de eventos do Windows (Event Viewer on-demand)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.common import MetaPayload, meta_payload
from collectors.events import collect_events

router = APIRouter()

EventLog = Literal["System", "Application", "Security"]
EventLevel = Literal["all", "critical", "error", "warning", "information"]
EventSince = Literal["1h", "6h", "24h", "7d"]

# Nível textual → código numérico do Get-WinEvent (None = sem filtro de nível).
_LEVELS: dict[str, int] = {"critical": 1, "error": 2, "warning": 3, "information": 4}
# Janela textual → segundos.
_SINCE: dict[str, int] = {"1h": 3600, "6h": 6 * 3600, "24h": 86400, "7d": 7 * 86400}


class EventOut(BaseModel):
    ts: datetime
    log: str
    provider: str
    event_id: int
    level: str
    message: str


class EventListResponse(BaseModel):
    events: list[EventOut]
    meta: MetaPayload


# Síncrono de propósito: roda PowerShell (I/O bloqueante) → threadpool do FastAPI.
@router.get("/events", response_model=EventListResponse)
def get_events(
    log: EventLog = "System",
    level: EventLevel = "all",
    since: EventSince = "24h",
    limit: int = Query(default=200, ge=1, le=1000),
) -> EventListResponse:
    """Lista eventos do log escolhido, filtrando por nível e janela de tempo."""
    events, meta = collect_events(
        log=log,
        level=_LEVELS.get(level),
        since_seconds=_SINCE[since],
        limit=limit,
    )
    return EventListResponse(
        events=[EventOut(**vars(e)) for e in events],
        meta=meta_payload(meta),
    )
