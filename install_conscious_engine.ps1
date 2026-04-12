param(
    [string]$GroqApiKey = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venvPy = Join-Path $root ".venv\Scripts\python.exe"

function Set-EnvValue {
    param(
        [string]$Path,
        [string]$Key,
        [string]$Value
    )
    $lines = New-Object System.Collections.Generic.List[string]
    if (Test-Path $Path) {
        $raw = [System.IO.File]::ReadAllText($Path)
        if (-not [string]::IsNullOrEmpty($raw)) {
            foreach ($ln in ($raw -split "`r?`n")) {
                if ($null -ne $ln) { [void]$lines.Add([string]$ln) }
            }
        }
    }

    $found = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^\s*$([Regex]::Escape($Key))=") {
            $lines[$i] = "$Key=$Value"
            $found = $true
        }
    }

    if (-not $found) {
        [void]$lines.Add("$Key=$Value")
    }

    $content = [string]::Join("`r`n", $lines)
    [System.IO.File]::WriteAllText($Path, $content, [System.Text.Encoding]::UTF8)
}

if (-not (Test-Path $venvPy)) {
    Write-Host "[SETUP] Creating virtual environment..."
    py -3 -m venv .venv
}

Write-Host "[SETUP] Installing dependencies..."
& $venvPy -m pip install --upgrade pip | Out-Null
& $venvPy -m pip install -r "antahkarana_kernel\requirements.txt" | Out-Null

if ([string]::IsNullOrWhiteSpace($GroqApiKey)) {
    $GroqApiKey = Read-Host "Enter GROQ_API_KEY"
}

if ([string]::IsNullOrWhiteSpace($GroqApiKey)) {
    throw "GROQ_API_KEY cannot be empty."
}

$envPath = Join-Path $root ".env"
Set-EnvValue -Path $envPath -Key "GROQ_API_KEY" -Value $GroqApiKey
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_ENABLED" -Value "true"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_PROVIDER" -Value "groq"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MODEL" -Value "llama-3.3-70b-versatile"

# Spend-protection defaults (safe for first-time users)
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_GUARDRAIL_ENABLED" -Value "true"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_REQUESTS_PER_HOUR" -Value "40"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_REQUESTS_PER_DAY" -Value "150"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_TOKENS_PER_DAY" -Value "80000"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_USD_PER_DAY" -Value "2.0"

Write-Host "[SETUP] Verifying LLM bridge connectivity..."
$verify = & $venvPy -c "import sys; sys.path.insert(0, r'antahkarana_kernel'); import InteractiveBridge as b; print(b._read_llm_config().get('provider')); print(b._read_llm_config().get('enabled'))"
Write-Host $verify

Write-Host ""
Write-Host "[DONE] Install complete."
Write-Host "Run: .\launch_conscious_engine.ps1"
