"""Coletor de configuração de segurança do Windows via PowerShell.

Faz uma única chamada que reúne firewall (por perfil), Defender (antivírus/tempo
real/assinaturas), antivírus de terceiros e a data do último hotfix. Collector só
coleta e normaliza. Degrada para ``partial`` (sem quebrar) fora do Windows ou quando
falta dado — vários itens só retornam completos em terminal de administrador.
"""

from __future__ import annotations

import json
import platform
import subprocess
import time

from models.schema import CollectorMeta, SecurityConfig

# Coleta tudo num PSCustomObject e emite JSON. SilentlyContinue para que um cmdlet
# indisponível (sem privilégio) deixe a seção nula em vez de abortar.
_PS_SCRIPT = (
    "$ErrorActionPreference='SilentlyContinue';"
    "$fw = @(Get-NetFirewallProfile | "
    "Select-Object Name,@{N='Enabled';E={[bool]$_.Enabled}});"
    "$d = Get-MpComputerStatus;"
    "$def = if ($d) { [pscustomobject]@{"
    " antivirus_enabled=[bool]$d.AntivirusEnabled;"
    " realtime_enabled=[bool]$d.RealTimeProtectionEnabled;"
    " signatures_last_updated=$(if ($d.AntivirusSignatureLastUpdated)"
    " { $d.AntivirusSignatureLastUpdated.ToString('yyyy-MM-dd') } else { $null }) } }"
    " else { $null };"
    "$av = @(Get-CimInstance -Namespace root/SecurityCenter2"
    " -ClassName AntiVirusProduct | Select-Object -ExpandProperty displayName);"
    "$h = (Get-HotFix | Sort-Object InstalledOn -Descending |"
    " Select-Object -First 1).InstalledOn;"
    "$hotfix = if ($h) { $h.ToString('yyyy-MM-dd') } else { $null };"
    "[pscustomobject]@{ firewall=$fw; defender=$def; antivirus=$av; hotfix=$hotfix }"
    " | ConvertTo-Json -Depth 5 -Compress"
)


def _truthy(value: object) -> bool:
    return value in (True, 1, "1", "True", "true", "Enabled")


def collect_security_config() -> tuple[SecurityConfig | None, CollectorMeta]:
    """Coleta firewall, Defender, antivírus de terceiros e último hotfix."""
    started = time.perf_counter()

    def _meta(partial: bool, reason: str | None) -> CollectorMeta:
        return CollectorMeta(
            source="security_config",
            partial=partial,
            reason=reason,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    if platform.system() != "Windows":
        return SecurityConfig(), _meta(True, "coleta de segurança só no Windows")

    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_SCRIPT],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return SecurityConfig(), _meta(True, f"falha ao executar PowerShell: {exc}")

    out = (completed.stdout or "").strip()
    if not out:
        return SecurityConfig(), _meta(True, "PowerShell não retornou dados")

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return SecurityConfig(), _meta(True, "resposta do PowerShell ilegível")

    firewall: dict[str, bool] = {}
    fw_raw = data.get("firewall")
    if isinstance(fw_raw, dict):  # único perfil vem como objeto
        fw_raw = [fw_raw]
    for item in fw_raw or []:
        name = item.get("Name")
        if name:
            firewall[str(name)] = _truthy(item.get("Enabled"))

    defender: dict[str, object] = {}
    def_raw = data.get("defender")
    if isinstance(def_raw, dict):
        defender = {
            "antivirus_enabled": def_raw.get("antivirus_enabled"),
            "realtime_enabled": def_raw.get("realtime_enabled"),
            "signatures_last_updated": def_raw.get("signatures_last_updated"),
        }

    av_raw = data.get("antivirus")
    if isinstance(av_raw, str):
        antivirus = [av_raw]
    else:
        antivirus = [str(a) for a in (av_raw or [])]

    config = SecurityConfig(
        firewall=firewall,
        defender=defender,
        antivirus=antivirus,
        last_hotfix=data.get("hotfix"),
    )

    partial = not firewall or not defender
    reason = "dados incompletos (rode como administrador)" if partial else None
    return config, _meta(partial, reason)
