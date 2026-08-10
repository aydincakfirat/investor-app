#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# setup.sh — Bir kerelik kurulum scripti
#
# Platform-agnostik: herhangi bir Kubernetes cluster'ında çalışır.
# (k3s, Docker Desktop, EKS, GKE, AKS, bare-metal — fark etmez)
#
# Gereksinimler:
#   - kubectl (cluster'a bağlı ve çalışıyor olmalı)
#   - helm 3.12+
#   - docker (image push için)
#
# Yapılanlar:
#   1. Bağımlılık kontrolü
#   2. Helm repo'ları (Bitnami, Argo)
#   3. Chart bağımlılıklarını indir
#   4. ArgoCD kurulumu (namespace + Helm)
#   5. Platform namespace'leri oluştur
#   6. ghcr.io image pull secret (opsiyonel)
#   7. ArgoCD erişim bilgilerini göster
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Investment Intelligence Platform — Setup        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Bağımlılık kontrolü ───────────────────────────────────────────────────
info "Bağımlılıklar kontrol ediliyor..."
command -v kubectl >/dev/null 2>&1 || error "kubectl bulunamadı. Kur: https://kubernetes.io/docs/tasks/tools/"
command -v helm    >/dev/null 2>&1 || error "Helm bulunamadı. Kur: https://helm.sh/docs/intro/install/"
command -v docker  >/dev/null 2>&1 || error "Docker bulunamadı. Kur: https://docs.docker.com/get-docker/"

info "Cluster bağlantısı kontrol ediliyor..."
kubectl cluster-info --request-timeout=10s >/dev/null 2>&1 \
  || error "kubectl cluster'a bağlanamıyor.\nKUBECONFIG ayarlı mı? kubectl get nodes çalışıyor mu?"
success "Cluster bağlantısı OK"
kubectl get nodes --no-headers | awk '{print "  Node: " $1 " (" $2 ")"}'

# ── 2. Helm repo'ları ────────────────────────────────────────────────────────
info "Helm repo'ları ekleniyor..."
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo add argo    https://argoproj.github.io/argo-helm 2>/dev/null || true
helm repo update
success "Helm repo'ları güncellendi"

# ── 3. Chart bağımlılıkları ──────────────────────────────────────────────────
info "Chart bağımlılıkları indiriliyor (Bitnami PostgreSQL)..."
helm dependency update helm/investment-platform
success "Chart bağımlılıkları hazır"

# ── 4. ArgoCD kurulumu ───────────────────────────────────────────────────────
info "ArgoCD kuruluyor..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --version "6.11.1" \
  --set server.service.type=ClusterIP \
  --set configs.params."server\.insecure"=true \
  --wait --timeout 300s

success "ArgoCD kuruldu"

# ── 5. Platform namespace'leri ───────────────────────────────────────────────
info "Namespace'ler oluşturuluyor..."
kubectl create namespace investment-platform-dev --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace investment-platform     --dry-run=client -o yaml | kubectl apply -f -
success "Namespace'ler hazır: investment-platform-dev, investment-platform"

# ── 6. ghcr.io image pull secret (opsiyonel) ─────────────────────────────────
if [ -n "${GITHUB_TOKEN:-}" ] && [ -n "${GITHUB_USER:-}" ]; then
  info "ghcr.io image pull secret oluşturuluyor..."
  for ns in investment-platform-dev investment-platform argocd; do
    kubectl create secret docker-registry ghcr-secret \
      --docker-server=ghcr.io \
      --docker-username="${GITHUB_USER}" \
      --docker-password="${GITHUB_TOKEN}" \
      --namespace="${ns}" \
      --dry-run=client -o yaml | kubectl apply -f -
  done
  success "Image pull secret oluşturuldu (ghcr-secret)"
else
  warn "GITHUB_TOKEN veya GITHUB_USER set edilmemiş — image pull secret atlandı."
  warn "Gerekirse:"
  warn "  export GITHUB_USER=kullanici_adin"
  warn "  export GITHUB_TOKEN=ghp_xxxxx"
  warn "  bash scripts/setup.sh"
fi

# ── 7. ArgoCD erişim bilgileri ────────────────────────────────────────────────
sleep 3
ARGOCD_PASS=$(kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" 2>/dev/null | base64 -d 2>/dev/null || echo "(henüz hazır değil)")

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Kurulum Tamamlandı                                      ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════╣${NC}"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" ""
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "ArgoCD erişim:"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "  kubectl port-forward svc/argocd-server -n argocd 8080:443"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "  URL:      http://localhost:8080"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "  Kullanıcı: admin"
printf "${GREEN}║${NC}  Şifre: %-48s${GREEN}║${NC}\n" "${ARGOCD_PASS}"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" ""
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "Sonraki adım:"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "  cp .env.example .env  # şifreleri doldur"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "  make build            # image'ları build et"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "  make push             # ghcr.io'ya push et"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" "  make deploy           # cluster'a deploy et"
printf "${GREEN}║${NC}  %-56s${GREEN}║${NC}\n" ""
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
