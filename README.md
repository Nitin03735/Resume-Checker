# Resume Checker (Local-Only DevOps Project)

> ⚠️ **LOCAL ONLY.** Do NOT `git init`, do NOT add a remote, do NOT push.
> This project stays inside the parent `AICHAT` folder on your laptop,
> or on your private Linux VM. A protective `.gitignore` is included as
> an extra safety net.

Flask web app that scans a resume PDF/DOCX, scores it against the
ATS + recruiter + Naukri rulebook codified in [`RUNBOOK.md`](./RUNBOOK.md),
**rewrites it to a target Job Description with pluggable AI**, and lets
you **download the tailored resume as DOCX or PDF**.

Built as a DevOps portfolio piece: **Python + Flask + Docker + GitHub
Actions + Nginx + Gunicorn + systemd**.

![pipeline](https://img.shields.io/badge/python-3.11%2B-blue) ![flask](https://img.shields.io/badge/flask-3.x-black) ![docker](https://img.shields.io/badge/docker-ready-2496ED) ![ci](https://img.shields.io/badge/github%20actions-ci%20%2B%20docker-181717) ![nginx](https://img.shields.io/badge/nginx-reverse%20proxy-009639)

---

## Features

- Upload a `.pdf` or `.docx` resume (max 5 MB).
- Score **100-point rubric** across:
  **parseability (25) · structure (20) · contact (10) · dates (10) · JD keywords (20) · metrics (10) · acronyms (5)**.
- Grade **A+ to F** with a short verdict.
- **AI tailor** — rewrites Summary, Skills, and Experience bullets to a
  pasted JD. Three pluggable backends:
  - `rule_based` (default, no AI, no deps)
  - `ollama` — local LLM, perfect for Linux VM (`llama3.1:8b`, `mistral:7b`, `phi3`)
  - `openai` — any OpenAI-compatible API (OpenAI, Azure, Groq, Together, LM Studio…)
- **DOCX + PDF download** of the tailored resume (pure-Python, no system binaries).
- Preset role JDs: DevOps Engineer, Cloud Support, SRE, NOC, Jr Cloud.
- Dark modern UI, drag-and-drop upload, animated score ring, live preview.
- Dockerized, non-root container, health-check, multi-stage build.
- Production deployment stack: **Nginx + Gunicorn + systemd** with a
  one-shot bootstrap script.

---

## Project layout

```
resume-checker/
├── app.py                         Flask entrypoint
├── analyzer/
│   ├── parser.py                  PDF/DOCX text + metadata + font + image extraction
│   ├── sections.py                heuristic text → structured sections
│   ├── keywords.py                tokenize, keyword overlap, acronym map
│   ├── presets.py                 preset JDs per role
│   ├── rules.py                   individual rule checks (11 across 7 categories)
│   ├── scorer.py                  orchestrator → JSON scorecard
│   ├── ai_tailor.py               rule_based / ollama / openai providers
│   ├── renderer_docx.py           python-docx renderer
│   └── renderer_pdf.py            fpdf2 renderer
├── templates/index.html           single-page UI
├── static/{styles.css, app.js}    styles + fetch/render logic
├── tests/
│   ├── test_rules.py              scorer rule tests
│   └── test_tailor.py             sections + rule-based tailor + renderers
├── samples/                       drop PDFs here (git-ignored)
├── deploy/
│   ├── nginx-resume-checker.conf  reverse-proxy config
│   ├── resume-checker.service     systemd unit for Gunicorn
│   ├── deploy.sh                  one-shot Ubuntu/Debian installer
│   └── README.md                  full VM deployment guide
├── Dockerfile                     multi-stage, non-root, healthcheck
├── docker-compose.yml             one-command local run
├── requirements.txt               runtime deps
├── requirements-dev.txt           + pytest + ruff
├── .github/workflows/ci.yml       lint + test matrix
├── .github/workflows/docker.yml   build + Trivy scan (push disabled by default)
├── RUNBOOK.md                     ATS + recruiter + Naukri rulebook
├── .gitignore                     strong local-only safeguards
└── .dockerignore
```

---

## 1 · Run locally (Python venv on Windows / macOS / Linux)

```powershell
cd C:\Users\N937262\Downloads\AICHAT\resume-checker

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python app.py
# -> http://127.0.0.1:5000
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), drop a resume,
optionally paste a JD / pick a preset, then click **Analyze** or
**✨ Tailor to JD**.

Tests + lint (optional):

```powershell
pip install -r requirements-dev.txt
pytest -q
ruff check .
```

---

## 2 · Run with Docker

```powershell
cd C:\Users\N937262\Downloads\AICHAT\resume-checker
docker compose up --build -d
# -> http://127.0.0.1:5050   (compose maps 5000 -> 5050)

docker compose logs -f resume-checker
docker compose down
```

---

## 3 · Deploy on a Linux VM with Nginx + Gunicorn

The whole deployment is scripted. See [`deploy/README.md`](./deploy/README.md)
for the full guide (TLS, firewall, updates, uninstall). TL;DR:

```bash
# Copy the project folder to your VM, then on the VM:
cd /path/to/resume-checker
sudo bash deploy/deploy.sh

# Open:
http://<your-vm-ip>/
```

What it builds:

```
Browser  ──HTTP──▶  Nginx (:80 /:443)  ──proxy──▶  Gunicorn (:5000)
                        │                                │
                        ▼                                ▼
              /opt/resume-checker/static/        Flask app (app:app)
                                                         │
                            ┌────────────────────────────┼────────────────┐
                            ▼                            ▼                ▼
                   rule_based tailor            Ollama (:11434)    OpenAI-compatible API
```

---

## 4 · Enable AI tailoring

### Option A — Local LLM via Ollama (recommended for your VM)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b     # or mistral:7b / phi3:mini for smaller VMs
```

Set these env vars (locally or via `systemctl edit resume-checker`):

```
AI_PROVIDER=ollama
AI_MODEL=llama3.1:8b
OLLAMA_URL=http://127.0.0.1:11434
```

### Option B — Any OpenAI-compatible API

Works with OpenAI, Azure OpenAI, Groq, Together, Mistral API, LM Studio…

```
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_BASE=https://api.openai.com/v1   # or vendor base URL
OPENAI_API_KEY=sk-...
```

### Option C — No AI (default)

Leave `AI_PROVIDER` unset. The rule-based tailor still:

- adds the JD's missing keywords to Skills,
- weaves top-3 missing keywords into Summary,
- flags bullets without numbers,
- produces downloadable DOCX + PDF.

Check which provider is active any time:

```bash
curl -s http://127.0.0.1:5000/api/ai-info
```

---

## 5 · API

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Single-page UI |
| GET | `/api/health` | Liveness probe |
| GET | `/api/ai-info` | Which AI provider is active |
| GET | `/api/presets` | List preset role JDs |
| POST | `/api/analyze` | Multipart: `file` + optional `jd_text` / `preset_id` → scorecard JSON |
| POST | `/api/tailor` | Multipart: `file` + `jd_text` / `preset_id` → tailored resume JSON |
| POST | `/api/download/docx` | JSON body (tailored dict) → `.docx` file |
| POST | `/api/download/pdf` | JSON body (tailored dict) → `.pdf` file |

Example — score a resume against the DevOps preset:

```bash
curl -s -X POST http://127.0.0.1:5000/api/analyze \
  -F "file=@samples/my_resume.pdf" \
  -F "preset_id=devops_engineer" | jq
```

Example — tailor + download PDF in one shot:

```bash
curl -s -X POST http://127.0.0.1:5000/api/tailor \
  -F "file=@samples/my_resume.pdf" \
  -F "preset_id=devops_engineer" > /tmp/tailored.json

curl -s -X POST http://127.0.0.1:5000/api/download/pdf \
  -H "Content-Type: application/json" \
  --data @/tmp/tailored.json \
  --output /tmp/tailored.pdf
```

---

## 6 · Reset / clean-up

Local venv:

```powershell
Remove-Item -Recurse -Force .\.venv
```

Docker:

```powershell
docker compose down -v
```

Linux VM — see [`deploy/README.md`](./deploy/README.md) `## Uninstall`.

---

Made for local / private VM use. Keep the folder inside `AICHAT/`. 🎯
