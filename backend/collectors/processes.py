"""Coletor de processos via psutil.

Collectors só coletam e normalizam — não analisam. Retornam ``(payload, meta)`` e
degradam para ``partial`` (sem quebrar) quando faltam privilégios para ler alguns
processos. O ``cpu_pct`` vem de ``cpu_percent(None)``: na primeira leitura de cada
processo retorna 0.0 (mede desde a chamada anterior); estabiliza no polling.
"""

from __future__ import annotations

import time

import psutil

from models.schema import CollectorMeta, ProcessInfo

_MB = 1024**2


def _process_exe(proc: psutil.Process) -> str | None:
    """Caminho do executável — comum dar AccessDenied em processos do sistema."""
    try:
        return proc.exe() or None
    except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
        return None


def collect_processes(top_n: int = 15) -> tuple[list[ProcessInfo], CollectorMeta]:
    """Coleta os processos e devolve os ``top_n`` por uso de CPU (desc).

    Empate de CPU é desfeito por memória residente (desc), dando ordenação estável.
    Processos sem acesso são contados e refletidos em ``partial``.
    """
    started = time.perf_counter()
    procs: list[ProcessInfo] = []
    denied = 0

    for proc in psutil.process_iter(["pid", "name", "username"]):
        try:
            cpu = proc.cpu_percent(None)
            rss = proc.memory_info().rss / _MB
            procs.append(
                ProcessInfo(
                    pid=proc.info["pid"],
                    name=proc.info["name"] or "",
                    cpu_pct=round(float(cpu), 1),
                    rss_mb=round(rss, 1),
                    username=proc.info.get("username") or "",
                    exe=_process_exe(proc),
                )
            )
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            denied += 1
            continue

    procs.sort(key=lambda p: (p.cpu_pct, p.rss_mb), reverse=True)

    meta = CollectorMeta(
        source="processes",
        partial=denied > 0,
        reason=f"{denied} processos sem acesso (sem elevação?)" if denied else None,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
    return procs[:top_n], meta


def get_process(pid: int) -> ProcessInfo:
    """Lê um único processo pelo pid. Levanta ``psutil.NoSuchProcess`` se não existir."""
    proc = psutil.Process(pid)  # NoSuchProcess se o pid não existe
    with proc.oneshot():
        try:
            rss = proc.memory_info().rss / _MB
        except psutil.AccessDenied:
            rss = 0.0
        try:
            username = proc.username()
        except psutil.AccessDenied:
            username = ""
        return ProcessInfo(
            pid=proc.pid,
            name=proc.name(),
            cpu_pct=round(float(proc.cpu_percent(None)), 1),
            rss_mb=round(rss, 1),
            username=username,
            exe=_process_exe(proc),
        )
