"""Testes do coletor de portas (Fatia 6)."""

from __future__ import annotations

from collectors.ports import collect_ports
from models.schema import CollectorMeta, PortInfo


def test_returns_list_and_meta():
    ports, meta = collect_ports()
    assert isinstance(meta, CollectorMeta)
    assert meta.source == "ports"
    assert all(isinstance(p, PortInfo) for p in ports)


def test_public_flag_is_bool():
    ports, _ = collect_ports()
    assert all(isinstance(p.public, bool) for p in ports)


def test_public_ports_sorted_first():
    ports, _ = collect_ports()
    publics = [p.public for p in ports]
    # Ordenação: públicas primeiro (não-crescente em `public`).
    assert publics == sorted(publics, reverse=True)
