$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:4000"
$apiKey = "litellm-local-key"
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

Write-Host "1) Health check..." -ForegroundColor Cyan
$health = Invoke-RestMethod -Method Get -Uri "$baseUrl/health/liveliness" -TimeoutSec 10
Write-Host "   Health: $health" -ForegroundColor Green

Write-Host "2) Fetch model list..." -ForegroundColor Cyan
$modelsResp = Invoke-RestMethod -Method Get -Uri "$baseUrl/v1/models" -Headers @{"Authorization" = "Bearer $apiKey"} -TimeoutSec 20
$modelIds = @($modelsResp.data | ForEach-Object { $_.id })
Write-Host "   Model count: $($modelIds.Count)" -ForegroundColor Green

$preferred = @(
    "claude-sonnet-4-6",
    "claude-opus-4-6",
    "claude-haiku-4-5",
    "github_copilot/gpt-4",
    "github_copilot/gpt-4o",
    "github_copilot/gpt-5",
    "github_copilot/gpt-5.3-codex"
)
$candidates = $preferred | Where-Object { $modelIds -contains $_ }
if (-not $candidates -or $candidates.Count -eq 0) {
    throw "No preferred test models found in /v1/models."
}

Write-Host "3) Run chat completion smoke test..." -ForegroundColor Cyan
$ok = $false
foreach ($testModel in $candidates) {
    Write-Host "   Trying: $testModel" -ForegroundColor Yellow
    $body = @{
        model = $testModel
        messages = @(
            @{
                role = "user"
                content = "Reply with exactly: OK"
            }
        )
    } | ConvertTo-Json -Depth 8

    try {
        $resp = Invoke-RestMethod -Method Post -Uri "$baseUrl/v1/chat/completions" -Headers $headers -Body $body -TimeoutSec 60
        $text = $resp.choices[0].message.content
        Write-Host "   Success model: $testModel" -ForegroundColor Green
        Write-Host "   Reply: $text" -ForegroundColor Green
        $ok = $true
        break
    } catch {
        Write-Warning "Model failed: $testModel"
    }
}

if (-not $ok) {
    throw "Smoke test failed for all candidate models."
}

Write-Host "All checks passed." -ForegroundColor Green
