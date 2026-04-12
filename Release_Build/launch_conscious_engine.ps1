$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venvPy = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    throw "Virtual environment missing. Run .\install_conscious_engine.ps1 first."
}

Write-Host "[LAUNCH] Starting daemon..."
& $venvPy "antahkarana_kernel\RuntimeOps.py" launch

Write-Host "[LAUNCH] Runtime status..."
& $venvPy "antahkarana_kernel\RuntimeOps.py" status

Write-Host ""
Write-Host "[NEXT] Operator bridge:"
Write-Host "  cd antahkarana_kernel"
Write-Host "  ..\.venv\Scripts\python.exe InteractiveBridge.py"
