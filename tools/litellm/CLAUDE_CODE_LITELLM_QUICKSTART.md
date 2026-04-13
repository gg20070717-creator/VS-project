# Claude Code + GitHub Copilot + LiteLLM Quick Start

This workspace is preconfigured for one-click local proxy usage.

## What is already set

- LiteLLM config: `tools/litellm/litellm_copilot_config.yaml`
- Start script: `tools/litellm/start_litellm_copilot.ps1`
- Stop script: `tools/litellm/stop_litellm_copilot.ps1`
- Health/model/chat check: `tools/litellm/check_litellm_copilot.ps1`
- VS Code tasks: `.vscode/tasks.json`

## One-click usage in VS Code

1. Run task: `LiteLLM: Start Copilot Proxy`
2. Wait for terminal message: `Uvicorn running on http://127.0.0.1:4000`
3. Run task: `LiteLLM: Check Proxy`
4. If check passes, configure Claude Code to use this endpoint.

## Claude Code connection settings

Use these values:

- base_url: `http://127.0.0.1:4000/v1`
- api_key: `litellm-local-key`
- model: one from `GET /v1/models`

Recommended first model:

- `claude-sonnet-4-6`

Alternative models:

- `github_copilot/gpt-5`
- `github_copilot/gpt-5.3-codex`
- `github_copilot/claude-sonnet-4.5`

## Verification command (optional)

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:4000/v1/models" -Headers @{"Authorization"="Bearer litellm-local-key"} | ConvertTo-Json -Depth 8
```

## First-time GitHub Copilot auth

On first request, LiteLLM may trigger GitHub device login in terminal. Complete it once and retry.

## Stop proxy

Run task: `LiteLLM: Stop Copilot Proxy`
