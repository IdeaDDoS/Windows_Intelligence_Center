"""Coletor de portas em escuta via psutil (porta da lógica do security_audit).

Usa ``psutil.net_connections`` (não varredura por socket): para auditar a própria
máquina é melhor — lê quem está em LISTEN e o processo dono. Collector só coleta e
normaliza; a análise (findings) é do analyzer. Degrada para ``partial`` sem quebrar.
"""

from __future__ import annotations

import socket
import time

import psutil

from models.schema import CollectorMeta, PortInfo

# Nomes conhecidos para portas comuns (complementa socket.getservbyport).
_WELL_KNOWN = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 143: "imap", 443: "https", 445: "smb",
    1433: "mssql", 1521: "oracle", 3306: "mysql", 3389: "rdp",
    5432: "postgresql", 5900: "vnc", 6379: "redis", 8080: "http-alt",
    27017: "mongodb",
}

# Binds que significam "exposto na rede".
_PUBLIC_BINDS = {"0.0.0.0", "::", ""}


def _service_name(port: int, proto: str) -> str | None:
    if port in _WELL_KNOWN:
        return _WELL_KNOWN[port]
    try:
        return socket.getservbyport(port, proto.lower())
    except OSError:
        return None


def collect_ports() -> tuple[list[PortInfo], CollectorMeta]:
    """Lista as portas TCP em LISTEN e UDP com bind local."""
    started = time.perf_counter()

    try:
        conns = psutil.net_connections(kind="inet")
    except psutil.AccessDenied:
        return [], CollectorMeta(
            source="ports",
            partial=True,
            reason="acesso negado à lista de conexões (rode como administrador)",
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    ports: list[PortInfo] = []
    partial = False

    for c in conns:
        proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
        if proto == "TCP" and c.status != psutil.CONN_LISTEN:
            continue
        if proto == "UDP" and c.raddr:
            continue

        addr = c.laddr.ip if c.laddr else ""
        port = c.laddr.port if c.laddr else 0

        proc_name = None
        if c.pid:
            try:
                proc_name = psutil.Process(c.pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                partial = True

        ports.append(
            PortInfo(
                port=port,
                protocol=proto,
                address=addr,
                status=c.status if proto == "TCP" else "BOUND",
                pid=c.pid,
                process=proc_name,
                service=_service_name(port, proto),
                public=addr in _PUBLIC_BINDS,
            )
        )

    ports.sort(key=lambda p: (not p.public, p.port))
    return ports, CollectorMeta(
        source="ports",
        partial=partial,
        reason="alguns processos sem acesso (sem elevação?)" if partial else None,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
