# AI Investment Intelligence Platform

A production-oriented, Kubernetes-native AI investment research and decision-support platform for monitoring and analyzing financial markets in Turkey, the United States, and Europe.

> **Phase 1 — Foundation is complete.**  
> The platform deploys cleanly to Kubernetes. Financial analysis, signals, and AI layers are added in Phases 2–11.

---

## Architecture

```text
Git Repository
      │
      ▼
CI / Docker Build
      │
      ▼
Container Registry
      │
      ▼
ArgoCD (GitOps)
      │
      ▼
Kubernetes Cluster — namespace: investment-platform
      │
  ┌───┼───────────┬────────────┐
  ▼   ▼           ▼            ▼
Frontend  Backend API    n8n        PostgreSQL
(React)   (FastAPI)   (Workflows)  (TimescaleDB-ready)
              │            │
              └────────────┘
                    │
                    ▼
              Analysis Engine  (Phase 3+)
                    │
                    ▼
               AI Analyst      (Phase 8+)
                    │
                    ▼
           Reports / Alerts    (Phase 9+)
```

### Responsibility split

| Layer | Tool | Responsible for |
|---|---|---|
| Deployment | ArgoCD + Helm | GitOps sync, Kubernetes resources |
| Orchestration | n8n | Scheduling, workflows, AI calls, email, alerts |
| Computation | FastAPI backend | All financial calculations, signals, DB writes |
| Storage | PostgreSQL | All persistent state |
| UI | React + Vite | Dashboard, charts, portfolio, watchlist |

---

## Project Structure

```
investment-platform/
├── backend/               Python/FastAPI backend
│   ├── app/
│   │   ├── api/           Route handlers
│   │   ├── core/          Config, logging
│   │   ├── database/      SQLAlchemy engine, session, base
│   │   ├── models/        ORM models          (Phase 2+)
│   │   ├── schemas/       Pydantic schemas    (Phase 2+)
│   │   ├── providers/     Data provider layer (Phase 2+)
│   │   ├── analytics/     Technical analysis  (Phase 3+)
│   │   ├── signals/       Signal engine       (Phase 6+)
│   │   ├── portfolio/     Portfolio logic     (Phase 10+)
│   │   └── ai/            AI analyst layer    (Phase 8+)
│   ├── alembic/           Database migrations
│   ├── tests/             pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/              React + TypeScript + Vite SPA
│   ├── src/
│   │   ├── components/    Reusable UI components
│   │   ├── pages/         Route-level page components
│   │   ├── services/      API client (axios)
│   │   ├── hooks/         React Query hooks
│   │   ├── charts/        Chart components    (Phase 2+)
│   │   └── types/         TypeScript interfaces
│   ├── nginx.conf         Production nginx config
│   └── Dockerfile
│
├── n8n/
│   └── workflows/         n8n workflow JSON exports
│
├── helm/
│   └── investment-platform/
│       ├── Chart.yaml     Declares postgresql sub-chart dependency
│       ├── values.yaml    Base defaults
│       ├── values-dev.yaml
│       ├── values-prod.yaml
│       └── templates/     All Kubernetes manifests as Helm templates
│
├── argocd/
│   └── investment-platform.yaml   ArgoCD Application CR
│
├── .env.example           Template for local development secrets
└── .gitignore
```

---

## Getting Started

### Prerequisites

- Docker
- Kubernetes cluster (local: [kind](https://kind.sigs.k8s.io/) or [k3s](https://k3s.io/))
- Helm 3.12+
- kubectl
- ArgoCD (optional for local, required for production GitOps)

### 1 — Configure secrets

```bash
cp .env.example .env
# Edit .env with real values (never commit this file)
```

### 2 — Build images

```bash
# Backend
docker build -t ghcr.io/your-org/investment-backend:dev ./backend

# Frontend
docker build -t ghcr.io/your-org/investment-frontend:dev ./frontend
```

### 3 — Deploy to Kubernetes with Helm

```bash
# Add Bitnami repo (once)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Download sub-chart dependencies
helm dependency update helm/investment-platform

# Lint
helm lint helm/investment-platform

# Dry-run to inspect manifests
helm template investment-platform helm/investment-platform \
  -f helm/investment-platform/values-dev.yaml \
  --set secrets.databasePassword=devpass \
  --set secrets.postgresPassword=devpost \
  --set secrets.n8nEncryptionKey=devkey00000000000000000000000000 \
  --set secrets.internalApiKey=devinternal

# Install
helm upgrade --install investment-platform helm/investment-platform \
  --namespace investment-platform-dev \
  --create-namespace \
  -f helm/investment-platform/values-dev.yaml \
  --set secrets.databasePassword=devpass \
  --set secrets.postgresPassword=devpost \
  --set secrets.n8nEncryptionKey=devkey00000000000000000000000000 \
  --set secrets.internalApiKey=devinternal \
  --set backend.image.registry=ghcr.io \
  --set backend.image.repository=your-org/investment-backend \
  --set backend.image.tag=dev \
  --set frontend.image.registry=ghcr.io \
  --set frontend.image.repository=your-org/investment-frontend \
  --set frontend.image.tag=dev
```

### 4 — GitOps with ArgoCD

1. Edit `argocd/investment-platform.yaml` — replace `YOUR_GIT_REPO_URL`.
2. Apply to your cluster:
   ```bash
   kubectl apply -f argocd/investment-platform.yaml
   ```
3. ArgoCD will sync the Helm chart from Git and deploy all resources automatically.

---

## Phase 1 Acceptance Criteria

| Criterion | How to verify |
|---|---|
| `helm lint` passes | `helm lint helm/investment-platform` |
| `helm template` renders | see dry-run command above |
| Docker images build | `docker build ./backend && docker build ./frontend` |
| Backend health endpoint | `curl http://<backend>/api/health` → `200 healthy` |
| Backend readiness endpoint | `curl http://<backend>/api/ready` → `200 ready` |
| Frontend serves | `curl http://<frontend>/` → HTML |
| n8n UI accessible | `kubectl port-forward svc/investment-platform-n8n 5678:5678` |
| n8n persists data | Workflows survive n8n pod restart |
| PostgreSQL persists data | Data survives PostgreSQL pod restart |
| n8n can call backend | n8n HTTP Request node → `http://investment-platform-backend:8000/api/health` |
| ArgoCD sync works | Application shows `Synced` / `Healthy` |
| Pods become Ready | `kubectl get pods -n investment-platform` — all `Running` |

---

## Development Phases

| Phase | Description |
|---|---|
| **1** ✅ | Kubernetes foundation: Docker, Helm, ArgoCD, Frontend, Backend, PostgreSQL, n8n |
| 2 | Database models + mock market data |
| 3 | Technical analysis engine (SMA, EMA, RSI, MACD, ATR, ADX, Bollinger, VWAP) |
| 4 | Fundamental analysis + valuation |
| 5 | News + official disclosures (KAP, SEC EDGAR, TCMB, FRED, ECB) |
| 6 | Signal engine (Long-term / Swing / Short-term) + Risk engine + Market regime |
| 7 | n8n workflows (daily analysis, news, ideas, portfolio) |
| 8 | AI analyst (structured data → interpretation → report) |
| 9 | Email + alerts |
| 10 | Portfolio + watchlist |
| 11 | Backtesting + AI prediction performance |

---

## Security Notes

- All secrets are injected at deploy time via `--set` or an external secrets operator.
- No secrets are stored in Git.
- All containers run as non-root where practical.
- NetworkPolicies enforce default-deny with explicit allow rules.
- The architecture supports future migration to External Secrets Operator, Vault, or Sealed Secrets without application changes.

---

## License

Private — all rights reserved.
