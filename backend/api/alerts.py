"""Endpoints de alertas: listar disparos, reconhecer e configurar regras."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from storage.repositories import (
    ack_alert,
    create_alert_rule,
    get_alert_rule,
    list_alert_rules,
    list_alerts,
    update_alert_rule,
)

router = APIRouter()

MetricName = Literal["cpu_pct", "mem_pct", "disk_pct"]
Operator = Literal[">", ">=", "<", "<="]


class AlertOut(BaseModel):
    id: int
    rule_id: int
    ts: datetime
    value: float
    message: str
    acknowledged: bool


class AlertListResponse(BaseModel):
    alerts: list[AlertOut]


class AlertRuleOut(BaseModel):
    id: int
    metric: str
    operator: str
    threshold: float
    duration_s: int
    enabled: bool


class AlertRuleListResponse(BaseModel):
    rules: list[AlertRuleOut]


class AlertRuleInput(BaseModel):
    metric: MetricName
    operator: Operator
    threshold: float
    duration_s: int = 0
    enabled: bool = True


class AlertRuleUpdate(BaseModel):
    metric: MetricName | None = None
    operator: Operator | None = None
    threshold: float | None = None
    duration_s: int | None = None
    enabled: bool | None = None


# Handlers síncronos: tocam o SQLite (I/O bloqueante) → threadpool do FastAPI.
@router.get("/alerts", response_model=AlertListResponse)
def get_alerts() -> AlertListResponse:
    """Alertas disparados, mais recentes primeiro."""
    return AlertListResponse(alerts=[AlertOut(**a) for a in list_alerts()])


@router.post("/alerts/{alert_id}/ack", response_model=AlertOut)
def acknowledge_alert(alert_id: int) -> AlertOut:
    """Reconhece um alerta. 404 se o alerta não existe."""
    if not ack_alert(alert_id):
        raise HTTPException(status_code=404, detail=f"alerta {alert_id} não encontrado")
    found = next((a for a in list_alerts() if a["id"] == alert_id), None)
    if found is None:  # corrida improvável; mantém o contrato honesto
        raise HTTPException(status_code=404, detail=f"alerta {alert_id} não encontrado")
    return AlertOut(**found)


@router.get("/alert_rules", response_model=AlertRuleListResponse)
def get_alert_rules() -> AlertRuleListResponse:
    """Lista todas as regras de alerta."""
    return AlertRuleListResponse(rules=[AlertRuleOut(**r) for r in list_alert_rules()])


@router.post("/alert_rules", response_model=AlertRuleOut, status_code=201)
def post_alert_rule(payload: AlertRuleInput) -> AlertRuleOut:
    """Cria uma regra de alerta."""
    rule_id = create_alert_rule(
        metric=payload.metric,
        operator=payload.operator,
        threshold=payload.threshold,
        duration_s=payload.duration_s,
        enabled=payload.enabled,
    )
    created = get_alert_rule(rule_id)
    assert created is not None  # acabou de ser criada
    return AlertRuleOut(**created)


@router.put("/alert_rules/{rule_id}", response_model=AlertRuleOut)
def put_alert_rule(rule_id: int, payload: AlertRuleUpdate) -> AlertRuleOut:
    """Edita uma regra existente. 404 se a regra não existe."""
    if get_alert_rule(rule_id) is None:
        raise HTTPException(status_code=404, detail=f"regra {rule_id} não encontrada")
    update_alert_rule(rule_id, payload.model_dump(exclude_none=True))
    updated = get_alert_rule(rule_id)
    assert updated is not None
    return AlertRuleOut(**updated)
