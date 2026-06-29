"""Analyzer de findings de segurança — aplica as regras sobre o dado cru.

Os collectors não decidem nada; é aqui que mora a "inteligência" da auditoria:
quais sinais viram achado e qual severidade. Porta da lógica do security_audit
(regra de portas) + regras de configuração (firewall/Defender).
"""

from __future__ import annotations

from models.schema import Finding, PortInfo, SecurityConfig, Severity

# Portas que, expostas na rede, costumam ser risco real.
_RISKY_PORTS = {
    23: "Telnet (tráfego sem criptografia)",
    21: "FTP (tráfego sem criptografia)",
    445: "SMB (alvo comum de ransomware/worm)",
    3389: "RDP (alvo comum de força bruta)",
    3306: "MySQL exposto",
    1433: "MS SQL Server exposto",
    5432: "PostgreSQL exposto",
    6379: "Redis (sem auth por padrão)",
    27017: "MongoDB exposto",
}


def from_ports(ports: list[PortInfo]) -> list[Finding]:
    """Achados a partir das portas em escuta."""
    findings: list[Finding] = []
    for p in ports:
        if p.port in _RISKY_PORTS and p.public:
            findings.append(
                Finding(
                    id=f"PORT-{p.port}-PUBLIC",
                    title=f"Porta de risco {p.port}/{p.protocol} exposta na rede",
                    severity=Severity.HIGH,
                    category="ports",
                    description=(
                        f"{_RISKY_PORTS[p.port]}. Escutando em {p.address} "
                        f"(acessível pela rede), dona: {p.process or '?'}."
                    ),
                    recommendation=(
                        "Restrinja ao localhost (127.0.0.1) ou bloqueie no firewall "
                        "se o acesso externo não for necessário."
                    ),
                    evidence={
                        "port": p.port,
                        "address": p.address,
                        "process": p.process,
                        "pid": p.pid,
                    },
                )
            )
        elif p.port in _RISKY_PORTS and not p.public:
            findings.append(
                Finding(
                    id=f"PORT-{p.port}-LOCAL",
                    title=f"Serviço sensível {p.port}/{p.protocol} (apenas local)",
                    severity=Severity.LOW,
                    category="ports",
                    description=(
                        f"{_RISKY_PORTS[p.port]} escutando só em {p.address}. "
                        "Sem exposição à rede, risco baixo."
                    ),
                    recommendation="Confirme que o bind local é intencional.",
                    evidence={"port": p.port, "address": p.address, "process": p.process},
                )
            )

    public = [p for p in ports if p.public]
    if public:
        findings.append(
            Finding(
                id="PORT-SUMMARY",
                title=f"{len(public)} porta(s) escutando na rede",
                severity=Severity.INFO,
                category="ports",
                description="Resumo das portas acessíveis externamente.",
                evidence={
                    "ports": [f"{p.port}/{p.protocol} ({p.process})" for p in public]
                },
            )
        )
    return findings


def from_security(security: SecurityConfig | None) -> list[Finding]:
    """Achados a partir da configuração de segurança do Windows.

    Usa ``is False`` de propósito: dado ausente (None, coleta parcial) não vira
    achado — honestidade sobre limitações, sem afirmar algo não verificado.
    """
    if security is None:
        return []

    findings: list[Finding] = []

    for profile, enabled in security.firewall.items():
        if enabled is False:
            findings.append(
                Finding(
                    id=f"FW-{profile}",
                    title=f"Firewall do perfil {profile} desativado",
                    severity=Severity.HIGH,
                    category="firewall",
                    description=f"O firewall do perfil {profile} está desligado.",
                    recommendation="Ative o firewall para esse perfil de rede.",
                    evidence={"profile": profile},
                )
            )

    defender = security.defender or {}
    if defender.get("antivirus_enabled") is False:
        findings.append(
            Finding(
                id="DEF-AV",
                title="Antivírus (Defender) desativado",
                severity=Severity.HIGH,
                category="defender",
                description="O Microsoft Defender Antivírus está desativado.",
                recommendation="Ative o antivírus ou confirme um antivírus de terceiros ativo.",
            )
        )
    if defender.get("realtime_enabled") is False:
        findings.append(
            Finding(
                id="DEF-RT",
                title="Proteção em tempo real desativada",
                severity=Severity.HIGH,
                category="defender",
                description="A proteção em tempo real do Defender está desligada.",
                recommendation="Reative a proteção em tempo real.",
            )
        )
    return findings


def build_all(
    ports: list[PortInfo], security: SecurityConfig | None
) -> list[Finding]:
    """Junta os findings de todas as seções."""
    return from_ports(ports) + from_security(security)
