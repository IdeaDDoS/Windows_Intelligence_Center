"""Testes do coletor de configuração de segurança (Fatia 6) — PowerShell mockado."""

from __future__ import annotations

import json

import collectors.security_config as sc


class _Fake:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_parses_full_config(monkeypatch):
    payload = json.dumps(
        {
            "firewall": [
                {"Name": "Domain", "Enabled": True},
                {"Name": "Public", "Enabled": False},
            ],
            "defender": {
                "antivirus_enabled": True,
                "realtime_enabled": True,
                "signatures_last_updated": "2026-06-01",
            },
            "antivirus": ["Windows Defender"],
            "hotfix": "2026-06-20",
        }
    )
    monkeypatch.setattr(sc.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sc.subprocess, "run", lambda *a, **k: _Fake(0, payload))

    cfg, meta = sc.collect_security_config()
    assert cfg.firewall == {"Domain": True, "Public": False}
    assert cfg.defender["antivirus_enabled"] is True
    assert cfg.last_hotfix == "2026-06-20"
    assert meta.partial is False


def test_single_firewall_profile_normalized(monkeypatch):
    payload = json.dumps(
        {
            "firewall": {"Name": "Domain", "Enabled": True},  # objeto único
            "defender": {"antivirus_enabled": True},
            "antivirus": [],
            "hotfix": None,
        }
    )
    monkeypatch.setattr(sc.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sc.subprocess, "run", lambda *a, **k: _Fake(0, payload))
    cfg, _ = sc.collect_security_config()
    assert cfg.firewall == {"Domain": True}


def test_empty_output_is_partial(monkeypatch):
    monkeypatch.setattr(sc.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sc.subprocess, "run", lambda *a, **k: _Fake(0, ""))
    cfg, meta = sc.collect_security_config()
    assert meta.partial is True
    assert meta.reason
