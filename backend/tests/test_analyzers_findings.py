"""Testes das regras de findings de segurança (Fatia 6)."""

from __future__ import annotations

from analyzers.findings import build_all, from_ports, from_security
from models.schema import PortInfo, SecurityConfig, Severity


def _port(port: int, public: bool) -> PortInfo:
    return PortInfo(
        port=port,
        protocol="TCP",
        address="0.0.0.0" if public else "127.0.0.1",
        status="LISTEN",
        pid=1,
        process="svc",
        service=None,
        public=public,
    )


def test_risky_public_port_is_high():
    findings = from_ports([_port(3389, public=True)])
    high = [f for f in findings if f.severity is Severity.HIGH]
    assert any(f.id == "PORT-3389-PUBLIC" for f in high)
    assert all(f.category == "ports" for f in findings)


def test_risky_local_port_is_low():
    findings = from_ports([_port(3306, public=False)])
    assert any(f.id == "PORT-3306-LOCAL" and f.severity is Severity.LOW for f in findings)


def test_non_risky_port_has_no_per_port_finding():
    findings = from_ports([_port(12345, public=True)])
    # Só o resumo INFO de portas públicas, nenhum achado por porta.
    assert all(f.id == "PORT-SUMMARY" for f in findings)


def test_public_summary_is_info():
    findings = from_ports([_port(3389, public=True)])
    summary = [f for f in findings if f.id == "PORT-SUMMARY"]
    assert len(summary) == 1
    assert summary[0].severity is Severity.INFO


def test_firewall_disabled_is_high():
    sec = SecurityConfig(firewall={"Domain": False, "Private": True})
    findings = from_security(sec)
    assert any(f.id == "FW-Domain" and f.severity is Severity.HIGH for f in findings)
    # Perfil ativo não vira achado.
    assert not any(f.id == "FW-Private" for f in findings)


def test_defender_disabled_is_high():
    sec = SecurityConfig(defender={"antivirus_enabled": False, "realtime_enabled": False})
    ids = {f.id for f in from_security(sec)}
    assert {"DEF-AV", "DEF-RT"} <= ids


def test_unknown_security_does_not_flag():
    # Dado ausente (None) não vira achado — honestidade sobre limitações.
    sec = SecurityConfig(defender={"antivirus_enabled": None})
    assert from_security(sec) == []
    assert from_security(None) == []


def test_build_all_merges_sections():
    findings = build_all(
        [_port(3389, public=True)],
        SecurityConfig(firewall={"Public": False}),
    )
    cats = {f.category for f in findings}
    assert {"ports", "firewall"} <= cats
