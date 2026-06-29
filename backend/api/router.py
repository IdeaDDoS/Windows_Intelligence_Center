"""Router central da API. Agrega os routers de cada domínio sob o prefixo /api."""

from __future__ import annotations

from fastapi import APIRouter

from api.alerts import router as alerts_router
from api.events import router as events_router
from api.health import router as health_router
from api.metrics import router as metrics_router
from api.processes import router as processes_router
from api.services import router as services_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(metrics_router, tags=["metrics"])
api_router.include_router(processes_router, tags=["processes"])
api_router.include_router(services_router, tags=["services"])
api_router.include_router(alerts_router, tags=["alerts"])
api_router.include_router(events_router, tags=["events"])
