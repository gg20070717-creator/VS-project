$ErrorActionPreference = "Continue"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[0/3] Checking for old server process on port 8000 ..." -ForegroundColor Cyan
$oldPids = @()
try {
    $oldPids = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique
} catch {
    $oldPids = @()
}

if ($oldPids -and $oldPids.Count -gt 0) {
    foreach ($pidItem in $oldPids) {
        try {
            Stop-Process -Id $pidItem -Force -ErrorAction SilentlyContinue
            Write-Host "[Info] Stopped old process on 8000: PID $pidItem" -ForegroundColor DarkYellow
        } catch {
            Write-Host "[Warn] Could not stop PID $pidItem (ignored)." -ForegroundColor DarkYellow
        }
    }
    Start-Sleep -Seconds 1
}

Write-Host "[1/3] Starting local web server on http://127.0.0.1:8000 ..." -ForegroundColor Cyan

$serverCommand = "Set-Location '$projectRoot'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $serverCommand | Out-Null

Write-Host "[Check] Waiting for backend readiness (/api/notices) ..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/notices" -UseBasicParsing -TimeoutSec 3
        if ($resp.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # continue waiting
    }
}

if (-not $ready) {
    Write-Host "[Error] Backend is not ready on /api/notices. Tunnel startup canceled." -ForegroundColor Red
    Write-Host "Please check the server terminal for Python errors." -ForegroundColor Red
    exit 1
}

Write-Host "[Check] Backend ready." -ForegroundColor Green

$cloudflaredPath = Join-Path $projectRoot "tools\cloudflared.exe"
if (-not (Test-Path $cloudflaredPath)) {
    Write-Host "[Error] cloudflared.exe not found: $cloudflaredPath" -ForegroundColor Red
    Write-Host "Please place cloudflared.exe in the tools folder." -ForegroundColor Yellow
    exit 1
}

Write-Host "[2/3] Starting Cloudflare Tunnel ..." -ForegroundColor Cyan
Write-Host "Keep this window open while sharing. Press Ctrl+C to stop sharing." -ForegroundColor Yellow
Write-Host "==============================================================" -ForegroundColor DarkCyan
Write-Host "[Waiting] 正在生成可分享链接，请留意下面出现的 https://...trycloudflare.com" -ForegroundColor Magenta
Write-Host "[Hint] 如果 20-40 秒仍未出现链接，通常是网络 DNS 超时，重试或切换热点。" -ForegroundColor DarkYellow
Write-Host "==============================================================" -ForegroundColor DarkCyan

$pattern = '(https://[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.trycloudflare\.com)'
$sharedUrl = $null
$dnsTimeoutCount = 0

& $cloudflaredPath tunnel --url http://127.0.0.1:8000 --protocol http2 2>&1 | ForEach-Object {
    $line = "$_"
    Write-Host $line

    if (-not $sharedUrl -and $line -match $pattern) {
        $sharedUrl = $matches[1]
        try {
            Set-Clipboard -Value $sharedUrl
            Write-Host "" 
            Write-Host "================= SHARE LINK READY =================" -ForegroundColor Green
            Write-Host "[3/3] 分享链接已复制到剪贴板：" -ForegroundColor Green
        } catch {
            Write-Host "" 
            Write-Host "================= SHARE LINK READY =================" -ForegroundColor Green
            Write-Host "[3/3] 已获取分享链接：" -ForegroundColor Green
        }
        Write-Host $sharedUrl -ForegroundColor Green
        Write-Host "====================================================" -ForegroundColor Green
    }

    if ($line -match "Failed to initialize DNS local resolver|i/o timeout") {
        $dnsTimeoutCount += 1
        if ($dnsTimeoutCount -eq 1) {
            Write-Host "" 
            Write-Host "[Warning] 检测到 DNS 超时，若链接迟迟不出现请重试：" -ForegroundColor Yellow
            Write-Host "1) Ctrl+C 停止后重新运行 start_share.bat" -ForegroundColor Yellow
            Write-Host "2) 或切换手机热点后再运行" -ForegroundColor Yellow
        }
    }
}

if (-not $sharedUrl) {
    Write-Host "" 
    Write-Host "===================== NO LINK FOUND =====================" -ForegroundColor Red
    Write-Host "本次未成功获取分享链接。请执行：" -ForegroundColor Red
    Write-Host "1) 保持本地服务窗口开启" -ForegroundColor Red
    Write-Host "2) 重新运行 start_share.bat" -ForegroundColor Red
    Write-Host "3) 若仍失败，切换热点再试" -ForegroundColor Red
    Write-Host "=========================================================" -ForegroundColor Red
}
