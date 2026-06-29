"""Coletor de serviços do Windows via psutil.

Disponível só no Windows (``psutil.win_service_iter``). Fora do Windows degrada
para ``partial`` com o motivo, em vez de quebrar. Serviços individuais sem acesso
são contados e refletidos em ``partial``.
"""

from __future__ import annotations

import time

import psutil

from models.schema import CollectorMeta, ServiceInfo


def collect_services() -> tuple[list[ServiceInfo], CollectorMeta]:
    """Lista os serviços do Windows e seu estado/tipo de inicialização."""
    started = time.perf_counter()

    if not hasattr(psutil, "win_service_iter"):
        meta = CollectorMeta(
            source="services",
            partial=True,
            reason="coleta de serviços disponível apenas no Windows",
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        return [], meta

    services: list[ServiceInfo] = []
    skipped = 0

    # Campos lidos individualmente de propósito: `as_dict()` também busca a
    # descrição, que estoura FileNotFoundError em serviços transitórios.
    for svc in psutil.win_service_iter():
        try:
            services.append(
                ServiceInfo(
                    name=svc.name() or "",
                    display_name=svc.display_name() or "",
                    status=svc.status() or "unknown",
                    start_type=svc.start_type() or "unknown",
                )
            )
        except psutil.NoSuchProcess:
            continue
        except (psutil.AccessDenied, OSError):
            # AccessDenied (sem elevação) ou FileNotFoundError (serviço removido
            # durante a varredura) — conta como ilegível, não quebra.
            skipped += 1
            continue

    services.sort(key=lambda s: s.display_name.lower())

    meta = CollectorMeta(
        source="services",
        partial=skipped > 0,
        reason=f"{skipped} serviços ilegíveis (sem elevação?)" if skipped else None,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
    return services, meta
