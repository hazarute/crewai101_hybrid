# Hybrid AI Software Agency

Bulut tabanlı güçlü LLM'ler ile yerel modelleri birleştiren, **8 otonom ajandan** oluşan üretim kalitesinde bir yazılım geliştirme ekibi.  
Her özellik talebi 4 aşamalı döngüden geçer; her aşama kendi kalite kapısına (VERDICT gate) sahiptir.

---

## Mimari Özet

```
Feature Request
      │
      ▼
Phase 1  ─ Project Architect       (Cloud LLM)
              sistem tasarımı, API kontratı, iskelet dosyalar
      │
      ▼
Phase 2  ─ Implementation Sprint Loop  (max 3 iterasyon)
              Backend Developer    (Local LLM)
              Frontend Developer   (Local LLM)
              Code Reviewer        (Cloud LLM)  ← OWASP analizi
              Team Leader gate     (Cloud LLM)  ← VERDICT: APPROVED / REJECTED
      │
      ▼
Phase 3  ─ Test Sprint Loop  (max 3 iterasyon)
              Test Engineer        (Local LLM)
              Team Leader gate     (Cloud LLM)  ← VERDICT: APPROVED / REJECTED
      │
      ▼
Phase 4  ─ Finalisation  (bir kez)
              DevOps Agent         (Local LLM)  ← Docker, CI/CD
              Tech Writer          (Local LLM)  ← README, API docs
              Team Leader          (Cloud LLM)  ← nihai VERDICT
      │
      ▼
projects/<slug>/   ← üretilen proje dosyaları
```

> Proje **Process.sequential** kullanır. Döngü ve kalite kapıları `crew/orchestrator.py` tarafından Python seviyesinde yönetilir — bu sayede ücretsiz OpenRouter modelleri (XML/JSON delegation uyumsuzluğu) ile de sorunsuz çalışır.

---

## Ajan Ekibi (8 Ajan)

| Ajan | Dosya | LLM Tipi | Rol |
|---|---|---|---|
| **Project Architect** | `agents/project_architect.py` | ☁ Cloud | Sistem tasarımı, API kontratı, iskelet dosyalar |
| **Backend Developer** | `agents/backend_developer.py` | 🏠 Local | FastAPI + Pydantic v2 + SQLModel backend |
| **Frontend Developer** | `agents/frontend_developer.py` | 🏠 Local | Next.js 14 + TypeScript + Tailwind CSS frontend |
| **Code Reviewer** | `agents/code_reviewer.py` | ☁ Cloud | OWASP güvenlik analizi, kod kalitesi denetimi |
| **Test Engineer** | `agents/test_engineer.py` | 🏠 Local | Pytest / Jest test süitleri |
| **DevOps Agent** | `agents/devops_agent.py` | 🏠 Local | Dockerfile, GitHub Actions CI/CD |
| **Tech Writer** | `agents/tech_writer.py` | 🏠 Local | README, API dökümantasyonu |
| **Team Leader** | `agents/team_leader.py` | ☁ Cloud | VERDICT kalite kapıları, nihai onay |

---

## Proje Yapısı

```
CrewAI-101/
├── .env.example              ← Tüm ortam değişkenleri (buradan kopyala)
├── .env                      ← Gerçek değerler (git'e commit etme)
├── requirements.txt
├── main.py                   ← Giriş noktası → python main.py
│
├── config/
│   └── settings.py           ← Tüm env değişkenleri tek yerden okunur
│
├── models/
│   └── llm_factory.py        ← LLM singleton'ları (cloud + local, per-agent)
│
├── agents/
│   ├── project_architect.py
│   ├── backend_developer.py
│   ├── frontend_developer.py
│   ├── code_reviewer.py
│   ├── test_engineer.py
│   ├── devops_agent.py
│   ├── tech_writer.py
│   └── team_leader.py
│
├── tasks/
│   └── task_definitions.py   ← 13 task factory fonksiyonu
│
├── crew/
│   └── orchestrator.py       ← 4 aşamalı üretim döngüsü (MAX_SPRINTS=3)
│
├── utils/
│   └── file_extractor.py     ← === FILE: === marker'larından dosya çıkarır
│
└── projects/                 ← Ajanlerin ürettiği proje dosyaları buraya yazılır
```

---

## Kurulum

### 1. Depoyu klonla

```bash
git clone <repo-url>
cd CrewAI-101
```

### 2. Sanal ortam oluştur

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
```

### 3. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarla

```bash
cp .env.example .env
# .env dosyasını düzenle
```

---

## Ortam Değişkenleri

### LLM Sağlayıcısı Seçimi

Sistem aşağıdaki öncelik sırasıyla çalışır:

```
USE_OPENROUTER_CLOUD=true  →  Cloud ajanlar OpenRouter üzerinden
USE_OPENROUTER_LOCAL=true  →  Worker ajanlar OpenRouter üzerinden
(ikisi de false)            →  Cloud=OpenAI, Local=Ollama
```

### OpenAI (doğrudan)

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4o
```

### Ollama (yerel çalıştırma)

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_BACKEND=llama3
OLLAMA_MODEL_FRONTEND=llama3
OLLAMA_MODEL_TESTER=mistral
OLLAMA_MODEL_REVIEWER=mistral       # Tech Writer
OLLAMA_MODEL_DEVOPS=llama3
```

### OpenRouter (200+ model, tek API anahtarı)

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...

# Cloud ajanları (Project Architect, Code Reviewer, Team Leader)
USE_OPENROUTER_CLOUD=true
OPENROUTER_CLOUD_MODEL=openai/gpt-4o-mini

# Worker ajanları (Backend, Frontend, Test, Tech Writer, DevOps)
USE_OPENROUTER_LOCAL=true
OPENROUTER_LOCAL_MODEL=openai/gpt-4o-mini
```

### Per-Ajan Model Override (isteğe bağlı)

Her ajana farklı bir model atanabilir; ayarlanmayan ajan otomatik olarak base modeli kullanır.

```dotenv
# Cloud per-agent
OPENROUTER_CLOUD_MODEL_ARCHITECT=openai/gpt-4.1
OPENROUTER_CLOUD_MODEL_REVIEWER=anthropic/claude-sonnet-4
OPENROUTER_CLOUD_MODEL_LEADER=openai/gpt-4.1

# Local per-agent
OPENROUTER_LOCAL_MODEL_BACKEND=openai/gpt-4o-mini
OPENROUTER_LOCAL_MODEL_FRONTEND=openai/gpt-4o-mini
OPENROUTER_LOCAL_MODEL_TESTER=openai/gpt-4o-mini
OPENROUTER_LOCAL_MODEL_REVIEWER=openai/gpt-4o-mini
OPENROUTER_LOCAL_MODEL_DEVOPS=openai/gpt-4o-mini
```

---

## Özellik Talebi Yöntemleri

### Yöntem 1 — Dosya ver (önerilen)

Markdown veya TXT formatındaki bir dosyayı doğrudan kaynak olarak göster:

```dotenv
FEATURE_REQUEST_FILE=HYBRID_AI_AGENCY_README.md
```

Dosya yolu proje köküne göre veya mutlak (`/home/user/proje/tanim.md`) verilebilir.

### Yöntem 2 — Satır içi metin

```dotenv
FEATURE_REQUEST=Build a TODO REST API with a React frontend
```

### Yöntem 3 — CLI ortam değişkeni

```bash
FEATURE_REQUEST="Build a URL shortener API" python main.py
```

> **Öncelik sırası:** `FEATURE_REQUEST_FILE` → `FEATURE_REQUEST` → yerleşik varsayılan

---

## Çalıştırma

```bash
python main.py
```

Proje dosyaları `projects/<slug>/` dizinine yazılır.  
Özet çıktı dosyaları `output/` dizinine yazılır:

| Dosya | İçerik |
|---|---|
| `output/01_architecture.md` | Sistem tasarımı, API kontratı |
| `output/02_backend.md` | Backend implementasyon notu |
| `output/03_frontend.md` | Frontend implementasyon notu |
| `output/review_sprint_N.md` | Sprint N kod inceleme raporu |
| `output/dev_gate_sprint_N.md` | Sprint N VERDICT kararı |
| `output/04_testing.md` | Test raporu |
| `output/test_gate_sprint_N.md` | Sprint N test VERDICT kararı |
| `output/05_devops.md` | DevOps konfigürasyon notu |
| `output/05b_docs.md` | Proje dökümantasyonu |
| `output/06_approval.md` | Nihai Team Leader onayı |

---

## Teknik Gereksinimler

| Bileşen | Versiyon |
|---|---|
| Python | 3.10+ (önerilen: 3.12) |
| CrewAI | ≥ 0.36.0 |
| crewai-tools | ≥ 0.4.0 |
| langchain-openai | ≥ 0.1.0 |
| langchain-community | ≥ 0.2.0 |
| Ollama (opsiyonel) | localhost:11434 |

---

*Hazar Üte — Hybrid AI Software Agency*
