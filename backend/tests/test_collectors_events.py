"""Testes do coletor de eventos (Fatia 5) — PowerShell mockado."""

from __future__ import annotations

import json

import collectors.events as ev


class _Fake:
    """Stub de subprocess.CompletedProcess."""

    def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _event_dict(event_id: int = 42) -> dict:
    return {
        "ts": "2026-06-29T12:00:00Z",
        "log": "System",
        "provider": "Service Control Manager",
        "event_id": event_id,
        "level": "Error",
        "message": "boom",
    }


def test_parses_list_of_events(monkeypatch):
    payload = json.dumps([_event_dict(1), _event_dict(2)])
    monkeypatch.setattr(ev.subprocess, "run", lambda *a, **k: _Fake(0, payload))
    events, meta = ev.collect_events(log="System", level=2)
    assert len(events) == 2
    assert events[0].event_id == 1
    assert events[0].level == "Error"
    assert meta.source == "events"
    assert meta.partial is False


def test_single_object_normalized_to_list(monkeypatch):
    payload = json.dumps(_event_dict(7))  # objeto único, não lista
    monkeypatch.setattr(ev.subprocess, "run", lambda *a, **k: _Fake(0, payload))
    events, _ = ev.collect_events()
    assert len(events) == 1
    assert events[0].event_id == 7


def test_no_events_is_empty_not_partial(monkeypatch):
    stderr = "No events were found that match the specified selection criteria."
    monkeypatch.setattr(ev.subprocess, "run", lambda *a, **k: _Fake(1, "", stderr))
    events, meta = ev.collect_events()
    assert events == []
    assert meta.partial is False


def test_access_denied_degrades_partial(monkeypatch):
    stderr = "Attempted to perform an unauthorized operation."
    monkeypatch.setattr(ev.subprocess, "run", lambda *a, **k: _Fake(1, "", stderr))
    events, meta = ev.collect_events(log="Security")
    assert events == []
    assert meta.partial is True
    assert meta.reason


def test_powershell_missing_degrades_partial(monkeypatch):
    def boom(*a, **k):
        raise OSError("powershell não encontrado")

    monkeypatch.setattr(ev.subprocess, "run", boom)
    events, meta = ev.collect_events()
    assert events == []
    assert meta.partial is True
