"""Endpoint de saúde do backend — usado pela tela inicial para mostrar 'online'."""

from __future__ import annotations

import ctypes
import platform

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Payload de status do backend."""

    status: str
    version: str
    platform: str
    is_admin: bool


def _is_admin() -> bool:
    """Detecta privilégio de administrador no Windows.

    Degrada para ``False`` fora do Windows ou quando não é possível verificar —
    honestidade sobre limitações, nunca afirma garantia que não pôde checar.
    """
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Retorna o estado atual do backend."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        platform=f"{platform.system()} {platform.release()}",
        is_admin=_is_admin(),
    )
