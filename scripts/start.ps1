# Sobe backend (:8000) e frontend (:5173) em paralelo, espelhando o dev.ps1 do
# molde us-media. Cada serviço abre numa janela própria do PowerShell.
#
# Uso:
#   .\scripts\start.ps1            # usa a venv do backend se existir
#
# Pré-requisitos (uma vez): criar a venv e instalar dependências —
#   cd backend; python -m venv .venv; .venv\Scripts\pip install -r requirements.txt
#   cd frontend; npm install

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

# Backend — prefere o uvicorn da venv; cai para o do PATH se a venv não existir.
$venvUvicorn = Join-Path $backend ".venv\Scripts\uvicorn.exe"
if (Test-Path $venvUvicorn) {
    $backendCmd = "cd '$backend'; .venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
} else {
    Write-Warning "venv não encontrada em $backend\.venv — usando o uvicorn do PATH."
    $backendCmd = "cd '$backend'; uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontend'; npm run dev"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
