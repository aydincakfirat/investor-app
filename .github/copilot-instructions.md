# Copilot Instructions for Investment Intelligence Platform

This file documents the high-level architecture, build/test commands, and key conventions for the investment platform repository. Use this to understand how to work effectively in this codebase.

---

## Overview

**Investment Intelligence Platform** is a production-oriented, Kubernetes-native AI investment research system comprising:

- **Frontend**: React + TypeScript + Vite SPA (port 3000)
- **Backend**: FastAPI + SQLAlchemy + async/await (port 8000)
- **Orchestration**: n8n for workflows (port 5678)
- **Database**: PostgreSQL (planned: TimescaleDB for time-series)
- **Deployment**: Kubernetes with Helm + ArgoCD (GitOps)

The project is in **Phase 1** (foundation). Phase 2+ add financial analysis, signals, and AI layers.

### Repository Structure

```
├── backend/              # Python/FastAPI service
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── core/         # Config, logging
│   │   ├── database/     # SQLAlchemy engine, session, base
│   │   ├── models/       # ORM models (Phase 2+)
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   └── services/     # Business logic layer
│   ├── alembic/          # Database migrations
│   ├── tests/            # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/             # React/TypeScript SPA
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route-level pages
│   │   ├── services/     # axios-based API client
│   │   ├── hooks/        # React Query custom hooks
│   │   └── types/        # TypeScript interfaces
│   ├── vite.config.ts
│   └── Dockerfile
│
├── helm/                 # Kubernetes deployment via Helm chart
│   └── investment-platform/
│       ├── values.yaml   # Base configuration
│       ├── values-dev.yaml
│       ├── values-prod.yaml
│       └── templates/    # Kubernetes manifests as Helm templates
│
├── n8n/                  # Workflow orchestration
│   └── workflows/        # Exported n8n workflow JSON
│
├── argocd/               # GitOps application definition
│   └── investment-platform.yaml
│
├── scripts/              # Setup, build, deploy scripts
├── Makefile              # Convenience targets (see below)
└── .github/workflows/    # CI/CD pipelines
```

---

## Build, Test & Lint Commands

### Makefile Targets (Recommended)

All commands are defined in the `Makefile`. Key targets:

```bash
# First-time setup (Helm repos, namespace, ArgoCD install)
make setup

# Build Docker images locally
make build               # Builds backend + frontend
make build IMAGE_TAG=1.2.3  # With custom tag

# Push to GitHub Container Registry (ghcr.io)
make push                # Requires GITHUB_TOKEN environment variable

# Deploy to Kubernetes
make deploy              # Dev namespace (investment-platform-dev)
make deploy-prod         # Production namespace (requires DB_PASSWORD, N8N_KEY, INTERNAL_KEY)

# Testing & linting
make test                # Backend pytest (see below for single test)
make lint                # Helm lint

# Cluster operations
make status              # Show pods, services, ingress
make forward             # Port-forward (frontend:3000, backend:8000, n8n:5678)
make logs-backend        # Tail backend logs
make logs-n8n            # Tail n8n logs
make logs-postgres       # Tail PostgreSQL logs
make db-shell            # psql into the database
make db-migrate          # Run alembic migrations

# GitOps (ArgoCD)
make argocd              # Register ArgoCD Application
make argocd-sync         # Force sync
make argocd-ui           # Port-forward ArgoCD UI (http://localhost:8080)

# Cleanup
make clean               # Delete dev namespace (with confirmation)
```

### Backend Tests

**Run all backend tests:**
```bash
cd backend && python -m pytest
```

**Run a single test file:**
```bash
cd backend && python -m pytest tests/test_health.py -v
```

**Run a single test function:**
```bash
cd backend && python -m pytest tests/test_health.py::test_health_endpoint -v
```

**Run only fast tests (skip integration tests marked `@pytest.mark.integration`):**
```bash
cd backend && python -m pytest -m "not integration"
```

**Pytest configuration** is in `backend/pytest.ini`:
- Async mode: `auto` (via `pytest-asyncio`)
- Default test path: `tests/`
- Markers: `integration` (requires PostgreSQL), `slow`

**Test database**: Unit tests use SQLite in-memory (via `aiosqlite`). Integration tests require a running PostgreSQL instance (provided by GitHub Actions or `make forward`).

### Frontend Build

**Development (local dev server with HMR):**
```bash
cd frontend && npm run dev
# Serves on http://localhost:5173
```

**Production build:**
```bash
cd frontend && npm run build
# Output: dist/
```

**Type check:**
```bash
cd frontend && npm run type-check  # Run tsc --noEmit
```

**Lint:**
```bash
cd frontend && npm run lint  # ESLint with TypeScript support
```

### Helm & Kubernetes

**Lint Helm chart:**
```bash
make lint
# Or manually:
helm lint helm/investment-platform \
  -f helm/investment-platform/values-dev.yaml \
  --set secrets.databasePassword=test \
  --set secrets.postgresPassword=test \
  --set secrets.n8nEncryptionKey=testkeyxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --set secrets.internalApiKey=testinternal
```

**Dry-run Helm deployment (preview manifests):**
```bash
helm template investment-platform helm/investment-platform \
  -f helm/investment-platform/values-dev.yaml \
  --set secrets.databasePassword=test \
  --set secrets.postgresPassword=test \
  --set secrets.n8nEncryptionKey=testkeyxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --set secrets.internalApiKey=testinternal
```

---

## Architecture & Patterns

### Dependency Injection & Configuration

- **Settings**: Loaded from environment variables (and `.env` file locally) via `pydantic_settings.BaseSettings` in `backend/app/core/config.py`.
- **Lazy initialization**: Database engine, clients, etc. are initialized on first access (cached with `@lru_cache`).
- **Never hard-code secrets**: All sensitive values come from the environment at runtime.

### Backend Layers

```
Request → api/ (route handlers)
        → schemas/ (request/response validation with Pydantic)
        → services/ (business logic)
        → database/ (ORM queries)
        → Response
```

**Example pattern** (from Phase 1):
```python
# api/health.py
@router.get("/api/health")
async def health_check() -> dict:
    return {"status": "healthy"}

# schemas/health.py
class HealthResponse(BaseModel):
    status: str

# services/health.py
class HealthService:
    def get_health(self) -> HealthResponse:
        return HealthResponse(status="healthy")
```

### Database

- **Engine**: Async SQLAlchemy 2.0 with `asyncpg` driver.
- **Session**: Scoped async session factory in `database/session.py`.
- **Models**: SQLAlchemy ORM models in `models/` (not yet added in Phase 1).
- **Migrations**: Alembic in `alembic/` — run with `make db-migrate` or `alembic upgrade head`.

**Connection string format**: `postgresql+asyncpg://user:password@host:port/dbname`

### Frontend

- **Routing**: React Router v6 (pages in `src/pages/`).
- **State management**: React Query for server state (configured in hooks).
- **HTTP client**: Axios with typed services in `src/services/` (not yet fully implemented in Phase 1).
- **UI components**: Reusable components in `src/components/` (lucide-react for icons).
- **Types**: All TypeScript interfaces in `src/types/` for consistency.

### Kubernetes & Helm

- **Helm chart**: Single chart at `helm/investment-platform/` manages all microservices.
- **Sub-charts**: PostgreSQL pulled from Bitnami Helm repo (declared in `Chart.yaml`).
- **Values files**: Base (`values.yaml`), dev (`values-dev.yaml`), prod (`values-prod.yaml`).
- **Secrets**: Never committed to Git. Injected at deploy time via `--set` or external secret operator.
- **Labels**: All Kubernetes resources use labels like `app.kubernetes.io/name`, `app.kubernetes.io/version` for consistency.
- **Namespace**: Resources deploy to `investment-platform-dev` (local) or `investment-platform` (prod).

### GitOps (ArgoCD)

- **Application manifest**: `argocd/investment-platform.yaml`
- **Sync strategy**: Automatic (pull from Git, apply Helm chart).
- **Image updater**: Annotations in `argocd/investment-platform.yaml` support auto-detection of new tags on ghcr.io.

### CI/CD

- **Trigger**: Pushes to `main` or `develop` branches (or PRs) affecting `backend/`, `frontend/`, or `.github/workflows/`.
- **Jobs**:
  - `test-backend`: pytest on Python 3.12 with PostgreSQL service.
  - `test-frontend`: (build check with TypeScript).
  - `build-and-push`: Builds images and pushes to `ghcr.io` on successful tests (main branch only).

---

## Key Conventions

### Python (Backend)

1. **Async-first**: All I/O (DB, HTTP) uses async/await. Use `async def` and `await`.
2. **Logging**: Structured logging with `structlog`. All logs are JSON-serializable.
   ```python
   import structlog
   logger = structlog.get_logger(__name__)
   logger.info("action", key=value, **context)
   ```
3. **Error handling**: Raise `HTTPException(status_code=..., detail=...)` from `fastapi` for API errors.
4. **Database queries**: Use async SQLAlchemy ORM. Never run synchronous queries in async context.
5. **Type hints**: Always provide type hints (Python 3.12+).
6. **Docstrings**: Include module docstrings and function docstrings describing purpose and context.
7. **Testing**: Use `pytest` with `@pytest.mark.integration` for tests requiring PostgreSQL.

### TypeScript/React (Frontend)

1. **Type safety**: No `any` types. Always use explicit types or let TypeScript infer them.
2. **Component naming**: PascalCase for components (`MyComponent.tsx`), camelCase for other files.
3. **Imports**: Use absolute imports (via `tsconfig.json` paths, if configured) or relative imports with explicit `./` prefix.
4. **Hooks**: Custom React Query hooks in `src/hooks/` for fetching (e.g., `useInvestments()`, `usePortfolio()`).
5. **Services**: API calls isolated in `src/services/` with typed endpoints (axios instances).
6. **ESLint**: Strict rules enforce React best practices. Fix linting issues before committing.

### Kubernetes & Helm

1. **Manifest naming**: Use lowercase resource names with hyphens (`investment-platform-backend`, not `InvestmentPlatformBackend`).
2. **Labels**: Always include `app.kubernetes.io/name`, `app.kubernetes.io/version`, `app.kubernetes.io/managed-by: Helm`.
3. **Namespace isolation**: All resources in the same namespace (either `investment-platform-dev` or `investment-platform`).
4. **Secrets**: Use `.spec.template.spec.imagePullSecrets` for private image registries.
5. **Resource limits**: Define `requests` and `limits` for CPU and memory in all Pod specs.
6. **Health probes**: All services expose `/health` and `/ready` endpoints for liveness and readiness checks.

### Git

1. **Commit messages**: Clear, present tense ("Fix health endpoint", not "Fixed").
2. **Branch naming**: `feature/xyz`, `bugfix/xyz`, `docs/xyz`.
3. **Never commit secrets**: Use `.env.example` as a template; `.env` and `kubeconfig` are in `.gitignore`.
4. **PR reviews**: Each PR should modify a single subsystem or feature.

---

## Common Tasks

### Adding a new Backend API endpoint

1. **Define schema** in `backend/app/schemas/` (Pydantic model).
2. **Create service logic** in `backend/app/services/` (business logic).
3. **Add route** in `backend/app/api/` (FastAPI router).
4. **Write test** in `backend/tests/` (pytest).
5. **Run locally**: `make forward` and `curl http://localhost:8000/api/...`
6. **Commit & push**: CI runs tests and builds images.

### Adding a new Frontend page

1. **Create component** in `src/pages/PageName.tsx`.
2. **Define types** in `src/types/` if needed.
3. **Add route** in `src/App.tsx` (React Router).
4. **Add service** in `src/services/` for API calls (axios).
5. **Build & test**: `npm run build`, `npm run lint`.
6. **Commit & push**: CI builds the image.

### Adding a database migration

1. **Create migration**: `cd backend && alembic revision --autogenerate -m "description"`
2. **Edit** `backend/alembic/versions/xxxx_description.py` if needed.
3. **Test locally**: `make db-migrate`
4. **Commit** the migration file.
5. **CI/CD** will apply it on deploy.

### Deploying to production

1. **Tag a release**: `git tag v1.2.3 && git push --tags`
2. **CI** builds and pushes images to `ghcr.io/user/investment-backend:1.2.3`.
3. **Edit** `argocd/investment-platform.yaml` to update the image tag.
4. **Commit & push**: ArgoCD syncs automatically.
5. **Verify**: Check `make argocd-ui` or `kubectl get application`.

### Debugging in the cluster

```bash
# View logs
make logs-backend
make logs-n8n

# Connect to database
make db-shell

# Port-forward individual services
kubectl port-forward -n investment-platform-dev svc/investment-platform-backend 8000:8000

# Shell into a pod
kubectl exec -it POD_NAME -n investment-platform-dev -- /bin/bash

# Describe a resource
kubectl describe pod POD_NAME -n investment-platform-dev

# View events
kubectl get events -n investment-platform-dev --sort-by='.lastTimestamp'
```

---

## Environment Setup

**Local development prerequisites:**
- Docker
- Kubernetes cluster (kind, k3s, or Docker Desktop)
- Helm 3.12+
- kubectl
- Python 3.12+ (for backend local testing)
- Node.js 18+ (for frontend development)

**First-time setup:**
```bash
git clone https://github.com/your-org/investment-platform
cd investment-platform
cp .env.example .env
# Edit .env with your values (never commit .env)
make setup        # Install Helm repos, create namespace, deploy
make forward      # Port-forward to local services
# Visit http://localhost:3000 (frontend), http://localhost:8000/api/docs (backend)
```

---

## Resources & References

- **README.md**: High-level overview and phase roadmap.
- **.github/SETUP.md**: GitHub Secrets and CI/CD configuration (in Turkish).
- **Makefile**: All deployment and cluster commands.
- **FastAPI docs**: Auto-generated OpenAPI at `http://localhost:8000/api/docs`.
- **Helm values**: Study `helm/investment-platform/values*.yaml` to understand deployment config.
- **Backend structure**: Follow examples in existing `api/`, `schemas/`, and `services/` code.
- **Frontend structure**: Follow patterns in existing React components and services.

---

## Notes

- **Phases**: This is Phase 1 (foundation). Phases 2–11 add financial models, signals, AI, and advanced features. Check README.md for the development roadmap.
- **Secrets management**: Use environment variables or a secret operator (Vault, AWS Secrets Manager, Sealed Secrets) for production. Never hard-code.
- **Async everywhere**: The backend is fully async. Avoid synchronous libraries or blocking calls.
- **Type safety**: The frontend enforces strict TypeScript. The backend uses Python type hints. Leverage these for early error detection.
