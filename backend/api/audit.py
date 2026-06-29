"""Endpoints de auditoria de postura de segurança."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.audit import run_audit
from storage.repositories import (
    get_audit,
    get_findings,
    get_latest_audit,
    list_audits,
)

router = APIRouter()


class PortItem(BaseModel):
    port: int
    protocol: str
    address: str
    status: str
    pid: int | None
    process: str | None
    service: str | None
    public: bool


class DefenderPayload(BaseModel):
    antivirus_enabled: bool | None = None
    realtime_enabled: bool | None = None
    signatures_last_updated: str | None = None


class SecurityConfigPayload(BaseModel):
    firewall: dict[str, bool]
    defender: DefenderPayload
    antivirus: list[str]
    last_hotfix: str | None


class FindingItem(BaseModel):
    id: str
    title: str
    severity: str
    category: str
    description: str
    recommendation: str
    evidence: dict


class ScoreLineItem(BaseModel):
    label: str
    delta: int


class AuditSummary(BaseModel):
    id: int
    ts: datetime
    score: int
    summary: str


class AuditRunResponse(BaseModel):
    id: int
    ts: datetime
    score: int
    summary: str
    partial: bool
    partial_reason: str | None
    findings: list[FindingItem]
    ports: list[PortItem]
    security: SecurityConfigPayload | None
    score_breakdown: list[ScoreLineItem]


class AuditDetailResponse(BaseModel):
    audit: AuditSummary | None
    findings: list[FindingItem]


class AuditListResponse(BaseModel):
    audits: list[AuditSummary]


def _finding_item(f: dict) -> FindingItem:
    """Mapeia uma linha persistida de finding (chave `finding_key`) para a API."""
    return FindingItem(
        id=f["finding_key"],
        title=f["title"],
        severity=f["severity"],
        category=f["category"],
        description=f["description"],
        recommendation=f["recommendation"],
        evidence=f["evidence"],
    )


# Síncrono de propósito: roda psutil + PowerShell + SQLite (I/O bloqueante) →
# threadpool do FastAPI, sem travar o event loop.
@router.post("/audit/run", response_model=AuditRunResponse)
def post_audit_run() -> AuditRunResponse:
    """Roda uma auditoria completa, persiste e devolve o resultado detalhado."""
    result = run_audit()
    security = None
    if result.security is not None:
        security = SecurityConfigPayload(
            firewall=result.security.firewall,
            defender=DefenderPayload(**result.security.defender),
            antivirus=result.security.antivirus,
            last_hotfix=result.security.last_hotfix,
        )
    return AuditRunResponse(
        id=result.id,
        ts=result.ts,
        score=result.score,
        summary=result.summary,
        partial=result.partial,
        partial_reason=result.partial_reason,
        findings=[
            FindingItem(
                id=f.id,
                title=f.title,
                severity=f.severity.value,
                category=f.category,
                description=f.description,
                recommendation=f.recommendation,
                evidence=f.evidence,
            )
            for f in result.findings
        ],
        ports=[PortItem(**vars(p)) for p in result.ports],
        security=security,
        score_breakdown=[ScoreLineItem(**vars(s)) for s in result.score_breakdown],
    )


@router.get("/audit/latest", response_model=AuditDetailResponse)
def get_audit_latest() -> AuditDetailResponse:
    """Auditoria mais recente persistida + seus findings (audit=None se nenhuma)."""
    audit = get_latest_audit()
    if audit is None:
        return AuditDetailResponse(audit=None, findings=[])
    findings = [_finding_item(f) for f in get_findings(audit["id"])]
    return AuditDetailResponse(audit=AuditSummary(**audit), findings=findings)


@router.get("/audit", response_model=AuditListResponse)
def get_audit_history() -> AuditListResponse:
    """Histórico de auditorias (resumos), mais recentes primeiro."""
    return AuditListResponse(audits=[AuditSummary(**a) for a in list_audits()])


@router.get("/audit/{audit_id}", response_model=AuditDetailResponse)
def get_audit_detail(audit_id: int) -> AuditDetailResponse:
    """Uma auditoria pelo id + seus findings. 404 se não existe."""
    audit = get_audit(audit_id)
    if audit is None:
        raise HTTPException(status_code=404, detail=f"auditoria {audit_id} não encontrada")
    findings = [_finding_item(f) for f in get_findings(audit_id)]
    return AuditDetailResponse(audit=AuditSummary(**audit), findings=findings)
