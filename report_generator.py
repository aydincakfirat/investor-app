from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen.canvas import Canvas

OUTPUT = "/home/firto/investor-app/rapor.pdf"
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", f"{FONT_DIR}/DejaVuSans-Oblique.ttf"))

NAVY = colors.HexColor("#14324A")
TEAL = colors.HexColor("#167D86")
GOLD = colors.HexColor("#C8902F")
INK = colors.HexColor("#20313D")
MUTED = colors.HexColor("#61717C")
PALE = colors.HexColor("#EEF5F4")
PALE_BLUE = colors.HexColor("#EAF1F7")
LINE = colors.HexColor("#D5E0E4")
RED = colors.HexColor("#A94747")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName="DejaVu-Bold", fontSize=28, leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="CoverSub", fontName="DejaVu", fontSize=13, leading=19, textColor=MUTED, alignment=TA_CENTER, spaceAfter=18))
styles.add(ParagraphStyle(name="H1x", fontName="DejaVu-Bold", fontSize=18, leading=23, textColor=NAVY, spaceBefore=8, spaceAfter=9))
styles.add(ParagraphStyle(name="H2x", fontName="DejaVu-Bold", fontSize=12, leading=16, textColor=TEAL, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", fontName="DejaVu", fontSize=9.2, leading=14, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", fontName="DejaVu", fontSize=7.7, leading=10.5, textColor=MUTED, spaceAfter=4))
styles.add(ParagraphStyle(name="CodeX", fontName="DejaVu", fontSize=7.4, leading=10.5, textColor=INK, backColor=PALE_BLUE, borderColor=LINE, borderWidth=0.5, borderPadding=5, spaceAfter=6))
styles.add(ParagraphStyle(name="Callout", fontName="DejaVu", fontSize=9, leading=13, textColor=INK, backColor=PALE, borderColor=TEAL, borderWidth=1, borderPadding=8, spaceBefore=5, spaceAfter=8))
styles.add(ParagraphStyle(name="WhiteSmall", fontName="DejaVu", fontSize=8.2, leading=12, textColor=colors.white, alignment=TA_CENTER))


def p(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullet(text):
    return p(f"• {text}", "Bodyx")


def code(text):
    return p(text.replace("\n", "<br/>"), "CodeX")


def section(title):
    return [p(title, "H1x"), HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8)]


def table(data, widths, header=True, font=7.8):
    converted = []
    for row in data:
        converted.append([cell if isinstance(cell, Paragraph) else p(str(cell), "Smallx") for cell in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
    for i in range(1 if header else 0, len(data)):
        if i % 2 == 0:
            commands.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7FAFB")))
    t.setStyle(TableStyle(commands))
    return t


def flow_box(label, detail, color=TEAL):
    return Table([[p(label, "WhiteSmall")], [p(detail, "Smallx")]], colWidths=[31*mm], rowHeights=[9*mm, 16*mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color), ("BACKGROUND", (0, 1), (0, 1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.8, color), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))


def page_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.line(18*mm, height - 14*mm, width - 18*mm, height - 14*mm)
        canvas.setFont("DejaVu-Bold", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(18*mm, height - 11*mm, "Investment Intelligence Platform")
        canvas.setFont("DejaVu", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(width - 18*mm, height - 11*mm, "Mimari ve çalışma raporu")
    canvas.setStrokeColor(LINE)
    canvas.line(18*mm, 13*mm, width - 18*mm, 13*mm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18*mm, 8*mm, "Kaynak: /home/firto/investor-app | Tarih: 17 Ağustos 2026")
    canvas.drawRightString(width - 18*mm, 8*mm, f"{doc.page}")
    canvas.restoreState()


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=20*mm, bottomMargin=18*mm, **kwargs)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=page_header_footer)])


story = []

# Cover
story += [Spacer(1, 28*mm), p("INVESTMENT INTELLIGENCE\nPLATFORM", "CoverTitle"), p("Uygulamanın çalışma modeli, veri akışı ve Kubernetes mimarisi", "CoverSub")]
story.append(HRFlowable(width="55%", thickness=3, color=GOLD, hAlign="CENTER", spaceAfter=18))
story.append(p("Mimari inceleme raporu", "H2x"))
story.append(p("Bu rapor, mevcut repository içindeki backend, frontend, Helm, ArgoCD, PostgreSQL ve n8n yapılandırmalarına dayanır. Mevcut Phase 1 davranışı ile ileride eklenmesi planlanan analiz ve yapay zekâ katmanları ayrı değerlendirilmiştir.", "Callout"))
story.append(Spacer(1, 12*mm))
story.append(table([
    ["Rapor kapsamı", "Mevcut kod ve deployment tanımları"],
    ["Uygulama aşaması", "Phase 1 — temel platform ve market görünümü"],
    ["Çalışma ortamı", "Kubernetes, Helm, ArgoCD, Docker, PostgreSQL, n8n"],
    ["Hazırlanma tarihi", "17 Ağustos 2026"],
], [42*mm, 112*mm]))
story.append(PageBreak())

# Executive summary
story += section("1. Yönetici özeti")
story.append(p("Platform; tarayıcıda çalışan React/Vite arayüzünü, HTTP API sunan FastAPI backend'ini, kalıcı PostgreSQL veritabanını ve otomasyon/workflow katmanı olarak n8n'i Kubernetes üzerinde bir araya getirir. ArgoCD, Git repository içindeki deployment tanımlarını cluster'a otomatik senkronize eder; Helm ise bileşenlerin Deployment, Service, Secret, ConfigMap, PVC, Ingress ve NetworkPolicy kaynaklarını üretir."))
story.append(p("Bugünkü gerçek çalışma kapsamı Phase 1'dir. Backend health/readiness uç noktalarını ve Yahoo Finance veya mock provider üzerinden market overview/history uç noktalarını sunar. Teknik indikatörler, sinyaller, portföy, AI analist ve alarm akışları repository dokümanında sonraki fazlar olarak tanımlanmıştır; bunlar henüz mevcut kodda tamamlanmış özellikler değildir."))
story.append(p("En kısa uçtan uca akış şöyledir:", "H2x"))
story.append(Table([[flow_box("Kullanıcı", "React dashboard"), p("→", "H1x"), flow_box("Frontend", "nginx + SPA", NAVY), p("→", "H1x"), flow_box("Backend", "FastAPI :8000", TEAL), p("→", "H1x"), flow_box("Yahoo", "Dış market verisi", GOLD)]], colWidths=[34*mm, 8*mm, 34*mm, 8*mm, 34*mm, 8*mm, 34*mm], style=TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ALIGN", (0,0), (-1,-1), "CENTER")])))
story.append(Spacer(1, 8))
story.append(p("Backend'in veritabanı bağlantısı hazırdır ve readiness kontrolünde kullanılır; ancak Phase 1 market endpoint'leri veriyi PostgreSQL'e kaydetmez. PostgreSQL'in asıl işlevi sonraki fazlarda kalıcı market zaman serileri, haberler, sinyaller, portföy ve AI raporları için merkezi state store olmaktır. n8n ise hesaplamanın sahibi değil, zamanlama, HTTP çağrıları, dallanma, dış servisler, bildirimler ve rapor dağıtımı için orkestrasyon katmanıdır."))

# Architecture
story += section("2. Bileşenler ve sorumluluk sınırları")
story.append(table([
    ["Bileşen", "Bugünkü görevi", "Kubernetes karşılığı"],
    ["React + Vite", "Dashboard, durum sayfası, market verisini gösterme", "Frontend Deployment + NodePort/Ingress"],
    ["nginx", "Statik dosya sunumu, /api proxy, SPA fallback, /health", "Frontend container"],
    ["FastAPI + Uvicorn", "HTTP API, CORS, health/readiness, market provider çağrıları", "Backend Deployment + ClusterIP"],
    ["SQLAlchemy async", "PostgreSQL async engine/session altyapısı", "Backend process içi kütüphane"],
    ["PostgreSQL", "Kalıcı ilişkisel veri; n8n için ayrı database", "Bitnami StatefulSet + PVC veya ArgoCD chart"],
    ["n8n", "Workflow scheduling ve dış sistem entegrasyonu", "Deployment + PVC + ClusterIP"],
    ["Helm", "Kubernetes manifest templating ve environment override", "Chart"],
    ["ArgoCD", "GitOps sync, self-heal, prune, retry", "ArgoCD Application CR'ları"],
], [33*mm, 82*mm, 43*mm]))
story.append(p("Repository'deki iki deployment modeli", "H2x"))
story.append(bullet("Tek chart kurulumu: values.yaml içinde backend, frontend, n8n ve PostgreSQL aynı Helm release ile açılabilir."))
story.append(bullet("Split-app kurulumu: mevcut ArgoCD manifestleri dört ayrı Application kullanıyor. Backend/frontend/n8n chart'ı PostgreSQL'i kapatıyor; PostgreSQL ayrı Bitnami chart olarak kuruluyor."))
story.append(p("Split-app modelinde global.databaseHost, global.backendServiceHost ve global.postgresSecretName değerleri bağımsız release'lerin gerçek Service/Secret isimleriyle eşleşmelidir. Bu isimler Kubernetes DNS ve Secret referansları açısından kritik çalışma sözleşmesidir.", "Callout"))

# Request flow
story += section("3. Kullanıcı isteği nasıl çalışır?")
story.append(p("Production'da varsayılan giriş noktası Ingress'tir. values-prod.yaml, aynı host üzerinde '/' yolunu frontend'e, '/api' yolunu backend'e yönlendirir. Frontend container'ı ayrıca kendi nginx proxy'siyle /api çağrılarını BACKEND_HOST üzerinden backend Service'ine aktarabilir. Bu nedenle deployment biçimine göre API yolu ya Ingress üzerinden ya da frontend nginx iç proxy'si üzerinden çözümlenir."))
story.append(code("Tarayıcı → https://invest.yourdomain.com/\n  /dashboard → frontend Service → nginx → index.html\n  /api/markets/overview → backend Service → FastAPI router\n  /api/ready → backend → PostgreSQL SELECT 1"))
story.append(p("Frontend tarafında api.ts, VITE_API_BASE_URL boşsa göreli URL kullanır. Dashboard ilk açılışta /api/markets/overview çağrısı yapar, 60 saniyede bir yeniler ve manuel Refresh butonuna izin verir. Axios interceptor, backend'in detail alanını kullanıcıya taşır. Health ve readiness hooks ise React Query ile sırasıyla 60 ve 30 saniyede yenilenir."))
story.append(p("Frontend nginx yapılandırması", "H2x"))
story.append(bullet("/api/ isteklerini http://${BACKEND_HOST}:8000 adresine proxy eder."))
story.append(bullet("Bilinmeyen UI yollarını /index.html'e yönlendirerek React SPA routing'i destekler."))
story.append(bullet("/health endpoint'i Kubernetes probe'ları için statik 200 döndürür."))
story.append(bullet("Gzip, immutable asset cache ve temel güvenlik header'ları uygular."))

# Backend
story += section("4. Backend nasıl çalışır?")
story.append(p("Uygulama backend/app/main.py içindeki create_app() ile oluşturulur. Pydantic Settings, environment değişkenlerini .env dosyası veya process environment içinden yükler. FastAPI; /api/docs, /api/redoc ve /api/openapi.json dokümantasyon uç noktalarını açar; health ve markets router'larını register eder."))
story.append(p("Açılış ve kapanış yaşam döngüsü", "H2x"))
story.append(bullet("Startup'ta ayarlar okunur ve yapılandırılmış structlog kaydı yazılır."))
story.append(bullet("Async SQLAlchemy engine oluşturulur; SELECT 1 ile veritabanı bağlantısı ısıtılır."))
story.append(bullet("DB yoksa process kapanmaz; warning loglanır ve /api/ready 503 döndürmeye devam eder."))
story.append(bullet("Shutdown'ta engine.dispose() çağrılır."))
story.append(p("Health endpoint'leri", "H2x"))
story.append(table([
    ["Endpoint", "Davranış", "Kubernetes anlamı"],
    ["GET /api/health", "healthy, version, environment, uptime", "Temel uygulama bilgisi"],
    ["GET /api/live", "Process/event loop canlıysa 200", "Liveness: pod yeniden başlatma kararı"],
    ["GET /api/ready", "DB SELECT 1 başarılıysa 200, değilse 503", "Readiness: trafik alıp almama kararı"],
], [38*mm, 75*mm, 45*mm]))
story.append(p("Market data akışı", "H2x"))
story.append(code("GET /api/markets/overview\n  → get_market_provider()\n  → MARKET_DATA_PROVIDER=yahoo ise YahooFinanceProvider\n  → MARKET_DEFINITIONS içindeki semboller için quote()\n  → MarketOverview(markets=[...])\n\nGET /api/markets/{symbol}/history?interval=1d&range=1mo\n  → provider.history() → MarketHistory(candles=[...])"))
story.append(p("Mevcut provider seçimi yalnızca yahoo ve mock davranışını uygular. values-dev.yaml'da provider yahoo görünse de .env.example varsayılanı mock'tur; hangi ortamın gerçekten çalıştığı pod env'ine bağlıdır. Yahoo çağrısı başarısız olursa overview tek bir sembol yüzünden bütünü düşürmez; history çağrısı ise 502 döndürür."))

# Data and DB
story += section("5. PostgreSQL ne işe yarar, nasıl çalışır?")
story.append(p("PostgreSQL, platformun kalıcı veri katmanıdır. Bitnami PostgreSQL chart'ı StatefulSet benzeri kalıcı bir veritabanı kurulumu, Secret tabanlı kimlik bilgileri ve PVC ile disk sürekliliği sağlar. Backend asyncpg üzerinden postgresql+asyncpg:// bağlantı şemasını kullanır; n8n ise kendi native postgres sürücüsü nedeniyle postgres:///DB_* değişkenleriyle bağlanır."))
story.append(Table([[flow_box("Backend DB", "investdb", NAVY), p("+", "H1x"), flow_box("n8n DB", "n8n", TEAL), p("→", "H1x"), flow_box("PostgreSQL", "5432 + PVC", GOLD)]], colWidths=[37*mm, 8*mm, 37*mm, 8*mm, 37*mm], style=TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ALIGN", (0,0), (-1,-1), "CENTER")])))
story.append(Spacer(1, 7))
story.append(bullet("investdb backend uygulama verileri içindir: Phase 2+ modeller, fiyat serileri, haber, sinyal, portföy ve raporlar burada tutulabilir."))
story.append(bullet("n8n database workflow tanımları, execution metadata ve credential/config state içindir; backend iş veritabanından ayrıdır."))
story.append(bullet("primary.persistence.size dev'de 2Gi, prod'da 50Gi olarak override edilir; storageClass boşsa cluster'ın varsayılanı kullanılır."))
story.append(bullet("initdb script'i n8n database'ini oluşturur ve investuser'a yetki verir; bu işlem yalnızca ilk database initialization koşullarında etkilidir."))
story.append(p("Önemli mevcut durum: Phase 1 market endpoint'leri Yahoo'dan okur ve response üretir, fakat bu kod yolunda market sonucunu PostgreSQL'e yazan repository/model katmanı henüz yoktur. PostgreSQL bağlantısının bugünkü gözle görünür kullanımı startup/readiness kontrolüdür; kalıcı finansal veri modeli sonraki faz işidir.", "Callout"))

# Env
story += section("6. Env, ConfigMap ve Secret akışı")
story.append(p("Ayarlar üç kaynaktan yönetilir: local development için .env, Kubernetes'te non-secret değerler için ConfigMap, secret değerler için Kubernetes Secret/SecretRef. Pydantic Settings değişken isimlerini case-insensitive olarak alan adlarına eşler; örneğin DATABASE_URL → database_url, MARKET_DATA_PROVIDER → market_data_provider."))
story.append(table([
    ["Değişken grubu", "Örnekler", "Kubernetes'te kaynak"],
    ["Backend davranışı", "ENVIRONMENT, LOG_LEVEL, DEBUG, AI_PROVIDER, MARKET_DATA_PROVIDER, NEWS_PROVIDER", "ConfigMap"],
    ["DB bağlantısı", "DATABASE_URL; host/user/name Helm ile, password Secret ile", "ConfigMap + SecretRef"],
    ["API anahtarları", "INTERNAL_API_KEY, OPENAI_API_KEY, MARKET_DATA_API_KEY, NEWS_API_KEY", "SecretRef"],
    ["n8n", "DB_TYPE, DB_POSTGRESDB_HOST/DATABASE/USER, N8N_LOG_LEVEL", "ConfigMap"],
    ["n8n güvenliği", "N8N_ENCRYPTION_KEY, DB_POSTGRESDB_PASSWORD", "SecretRef"],
    ["Frontend", "VITE_API_BASE_URL build-time; BACKEND_HOST runtime", "Vite env + Deployment env"],
], [35*mm, 75*mm, 45*mm]))
story.append(code("Backend DATABASE_URL örneği\npostgresql+asyncpg://investuser:$(_DB_PASS)@<database-host>:5432/investdb\n\nLocal .env örneği\nDATABASE_URL=postgresql+asyncpg://investuser:change-me@localhost:5432/investdb\nMARKET_DATA_PROVIDER=mock\nINTERNAL_API_KEY=change-me-internal-api-key"))
story.append(p("Helm Secret template stringData üretir; production için değerlerin --set, External Secrets Operator, Vault veya Sealed Secrets üzerinden sağlanması amaçlanmıştır. Gerçek secret'ların values.yaml, values-prod.yaml veya Git içindeki ArgoCD manifestlerinde tutulmaması gerekir."))

# Kubernetes
story += section("7. Kubernetes ve Helm çalışma modeli")
story.append(p("Helm chart, feature flag gibi çalışan enabled alanlarıyla bileşenleri koşullu üretir. Deployment'lar RollingUpdate kullanır; backend ve frontend için maxUnavailable=0 ayarıyla güncelleme sırasında erişilebilirlik korunmaya çalışılır. Backend ve n8n, PostgreSQL erişilebilir olana kadar busybox initContainer içinde nc ile bekler."))
story.append(table([
    ["Kaynak", "Rol"],
    ["Deployment", "Pod replica, image, env, securityContext, resource limit ve probe tanımları"],
    ["Service", "Cluster içi DNS ve port erişimi; backend/n8n ClusterIP, frontend varsayılan NodePort"],
    ["ConfigMap", "Secret olmayan backend/n8n ayarları ve service discovery URL'leri"],
    ["Secret", "DB/API/n8n encryption key gibi hassas değerler"],
    ["PVC", "PostgreSQL ve n8n state sürekliliği"],
    ["Ingress", "Production'da TLS ve host/path yönlendirmesi"],
    ["NetworkPolicy", "Production'da default deny + açıkça izin verilen bağlantılar"],
    ["HPA", "Tanımlı ancak values-prod.yaml'da disabled; replica sayısı sabit"],
], [38*mm, 117*mm]))
story.append(p("Probe davranışı", "H2x"))
story.append(bullet("Backend startup/liveness /api/live, readiness /api/ready kullanır."))
story.append(bullet("Frontend /health, n8n /healthz ile kontrol edilir."))
story.append(bullet("Readiness başarısız backend pod'unu Service trafiğinden çıkarır; bu, database geçici olarak kapalıyken hatalı trafik dağıtımını azaltır."))
story.append(p("SecurityContext'ler backend, frontend ve n8n için non-root kullanıcı, privilege escalation kapalı, capability drop ve service account token otomount kapalı gibi kısıtlar uygular. Backend read-only root filesystem kullandığı için /tmp emptyDir mount edilir; frontend nginx için cache ve pid dizinleri emptyDir ile yazılabilir hale getirilir."))

# ArgoCD
story += section("8. ArgoCD ve GitOps akışı")
story.append(p("ArgoCD Application kaynakları repository'nin main branch'ini izler. Her Application aynı chart yolunu farklı Helm parametreleriyle render eder; böylece bileşenler bağımsız sync edilir ve bir bileşenin değişimi diğerlerinin Deployment'ını gereksiz yere yeniden kurmaz."))
story.append(code("Git push\n  → ArgoCD repo refresh\n  → Helm render (values.yaml + values-dev.yaml + parameters)\n  → Kubernetes apply\n  → automated sync / selfHeal / prune\n  → Pod probes ve rollout durumu"))
story.append(table([
    ["Application", "Açtığı bileşen", "Kapattığı bileşenler"],
    ["investment-platform-be", "Backend", "Frontend, n8n, embedded PostgreSQL"],
    ["investment-platform-fe", "Frontend", "Backend, n8n, embedded PostgreSQL"],
    ["investment-platform-n8n", "n8n", "Backend, frontend, embedded PostgreSQL"],
    ["investment-platform-postgre", "Bitnami PostgreSQL 18.8.6", "Chart içindeki diğer bileşenler"],
], [48*mm, 55*mm, 52*mm]))
story.append(p("Split-app modelinde backend, frontend ve n8n'in kendi chart release adlarından üretilecek Service/Secret isimleri ile global.* değerlerinde yazan sabit isimler aynı olmalıdır. Bu sözleşme bozulursa pod çalışsa bile frontend backend'e, backend/n8n PostgreSQL'e DNS veya Secret üzerinden ulaşamayabilir.", "Callout"))

# n8n
story += section("9. n8n neden var ve ne yapacak?")
story.append(p("n8n, finansal hesaplamaların yerine geçen bir servis değildir. Onun rolü “ne zaman çalışacak, hangi sistemi çağıracak, sonuç hangi karara gidecek?” sorularını görsel workflow'larla yönetmektir. Backend; veri çekme, validasyon, hesaplama ve domain kurallarının sahibi kalır. n8n ise bu fonksiyonları schedule, HTTP Request, IF, Code, AI, email ve webhook düğümleriyle birleştirir."))
story.append(table([
    ["n8n kullanım alanı", "Örnek akış"],
    ["Zamanlama", "Her sabah market verisi çekme ve analiz başlatma"],
    ["Orkestrasyon", "Backend endpoint'lerini sırayla çağırma; başarısız adımda branch"],
    ["Dış veri", "KAP, SEC, TCMB, FRED, ECB, haber ve veri sağlayıcıları"],
    ["AI koordinasyonu", "Yapılandırılmış backend çıktısını AI provider'a gönderme"],
    ["Bildirim", "Email, webhook veya ileride mesajlaşma kanallarına alarm gönderme"],
    ["Operasyon", "Health/readiness kontrolü, execution log ve retry"],
], [44*mm, 111*mm]))
story.append(p("Repository'deki mevcut health-check workflow'u her 5 dakikada /api/health çağırır; status healthy ise healthy log, değilse unhealthy log branch'ine gider. Workflow export edilmiş ancak active:false durumundadır; canlı n8n'e import/activate edilmeden otomatik çalışmaz."))
story.append(p("n8n persistence PVC ile /home/node/.n8n dizinini korur. Community Edition için Recreate strategy ve tek replica seçilmiştir; aynı PVC'ye iki aktif n8n pod'unun yazması engellenir. Production'da n8n dışarıya varsayılan olarak açılmaz; ingress.n8n.enabled false'tur.", "Callout"))

# Security and observations
story += section("10. Güvenlik ve işletim gözlemleri")
story.append(p("Mevcut tasarımda güçlü taraflar", "H2x"))
story.append(bullet("Secret değerleri için Helm SecretRef, runtime env ve dış secret sistemi geçiş yolu tanımlanmış."))
story.append(bullet("Production NetworkPolicy default-deny ile başlıyor; backend, n8n, PostgreSQL ve ingress bağlantıları ayrı izinlerle sınırlandırılıyor."))
story.append(bullet("Pod'lar non-root çalışıyor, service account token otomatik bağlanmıyor ve container capability'leri düşürülüyor."))
story.append(bullet("TLS Ingress ve cert-manager annotation'ı production override'ında hazır."))
story.append(p("Dikkat edilmesi gereken bulgular", "H2x"))
story.append(bullet("argocd/postgres-app.yaml içinde auth.password değeri düz metin olarak investpass yazılmış. Bu değer Git'e commit edilmemeli; existingSecret veya External Secrets yaklaşımı kullanılmalı ve mevcut parola döndürülmeli."))
story.append(bullet("values.yaml içindeki global backend/database/postgres secret isimleri split-app ArgoCD release isimleriyle uyumlu kontrol edilmeden deploy edilmemeli."))
story.append(bullet("values-prod.yaml AI_PROVIDER=openai, MARKET_DATA_PROVIDER=alpha_vantage ve NEWS_PROVIDER=newsapi seçiyor; ilgili API key Secret değerleri ve provider kodları tamamlanmadan production'da gerçek veri/AI beklentisi karşılanmayabilir."))
story.append(bullet("values-prod.yaml'da autoscaling yapılandırması tanımlı olsa da enabled:false; kaynak kullanımı artınca HPA kendiliğinden devreye girmez."))
story.append(bullet("NetworkPolicy dış provider'lara 80/443 izni veriyor; DNS, egress gözlemlenebilirliği ve provider rate-limit/retry politikaları ayrıca işletilmelidir."))

# roadmap
story += section("11. Fazlar ve uygulamanın evrimi")
story.append(table([
    ["Faz", "Planlanan yetenek", "Bugünkü dayanak"],
    ["1", "Kubernetes foundation, health, market overview", "Mevcut ve çalışır temel"],
    ["2", "DB modelleri ve mock market data", "SQLAlchemy Base ve Alembic altyapısı hazır"],
    ["3", "SMA, EMA, RSI, MACD, ATR, ADX, Bollinger, VWAP", "Henüz eklenmedi"],
    ["4", "Fundamental analysis ve valuation", "Henüz eklenmedi"],
    ["5", "News ve resmi açıklamalar", "Provider ayarları var, iş akışı henüz yok"],
    ["6", "Signal/risk/market regime", "Henüz eklenmedi"],
    ["7", "n8n daily analysis, news, ideas, portfolio workflows", "Health-check örneği mevcut"],
    ["8", "AI analyst", "Provider ayarı/mock seçeneği mevcut"],
    ["9", "Email ve alerts", "n8n egress izinleri geleceğe hazırlıyor"],
    ["10-11", "Portfolio, watchlist, backtesting, AI performance", "Henüz eklenmedi"],
], [17*mm, 78*mm, 60*mm]))
story.append(p("Önerilen bir sonraki teknik adım", "H2x"))
story.append(p("Önce split-app deployment sözleşmesini tekilleştirmek ve düz metin PostgreSQL secret'ını kaldırmak; ardından SQLAlchemy modelleri, Alembic migration'ları ve market data persistence akışını eklemek en düşük riskli sıradır. Bu temel tamamlanmadan analiz, AI ve n8n rapor workflow'larının üzerine çıkılması gözlemlenebilirlik ve veri sürekliliği açısından erken olur."))

# source map
story += section("12. Kaynak ve doğrulama haritası")
story.append(table([
    ["Konu", "Kaynak dosyalar"],
    ["Genel hedef mimari", "README.md"],
    ["Local env sözleşmesi", ".env.example"],
    ["Backend lifecycle/config", "backend/app/main.py; backend/app/core/config.py"],
    ["Health/readiness", "backend/app/api/health.py"],
    ["Market data", "backend/app/api/markets.py; backend/app/services/market_data.py; backend/app/schemas/market.py"],
    ["Frontend API ve dashboard", "frontend/src/services/api.ts; frontend/src/pages/DashboardPage.tsx; frontend/nginx.conf"],
    ["Base Helm değerleri", "helm/investment-platform/values.yaml"],
    ["Environment override", "helm/investment-platform/values-dev.yaml; values-prod.yaml"],
    ["Kubernetes wiring", "helm/investment-platform/templates/*.yaml"],
    ["GitOps", "argocd/backend-app.yaml; frontend-app.yaml; n8n-app.yaml; postgres-app.yaml"],
    ["n8n örnek workflow", "n8n/workflows/health-check.json"],
], [43*mm, 112*mm]))
story.append(Spacer(1, 8))
story.append(p("Sonuç: Platformun omurgası doğru sorumluluk ayrımına sahip ve Kubernetes'e taşınabilir biçimde hazırlanmış durumda. Ancak mevcut davranış hâlâ temel gözlemleme ve market görünümü seviyesinde; kalıcı finansal veri, analiz motoru, sinyal, AI ve bildirim değer zinciri sonraki implementasyonlarla oluşacaktır.", "Callout"))

doc = ReportDocTemplate(OUTPUT, title="Investment Intelligence Platform - Mimari ve çalışma raporu", author="GitHub Copilot")
doc.build(story)
print(OUTPUT)
