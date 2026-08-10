# GitHub Repository Kurulum Rehberi

CI/CD pipeline'ının çalışması için GitHub'da yapılması gereken tek seferlik ayarlar.

---

## 1. GitHub Secrets

**Settings → Secrets and variables → Actions → New repository secret**

### CI için (otomatik sağlanır)

| Secret | Açıklama |
|--------|----------|
| `GITHUB_TOKEN` | GitHub tarafından otomatik sağlanır, ek işlem gerekmez |

### CD için (cluster deploy)

| Secret | Açıklama | Nasıl oluşturulur |
|--------|----------|-------------------|
| `DEV_DB_PASSWORD` | Dev PostgreSQL şifresi | Rastgele güçlü şifre |
| `DEV_PG_PASSWORD` | Dev PostgreSQL superuser şifresi | Rastgele güçlü şifre |
| `DEV_N8N_KEY` | n8n encryption key | `openssl rand -hex 32` |
| `DEV_INTERNAL_KEY` | Backend internal API key | `openssl rand -hex 24` |
| `KUBECONFIG_DEV` | Cluster erişim bilgisi (base64) | Aşağıya bak |

**KUBECONFIG_DEV nasıl oluşturulur:**
```bash
# Cluster'ınızın kubeconfig dosyasını base64'e çevir:
cat ~/.kube/config | base64 -w 0   # Linux
cat ~/.kube/config | base64        # macOS
# Çıktıyı GitHub secret olarak kaydet
```

### Production için

| Secret | Açıklama |
|--------|----------|
| `PROD_DB_PASSWORD` | Production PostgreSQL şifresi |
| `PROD_N8N_KEY` | Production n8n encryption key |
| `PROD_INTERNAL_KEY` | Production internal API key |
| `PROD_OPENAI_KEY` | OpenAI API anahtarı |
| `PROD_MARKET_KEY` | Market data API anahtarı |
| `PROD_NEWS_KEY` | News API anahtarı |
| `KUBECONFIG_PROD` | Production cluster kubeconfig (base64) |

---

## 2. ghcr.io Image Visibility

Image'lar `ghcr.io/KULLANICI_ADI/investment-platform-backend` adresine push edilir.

**Private cluster'dan çekmek için image pull secret gerekir:**
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=GITHUB_KULLANICI_ADINIZ \
  --docker-password=GITHUB_TOKEN \
  --namespace=investment-platform-dev
```

`values-dev.yaml` veya `values-prod.yaml`'da aktif et:
```yaml
global:
  imagePullSecrets:
    - name: ghcr-secret
```

**Public yapmak için** (daha basit):
Settings → Packages → Image → Make public

---

## 3. ArgoCD Application kaydı

`argocd/investment-platform.yaml` içindeki `YOUR_GIT_REPO_URL` ve
`YOUR_GITHUB_USER` değerlerini kendi bilgilerinizle değiştirin, sonra:

```bash
# ArgoCD'ye repo erişimi ver (private repo ise):
kubectl create secret generic github-repo-secret \
  --from-literal=username=KULLANICI \
  --from-literal=password=GITHUB_TOKEN \
  -n argocd

# Application'ı kaydet:
make argocd

# İlk sync:
make argocd-sync
```

---

## 4. ArgoCD Image Updater (opsiyonel)

Yeni image tag'lerini otomatik algılar ve GitOps ile deploy eder.
CD workflow zaten bu işi yapıyor; Image Updater ek bir alternatif.

```bash
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
```

`argocd/investment-platform.yaml` içindeki annotation'lar zaten hazır.
`YOUR_GITHUB_USER` değerini güncelleyin.

---

## 5. İlk deploy — adım adım

```bash
# 1. Repo'yu klonla
git clone https://github.com/KULLANICI/investment-platform
cd investment-platform

# 2. Şifreleri doldur
cp .env.example .env
# .env dosyasını düzenle

# 3. Kurulum (Helm + ArgoCD)
make setup

# 4. Image'ları build et ve push et
export GITHUB_TOKEN=ghp_xxxxx
make build push

# 5. Cluster'a deploy et
make deploy

# 6. Portları aç
make forward
# → http://localhost:3000   (Frontend)
# → http://localhost:8000/api/docs  (Backend API)
# → http://localhost:5678   (n8n)

# 7. ArgoCD'ye kaydet (GitOps için)
make argocd
```

---

## 6. AWS EKS'e taşıma

Helm chart ve ArgoCD Application değişmez. Sadece:

1. `KUBECONFIG` → EKS cluster'ını göstersin
2. `values-prod.yaml` içinde:
   - `ingress.className: alb` (AWS Load Balancer Controller için)
   - `ingress.annotations` → ALB annotation'ları ekle
   - `postgresql.primary.persistence.storageClass: gp3`
3. Production secrets AWS Secrets Manager'dan ESO ile çekilebilir

```bash
# EKS'e bağlan:
aws eks update-kubeconfig --name CLUSTER_ADI --region eu-west-1

# Aynı komutlar çalışır:
make setup
make deploy-prod DB_PASSWORD=xxx N8N_KEY=xxx INTERNAL_KEY=xxx
```
