"""Motor de alertas — aplica as regras (analyzer), não coleta.

Respeita ``duration_s``: a regra precisa permanecer violada por X segundos antes de
disparar. Mantém estado entre avaliações (desde quando viola e se já disparou) para
não repetir o mesmo alerta a cada amostra enquanto a violação persiste.
"""

from __future__ import annotations

import operator
from datetime import datetime

from models.schema import Alert, AlertRule, SystemMetrics

# Operadores suportados nas regras.
_OPERATORS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

# Métricas que uma regra pode observar (atributos de SystemMetrics).
_ALLOWED_METRICS = {"cpu_pct", "mem_pct", "disk_pct"}


class AlertEngine:
    """Avalia regras contra amostras sucessivas, com histerese por duração."""

    def __init__(self) -> None:
        # rule_id -> instante em que a violação começou.
        self._violating_since: dict[int, datetime] = {}
        # rule_id já disparados (evita alerta duplicado durante a mesma violação).
        self._fired: set[int] = set()

    def evaluate(
        self,
        metrics: SystemMetrics,
        rules: list[AlertRule],
        now: datetime,
    ) -> list[Alert]:
        """Retorna os alertas que dispararam nesta amostra."""
        fired: list[Alert] = []
        for rule in rules:
            if not rule.enabled or rule.metric not in _ALLOWED_METRICS:
                continue
            op = _OPERATORS.get(rule.operator)
            if op is None:
                continue

            value = float(getattr(metrics, rule.metric))
            if not op(value, rule.threshold):
                # Voltou ao normal: limpa o estado para permitir disparo futuro.
                self._violating_since.pop(rule.id, None)
                self._fired.discard(rule.id)
                continue

            since = self._violating_since.setdefault(rule.id, now)
            elapsed = (now - since).total_seconds()
            if elapsed >= rule.duration_s and rule.id not in self._fired:
                self._fired.add(rule.id)
                fired.append(
                    Alert(
                        rule_id=rule.id,
                        ts=now,
                        value=value,
                        message=(
                            f"{rule.metric} {rule.operator} {rule.threshold} "
                            f"(atual: {value:.1f})"
                        ),
                    )
                )
        return fired
