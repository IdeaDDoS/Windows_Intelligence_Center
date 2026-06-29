"""Testes do cálculo de score (Fatia 6)."""

from __future__ import annotations

from analyzers.scoring import compute
from models.schema import Finding, Severity


def _finding(sev: Severity, key: str = "X") -> Finding:
    return Finding(id=key, title=key, severity=sev, category="test", description="")


def test_empty_findings_is_100():
    score, breakdown = compute([])
    assert score == 100
    assert len(breakdown) == 1  # linha "nenhum problema"


def test_deducts_by_severity():
    score, _ = compute([_finding(Severity.HIGH, "a"), _finding(Severity.LOW, "b")])
    assert score == 100 - 15 - 3


def test_info_does_not_deduct():
    score, breakdown = compute([_finding(Severity.INFO)])
    assert score == 100
    assert all(line.delta == 0 for line in breakdown)


def test_score_floored_at_zero():
    score, _ = compute([_finding(Severity.CRITICAL, str(i)) for i in range(10)])
    assert score == 0


def test_breakdown_has_negative_deltas():
    _, breakdown = compute([_finding(Severity.MEDIUM, "m")])
    assert breakdown[0].delta == -8
