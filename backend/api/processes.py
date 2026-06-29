"""Endpoints de processos (lista e detalhe com assinatura sob demanda)."""

from __future__ import annotations

import psutil
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.common import MetaPayload, meta_payload
from collectors.processes import collect_processes, get_process
from collectors.signature import get_signature

router = APIRouter()


class ProcessItem(BaseModel):
    pid: int
    name: str
    cpu_pct: float
    rss_mb: float
    username: str
    exe: str | None


class ProcessListResponse(BaseModel):
    processes: list[ProcessItem]
    meta: MetaPayload


class SignaturePayload(BaseModel):
    is_signed: bool
    status: str
    signer: str | None


class ProcessDetailResponse(BaseModel):
    process: ProcessItem
    signature: SignaturePayload


# Os handlers são síncronos de propósito: a coleta via psutil (e o PowerShell da
# assinatura) é I/O bloqueante; o FastAPI roda funções `def` em threadpool, sem
# travar o event loop.
@router.get("/processes", response_model=ProcessListResponse)
def list_processes(
    top_n: int = Query(default=15, ge=1, le=200),
) -> ProcessListResponse:
    """Top-N processos por uso de CPU."""
    processes, meta = collect_processes(top_n=top_n)
    return ProcessListResponse(
        processes=[ProcessItem(**vars(p)) for p in processes],
        meta=meta_payload(meta),
    )


@router.get("/processes/{pid}", response_model=ProcessDetailResponse)
def process_detail(pid: int) -> ProcessDetailResponse:
    """Detalhe de um processo + verificação de assinatura. 404 se o pid sumiu."""
    try:
        info = get_process(pid)
    except psutil.NoSuchProcess as exc:
        raise HTTPException(status_code=404, detail=f"processo {pid} não encontrado") from exc
    except psutil.AccessDenied as exc:
        raise HTTPException(status_code=403, detail=f"sem acesso ao processo {pid}") from exc

    signature = get_signature(info.exe)
    return ProcessDetailResponse(
        process=ProcessItem(**vars(info)),
        signature=SignaturePayload(**vars(signature)),
    )
