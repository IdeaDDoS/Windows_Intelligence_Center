"""Router central da API. Agrega os routers de cada domínio sob o prefixo /api."""

from __future__ import annotations

from fastapi import APIRouter

from api.health import router as health_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router, tags=["health"])
