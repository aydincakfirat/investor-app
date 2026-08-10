#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# build-images.sh — Docker image build scripti
#
# Kullanım:
#   bash scripts/build-images.sh <registry> <tag>
#   bash scripts/build-images.sh ghcr.io/kullanici dev
#   bash scripts/build-images.sh ghcr.io/kullanici 1.2.3
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REGISTRY="${1:-ghcr.io/your-org}"
TAG="${2:-dev}"
PLATFORM="${BUILD_PLATFORM:-linux/amd64}"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

info()    { echo -e "${YELLOW}[BUILD]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
info "Registry : ${REGISTRY}"
info "Tag      : ${TAG}"
info "Platform : ${PLATFORM}"
echo ""

# ── Backend image ─────────────────────────────────────────────────────────────
info "Backend image build ediliyor..."
docker build \
  --platform "${PLATFORM}" \
  --file "${ROOT_DIR}/backend/Dockerfile" \
  --tag  "${REGISTRY}/investment-platform-backend:${TAG}" \
  --tag  "${REGISTRY}/investment-platform-backend:latest" \
  --label "org.opencontainers.image.source=https://github.com/${GITHUB_REPOSITORY:-your-org/investment-platform}" \
  --label "org.opencontainers.image.revision=$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || echo unknown)" \
  --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "${ROOT_DIR}/backend"

success "Backend: ${REGISTRY}/investment-platform-backend:${TAG}"

# ── Frontend image ────────────────────────────────────────────────────────────
info "Frontend image build ediliyor..."
docker build \
  --platform "${PLATFORM}" \
  --file "${ROOT_DIR}/frontend/Dockerfile" \
  --tag  "${REGISTRY}/investment-platform-frontend:${TAG}" \
  --tag  "${REGISTRY}/investment-platform-frontend:latest" \
  --label "org.opencontainers.image.source=https://github.com/${GITHUB_REPOSITORY:-your-org/investment-platform}" \
  --label "org.opencontainers.image.revision=$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || echo unknown)" \
  --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "${ROOT_DIR}/frontend"

success "Frontend: ${REGISTRY}/investment-platform-frontend:${TAG}"

echo ""
echo -e "${GREEN}Build tamamlandı.${NC}"
echo "  Push için: make push"
echo "  Veya:      docker push ${REGISTRY}/investment-platform-backend:${TAG}"
echo "             docker push ${REGISTRY}/investment-platform-frontend:${TAG}"
echo ""
