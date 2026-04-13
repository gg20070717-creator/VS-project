[CmdletBinding()]
param(
    [string]$Model = ""
)

$ErrorActionPreference = "Stop"

$env:ANTHROPIC_BASE_URL = "http://127.0.0.1:4000"
$env:ANTHROPIC_API_KEY = "litellm-local-key"

# Optional fallback used by some OpenAI-compatible clients
$env:OPENAI_BASE_URL = "http://127.0.0.1:4000/v1"
$env:OPENAI_API_KEY = "litellm-local-key"
$env:CLAUDE_CODE_SIMPLE = "1"

$headers = @{
    "Authorization" = "Bearer $($env:ANTHROPIC_API_KEY)"
}

try {
    Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:4000/health/liveliness" -TimeoutSec 5 | Out-Null
} catch {
    Write-Host "LiteLLM proxy is not running. Please run task: LiteLLM: Start Copilot Proxy" -ForegroundColor Yellow
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Model)) {
    try {
        $modelsResp = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:4000/v1/models" -Headers $headers -TimeoutSec 10
        $modelIds = @($modelsResp.data | ForEach-Object { $_.id })
        if (-not $modelIds -or $modelIds.Count -eq 0) {
            throw "No models found from LiteLLM /v1/models"
        }

        Write-Host "Select model by number (original names):" -ForegroundColor Cyan
        for ($i = 0; $i -lt $modelIds.Count; $i++) {
            Write-Host ("[{0}] {1}" -f ($i + 1), $modelIds[$i])
        }

        $pick = Read-Host "Enter number"
        $idx = 0
        if (-not [int]::TryParse($pick, [ref]$idx) -or $idx -lt 1 -or $idx -gt $modelIds.Count) {
            throw "Invalid selection: $pick"
        }
        $Model = $modelIds[$idx - 1]
    } catch {
        Write-Host "Could not fetch model list. Falling back to github_copilot/gpt-4.1" -ForegroundColor Yellow
        $Model = "github_copilot/gpt-4.1"
    }
}

Write-Host "Starting Claude Code with LiteLLM endpoint..." -ForegroundColor Cyan
Write-Host "ANTHROPIC_BASE_URL=$env:ANTHROPIC_BASE_URL" -ForegroundColor DarkGray
Write-Host "Model: $Model" -ForegroundColor DarkGray

# Ensure Claude uses API-key mode instead of account-login mode.
& "C:\Users\muziguoguozhu\AppData\Roaming\npm\claude.ps1" auth logout | Out-Null

# Preflight: verify Claude can reach LiteLLM before opening interactive UI.
try {
    $preflight = & "C:\Users\muziguoguozhu\AppData\Roaming\npm\claude.ps1" -p "Reply with exactly OK" --model $Model
    if ($preflight -notmatch "OK") {
        throw "Preflight response did not contain OK"
    }
} catch {
    Write-Host "Preflight failed. Claude could not reach LiteLLM." -ForegroundColor Red
    Write-Host "Please run task: LiteLLM: Check Proxy" -ForegroundColor Yellow
    exit 1
}

& "C:\Users\muziguoguozhu\AppData\Roaming\npm\claude.ps1" --model $Model
