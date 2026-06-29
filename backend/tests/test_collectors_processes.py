"""Testes do coletor de processos (Fatia 2)."""

from __future__ import annotations

from collectors.processes import collect_processes
from models.schema import CollectorMeta, ProcessInfo


def test_returns_list_and_meta():
    procs, meta = collect_processes(top_n=5)
    assert isinstance(meta, CollectorMeta)
    assert meta.source == "processes"
    assert all(isinstance(p, ProcessInfo) for p in procs)


def test_respects_top_n():
    procs, _ = collect_processes(top_n=3)
    assert len(procs) <= 3


def test_sorted_by_cpu_desc():
    procs, _ = collect_processes(top_n=15)
    cpus = [p.cpu_pct for p in procs]
    assert cpus == sorted(cpus, reverse=True)


def test_meta_has_duration():
    _, meta = collect_processes(top_n=1)
    assert meta.duration_ms >= 0
    assert meta.collected_at is not None
