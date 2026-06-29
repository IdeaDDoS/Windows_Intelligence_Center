"""Coletor de métricas de sistema (CPU, memória, disco, rede) via psutil.

Porta da lógica do protótipo Dash_Manager. Collectors só coletam e normalizam —
não analisam. Retornam `(payload, CollectorMeta)` e degradam para `partial` em vez
de quebrar.
"""

from __future__ import annotations

import platform
import socket
import time
from datetime import datetime, timezone

import psutil

from models.schema import CollectorMeta, HostInfo, SystemMetrics

_GB = 1024**3
# Volume do sistema monitorado na Fatia 1 (multi-volume fica para fatia futura).
_SYSTEM_DISK = "C:\\"


def collect_system_metrics() -> tuple[SystemMetrics, CollectorMeta]:
    """Coleta um snapshot de CPU, memória, disco e rede.

    Não bloqueia: `cpu_percent(interval=None)` mede desde a última chamada. Se uma
    fonte falhar, marca `partial` com o motivo, sem interromper a coleta.
    """
    started = time.perf_counter()
    partial = False
    reasons: list[str] = []

    cpu_pct = psutil.cpu_percent(interval=None)

    vm = psutil.virtual_memory()
    mem_pct = float(vm.percent)
    mem_used_gb = round(vm.used / _GB, 2)
    mem_total_gb = round(vm.total / _GB, 2)

    try:
        disk = psutil.disk_usage(_SYSTEM_DISK)
        disk_pct = float(disk.percent)
        disk_used_gb = round(disk.used / _GB, 2)
        disk_total_gb = round(disk.total / _GB, 2)
    except OSError as exc:
        partial = True
        reasons.append(f"disco {_SYSTEM_DISK}: {exc}")
        disk_pct = disk_used_gb = disk_total_gb = 0.0

    net = psutil.net_io_counters()
    net_sent = int(net.bytes_sent)
    net_recv = int(net.bytes_recv)

    boot = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
    uptime_seconds = (datetime.now(timezone.utc) - boot).total_seconds()

    metrics = SystemMetrics(
        cpu_pct=cpu_pct,
        mem_pct=mem_pct,
        mem_used_gb=mem_used_gb,
        mem_total_gb=mem_total_gb,
        disk_pct=disk_pct,
        disk_used_gb=disk_used_gb,
        disk_total_gb=disk_total_gb,
        net_sent=net_sent,
        net_recv=net_recv,
        uptime_seconds=uptime_seconds,
    )
    meta = CollectorMeta(
        source="system",
        partial=partial,
        reason="; ".join(reasons) or None,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
    return metrics, meta


def collect_host_info() -> HostInfo:
    """Coleta a identificação da máquina (hostname, OS, boot)."""
    return HostInfo(
        hostname=socket.gethostname(),
        os=f"{platform.system()} {platform.release()}",
        boot_time=datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc),
    )
