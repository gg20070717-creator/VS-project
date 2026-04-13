$ErrorActionPreference = "Stop"

$targets = Get-CimInstance Win32_Process -Filter "name = 'litellm.exe'" -ErrorAction SilentlyContinue

if (-not $targets) {
    Write-Host "No litellm.exe process found." -ForegroundColor Yellow
    exit 0
}

foreach ($p in $targets) {
    try {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop
        Write-Host "Stopped litellm.exe PID=$($p.ProcessId)" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to stop PID=$($p.ProcessId): $($_.Exception.Message)"
    }
}

$stillListening = Get-NetTCPConnection -LocalPort 4000 -State Listen -ErrorAction SilentlyContinue
if ($stillListening) {
    $pidList = ($stillListening | Select-Object -ExpandProperty OwningProcess -Unique) -join ", "
    Write-Warning "Port 4000 is still occupied by PID(s): $pidList"
} else {
    Write-Host "Port 4000 is now free." -ForegroundColor Green
}
