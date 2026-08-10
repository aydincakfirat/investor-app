# n8n Workflows

This directory contains exported n8n workflow JSON files.

Workflows are imported into the running n8n instance and are stored
persistently in PostgreSQL. The JSON exports here serve as version-controlled
backups and as the source of truth for GitOps-based workflow management.

## Planned Workflows (Phase 7+)

| File | Trigger | Description |
|---|---|---|
| `daily-market-analysis.json` | Cron 06:00 UTC | Collect data → backend analysis → AI → email report |
| `important-news.json` | Webhook / polling | Detect important news → score → alert |
| `daily-investment-ideas.json` | Cron 07:00 UTC | Signal engine → rank → AI analyst → report |
| `portfolio-analysis.json` | Cron / on-demand | Portfolio metrics → risk → AI → report |
| `kap-disclosure.json` | Polling | KAP official disclosure → importance score → alert |
| `sec-edgar.json` | Polling | SEC EDGAR filing → importance score → alert |

## How to import

1. Open the n8n UI (port-forward or Ingress URL).
2. Go to **Workflows → Import from File**.
3. Select the JSON file from this directory.

## How to export

After editing a workflow in the UI:
1. Open the workflow.
2. Click the three-dot menu → **Download**.
3. Save the JSON to this directory and commit to Git.

## Calling the backend

n8n communicates with the backend using the Kubernetes Service DNS name:

```
http://investment-platform-backend:8000/api/...
```

Internal endpoints requiring authentication use the `INTERNAL_API_KEY`
environment variable injected from the Kubernetes Secret.

Example HTTP Request node configuration:
```json
{
  "method": "POST",
  "url": "http://investment-platform-backend:8000/api/internal/market-analysis",
  "headers": {
    "X-Internal-API-Key": "={{ $env.INTERNAL_API_KEY }}"
  }
}
```
