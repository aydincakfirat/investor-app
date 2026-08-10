#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# deploy-dev.sh — Dev ortamına tek komutla Helm deploy
#
# Kullanım:
#   bash scripts/deploy-dev.sh <registry> <tag> <namespace> <release> <chart>
#   veya:  make dev
#
# Secrets için önce .env dosyasını doldur (bkz. .env.example).
# Script .env dosyasını okur ve Helm'e --set ile iletir.
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REGISTRY="${1:-ghcr.io/your-org}"
TAG="${2:-dev}"
NAMESPACE="${3:-investment-platform-dev}"
RELEASE="${4:-investment-platform}"
CHART="${5:-helm/investment-platform}"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${YELLOW}[DEPLOY]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}     $*"; }
error()   { echo -e "${RED}[ERROR]${NC}  $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# ── .env dosyasından secret'ları oku ─────────────────────────────────────────
ENV_FILE="${ROOT_DIR}/.env"
if [ -f "${ENV_FILE}" ]; then
  info ".env dosyası okunuyor..."
  # Sadece gerekli değişkenleri al (eval yerine güvenli grep)
  DB_PASSWORD=$(grep    -E "^POSTGRES_PASSWORD="        "${ENV_FILE}" | cut -d= -f2- | tr -d '"' || echo "")
  N8N_KEY=$(grep        -E "^N8N_ENCRYPTION_KEY="       "${ENV_FILE}" | cut -d= -f2- | tr -d '"' || echo "")
  INTERNAL_KEY=$(grep   -E "^INTERNAL_API_KEY="         "${ENV_FILE}" | cut -d= -f2- | tr -d '"' || echo "")
  OPENAI_KEY=$(grep     -E "^OPENAI_API_KEY="           "${ENV_FILE}" | cut -d= -f2- | tr -d '"' || echo "")
  MARKET_KEY=$(grep     -E "^MARKET_DATA_API_KEY="      "${ENV_FILE}" | cut -d= -f2- | tr -d '"' || echo "")
  NEWS_KEY=$(grep       -E "^NEWS_API_KEY="             "${ENV_FILE}" | cut -d= -f2- | tr -d '"' || echo "")
else
  warn() { echo -e "${YELLOW}[WARN]${NC}   $*"; }
  warn ".env bulunamadı. cp .env.example .env yapın ve doldurun."
  warn "Devam etmek için varsayılan dev şifreler kullanılıyor..."
  DB_PASSWORD="devpassword123"
  N8N_KEY="devn8nkey0000000000000000000000"
  INTERNAL_KEY="devinternal"
  OPENAI_KEY=""
  MARKET_KEY=""
  NEWS_KEY=""
fi

# Zorunlu alanlar kontrolü
[ -z "${DB_PASSWORD}" ]  && DB_PASSWORD="devpassword123"
[ -z "${N8N_KEY}" ]      && N8N_KEY="devn8nkey0000000000000000000000"
[ -z "${INTERNAL_KEY}" ] && INTERNAL_KEY="devinternal"

echo ""
info "Deploy başlıyor..."
info "Release   : ${RELEASE}"
info "Namespace : ${NAMESPACE}"
info "Registry  : ${REGISTRY}"
info "Tag       : ${TAG}"
echo ""

# ── Namespace oluştur ─────────────────────────────────────────────────────────
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# ── Helm upgrade/install ──────────────────────────────────────────────────────
helm upgrade --install "${RELEASE}" "${CHART}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  -f "${CHART}/values.yaml" \
  -f "${CHART}/values-dev.yaml" \
  --set "backend.image.registry=${REGISTRY}" \
  --set "backend.image.repository=investment-platform-backend" \
  --set "backend.image.tag=${TAG}" \
  --set "frontend.image.registry=${REGISTRY}" \
  --set "frontend.image.repository=investment-platform-frontend" \
  --set "frontend.image.tag=${TAG}" \
  --set "secrets.databasePassword=${DB_PASSWORD}" \
  --set "secrets.postgresPassword=${DB_PASSWORD}" \
  --set "secrets.n8nEncryptionKey=${N8N_KEY}" \
  --set "secrets.internalApiKey=${INTERNAL_KEY}" \
  --set "secrets.openaiApiKey=${OPENAI_KEY}" \
  --set "secrets.marketDataApiKey=${MARKET_KEY}" \
  --set "secrets.newsApiKey=${NEWS_KEY}" \
  --timeout 600s \
  --wait

echo ""
success "Deploy tamamlandı!"
echo ""

# ── Pod durumunu göster ───────────────────────────────────────────────────────
echo -e "${YELLOW}Pod durumu:${NC}"
kubectl get pods -n "${NAMESPACE}" -o wide

echo ""
echo -e "${GREEN}Erişim için:${NC}"
echo "  make forward"
echo "  veya:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/${RELEASE}-frontend  3000:80"
echo "  kubectl port-forward -n ${NAMESPACE} svc/${RELEASE}-backend   8000:8000"
echo "  kubectl port-forward -n ${NAMESPACE} svc/${RELEASE}-n8n       5678:5678"
echo ""
echo "  Frontend  → http://localhost:3000"
echo "  API Docs  → http://localhost:8000/api/docs"
echo "  n8n       → http://localhost:5678"
echo ""
