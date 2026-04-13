[CmdletBinding()]
param(
    [string]$Model = ""
)

$ErrorActionPreference = "Stop"

$env:ANTHROPIC_BASE_URL = "http://127.0.0.1:4000"
$env:ANTHROPIC_API_KEY = "litellm-local-key"
$env:CLAUDE_CODE_SIMPLE = "1"

$headers = @{
    "Authorization" = "Bearer $($env:ANTHROPIC_API_KEY)"
}

$claude = "C:\Users\muziguoguozhu\AppData\Roaming\npm\claude.ps1"

try {
    Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:4000/health/liveliness" -TimeoutSec 5 | Out-Null
} catch {
    Write-Host "LiteLLM proxy is not running. Run task: LiteLLM: Start Copilot Proxy" -ForegroundColor Yellow
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

Write-Host "Claude LiteLLM Chat (no web login)" -ForegroundColor Cyan
Write-Host "Model: $Model" -ForegroundColor DarkGray
Write-Host "Use original names from GitHub Copilot list (e.g. github_copilot/gpt-4.1)" -ForegroundColor DarkGray
Write-Host "Type 'exit' to quit." -ForegroundColor DarkGray

while ($true) {
    $prompt = Read-Host "You"
    if ($null -eq $prompt) { continue }
    $trimmed = $prompt.Trim()
    if ($trimmed -eq "") { continue }
    if ($trimmed -eq "exit") { break }

    try {
        $reply = & $claude -p $trimmed --model $Model
        Write-Host "Claude: $reply" -ForegroundColor Green
    } catch {
        Write-Host "Request failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}
