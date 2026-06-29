"""Analyzer de score — deriva a nota dos findings (single source of truth).

O score parte de 100 e desconta por severidade. Fica amarrado aos achados reais
e escala com a gravidade; cada ponto perdido carrega o motivo, então "se explica".
"""

from __future__ import annotations

from models.schema import Finding, ScoreLine, SEVERITY_WEIGHT


def compute(findings: list[Finding]) -> tuple[int, list[ScoreLine]]:
    """Calcula o score (0–100) e o detalhamento das deduções."""
    score = 100
    breakdown: list[ScoreLine] = []
    for f in findings:
        delta = -SEVERITY_WEIGHT[f.severity]
        if delta == 0:
            continue  # INFO não tira ponto
        score += delta
        breakdown.append(
            ScoreLine(label=f"{f.severity.value.upper()}: {f.title}", delta=delta)
        )
    score = max(0, min(100, score))
    if not breakdown:
        breakdown.append(ScoreLine(label="Nenhum problema com peso de score", delta=0))
    return score, breakdown
