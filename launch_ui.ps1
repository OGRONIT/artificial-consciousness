# Load .env file and start the UI
$envFile = ".\.env"

if (Test-Path $envFile) {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Cyan
    Get-Content $envFile | ForEach-Object {
        if ($_ -and -not $_.StartsWith("#")) {
            $parts = $_ -split "=", 2
            if ($parts.Count -eq 2) {
                $name = $parts[0].Trim()
                $value = $parts[1].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, 'Process')
                Write-Host "✓ Set: $name" -ForegroundColor Green
            }
        }
    }
} else {
    Write-Host "ERROR: .env file not found at $envFile" -ForegroundColor Red
    Write-Host "Create .env in project root (see .env.example) and set your LLM provider key." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Launching Mission Control UI..." -ForegroundColor Cyan
Write-Host ""

python antahkarana_kernel\UnifiedConsciousnessUI.py
