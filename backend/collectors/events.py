"""Coletor de eventos do Windows (Event Viewer) via PowerShell Get-WinEvent.

On-demand: cada chamada consulta o log ao vivo com filtros (log, nível, janela,
limite) — sem persistência. Parâmetros passam por variáveis de ambiente, nunca
concatenados no comando (anti-injeção). Degrada para ``partial`` sem quebrar:
sem elevação, o log ``Security`` costuma dar acesso negado.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone

from models.schema import CollectorMeta, EventInfo

# Lê os filtros de variáveis de ambiente (sem concatenar entrada no comando).
# Monta o FilterHashtable do Get-WinEvent e emite JSON com campos normalizados.
_PS_SCRIPT = (
    "$ErrorActionPreference='Stop';"
    "$filter=@{ LogName = $env:WIC_EV_LOG };"
    "if ($env:WIC_EV_LEVEL) { $filter['Level'] = [int]$env:WIC_EV_LEVEL };"
    "if ($env:WIC_EV_SINCE) { $filter['StartTime'] = (Get-Date).AddSeconds(-[int]$env:WIC_EV_SINCE) };"
    "Get-WinEvent -FilterHashtable $filter -MaxEvents ([int]$env:WIC_EV_LIMIT) |"
    " Select-Object"
    " @{N='ts';E={$_.TimeCreated.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')}},"
    " @{N='log';E={$_.LogName}},"
    " @{N='provider';E={$_.ProviderName}},"
    " @{N='event_id';E={$_.Id}},"
    " @{N='level';E={$_.LevelDisplayName}},"
    " @{N='message';E={$_.Message}} |"
    " ConvertTo-Json -Depth 3 -Compress"
)

# Mensagem do Get-WinEvent quando o filtro não casa nenhum evento (não é erro).
_NO_EVENTS_MARKER = "No events were found"


def _parse_ts(value: str) -> datetime:
    """Converte o ISO-8601 UTC do PowerShell em datetime ciente de timezone."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _to_event(raw: dict) -> EventInfo:
    return EventInfo(
        ts=_parse_ts(str(raw.get("ts") or "")),
        log=str(raw.get("log") or ""),
        provider=str(raw.get("provider") or ""),
        event_id=int(raw.get("event_id") or 0),
        level=str(raw.get("level") or ""),
        message=str(raw.get("message") or ""),
    )


def collect_events(
    log: str = "System",
    level: int | None = None,
    since_seconds: int = 86400,
    limit: int = 200,
) -> tuple[list[EventInfo], CollectorMeta]:
    """Consulta os eventos do log escolhido com os filtros dados."""
    started = time.perf_counter()
    env = {
        **os.environ,
        "WIC_EV_LOG": log,
        "WIC_EV_LIMIT": str(limit),
        "WIC_EV_SINCE": str(since_seconds),
    }
    if level is not None:
        env["WIC_EV_LEVEL"] = str(level)

    def _meta(partial: bool, reason: str | None) -> CollectorMeta:
        return CollectorMeta(
            source="events",
            partial=partial,
            reason=reason,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [], _meta(True, f"falha ao executar PowerShell: {exc}")

    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        if _NO_EVENTS_MARKER in stderr:
            return [], _meta(False, None)  # filtro sem resultados não é falha
        return [], _meta(True, stderr[:200] or f"Get-WinEvent (log {log}) falhou")

    out = (completed.stdout or "").strip()
    if not out:
        return [], _meta(False, None)

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return [], _meta(True, "resposta do PowerShell ilegível")

    if isinstance(data, dict):  # ConvertTo-Json devolve objeto único quando há 1 item
        data = [data]

    events = [_to_event(item) for item in data]
    return events, _meta(False, None)
