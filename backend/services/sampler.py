"""Sampler de métricas em segundo plano (asyncio task no lifespan).

A cada ``sample_interval_seconds`` coleta uma amostra, persiste e aplica a
retenção (raw por 7 dias). Roda a coleta (bloqueante) em thread separada para
não travar o event loop. Resiliente: uma falha de iteração é logada e o loop
segue — o painel não pode cair por causa do coletor.
"""

from __future__ import annotations

import asyncio
import logging

from collectors.system import collect_system_metrics
from config import settings
from storage.repositories import delete_samples_older_than, insert_metric_sample

logger = logging.getLogger("wic.sampler")

# Dias de retenção das amostras raw (ver PLANEJAMENTO §5).
_RETENTION_DAYS = 7


def sample_once() -> None:
    """Uma iteração: coleta, persiste e expurga amostras além da retenção."""
    metrics, _meta = collect_system_metrics()
    insert_metric_sample(metrics)
    delete_samples_older_than(days=_RETENTION_DAYS)


async def run_sampler(stop: asyncio.Event) -> None:
    """Loop do sampler até ``stop`` ser sinalizado (no shutdown da app)."""
    logger.info("Sampler iniciado (intervalo %ss)", settings.sample_interval_seconds)
    while not stop.is_set():
        try:
            await asyncio.to_thread(sample_once)
        except Exception:  # noqa: BLE001 — resiliência: loga e segue, não derruba o loop
            logger.exception("Falha ao coletar/gravar amostra")
        try:
            await asyncio.wait_for(stop.wait(), timeout=settings.sample_interval_seconds)
        except asyncio.TimeoutError:
            pass
    logger.info("Sampler encerrado")
