$ErrorActionPreference = "Stop"

$HostIp = "127.0.0.1"
$Port = 4000
$WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ConfigPath = Join-Path $PSScriptRoot "litellm_copilot_config.yaml"
$LiteLLMExe = Join-Path $WorkspaceRoot "environments\pvz_env\Scripts\litellm.exe"

$env:LITELLM_LOG = "INFO"

if (-not (Test-Path $LiteLLMExe)) {
	throw "LiteLLM executable not found: $LiteLLMExe"
}

if (-not (Test-Path $ConfigPath)) {
	throw "Config file not found: $ConfigPath"
}

# Stop stale litellm.exe processes so localhost:4000 stays stable for Claude Code.
$stale = Get-CimInstance Win32_Process -Filter "name = 'litellm.exe'" -ErrorAction SilentlyContinue
if ($stale) {
	Write-Host "Stopping stale LiteLLM processes..." -ForegroundColor Yellow
	foreach ($p in $stale) {
		try {
			Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop
		} catch {
			Write-Warning "Failed to stop process ID $($p.ProcessId): $($_.Exception.Message)"
		}
	}
}

$occupied = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($occupied) {
	$pids = ($occupied | Select-Object -ExpandProperty OwningProcess -Unique) -join ", "
	throw "Port $Port is already in use by process ID(s): $pids"
}

Write-Host "Starting LiteLLM proxy on http://${HostIp}:$Port ..." -ForegroundColor Cyan
Write-Host "If this is your first GitHub Copilot request, LiteLLM will prompt device login in terminal." -ForegroundColor Yellow

& $LiteLLMExe --config $ConfigPath --host $HostIp --port $Port
