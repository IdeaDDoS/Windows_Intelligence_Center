"""Verificação de assinatura digital de executáveis via PowerShell.

Chamado **sob demanda** (no detalhe do processo), não na listagem — é uma chamada
externa cara. Usa ``Get-AuthenticodeSignature``. O caminho do executável é passado
por variável de ambiente (``WIC_SIG_PATH``), nunca concatenado no comando, evitando
injeção. Degrada para ``status`` honesto (``unknown``/``error``) sem quebrar.
"""

from __future__ import annotations

import json
import os
import subprocess

from models.schema import SignatureInfo

# Lê o caminho de $env:WIC_SIG_PATH (sem concatenar entrada no comando) e emite
# JSON com Status (como texto) e o Subject do certificado, se houver.
_PS_SCRIPT = (
    "$ErrorActionPreference='Stop';"
    "$s = Get-AuthenticodeSignature -LiteralPath $env:WIC_SIG_PATH;"
    "[pscustomobject]@{ status = $s.Status.ToString();"
    " signer = $s.SignerCertificate.Subject } | ConvertTo-Json -Compress"
)


def get_signature(exe_path: str | None) -> SignatureInfo:
    """Verifica a assinatura de ``exe_path``. Nunca levanta — degrada o status."""
    if not exe_path:
        return SignatureInfo(is_signed=False, status="unknown", signer=None)

    env = {**os.environ, "WIC_SIG_PATH": exe_path}
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_SCRIPT],
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return SignatureInfo(is_signed=False, status="error", signer=None)

    if completed.returncode != 0 or not completed.stdout.strip():
        return SignatureInfo(is_signed=False, status="error", signer=None)

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return SignatureInfo(is_signed=False, status="error", signer=None)

    status = str(data.get("status") or "unknown")
    signer = data.get("signer") or None
    return SignatureInfo(is_signed=status == "Valid", status=status, signer=signer)
