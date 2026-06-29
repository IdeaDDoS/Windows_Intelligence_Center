"""Modelos Pydantic compartilhados entre routers.

Uma fonte canônica, múltiplos destinos: o ``MetaPayload`` serializa o
``CollectorMeta`` interno para todos os endpoints que expõem metadados de coleta.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from models.schema import CollectorMeta


class MetaPayload(BaseModel):
    """Espelho HTTP de ``CollectorMeta`` (honestidade sobre limitações)."""

    source: str
    partial: bool
    reason: str | None
    collected_at: datetime
    duration_ms: int


def meta_payload(meta: CollectorMeta) -> MetaPayload:
    """Converte o ``CollectorMeta`` interno no payload de API."""
    return MetaPayload(**vars(meta))
