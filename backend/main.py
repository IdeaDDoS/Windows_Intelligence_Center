"""Ponto de entrada da aplicação FastAPI do Windows Intelligence Center.

Em desenvolvimento, o frontend roda no Vite (:5173) e fala com o backend (:8000)
via proxy. Em produção, o build do React é servido como estático a partir de
``backend/static``. O padrão de servir a SPA segue o molde ``dashboards_us-media``.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.router import api_router
from config import settings
from services.sampler import run_sampler
from storage.db import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("wic")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco e sobe o sampler em background; encerra no shutdown."""
    init_db()
    logger.info("Banco inicializado em %s", settings.db_path)

    stop = asyncio.Event()
    sampler_task: asyncio.Task[None] | None = None
    if settings.sampler_enabled:
        sampler_task = asyncio.create_task(run_sampler(stop))

    yield

    if sampler_task is not None:
        stop.set()
        await sampler_task


app = FastAPI(
    title="Windows Intelligence Center",
    version="0.1.0",
    docs_url="/api/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# ── SPA estática (build do React) ────────────────────────────────────────────
# Só é montada quando o build existe (produção). Em dev, o Vite serve o frontend.
_STATIC = Path(__file__).parent / "static"

if _STATIC.exists():
    app.mount("/assets", StaticFiles(directory=_STATIC / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        """Serve o arquivo estático se existir; senão devolve index.html (rota SPA)."""
        candidate = _STATIC / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_STATIC / "index.html")
