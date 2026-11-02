$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "No existe .venv. Crea el entorno e instala requirements-web.txt."
    exit 1
}
& $python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
