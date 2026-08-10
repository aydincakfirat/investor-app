# ══════════════════════════════════════════════════════════════════════════════
# Investment Intelligence Platform — Makefile
#
# Platform-agnostik: Linux, macOS, WSL, CI ortamlarında çalışır.
# Kubernetes cluster'ı fark etmez: k3s, Docker Desktop, EKS, GKE, AKS.
#
# Kullanım:
#   make setup     → ArgoCD + Helm ilk kurulum
#   make build     → Docker image'larını build et
#   make push      → ghcr.io'ya push et
#   make deploy    → cluster'a Helm ile deploy et
#   make test      → backend testlerini çalıştır
#   make lint      → Helm lint
#   make status    → cluster durumunu göster
#   make forward   → port-forward (frontend:3000, backend:8000, n8n:5678)
#   make argocd    → ArgoCD uygulamasını kaydet
#   make clean     → namespace'i sil
# ══════════════════════════════════════════════════════════════════════════════

# ── Değişkenler ───────────────────────────────────────────────────────────────
# GitHub kullanıcı adını git remote'dan otomatik çeker
GITHUB_USER     ?= $(shell git config --get remote.origin.url 2>/dev/null \
                     | sed 's/.*github\.com[:/]\([^/]*\)\/.*/\1/' \
                     | tr '[:upper:]' '[:lower:]')
REPO_NAME       := investment-platform
REGISTRY        := ghcr.io/$(GITHUB_USER)
IMAGE_TAG       ?= dev
NAMESPACE_DEV   := investment-platform-dev
NAMESPACE_PROD  := investment-platform
HELM_RELEASE    := investment-platform
HELM_CHART      := helm/investment-platform

# Renkler (terminal destekliyorsa)
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

.PHONY: help setup helm-deps lint build push test deploy deploy-prod \
        status forward logs-backend logs-n8n logs-postgres \
        db-shell db-migrate argocd argocd-sync argocd-ui clean check-deps

# ── Yardım ───────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  $(GREEN)Investment Intelligence Platform$(NC)"
	@echo "  Registry : $(REGISTRY)"
	@echo "  Tag      : $(IMAGE_TAG)"
	@echo ""
	@echo "  $(YELLOW)Kurulum$(NC)"
	@echo "    make setup          İlk kurulum (Helm repo, ArgoCD, namespace)"
	@echo "    make helm-deps      Helm bağımlılıklarını indir"
	@echo ""
	@echo "  $(YELLOW)Build & Push$(NC)"
	@echo "    make build          Docker image'larını build et"
	@echo "    make push           ghcr.io'ya push et"
	@echo "    make build push     Build + push (tek satır)"
	@echo ""
	@echo "  $(YELLOW)Deploy$(NC)"
	@echo "    make deploy         Dev namespace'e deploy et"
	@echo "    make deploy-prod    Production namespace'e deploy et"
	@echo "    make argocd         ArgoCD Application'ı cluster'a kaydet"
	@echo "    make argocd-sync    ArgoCD sync tetikle"
	@echo ""
	@echo "  $(YELLOW)Geliştirme$(NC)"
	@echo "    make test           Backend testlerini çalıştır"
	@echo "    make lint           Helm lint çalıştır"
	@echo ""
	@echo "  $(YELLOW)Cluster$(NC)"
	@echo "    make status         Pod/Service/Ingress durumunu göster"
	@echo "    make forward        Port-forward başlat"
	@echo "    make logs-backend   Backend logları"
	@echo "    make logs-n8n       n8n logları"
	@echo "    make logs-postgres  PostgreSQL logları"
	@echo "    make argocd-ui      ArgoCD UI (port-forward)"
	@echo "    make db-shell       PostgreSQL shell"
	@echo "    make db-migrate     Alembic migrate"
	@echo ""
	@echo "  $(YELLOW)Temizlik$(NC)"
	@echo "    make clean          Dev namespace'i sil"
	@echo ""
	@echo "  $(YELLOW)Değişkenler$(NC)"
	@echo "    IMAGE_TAG=1.2.3 make build push    Belirli tag ile build/push"
	@echo "    GITHUB_USER=xyz make build         Farklı kullanıcı"
	@echo ""

# ── Bağımlılık kontrolü ───────────────────────────────────────────────────────
check-deps:
	@command -v docker  >/dev/null 2>&1 || (echo "$(RED)Docker bulunamadı$(NC)" && exit 1)
	@command -v kubectl >/dev/null 2>&1 || (echo "$(RED)kubectl bulunamadı$(NC)" && exit 1)
	@command -v helm    >/dev/null 2>&1 || (echo "$(RED)Helm bulunamadı$(NC)" && exit 1)
	@kubectl cluster-info --request-timeout=5s >/dev/null 2>&1 \
		|| (echo "$(RED)Kubernetes cluster'a bağlanılamıyor$(NC)" && exit 1)
	@echo "$(GREEN)Tüm bağımlılıklar mevcut$(NC)"

# ── İlk kurulum ───────────────────────────────────────────────────────────────
setup:
	@bash scripts/setup.sh

# ── Helm bağımlılıkları ───────────────────────────────────────────────────────
helm-deps:
	@helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
	@helm repo update --fail-on-repo-update-fail 2>/dev/null || helm repo update
	@helm dependency update $(HELM_CHART)

# ── Helm lint ─────────────────────────────────────────────────────────────────
lint: helm-deps
	@echo "$(YELLOW)Helm lint çalıştırılıyor...$(NC)"
	@helm lint $(HELM_CHART) \
		-f $(HELM_CHART)/values-dev.yaml \
		--set secrets.databasePassword=testpass \
		--set secrets.postgresPassword=testsuper \
		--set secrets.n8nEncryptionKey=testkey0000000000000000000000000 \
		--set secrets.internalApiKey=testinternal \
		--set backend.image.registry=$(REGISTRY) \
		--set backend.image.repository=$(REPO_NAME)-backend \
		--set frontend.image.registry=$(REGISTRY) \
		--set frontend.image.repository=$(REPO_NAME)-frontend
	@echo "$(GREEN)Helm lint başarılı$(NC)"

# ── Docker build ──────────────────────────────────────────────────────────────
build:
	@bash scripts/build-images.sh $(REGISTRY) $(IMAGE_TAG)

# ── ghcr.io push ─────────────────────────────────────────────────────────────
push:
	@[ -n "$(GITHUB_TOKEN)" ] || (echo "$(RED)GITHUB_TOKEN set edilmemiş$(NC)" && exit 1)
	@echo "$(YELLOW)ghcr.io login...$(NC)"
	@echo "$(GITHUB_TOKEN)" | docker login ghcr.io -u $(GITHUB_USER) --password-stdin
	@docker push $(REGISTRY)/$(REPO_NAME)-backend:$(IMAGE_TAG)
	@docker push $(REGISTRY)/$(REPO_NAME)-frontend:$(IMAGE_TAG)
	@echo "$(GREEN)Push tamamlandı: $(REGISTRY) tag=$(IMAGE_TAG)$(NC)"

# ── Backend testleri ──────────────────────────────────────────────────────────
test:
	@echo "$(YELLOW)Backend testleri çalıştırılıyor...$(NC)"
	@cd backend && \
		python -m venv .venv 2>/dev/null || true && \
		. .venv/bin/activate && \
		pip install -q -r requirements.txt && \
		pytest --tb=short -v
	@echo "$(GREEN)Testler tamamlandı$(NC)"

# ── Dev deploy ────────────────────────────────────────────────────────────────
deploy: helm-deps
	@bash scripts/deploy-dev.sh \
		$(REGISTRY) $(IMAGE_TAG) \
		$(NAMESPACE_DEV) $(HELM_RELEASE) $(HELM_CHART)

# ── Production deploy ─────────────────────────────────────────────────────────
# Production'da ArgoCD kullanılır (GitOps).
# Bu hedef yalnızca ArgoCD'siz acil durum deploy'u içindir.
deploy-prod: helm-deps
	@[ -n "$(DB_PASSWORD)" ]  || (echo "$(RED)DB_PASSWORD set edilmemiş$(NC)" && exit 1)
	@[ -n "$(N8N_KEY)" ]      || (echo "$(RED)N8N_KEY set edilmemiş$(NC)" && exit 1)
	@[ -n "$(INTERNAL_KEY)" ] || (echo "$(RED)INTERNAL_KEY set edilmemiş$(NC)" && exit 1)
	@echo "$(YELLOW)Production deploy — $(NAMESPACE_PROD)$(NC)"
	@helm upgrade --install $(HELM_RELEASE) $(HELM_CHART) \
		--namespace $(NAMESPACE_PROD) \
		--create-namespace \
		-f $(HELM_CHART)/values.yaml \
		-f $(HELM_CHART)/values-prod.yaml \
		--set backend.image.registry=$(REGISTRY) \
		--set backend.image.repository=$(REPO_NAME)-backend \
		--set backend.image.tag=$(IMAGE_TAG) \
		--set frontend.image.registry=$(REGISTRY) \
		--set frontend.image.repository=$(REPO_NAME)-frontend \
		--set frontend.image.tag=$(IMAGE_TAG) \
		--set secrets.databasePassword=$(DB_PASSWORD) \
		--set secrets.postgresPassword=$(DB_PASSWORD) \
		--set secrets.n8nEncryptionKey=$(N8N_KEY) \
		--set secrets.internalApiKey=$(INTERNAL_KEY) \
		--set secrets.openaiApiKey=$(OPENAI_KEY) \
		--timeout 600s \
		--wait
	@echo "$(GREEN)Production deploy tamamlandı$(NC)"

# ── ArgoCD Application kaydı ──────────────────────────────────────────────────
argocd:
	@echo "$(YELLOW)ArgoCD Application kaydediliyor...$(NC)"
	@kubectl apply -f argocd/investment-platform.yaml
	@echo "$(GREEN)ArgoCD Application oluşturuldu$(NC)"
	@echo "ArgoCD UI için: make argocd-ui"

argocd-sync:
	@echo "$(YELLOW)ArgoCD sync tetikleniyor...$(NC)"
	@kubectl annotate application $(HELM_RELEASE) -n argocd \
		argocd.argoproj.io/refresh=hard --overwrite 2>/dev/null \
		|| echo "$(YELLOW)argocd namespace erişilemiyor — kurulum tamamlandı mı?$(NC)"

argocd-ui:
	@echo "$(GREEN)ArgoCD UI → http://localhost:8080$(NC)"
	@echo -n "Admin şifresi: "
	@kubectl -n argocd get secret argocd-initial-admin-secret \
		-o jsonpath="{.data.password}" 2>/dev/null | base64 -d && echo ""
	@kubectl port-forward svc/argocd-server -n argocd 8080:443

# ── Cluster durumu ────────────────────────────────────────────────────────────
status:
	@echo "$(YELLOW)=== Pods (dev) ===$(NC)"
	@kubectl get pods -n $(NAMESPACE_DEV) -o wide 2>/dev/null || echo "Namespace yok: $(NAMESPACE_DEV)"
	@echo ""
	@echo "$(YELLOW)=== Services ===$(NC)"
	@kubectl get svc -n $(NAMESPACE_DEV) 2>/dev/null
	@echo ""
	@echo "$(YELLOW)=== Ingress ===$(NC)"
	@kubectl get ingress -n $(NAMESPACE_DEV) 2>/dev/null
	@echo ""
	@echo "$(YELLOW)=== PVCs ===$(NC)"
	@kubectl get pvc -n $(NAMESPACE_DEV) 2>/dev/null
	@echo ""
	@echo "$(YELLOW)=== Helm release ===$(NC)"
	@helm status $(HELM_RELEASE) -n $(NAMESPACE_DEV) 2>/dev/null | head -15

# ── Port-forward ──────────────────────────────────────────────────────────────
forward:
	@echo "$(GREEN)Port-forward başlatılıyor:$(NC)"
	@echo "  Frontend  → http://localhost:3000"
	@echo "  Backend   → http://localhost:8000/api/docs"
	@echo "  n8n       → http://localhost:5678"
	@echo "  Ctrl+C ile durdur"
	@kubectl port-forward -n $(NAMESPACE_DEV) svc/$(HELM_RELEASE)-frontend  3000:80    &
	@kubectl port-forward -n $(NAMESPACE_DEV) svc/$(HELM_RELEASE)-backend   8000:8000  &
	@kubectl port-forward -n $(NAMESPACE_DEV) svc/$(HELM_RELEASE)-n8n       5678:5678  &
	@wait

# ── Loglar ───────────────────────────────────────────────────────────────────
logs-backend:
	@kubectl logs -n $(NAMESPACE_DEV) -l app.kubernetes.io/name=backend \
		--tail=100 -f --all-containers=true

logs-n8n:
	@kubectl logs -n $(NAMESPACE_DEV) -l app.kubernetes.io/name=n8n \
		--tail=100 -f --all-containers=true

logs-postgres:
	@kubectl logs -n $(NAMESPACE_DEV) -l app.kubernetes.io/name=postgresql \
		--tail=100 -f --all-containers=true

# ── DB araçları ───────────────────────────────────────────────────────────────
db-shell:
	@kubectl exec -it -n $(NAMESPACE_DEV) \
		$$(kubectl get pod -n $(NAMESPACE_DEV) \
		   -l app.kubernetes.io/name=postgresql \
		   -o jsonpath='{.items[0].metadata.name}') \
		-- psql -U investuser -d investdb

db-migrate:
	@kubectl exec -it -n $(NAMESPACE_DEV) \
		$$(kubectl get pod -n $(NAMESPACE_DEV) \
		   -l app.kubernetes.io/name=backend \
		   -o jsonpath='{.items[0].metadata.name}') \
		-- alembic upgrade head

# ── Temizlik ─────────────────────────────────────────────────────────────────
clean:
	@echo "$(RED)UYARI: $(NAMESPACE_DEV) namespace'i silinecek.$(NC)"
	@printf "Devam etmek için 'yes' yaz: "; read c && [ "$$c" = "yes" ] || exit 1
	@helm uninstall $(HELM_RELEASE) -n $(NAMESPACE_DEV) 2>/dev/null || true
	@kubectl delete namespace $(NAMESPACE_DEV) 2>/dev/null || true
	@echo "$(GREEN)Temizlik tamamlandı$(NC)"
