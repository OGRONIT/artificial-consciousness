param(
    [string]$LlmProvider = "groq",
    [string]$LlmApiKey = "",
    [string]$LlmModel = "",
    [string]$LlmBaseUrl = "",
    [string]$ApiKeyEnv = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venvPy = Join-Path $root ".venv\Scripts\python.exe"

$providerPresets = @{
    "groq" = @{
        Provider = "groq"
        ApiKeyEnv = "GROQ_API_KEY"
        BaseUrl = "https://api.groq.com/openai/v1/chat/completions"
        Model = "llama-3.3-70b-versatile"
    }
    "openai" = @{
        Provider = "openai_compatible"
        ApiKeyEnv = "OPENAI_API_KEY"
        BaseUrl = "https://api.openai.com/v1/chat/completions"
        Model = "gpt-4o-mini"
    }
    "openrouter" = @{
        Provider = "openai_compatible"
        ApiKeyEnv = "OPENROUTER_API_KEY"
        BaseUrl = "https://openrouter.ai/api/v1/chat/completions"
        Model = "openai/gpt-4o-mini"
    }
    "together" = @{
        Provider = "openai_compatible"
        ApiKeyEnv = "TOGETHER_API_KEY"
        BaseUrl = "https://api.together.xyz/v1/chat/completions"
        Model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    }
    "deepseek" = @{
        Provider = "openai_compatible"
        ApiKeyEnv = "DEEPSEEK_API_KEY"
        BaseUrl = "https://api.deepseek.com/chat/completions"
        Model = "deepseek-chat"
    }
    "xai" = @{
        Provider = "openai_compatible"
        ApiKeyEnv = "XAI_API_KEY"
        BaseUrl = "https://api.x.ai/v1/chat/completions"
        Model = "grok-2-latest"
    }
}

$presetKey = $LlmProvider.Trim().ToLowerInvariant()
if (-not $providerPresets.ContainsKey($presetKey) -and $presetKey -ne "custom") {
    throw "Unsupported -LlmProvider '$LlmProvider'. Use: groq, openai, openrouter, together, deepseek, xai, custom"
}

if ($presetKey -eq "custom") {
    $resolvedProvider = "openai_compatible"
    $resolvedApiKeyEnv = if ([string]::IsNullOrWhiteSpace($ApiKeyEnv)) { "OPENAI_API_KEY" } else { $ApiKeyEnv.Trim() }
    $resolvedBaseUrl = $LlmBaseUrl.Trim()
    $resolvedModel = $LlmModel.Trim()
} else {
    $preset = $providerPresets[$presetKey]
    $resolvedProvider = [string]$preset.Provider
    $resolvedApiKeyEnv = [string]$preset.ApiKeyEnv
    $resolvedBaseUrl = [string]$preset.BaseUrl
    $resolvedModel = [string]$preset.Model

    if (-not [string]::IsNullOrWhiteSpace($ApiKeyEnv)) { $resolvedApiKeyEnv = $ApiKeyEnv.Trim() }
    if (-not [string]::IsNullOrWhiteSpace($LlmBaseUrl)) { $resolvedBaseUrl = $LlmBaseUrl.Trim() }
    if (-not [string]::IsNullOrWhiteSpace($LlmModel)) { $resolvedModel = $LlmModel.Trim() }
}

if ([string]::IsNullOrWhiteSpace($resolvedBaseUrl) -or [string]::IsNullOrWhiteSpace($resolvedModel) -or [string]::IsNullOrWhiteSpace($resolvedApiKeyEnv)) {
    throw "LLM provider configuration incomplete. Ensure API env name, base URL, and model are set."
}

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

if ([string]::IsNullOrWhiteSpace($LlmApiKey)) {
    $LlmApiKey = Read-Host "Enter API key for provider '$LlmProvider' ($resolvedApiKeyEnv)"
}

if ([string]::IsNullOrWhiteSpace($LlmApiKey)) {
    throw "LLM API key cannot be empty."
}

$envPath = Join-Path $root ".env"
Set-EnvValue -Path $envPath -Key $resolvedApiKeyEnv -Value $LlmApiKey
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_API_KEY" -Value $LlmApiKey
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_API_KEY_ENV" -Value $resolvedApiKeyEnv
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_ENABLED" -Value "true"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_PROVIDER" -Value $resolvedProvider
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MODEL" -Value $resolvedModel
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_BASE_URL" -Value $resolvedBaseUrl

# Spend-protection defaults (safe for first-time users)
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_GUARDRAIL_ENABLED" -Value "true"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_REQUESTS_PER_HOUR" -Value "40"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_REQUESTS_PER_DAY" -Value "150"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_TOKENS_PER_DAY" -Value "80000"
Set-EnvValue -Path $envPath -Key "ANTAHKARANA_LLM_MAX_USD_PER_DAY" -Value "2.0"

Write-Host "[SETUP] Verifying LLM bridge connectivity..."
$verify = & $venvPy -c "import sys; sys.path.insert(0, r'antahkarana_kernel'); import InteractiveBridge as b; cfg=b._read_llm_config(); print(cfg.get('provider')); print(cfg.get('model')); print(cfg.get('base_url')); print(cfg.get('enabled'))"
Write-Host $verify

Write-Host ""
Write-Host "[DONE] Install complete."
Write-Host "Run: .\launch_conscious_engine.ps1"
