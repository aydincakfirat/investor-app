# investment-platform Helm Chart

Kubernetes-native AI Investment Intelligence Platform.

## Prerequisites

- Kubernetes 1.25+
- Helm 3.12+
- `kubectl` configured for your cluster
- Container registry access

## Install / Upgrade

```bash
# Add Bitnami repository (required for the PostgreSQL sub-chart)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Download chart dependencies
helm dependency update helm/investment-platform

# Install in dev
helm upgrade --install investment-platform helm/investment-platform \
  --namespace investment-platform-dev \
  --create-namespace \
  -f helm/investment-platform/values-dev.yaml \
  --set secrets.databasePassword=devpassword \
  --set secrets.postgresPassword=devpostgres \
  --set secrets.n8nEncryptionKey=devenckey32chars \
  --set secrets.internalApiKey=devinternal

# Install in production (use external secrets / vault instead of --set)
helm upgrade --install investment-platform helm/investment-platform \
  --namespace investment-platform \
  --create-namespace \
  -f helm/investment-platform/values-prod.yaml \
  --set secrets.databasePassword=$DB_PASSWORD \
  --set secrets.postgresPassword=$PG_PASSWORD \
  --set secrets.n8nEncryptionKey=$N8N_KEY \
  --set secrets.internalApiKey=$INTERNAL_KEY \
  --set secrets.openaiApiKey=$OPENAI_KEY
```

## Lint & Dry-run

```bash
helm lint helm/investment-platform
helm template investment-platform helm/investment-platform \
  -f helm/investment-platform/values-dev.yaml \
  --set secrets.databasePassword=test | kubectl apply --dry-run=client -f -
```

## Values Summary

| Key | Description |
|---|---|
| `backend.image.tag` | Backend Docker image tag |
| `frontend.image.tag` | Frontend Docker image tag |
| `postgresql.enabled` | Use bundled PostgreSQL sub-chart |
| `externalDatabase.*` | External DB config when `postgresql.enabled=false` |
| `ingress.enabled` | Enable Ingress |
| `networkPolicy.enabled` | Enable NetworkPolicies (deny-all default) |
| `secrets.*` | Inject at deploy time — never commit real values |
