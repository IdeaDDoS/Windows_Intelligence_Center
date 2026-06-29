"""Serviço de auditoria de postura de segurança (orquestra o pipeline).

Camada de serviço: roda os collectors (EXTRACT), os analyzers (TRANSFORM) e
persiste (LOAD), devolvendo o ``AuditResult`` canônico. O router só serializa.
"""

from __future__ import annotations

from datetime import datetime, timezone

from analyzers.findings import build_all
from analyzers.scoring import compute
from collectors.ports import collect_ports
from collectors.security_config import collect_security_config
from models.schema import AuditResult, Finding, Severity
from storage.repositories import insert_audit


def _summarize(score: int, findings: list[Finding]) -> str:
    """Resumo curto da auditoria: score + contagem por severidade (sem INFO)."""
    counts: dict[str, int] = {}
    for f in findings:
        if f.severity is Severity.INFO:
            continue
        counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
    if not counts:
        return f"{score}/100 · nenhum problema relevante"
    parts = ", ".join(
        f"{counts[s]} {s}" for s in ("critical", "high", "medium", "low") if s in counts
    )
    return f"{score}/100 · {parts}"


def run_audit() -> AuditResult:
    """Executa uma auditoria completa, persiste e devolve o resultado."""
    ports, ports_meta = collect_ports()
    security, sec_meta = collect_security_config()

    findings = build_all(ports, security)
    score, breakdown = compute(findings)
    ts = datetime.now(timezone.utc)
    summary = _summarize(score, findings)

    audit_id = insert_audit(ts, score, summary, findings)

    partial_reasons = [
        m.reason for m in (ports_meta, sec_meta) if m.partial and m.reason
    ]
    return AuditResult(
        id=audit_id,
        ts=ts,
        score=score,
        summary=summary,
        findings=findings,
        ports=ports,
        security=security,
        score_breakdown=breakdown,
        partial=bool(partial_reasons),
        partial_reason="; ".join(partial_reasons) or None,
    )
