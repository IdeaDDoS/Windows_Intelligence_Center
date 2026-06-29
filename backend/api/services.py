"""Endpoint de serviços do Windows."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from api.common import MetaPayload, meta_payload
from collectors.services import collect_services

router = APIRouter()


class ServiceItem(BaseModel):
    name: str
    display_name: str
    status: str
    start_type: str


class ServiceListResponse(BaseModel):
    services: list[ServiceItem]
    meta: MetaPayload


# Síncrono de propósito: a coleta de serviços é I/O bloqueante; o FastAPI roda
# funções `def` em threadpool.
@router.get("/services", response_model=ServiceListResponse)
def list_services() -> ServiceListResponse:
    """Lista os serviços do Windows e seu estado."""
    services, meta = collect_services()
    return ServiceListResponse(
        services=[ServiceItem(**vars(s)) for s in services],
        meta=meta_payload(meta),
    )
