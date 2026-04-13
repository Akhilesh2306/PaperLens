# PaperLens — Master Implementation Plan & Complete Progress Tracker

> **Single source of truth** for all work across Backend, Frontend, and Infrastructure/Learning tracks.
> Covers 16 calendar weeks, 3 parallel tracks, ~170+ files, and every task from skeleton to portfolio.
>
> Generated from: `PAPERLENS_IMPLEMENTATION_PLAN.md`, `PAPERLENS_FRONTEND_PLAN.md`, `PAPERLENS_UNIFIED_PLAN.md`, `SESSION_CONTEXT.md`, `PAPERLENS_FULL_CONTEXT.md`
>
> Visual companion: `PAPERLENS_MASTER_STORYBOOK.html`

---

## Table of Contents

1. [Project Identity & Overview](#1-project-identity--overview)
2. [The Problem & Solution](#2-the-problem--solution)
3. [System Architecture](#3-system-architecture)
4. [Key Architecture Decisions](#4-key-architecture-decisions)
5. [Technology Stack (All Tracks)](#5-technology-stack-all-tracks)
6. [Three-Track Strategy](#6-three-track-strategy)
7. [16-Week Calendar (Bird's Eye)](#7-16-week-calendar-birds-eye)
8. [Phase 1 — Foundations (CW 1-4)](#8-phase-1--foundations-cw-1-4)
9. [Phase 2 — MLOps & Search (CW 5-8)](#9-phase-2--mlops--search-cw-5-8)
10. [Phase 3 — Infrastructure & Security (CW 9-12)](#10-phase-3--infrastructure--security-cw-9-12)
11. [Phase 4 — Advanced & Portfolio (CW 13-16)](#11-phase-4--advanced--portfolio-cw-13-16)
12. [Backend Deep Dives (Weeks 1-8)](#12-backend-deep-dives-weeks-1-8)
13. [Frontend Deep Dives (Weeks 1-6)](#13-frontend-deep-dives-weeks-1-6)
14. [Agentic RAG Architecture (W7+W8)](#14-agentic-rag-architecture-w7w8)
15. [Complete File Inventory](#15-complete-file-inventory)
16. [Testing Strategy](#16-testing-strategy)
17. [Design Patterns & SOLID Principles](#17-design-patterns--solid-principles)
18. [Portfolio Outcomes](#18-portfolio-outcomes)
19. [Interview Preparation Map](#19-interview-preparation-map)
20. [Progress Summary](#20-progress-summary)

---

## 1. Project Identity & Overview

| Field | Value |
|-------|-------|
| **Name** | PaperLens |
| **Type** | Production-grade Agentic Literature Review Engine |
| **Purpose** | Personal learning project → deployable portfolio piece demonstrating senior AI engineer capabilities |
| **Local Path** | `c:\Users\UB992GN\OneDrive - EY\Documents\Self-Projects\PaperLens` |
| **Reference Course** | `c:\Users\UB992GN\OneDrive - EY\Documents\Self-Projects\production-agentic-rag-course` |
| **Code Overlap** | ~85% identical to reference course, ~15% domain adaptation, Week 8 entirely new |
| **Branch** | `main` |
| **Python** | 3.12 (pinned `>=3.12,<3.13`) |
| **Package Manager** | UV |

### User Context

- **Background**: AI/ML developer, 1-2 years professional experience
- **Goal**: Transition to AI Integration Engineer (JD requires 4-7 years)
- **Available**: 3-4 hours/day for 16 weeks (~400 total hours)
- **Hardware**: CPU only, 8-16GB RAM, Windows OS, VS Code
- **Cloud**: GCP Free Trial ($300 credits) from Week 9

### Working Agreement

- **User writes all code**. Assistant guides, reviews, and explains the *why*.
- **Incremental development**: Only build what's needed for the current week.
- **Git discipline**: Logical, atomic commits. Imperative mood. Commit after logical units.
- **No cosmetics over code**: Focus on implementation, not formatting.
- **Reference code is reference only**: Reason from the implementation plan + first principles.

---

## 2. The Problem & Solution

### The Problem

Researchers in 2026 juggle 4-5 fragmented tools for literature reviews. 46.3% struggle with synthesizing data, 41.3% can't identify cross-source patterns. Systematic reviews cost £13,825-£35,781 and take 60+ hours. No existing tool handles cross-paper synthesis, contradiction detection, or persistent research memory.

### What PaperLens Does

Given a research question, PaperLens:

1. **Discovers** papers from Semantic Scholar (200M+ papers, all disciplines)
2. **Downloads & parses** full-text PDFs using Docling (tables, sections, references)
3. **Indexes** with hybrid search (BM25 + Jina 1024-dim embeddings + RRF via OpenSearch)
4. **Answers** research questions using a local LLM with hybrid retrieval (RAG)
5. **Synthesizes** findings across multiple papers (cross-paper analysis)
6. **Detects contradictions** between papers (conflicting findings, methods, conclusions)
7. **Self-critiques** via a reflection loop that scores and improves output quality
8. **Remembers** prior research sessions (persistent knowledge base)
9. **Reasons** intelligently about when/how to retrieve (Agentic RAG via LangGraph)
10. **Monitors** with distributed tracing (Langfuse) and caches repeated queries (Redis)
11. **Serves** via REST API, React frontend, Gradio web UI, and Telegram bot

### Who This Serves

- Graduate students & postdocs conducting literature reviews
- Industry R&D professionals tracking state-of-the-art
- Independent researchers processing hundreds of papers
- Anyone asking: _"What is the current evidence on [topic] and where do the studies disagree?"_

### Pain Points Solved

| Pain Point | Today | PaperLens |
|---|---|---|
| Paper discovery | Manual search across 3+ databases | Automated daily ingestion from Semantic Scholar |
| Reading 50+ papers | 60+ hours of manual review | Hybrid search surfaces most relevant chunks |
| Finding contradictions | Read every paper end-to-end | Contradiction detection node identifies conflicts |
| Synthesizing findings | Copy-paste quotes into docs | Cross-paper synthesis with citations |
| Losing context | Start from scratch each session | Persistent research memory across sessions |
| Quality assurance | Re-read and manually verify | Critic agent scores and improves iteratively |

---

## 3. System Architecture

```
┌──────────────────┐    ┌─────────────────────────┐    ┌───────────────────┐
│    Data Source    │    │  Data Processing (DAG)  │    │     Storage       │
│ Semantic Scholar  │───▶│  Airflow: Fetch → Parse │───▶│ PostgreSQL (meta) │
│       API        │    │  → Chunk → Embed → Index │    │ OpenSearch (search)│
└──────────────────┘    └─────────────────────────┘    └───────────────────┘
                                                              │
┌──────────────────┐    ┌─────────────────────────┐           │
│     Clients      │    │      API Layer          │◀──────────┘
│  React Frontend  │◀──▶│  FastAPI + Routers      │
│  Gradio UI       │    │  /search /ask /ask-agent │
│  Telegram Bot    │    │  /synthesize /memory     │
└──────────────────┘    └──────────┬──────────────┘
                                   │
                        ┌──────────▼──────────────┐
                        │      Core Services      │
                        │  Ollama (LLM)           │
                        │  Jina (Embeddings)      │
                        │  Redis (Cache+Memory)   │
                        │  Langfuse (Tracing)     │
                        │  LangGraph (Agent)      │
                        │  ┌────────────────────┐ │
                        │  │ Week 8 Extensions  │ │
                        │  │ Synthesis Node     │ │
                        │  │ Contradiction Node │ │
                        │  │ Critic Node        │ │
                        │  │ Memory Node        │ │
                        │  └────────────────────┘ │
                        └─────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────┐
│                     Infrastructure Layer                            │
│  Docker Compose (dev) → Helm Chart → GKE (prod) via Argo CD       │
│  Prometheus + Grafana │ Trivy + Snyk │ Terraform (GCP IaC)         │
└─────────────────────────────────────────────────────────────────────┘
```

### Frontend Architecture (React)

```
App
├── SettingsProvider (Context)
│   ├── Layout
│   │   ├── Navbar → NavLink (×N)
│   │   ├── Sidebar
│   │   │   ├── RecentQueries
│   │   │   ├── MemoryCards (Week 5)
│   │   │   └── FilterPanel (Search page)
│   │   ├── MainContent (Router Outlet)
│   │   │   ├── HomePage
│   │   │   ├── SearchPage → SearchBar, SearchResults → PaperCard (×N), Pagination
│   │   │   ├── ChatPage → ChatPanel → ChatMessage (×N) → SourceCard (×N), StreamingIndicator, ChatInput
│   │   │   ├── SynthesisPage → SynthesisForm, SynthesisResult → FindingsList, ContradictionCard (×N), ReasoningTrace
│   │   │   └── HealthPage → HealthDashboard → ServiceStatusCard (×N)
│   │   └── StatusBar
│   └── ErrorBoundary
```

---

## 4. Key Architecture Decisions

### PaperLens vs Reference Course

| Component | arXiv RAG (Course) | PaperLens | Rationale |
|---|---|---|---|
| Data source | arXiv API (CS/AI only) | Semantic Scholar API (all disciplines, 200M+) | Global access, richer metadata |
| Paper model | arxiv_id, categories | paper_id (S2), fields_of_study, citation_count, year, venue, is_open_access, tldr | Richer metadata |
| Domain guardrail | "Is this CS/AI/ML?" | "Is this a scientific research question?" | Broader scope |
| Agent nodes (W7) | 7 nodes | Same 7 nodes | Identical |
| Agent nodes (W8) | — | +4 nodes: synthesis, contradiction, critic, memory | Entirely new |

### User's Design Choices (Deviations)

| Decision | Course | PaperLens | Rationale |
|---|---|---|---|
| Database driver | Sync (psycopg2) | Async (asyncpg + async_sessionmaker) | Non-blocking for FastAPI |
| Config location | `src/config.py` | `src/settings/config.py` + `src/settings/logging.py` | Settings as a package |
| Environment values | development/staging/production | DEV/UAT/PROD | User preference |
| Exception naming | `OllamaConnectionError` | `OllamaConnectionException` | Consistent style |
| Method naming | `teardown()` | `close()` | User preference |
| ORM style | Legacy `Column()` | `Mapped[]` + `mapped_column()` | Modern SQLAlchemy 2.0 |
| Base class | `declarative_base()` | `DeclarativeBase` | Modern approach |

### Core Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| BM25 before vectors | Professional RAG starts with keyword search (90% baseline) | Proven, then enhanced |
| Hybrid search with RRF | Reciprocal Rank Fusion | Combines BM25 precision + semantic recall |
| Local LLM (Ollama) | No API keys needed | Private, cost-free |
| Factory pattern everywhere | Decouples construction from use | Enables testing |
| Pydantic Settings | Type-safe config with env-var loading | Nested prefixes |
| Abstract DB interface | Swap backends without touching business logic | Flexibility |
| LangGraph for agentic | State machine: guardrail → retrieve → grade → rewrite | Explicit workflow |
| Graceful degradation | Embeddings fail → BM25. Cache down → skip. | Resilience |
| React (not TypeScript) | Lower barrier for React beginner | Learn fundamentals first |
| Vite + React SPA | No SSR needed, tool not content site | Simplicity |
| Tailwind CSS | Utility-first, no CSS files | Rapid prototyping |
| fetch (not axios) | Built-in, zero dependencies | Teaches fundamentals |

---

## 5. Technology Stack (All Tracks)

### Track A — Backend

| Component | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.12 | Application code |
| Package Manager | UV | latest | Fast dependency management |
| Web Framework | FastAPI | ≥0.115 | REST API with async |
| ORM | SQLAlchemy | ≥2.0 (async) | Database abstraction |
| DB Driver | asyncpg | latest | Async PostgreSQL |
| Validation | Pydantic v2 + Settings | ≥2.11 | Data validation & config |
| HTTP Client | httpx | ≥0.28 | Async HTTP requests |
| Database | PostgreSQL | 16-alpine | Paper metadata storage |
| Search Engine | OpenSearch | 2.19.0 | BM25 + KNN search |
| Search Dashboard | OpenSearch Dashboards | 2.19.0 | Search visualization |
| LLM Server | Ollama | 0.11.2 | Local LLM (llama3.2:1b) |
| Orchestration | Apache Airflow | 2.10.3 | Daily paper ingestion |
| Cache | Redis | 7-alpine | Response caching + memory |
| Tracing | Langfuse | v3 | Observability |
| Langfuse Backend | ClickHouse | 24.8-alpine | Analytics backend |
| Langfuse Storage | MinIO | latest | Blob storage |
| Agent Framework | LangGraph | ≥0.2 | State machine agent |
| LangChain | LangChain | ≥0.3 | LLM abstractions |
| PDF Parsing | Docling | ≥2.43 | Table extraction |
| Embeddings | Jina AI v3 | 1024-dim | Passage/query vectors |
| Telegram | python-telegram-bot | ≥21 | Bot interface |
| Web UI (dev) | Gradio | ≥4.0 | Developer UI |
| Linting | Ruff | latest | Code quality |
| Testing | pytest + pytest-asyncio | latest | Async testing |

### Track B — Frontend

| Component | Technology | Version | Purpose |
|---|---|---|---|
| UI Library | React | 19 | Component-based UI |
| Build Tool | Vite | 6+ | Dev server + bundler |
| Language | JavaScript | ES2022+ | No TypeScript |
| Routing | React Router | 7 | Client-side SPA routing |
| Styling | Tailwind CSS | 4 | Utility-first CSS |
| Testing | Vitest + React Testing Library | latest | Component testing |
| Production Server | Nginx | alpine | Static serve + proxy |
| Package Manager | npm | (ships with Node 22) | Dependencies |
| Linting | ESLint | latest | Code quality |
| Formatting | Prettier | latest | Code formatting |

### Track C — Infrastructure & Learning

| Component | Technology | Purpose |
|---|---|---|
| Local K8s | Minikube | Learning + dev |
| Cloud K8s | GKE Autopilot | Production |
| K8s Packaging | Helm | Chart management |
| CI/CD | GitHub Actions | Pipeline automation |
| GitOps | Argo CD | Git-driven deployment |
| Progressive Delivery | Argo Rollouts | Canary deployments |
| IaC | Terraform | GCP provisioning |
| Cloud | GCP (GKE, AR, Cloud SQL) | Production infra |
| ML Tracking | MLflow | Experiment tracking |
| ML Logging | Weights & Biases | Experiment comparison |
| Model Serving | BentoML | Classifier serving |
| Model Export | ONNX + ONNX Runtime | Optimized inference |
| Monitoring | Prometheus + Grafana | Metrics + dashboards |
| Container Scanning | Trivy | Image vulnerabilities |
| Dependency Scanning | Snyk | Library vulnerabilities |
| SAST | SonarCloud | Code quality/security |
| Policy Engine | OPA Gatekeeper | K8s policy enforcement |
| RAG Evaluation | Ragas | Faithfulness, relevancy |
| Drift Monitoring | Evidently | Data/model drift |
| PII Redaction | Presidio | GDPR/CCPA compliance |

### Data Source

| Field | Detail |
|---|---|
| API | Semantic Scholar Graph API v1 |
| Base URL | `https://api.semanticscholar.org/graph/v1` |
| Coverage | 200M+ papers, all disciplines |
| Rate Limit | 1 req/s (unauth) / 10 req/s (with API key) |
| Auth | Optional `x-api-key` header (free) |
| Key Endpoints | `/paper/search`, `/paper/{id}`, `/paper/batch` |

---

## 6. Three-Track Strategy

### Track A — PaperLens Backend (8 Backend Weeks)

The core agentic RAG application. 80+ source files. Python 3.12, FastAPI, SQLAlchemy async, OpenSearch, Ollama, Airflow, LangGraph, Redis, Langfuse.

### Track B — PaperLens Frontend (6 Frontend Weeks)

Production React SPA replacing Gradio as primary UI. Chat-first with search, synthesis, agent trace, memory. 45+ files. React 19, Vite 6, Tailwind CSS 4, Nginx.

### Track C — Infrastructure & Learning (16 Learning Weeks)

Bridges AI Developer → AI Integration Engineer. K8s, CI/CD, MLOps, Terraform, DevSecOps, monitoring. Includes Paper Classifier side project for MLOps skills.

### Daily Schedule (3-4 hours)

| Block | Duration | Activity |
|---|---|---|
| Block 1 | 1.5-2 hrs | Track A (Backend) or Track B (Frontend) |
| Block 2 | 1-1.5 hrs | Track C (Infrastructure/Learning) |
| Block 3 | 30 min | Documentation, notes, review |

---

## 7. 16-Week Calendar (Bird's Eye)

| CW | Track A (Backend) | Track B (Frontend) | Track C (Infra/Learning) |
|:---:|---|---|---|
| **1** | Backend W1 (Part 1) | — | K8s basics |
| **2** | Backend W1 (Part 2) | — | Deploy on Minikube |
| **3** | Backend W2 (Part 1) | — | GitHub Actions CI |
| **4** | Backend W2 (Part 2) | FE W1 (React shell) | Helm chart |
| **5** | Backend W3 | FE W2 (Health dashboard) | MLflow + Paper Classifier |
| **6** | Backend W4 | FE W3 (Search page) | DistilBERT + LoRA |
| **7** | Backend W5 (Part 1) | FE W3 (finish) | ONNX + BentoML |
| **8** | Backend W5 (Part 2) | FE W4 (Chat + streaming) | BentoML deploy + W&B |
| **9** | Backend W6 (Part 1) | FE W4 (finish) | Terraform + GCP setup |
| **10** | Backend W6 (Part 2) | FE W5 (Routing + Agent) | GKE via Terraform |
| **11** | Polish + bugs | FE W5 (finish) | Prometheus/Grafana + DevSecOps |
| **12** | Polish + bugs | FE W6 (Production deploy) | OPA policies |
| **13** | Backend W7 | FE W6 (finish) | Argo CD GitOps |
| **14** | Backend W7 (finish) | — | Ragas + Evidently |
| **15** | Backend W8 | — | AI Safety (Presidio) |
| **16** | Backend W8 (finish) | — | Portfolio polish |

---

## 8. Phase 1 — Foundations (CW 1-4)

### Phase 1 Deliverables

| Deliverable | Status |
|---|---|
| PaperLens Backend Weeks 1-2 complete (FastAPI + data ingestion) | 🟡 |
| Frontend Week 1 complete (React shell with Tailwind) | ❌ |
| Minikube cluster running PaperLens | ❌ |
| Helm chart for PaperLens (API + Postgres + OpenSearch) | ❌ |
| GitHub Actions CI pipeline (lint → test → build → push) | ❌ |

---

### Calendar Week 1

#### Track A — Backend Week 1 (Part 1): Infrastructure & Project Skeleton

> **Goal**: FastAPI app scaffold with PostgreSQL, settings, exceptions, DB abstraction, ORM model, schemas, and repository.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `pyproject.toml` | Project config, deps, dev deps, ruff, pytest | ✅ |
| 2 | `.env.example` / `.env` | Environment configuration (Week 1 vars only) | ✅ |
| 3 | `src/settings/config.py` | BaseConfigSettings, OpenSearchSettings, Settings, get_settings() | ✅ |
| 4 | `src/settings/logging.py` | setup_logging() with basicConfig | ✅ |
| 5 | `src/exceptions.py` | Full exception hierarchy (Repository, Parsing, PDF, OpenSearch, LLM, Config) | ✅ |
| 6 | `src/db/interfaces/base.py` | BaseDatabase(ABC), BaseRepository(ABC) — all async | ✅ |
| 7 | `src/db/interfaces/postgresql.py` | Base(DeclarativeBase), PostgreSQLSettings, PostgreSQLDatabase (async) | ✅ |
| 8 | `src/db/interfaces/__init__.py` | DB interface exports | ✅ |
| 9 | `src/db/factory.py` | async make_database() → PostgreSQLDatabase | ✅ |
| 10 | `src/models/paper.py` | Paper ORM model (25+ S2 fields, PDF content, timestamps) | ✅ |
| 11 | `src/schemas/semantic_scholar/paper.py` | SemanticScholarPaper (S2 aliases), PaperBase, PaperCreate, PaperResponse | ✅ |
| 12 | `src/schemas/api/health.py` | ServiceStatus, HealthResponse | ✅ |
| 13 | `src/repositories/paper.py` | Async PaperRepository (CRUD, upsert, stats, get_by_s2_id) | ✅ |

**Implementation details:**
- Config uses Pydantic Settings with `frozen=True`, `env_nested_delimiter="__"`
- SemanticScholarSettings with `env_prefix="SEMANTIC_SCHOLAR__"` (base_url, api_key, max_results, rate_limit_delay, pdf_cache_dir, fields_of_study, paper_fields)
- Paper model: id (UUID), paper_id, title, authors (JSON), abstract, year, venue, citation_count, fields_of_study (JSON), is_open_access, pdf_url, publication_date, tldr, doi, raw_text, sections (JSON), references (JSON), parser_used, parser_metadata (JSON), pdf_processed, pdf_processing_date, created_at, updated_at
- Repository uses `model_dump(exclude_unset=True)` for upsert to avoid overwriting with None

#### Track B — Not Started

No frontend work. Backend foundation needed first.

#### Track C — K8s Basics

| # | Task | Status |
|---|---|---|
| 1 | Install minikube, kubectl, helm | ❌ |
| 2 | Start minikube cluster (4GB RAM, 2 CPUs) | ❌ |
| 3 | Create/inspect/delete Pods, Deployments, Services | ❌ |
| 4 | Learn ConfigMaps vs Secrets | ❌ |
| 5 | Practice: `kubectl get/describe/logs/exec/apply/delete` | ❌ |
| 6 | Create learning manifests: `k8s/learning/01-nginx-pod.yaml` through `05-secret.yaml` | ❌ |

---

### Calendar Week 2

#### Track A — Backend Week 1 (Part 2): Finish Skeleton

> **Goal**: Complete FastAPI app running in Docker with PostgreSQL, OpenSearch, Airflow, and Ollama — all health-checked.

| # | File | Purpose | Status |
|---|---|---|---|
| 14 | `src/middlewares.py` | Request/response logging (log_request, log_error) | ✅ |
| 15 | `src/dependencies.py` | FastAPI DI: SettingsDep, DatabaseDep, SessionDep, OpenSearchDep, etc. | ❌ |
| 16 | `src/routers/health.py` | GET /health endpoint (DB, OpenSearch, Ollama checks) | ❌ |
| 17 | `src/main.py` | FastAPI app with lifespan, router includes | ❌ |
| 18 | `Dockerfile` | Multi-stage build (UV + Python 3.12-slim) | ❌ |
| 19 | `compose.yml` | Docker Compose: api, postgres, opensearch, dashboards, ollama | ❌ |
| 20 | `Makefile` | Dev commands: start, stop, logs, test, lint, health | ❌ |
| 21 | `airflow/Dockerfile` | Airflow container (Python 3.12, PostgreSQL backend) | ❌ |
| 22 | `airflow/entrypoint.sh` | Kill stale, `airflow db init`, create admin, start webserver+scheduler | ❌ |
| 23 | `airflow/requirements-airflow.txt` | httpx, sqlalchemy, pydantic, docling, opensearch-py, psycopg2-binary | ❌ |
| 24 | `airflow/dags/hello_world_dag.py` | Test DAG checking API and DB connectivity | ❌ |
| 25 | `tests/conftest.py` | Global test config + fixtures | ❌ |
| 26 | `tests/unit/test_config.py` | Config/settings tests | ❌ |
| 27 | `tests/api/conftest.py` | FastAPI TestClient + mock overrides | ❌ |
| 28 | `tests/api/routers/test_health.py` | Health endpoint tests | ❌ |
| 29 | `.env.test` | Test environment config | ❌ |

**Implementation details:**
- Dependencies: type-annotated aliases (SettingsDep, DatabaseDep, SessionDep) from `request.app.state`
- Main: `lifespan()` async context manager initializes all services, cleans up on shutdown
- Dockerfile: base stage with UV image, final stage with python:3.12.8-slim, expose 8000
- Compose: health checks, volumes, `paperlens-network`
- Makefile: `start`, `stop`, `restart`, `status`, `logs`, `health`, `setup`, `format`, `lint`, `test`, `clean`

**Verification**: `docker compose up --build -d && curl http://localhost:8000/api/v1/health`

#### Track B — Not Started

#### Track C — Deploy PaperLens on Minikube

| # | Task | Status |
|---|---|---|
| 1 | Create `paperlens` namespace | ❌ |
| 2 | Deploy PostgreSQL on K8s (PVC, probes, Secrets) | ❌ |
| 3 | Build PaperLens Docker image into Minikube | ❌ |
| 4 | Deploy PaperLens API on K8s (2 replicas, probes) | ❌ |
| 5 | Access health endpoint via `minikube service` | ❌ |
| 6 | Practice: port-forward, rolling update, rollback | ❌ |
| 7 | Create `k8s/base/postgres-deployment.yaml` | ❌ |
| 8 | Create `k8s/base/api-deployment.yaml` | ❌ |

---

### Calendar Week 3

#### Track A — Backend Week 2 (Part 1): Data Ingestion Pipeline

> **Goal**: Fetch papers from Semantic Scholar, download PDFs, parse with Docling, store in PostgreSQL.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `src/schemas/pdf_parser/models.py` | PDFContent (raw_text, sections, references, tables, figures, page_count), PDFMetadata | ❌ |
| 2 | `src/services/pdf_parser/docling.py` | Docling wrapper (parse, extract text/sections/tables, OCR fallback) | ❌ |
| 3 | `src/services/pdf_parser/parser.py` | PDFParserService (parse_pdf, validate_pdf, configurable max_pages/OCR) | ❌ |
| 4 | `src/services/pdf_parser/factory.py` | make_pdf_parser_service() | ❌ |
| 5 | `src/services/semantic_scholar/client.py` | S2 API client: search_papers, get_paper, get_papers_batch, get_citations, get_references, download_pdf, rate_limit | ❌ |
| 6 | `src/services/semantic_scholar/factory.py` | make_s2_client() | ❌ |
| 7 | `src/services/metadata_fetcher.py` | Pipeline orchestrator: S2 → download → parse → store, concurrent with semaphores | ❌ |

**Implementation details:**
- S2 client: REST JSON API, `GET /paper/search`, `POST /paper/batch` (500/request), API key as `x-api-key`, pagination via offset+limit
- MetadataFetcher: max_concurrent_downloads=5, max_concurrent_parsing=1 (CPU-heavy), stores TLDR from API, only downloads open-access PDFs
- Response structure: `{total, offset, data: [{paperId, title, abstract, authors, year, venue, citationCount, fieldsOfStudy, isOpenAccess, openAccessPdf: {url}, tldr: {text}, publicationDate}]}`

#### Track B — Not Started

#### Track C — GitHub Actions CI Pipeline

| # | Task | Status |
|---|---|---|
| 1 | Push PaperLens to GitHub | ❌ |
| 2 | Create `.github/workflows/ci.yml` (lint → test → build → push) | ❌ |
| 3 | Set up GitHub Actions service containers (Postgres) | ❌ |
| 4 | Configure GHCR (GitHub Container Registry) | ❌ |
| 5 | Learn: job dependency, branch-conditional jobs, artifact upload | ❌ |

---

### Calendar Week 4

#### Track A — Backend Week 2 (Part 2): Airflow DAG

> **Goal**: Automated daily paper ingestion via Airflow.

| # | File | Purpose | Status |
|---|---|---|---|
| 8 | `airflow/dags/paper_ingestion/common.py` | get_cached_services() (LRU cached) → initialized services | ❌ |
| 9 | `airflow/dags/paper_ingestion/setup.py` | setup_environment() task: verify DB, OpenSearch health, create indices | ❌ |
| 10 | `airflow/dags/paper_ingestion/fetching.py` | fetch_daily_papers(**context): search by fields_of_study, store to DB | ❌ |
| 11 | `airflow/dags/paper_ingestion/indexing.py` | index_papers_hybrid(**context): stub for Week 4 | ❌ |
| 12 | `airflow/dags/paper_ingestion/reporting.py` | generate_daily_report(**context): aggregate stats from XCom | ❌ |
| 13 | `airflow/dags/paper_ingestion_dag.py` | DAG: `0 6 * * 1-5` (weekdays 6AM UTC), retries=2, catchup=False | ❌ |
| 14 | `tests/unit/services/test_s2_client.py` | S2 client tests | ❌ |
| 15 | `tests/unit/services/test_pdf_parser.py` | PDF parser tests | ❌ |
| 16 | `tests/unit/services/test_metadata_fetcher.py` | Metadata fetcher tests | ❌ |

**Verification**: Airflow DAG runs and fetches papers into PostgreSQL.

#### Track B — Frontend Week 1: React Foundations & Project Shell

> **Goal**: JSX, components, props. Build static layout shell with Tailwind CSS. No API calls.

**React concepts**: JSX, Components, Props, Children, Import/Export, className, List rendering (.map() + key)

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `frontend/` (via `npm create vite@latest`) | Vite + React project init | ❌ |
| 2 | `frontend/vite.config.js` | Vite config with Tailwind plugin | ❌ |
| 3 | `frontend/src/styles/index.css` | `@import "tailwindcss"` | ❌ |
| 4 | `frontend/.env.example` | VITE_API_URL=http://localhost:8585 | ❌ |
| 5 | `frontend/src/utils/constants.js` | API_BASE_URL, APP_NAME, NAV_LINKS (Chat, Search, Synthesis, Health) | ❌ |
| 6 | `frontend/src/components/common/LoadingSpinner.jsx` | Spinning indicator (size prop) | ❌ |
| 7 | `frontend/src/components/common/ErrorMessage.jsx` | Error display with optional retry button | ❌ |
| 8 | `frontend/src/components/common/Badge.jsx` | Status badge (success/warning/error/info variants) | ❌ |
| 9 | `frontend/src/components/layout/Navbar.jsx` | Top nav: logo + NAV_LINKS + settings icon | ❌ |
| 10 | `frontend/src/components/layout/Sidebar.jsx` | Left sidebar (240px): Recent Queries, Memory, children slot | ❌ |
| 11 | `frontend/src/components/layout/StatusBar.jsx` | Bottom bar: service status dots (static placeholders) | ❌ |
| 12 | `frontend/src/components/layout/Layout.jsx` | Shell: Navbar + Sidebar + Main + StatusBar (CSS Grid/Flex) | ❌ |
| 13 | `frontend/src/pages/HomePage.jsx` | Welcome + quick-action cards (Search, Ask, Synthesize) | ❌ |
| 14 | `frontend/src/pages/HealthPage.jsx` | Static placeholder (3 cards showing "Checking...") | ❌ |
| 15 | `frontend/src/App.jsx` | Root: `<Layout><HomePage /></Layout>` | ❌ |
| 16 | `frontend/src/main.jsx` | Entry: StrictMode + createRoot + render | ❌ |

**Verification**: `npm run dev` — Navbar, Sidebar, Main Content, StatusBar visible.

#### Track C — Helm Chart for PaperLens

| # | Task | Status |
|---|---|---|
| 1 | `helm create charts/paperlens` | ❌ |
| 2 | Customize `values.yaml` (API + Postgres + OpenSearch) | ❌ |
| 3 | Create templates: deployment, service, configmap, secrets | ❌ |
| 4 | Create `values-dev.yaml` + `values-prod.yaml` | ❌ |
| 5 | `helm install paperlens charts/paperlens -n paperlens` | ❌ |
| 6 | Practice: helm lint, template, upgrade, rollback, uninstall | ❌ |

---

## 9. Phase 2 — MLOps & Search (CW 5-8)

### Phase 2 Deliverables

| Deliverable | Status |
|---|---|
| PaperLens Backend Weeks 3-5 complete (BM25 + hybrid search + RAG) | ❌ |
| Frontend Weeks 2-4 complete (Health, Search, Chat + streaming) | ❌ |
| Paper Classifier trained (DistilBERT + LoRA, CPU) | ❌ |
| MLflow experiment tracking + model registry | ❌ |
| BentoML service + ONNX export | ❌ |

---

### Calendar Week 5

#### Track A — Backend Week 3: Keyword Search (BM25)

> **Goal**: Production BM25 search with filtering, highlighting, pagination, multi-field boosted scoring.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `src/services/opensearch/index_config_hybrid.py` | Index mapping: text fields (title 3x, abstract 2x, chunk_text, tldr 1.5x), keyword fields, integer fields, dense vector (1024d), English analyzer | ❌ |
| 2 | `src/services/opensearch/query_builder.py` | QueryBuilder: build_bm25_query() with multi-match, field boosts, terms/range filters, highlighting | ❌ |
| 3 | `src/services/opensearch/client.py` | OpenSearchClient: health_check, get_index_stats, setup_indices, search_papers (BM25), search_unified | ❌ |
| 4 | `src/services/opensearch/factory.py` | make_opensearch_client() (LRU cached), make_opensearch_client_fresh() | ❌ |
| 5 | `src/schemas/api/search.py` | HybridSearchRequest (query 1-500, size 1-50, from_, filters), SearchHit, SearchResponse | ❌ |
| 6 | `src/routers/hybrid_search.py` | POST /hybrid-search: query → embed → search → map → respond | ❌ |
| 7 | `tests/unit/services/test_opensearch_query_builder.py` | Query builder tests | ❌ |
| 8 | `tests/api/routers/test_hybrid_search.py` | Search endpoint tests | ❌ |
| 9 | `tests/unit/schemas/test_search.py` | Schema validation tests | ❌ |

#### Track B — Frontend Week 2: API Integration & Health Dashboard

> **Goal**: useState/useEffect. API client layer. Live health dashboard.
> **Depends on**: Backend Week 1 (health endpoint)

**React concepts**: useState, useEffect, Conditional rendering, Async/await, Prop drilling, Lifting state up

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `frontend/src/api/client.js` | Base fetch wrapper: apiGet(), apiPost() with error handling | ❌ |
| 2 | `frontend/src/api/health.js` | fetchHealth() → apiGet("/api/v1/health") | ❌ |
| 3 | `frontend/src/components/health/ServiceStatusCard.jsx` | Single service card (name, status dot, message) | ❌ |
| 4 | `frontend/src/components/health/HealthDashboard.jsx` | Dashboard: loading/error/data states, maps services | ❌ |
| 5 | `frontend/src/pages/HealthPage.jsx` | Rewrite: useState + useEffect for live data | ❌ |
| 6 | `frontend/src/components/layout/StatusBar.jsx` | Update: live status from health data | ❌ |
| 7 | `frontend/src/App.jsx` | Lift health state up for StatusBar + HealthPage | ❌ |
| 8 | `frontend/vite.config.js` | Add dev proxy: `/api` → `http://localhost:8585` | ❌ |

#### Track C — MLflow + Paper Classifier Dataset

| # | Task | Status |
|---|---|---|
| 1 | Start MLflow server locally | ❌ |
| 2 | Create Paper Classifier project (`paper-classifier/`) | ❌ |
| 3 | `paper-classifier/src/train_basic.py` — TF-IDF + LogReg baseline in MLflow | ❌ |
| 4 | `paper-classifier/src/registry_demo.py` — Model registry lifecycle | ❌ |
| 5 | `paper-classifier/src/hyperparameter_search.py` — 4 experiments compared | ❌ |
| 6 | `paper-classifier/src/train_wandb.py` — W&B experiment logging | ❌ |

---

### Calendar Week 6

#### Track A — Backend Week 4: Hybrid Search (Chunking + Embeddings + RRF)

> **Goal**: Section-aware chunking, Jina AI embeddings, BM25+vector hybrid with Reciprocal Rank Fusion.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `src/schemas/indexing/models.py` | ChunkMetadata (chunk_index, section_name, word_count, overlap), TextChunk (chunk_id, paper_id, text, title, abstract, metadata) | ❌ |
| 2 | `src/services/indexing/text_chunker.py` | TextChunker: word-based (600w, 100w overlap, 100w min), section-aware (100-800w → single, <100 → merge, >800 → split) | ❌ |
| 3 | `src/schemas/embeddings/jina.py` | EmbeddingRequest (texts, model, task, dimensions), EmbeddingResponse | ❌ |
| 4 | `src/services/embeddings/jina_client.py` | JinaEmbeddingsClient: embed_passages (task=retrieval.passage, batch_size=100), embed_query (task=retrieval.query), model=jina-embeddings-v3, dim=1024 | ❌ |
| 5 | `src/services/embeddings/factory.py` | make_embeddings_client() | ❌ |
| 6 | `src/services/indexing/hybrid_indexer.py` | HybridIndexingService: chunk → embed (batch_size=50) → bulk index to OpenSearch | ❌ |
| 7 | `src/services/indexing/factory.py` | make_hybrid_indexing_service() | ❌ |

**Also update**: OpenSearch client (RRF pipeline, vector search, hybrid native), search router (embed query, hybrid fallback), Airflow indexing task (real implementation).

#### Track B — Frontend Week 3: Search Interface

> **Goal**: Search page with search bar, filters, results. Controlled components, forms, events.
> **Depends on**: Backend Weeks 3-4

**React concepts**: Controlled components, Event handling (onChange, onSubmit), Lifting state up, useCallback, e.preventDefault()

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `frontend/src/api/search.js` | searchPapers(), hybridSearchPapers() | ❌ |
| 2 | `frontend/src/components/search/SearchBar.jsx` | Controlled input + submit form | ❌ |
| 3 | `frontend/src/components/search/FilterPanel.jsx` | Size dropdown, fields checkboxes, min_citations, year_range, hybrid toggle | ❌ |
| 4 | `frontend/src/components/search/PaperCard.jsx` | Title (→S2 link), authors (3+N), abstract (truncate+toggle), citations badge, FoS badges, score | ❌ |
| 5 | `frontend/src/components/search/SearchResults.jsx` | Results list: loading/error/empty/data states, maps hits | ❌ |
| 6 | `frontend/src/components/search/Pagination.jsx` | Prev/Next + page indicator, disabled at bounds | ❌ |
| 7 | `frontend/src/pages/SearchPage.jsx` | Orchestrator: state (query, filters, results, loading, error, page), handlers | ❌ |
| 8 | `frontend/src/utils/formatters.js` | Author/date formatters | ❌ |

#### Track C — DistilBERT Fine-tuning + LoRA

| # | Task | Status |
|---|---|---|
| 1 | `paper-classifier/src/train_distilbert.py` — Fine-tune on paper abstracts (CPU, 2000 samples, 3 epochs) | ❌ |
| 2 | `paper-classifier/src/train_lora.py` — LoRA (r=8, alpha=16, target: q_lin/v_lin, 0.45% trainable) | ❌ |
| 3 | Compare full fine-tune vs LoRA in MLflow UI | ❌ |
| 4 | `paper-classifier/src/compare_runs.py` — Programmatic comparison | ❌ |

---

### Calendar Week 7

#### Track A — Backend Week 5 (Part 1): RAG System

> **Goal**: Full RAG pipeline — retrieve chunks, LLM answer with citations, streaming.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `src/services/ollama/prompts/rag_system.txt` | System prompt: "You are PaperLens...", cite with [S2:paper_id], limit 200 words, note contradictions | ❌ |
| 2 | `src/services/ollama/prompts.py` | RAGPromptBuilder (create_rag_prompt, create_structured_prompt), ResponseParser (parse_structured_response, regex fallback) | ❌ |
| 3 | `src/services/ollama/client.py` | OllamaClient: health_check, list_models, generate, generate_rag_answer, generate_rag_answer_stream (AsyncGenerator), usage metadata | ❌ |
| 4 | `src/services/ollama/factory.py` | make_ollama_client() (LRU cached) | ❌ |
| 5 | `src/schemas/api/ask.py` | AskRequest (query 1-1000, top_k 1-10, use_hybrid, model, fields_of_study), AskResponse, FeedbackRequest/Response | ❌ |
| 6 | `src/routers/ask.py` | POST /ask (standard RAG), POST /stream (SSE streaming), shared _prepare_chunks_and_sources() | ❌ |

#### Track B — Frontend Week 3 (Finish)

| # | Task | Status |
|---|---|---|
| 1 | `frontend/src/App.jsx` — Add temporary state-based page switcher | ❌ |
| 2 | Inject FilterPanel into Sidebar on search page | ❌ |
| 3 | Polish search page end-to-end | ❌ |

#### Track C — ONNX Export + BentoML Serving

| # | Task | Status |
|---|---|---|
| 1 | `paper-classifier/src/export_onnx.py` — Export DistilBERT to ONNX | ❌ |
| 2 | Benchmark PyTorch vs ONNX (1.5-3x speedup) | ❌ |
| 3 | `paper-classifier/src/serve_bentoml.py` — BentoML service (classify + classify_batch) | ❌ |
| 4 | `paper-classifier/bentofile.yaml` — BentoML config | ❌ |
| 5 | `bentoml build` + `bentoml serve` | ❌ |
| 6 | `bentoml containerize` → Docker image | ❌ |

---

### Calendar Week 8

#### Track A — Backend Week 5 (Part 2): Gradio + Finish RAG

| # | File | Purpose | Status |
|---|---|---|---|
| 7 | `src/gradio_app.py` | Gradio: chat interface, model selector, top-K/hybrid toggles, FoS filter, S2 links, streaming | ❌ |
| 8 | `gradio_launcher.py` | Simple launcher: adds src/ to path, calls main() | ❌ |
| 9 | `tests/api/routers/test_ask.py` | RAG endpoint tests | ❌ |

**Update**: `src/main.py` (add Ollama to lifespan, include ask_router)

#### Track B — Frontend Week 4: Chat Interface & Streaming

> **Goal**: Chat UI with streaming SSE. useRef, useReducer, custom hooks.
> **Depends on**: Backend Week 5

**React concepts**: useRef, useReducer, Custom hooks, SSE/ReadableStream, Cleanup functions

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `frontend/src/api/chat.js` | askQuestion() (POST /ask), streamQuestion() (POST /stream with fetch ReadableStream, SSE parsing, abort controller) | ❌ |
| 2 | `frontend/src/hooks/useChat.js` | useReducer-based: ADD_USER_MESSAGE, ADD_ASSISTANT_MESSAGE, APPEND_TOKEN, ADD_SOURCE, COMPLETE_STREAM, SET_ERROR, CLEAR | ❌ |
| 3 | `frontend/src/components/chat/ChatMessage.jsx` | User (right, blue) / Assistant (left, gray) bubbles, timestamp, sources below, streaming cursor | ❌ |
| 4 | `frontend/src/components/chat/SourceCard.jsx` | Citation card: title → S2 link, authors, year, venue, relevance | ❌ |
| 5 | `frontend/src/components/chat/ChatInput.jsx` | Textarea with Enter/Shift+Enter, submit button, disabled while streaming | ❌ |
| 6 | `frontend/src/components/chat/ChatPanel.jsx` | Chat container with auto-scroll (useRef), message list | ❌ |
| 7 | `frontend/src/pages/ChatPage.jsx` | Chat page using useChat() hook | ❌ |

#### Track C — BentoML Deploy + W&B Comparison

| # | Task | Status |
|---|---|---|
| 1 | Deploy BentoML service to Minikube | ❌ |
| 2 | Compare MLflow vs W&B workflows | ❌ |
| 3 | Final Paper Classifier evaluation and documentation | ❌ |

---

## 10. Phase 3 — Infrastructure & Security (CW 9-12)

### Phase 3 Deliverables

| Deliverable | Status |
|---|---|
| PaperLens Backend Weeks 5-6 complete (RAG + observability) | ❌ |
| Frontend Weeks 4-6 complete (Chat, Routing, Agent, Production) | ❌ |
| GCP Free Trial with Terraform-managed infrastructure | ❌ |
| GKE cluster running PaperLens | ❌ |
| Prometheus + Grafana monitoring | ❌ |
| DevSecOps pipeline (Trivy, Snyk, SonarCloud) | ❌ |

---

### Calendar Week 9

#### Track A — Backend Week 6 (Part 1): Observability & Caching

> **Goal**: Langfuse tracing for every RAG request. Redis caching for 150-400x speedup.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `src/services/langfuse/client.py` | LangfuseTracer: get_callback_handler, trace_langgraph_agent, get_trace_id, graceful disable | ❌ |
| 2 | `src/services/langfuse/tracer.py` | RAGTracer: trace_request, trace_embedding, trace_search, trace_prompt_construction, trace_generation (context managers) | ❌ |
| 3 | `src/services/langfuse/factory.py` | make_langfuse_tracer() (LRU cached) | ❌ |
| 4 | `src/services/cache/client.py` | CacheClient: SHA256 key (query+model+top_k+hybrid+FoS), find_cached_response (O(1) GET), store_response (SET with TTL 6h) | ❌ |
| 5 | `src/services/cache/factory.py` | make_redis_client() (connection pooling, retry), make_cache_client() | ❌ |

**Update**: `src/routers/ask.py` (cache check first → tracing spans → cache store), `compose.yml` (add Redis, Langfuse-web, Langfuse-worker, Langfuse-postgres, Langfuse-redis, MinIO, ClickHouse), `.env.example` (Langfuse + Redis vars)

#### Track B — Frontend Week 4 (Finish): Polish Chat

| # | Task | Status |
|---|---|---|
| 1 | Finish chat streaming edge cases | ❌ |
| 2 | Polish ChatMessage/SourceCard rendering | ❌ |
| 3 | Add chat-first as default page | ❌ |

#### Track C — Terraform Fundamentals + GCP Setup

| # | Task | Status |
|---|---|---|
| 1 | Install Terraform, practice with Docker provider | ❌ |
| 2 | `infra/terraform/practice/main.tf` — Local Docker practice | ❌ |
| 3 | Set up GCP Free Trial ($300 credits/90 days) | ❌ |
| 4 | Enable GCP APIs (GKE, Artifact Registry, Cloud SQL, Compute) | ❌ |
| 5 | `infra/terraform/modules/vpc/main.tf` — VPC module | ❌ |
| 6 | `infra/terraform/environments/dev/main.tf` — Dev environment | ❌ |
| 7 | Apply VPC to GCP | ❌ |

---

### Calendar Week 10

#### Track A — Backend Week 6 (Part 2): Finish Observability

| # | Task | Status |
|---|---|---|
| 1 | Verify Langfuse traces in UI | ❌ |
| 2 | Verify Redis caching (check speedup) | ❌ |
| 3 | Test graceful degradation (cache down → skip) | ❌ |

#### Track B — Frontend Week 5: Routing, Agent Mode & Synthesis

> **Goal**: React Router, Agent reasoning trace, Synthesis page, Context for global settings.
> **Depends on**: Backend Weeks 7-8

**React concepts**: React Router (createBrowserRouter, Link, Outlet, useLocation, useNavigate), Context (createContext, Provider, useContext), useLocalStorage custom hook

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `frontend/src/context/SettingsContext.jsx` | Global settings Context + Provider | ❌ |
| 2 | `frontend/src/hooks/useLocalStorage.js` | Persist settings to localStorage | ❌ |
| 3 | `frontend/src/App.jsx` | React Router setup + SettingsProvider wrapping | ❌ |
| 4 | `frontend/src/components/layout/Layout.jsx` | Update: Outlet instead of children | ❌ |
| 5 | `frontend/src/components/layout/Navbar.jsx` | Update: Link + useLocation for active state | ❌ |
| 6 | `frontend/src/api/agent.js` | askAgent() → POST /ask-agent | ❌ |
| 7 | `frontend/src/api/synthesis.js` | synthesizePapers() → POST /synthesize | ❌ |
| 8 | `frontend/src/api/memory.js` | fetchMemories() → GET /memory | ❌ |
| 9 | `frontend/src/components/agent/ReasoningTrace.jsx` | Agent trace timeline visualization | ❌ |
| 10 | `frontend/src/components/synthesis/SynthesisForm.jsx` | Multi-query input form | ❌ |
| 11 | `frontend/src/components/synthesis/ContradictionCard.jsx` | Contradiction display (paper_a vs paper_b) | ❌ |
| 12 | `frontend/src/components/synthesis/FindingsList.jsx` | Key findings with themes | ❌ |
| 13 | `frontend/src/pages/SynthesisPage.jsx` | Synthesis orchestrator | ❌ |
| 14 | `frontend/src/pages/ChatPage.jsx` | Update: agent mode toggle | ❌ |
| 15 | `frontend/src/components/memory/MemoryCard.jsx` | Memory item card | ❌ |
| 16 | `frontend/src/components/memory/MemorySidebar.jsx` | Memory panel in sidebar | ❌ |
| 17 | `frontend/src/pages/NotFoundPage.jsx` | 404 page | ❌ |

#### Track C — GKE Cluster via Terraform

| # | Task | Status |
|---|---|---|
| 1 | `infra/terraform/modules/gke/main.tf` — GKE Autopilot module | ❌ |
| 2 | `infra/terraform/modules/artifact-registry/main.tf` — Docker registry | ❌ |
| 3 | Apply GKE + Artifact Registry to GCP | ❌ |
| 4 | Push Docker image to Artifact Registry | ❌ |
| 5 | Deploy PaperLens on GKE via Helm | ❌ |
| 6 | Set up Terraform remote state in GCS | ❌ |

---

### Calendar Week 11

#### Track A — Backend: Polish + Bug Fixes

| # | Task | Status |
|---|---|---|
| 1 | Fix any bugs from Weeks 1-6 | ❌ |
| 2 | Write missing tests | ❌ |
| 3 | Code review and cleanup | ❌ |

#### Track B — Frontend Week 5 (Finish)

| # | Task | Status |
|---|---|---|
| 1 | Verify all routes end-to-end | ❌ |
| 2 | Polish synthesis page rendering | ❌ |
| 3 | Test Context settings persistence | ❌ |

#### Track C — Prometheus/Grafana + DevSecOps

| # | Task | Status |
|---|---|---|
| 1 | `src/metrics.py` — Prometheus metrics for PaperLens (custom counters/histograms) | ❌ |
| 2 | Add Prometheus middleware to FastAPI | ❌ |
| 3 | Add `/metrics` endpoint | ❌ |
| 4 | Install kube-prometheus-stack via Helm | ❌ |
| 5 | Create ServiceMonitor for PaperLens | ❌ |
| 6 | Build Grafana dashboard (request rate, latency p50/p95/p99, error rate, cache hits) | ❌ |
| 7 | Add Trivy container scanning to CI | ❌ |
| 8 | Add Snyk dependency scanning to CI | ❌ |
| 9 | Add SonarCloud SAST to CI | ❌ |

---

### Calendar Week 12

#### Track A — Backend: Polish + Bug Fixes (cont.)

| # | Task | Status |
|---|---|---|
| 1 | Integration tests against real containers | ❌ |
| 2 | Performance baseline measurements | ❌ |

#### Track B — Frontend Week 6: Production Polish & Deployment

> **Goal**: Error handling, dark/light theme, responsive, testing, Docker + Nginx.

**React concepts**: Error Boundaries, React.lazy, Suspense, React Testing Library, Vitest

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `frontend/src/components/common/ErrorBoundary.jsx` | Error boundary (class component) | ❌ |
| 2 | `frontend/src/context/ThemeContext.jsx` | Dark/light theme toggle (Tailwind dark mode + Context) | ❌ |
| 3 | Responsive layout | Mobile hamburger, stacked cards | ❌ |
| 4 | `frontend/src/App.jsx` | React.lazy + Suspense for code splitting | ❌ |
| 5 | `frontend/tests/setup.js` | Vitest + RTL setup | ❌ |
| 6 | `frontend/tests/components/LoadingSpinner.test.jsx` | Component test | ❌ |
| 7 | `frontend/tests/components/Badge.test.jsx` | Component test | ❌ |
| 8 | `frontend/tests/components/PaperCard.test.jsx` | Component test | ❌ |
| 9 | `frontend/tests/components/SearchBar.test.jsx` | Component test | ❌ |
| 10 | `frontend/tests/components/ChatMessage.test.jsx` | Component test | ❌ |
| 11 | `frontend/tests/components/ChatInput.test.jsx` | Component test | ❌ |
| 12 | `frontend/tests/components/HealthDashboard.test.jsx` | Component test | ❌ |
| 13 | `frontend/tests/hooks/useChat.test.js` | Hook test | ❌ |
| 14 | `frontend/tests/hooks/useLocalStorage.test.js` | Hook test | ❌ |
| 15 | `frontend/Dockerfile` | Multi-stage: Node build → Nginx serve | ❌ |
| 16 | `frontend/nginx.conf` | SPA routing + API proxy + SSE support | ❌ |
| 17 | `frontend/.dockerignore` | Exclude node_modules, dist, tests | ❌ |
| 18 | `compose.yml` | Update: add `frontend` service (port 3000:80) | ❌ |

#### Track C — OPA Policies + DevSecOps in CI

| # | Task | Status |
|---|---|---|
| 1 | Install OPA Gatekeeper on K8s | ❌ |
| 2 | Create constraint templates (enforce resource limits, no privileged containers) | ❌ |
| 3 | Verify policies block non-compliant deployments | ❌ |
| 4 | Full CI: lint → test → scan (Trivy+Snyk+SAST) → build → push | ❌ |

---

## 11. Phase 4 — Advanced & Portfolio (CW 13-16)

### Phase 4 Deliverables

| Deliverable | Status |
|---|---|
| PaperLens Backend Weeks 7-8 complete (agentic RAG + extensions) | ❌ |
| Argo CD GitOps deployment | ❌ |
| Ragas evaluation pipeline for RAG quality | ❌ |
| Evidently data drift dashboard | ❌ |
| Presidio PII redaction | ❌ |
| Portfolio README + interview prep | ❌ |

---

### Calendar Week 13

#### Track A — Backend Week 7: Agentic RAG (LangGraph) & Telegram Bot

> **Goal**: Intelligent agent that decides when/how to retrieve, grades relevance, rewrites queries, transparent reasoning.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `src/services/agents/config.py` | GraphConfig: max_retrieval_attempts=2, guardrail_threshold=60, model, temperature, top_k, use_hybrid, enable_tracing | ❌ |
| 2 | `src/services/agents/models.py` | GuardrailScoring, GradeDocuments, SourceItem, ToolArtefact, RoutingDecision, GradingResult, ReasoningStep | ❌ |
| 3 | `src/services/agents/state.py` | AgentState(TypedDict): messages (add_messages), original_query, rewritten_query, retrieval_attempts, guardrail_result, routing_decision, sources, relevant_sources, grading_results, metadata | ❌ |
| 4 | `src/services/agents/context.py` | Context(dataclass): ollama_client, opensearch_client, embeddings_client, langfuse_tracer, trace, config fields | ❌ |
| 5 | `src/services/agents/prompts.py` | 7 prompts: GUARDRAIL ("Is this scientific research? Score 0-100"), DECISION, GRADE_DOCUMENTS (binary), REWRITE, GENERATE_ANSWER ([Author, Year] citations), SYSTEM_MESSAGE, DIRECT_RESPONSE | ❌ |
| 6 | `src/services/agents/tools.py` | create_retriever_tool(): @tool retrieve_papers(query) → embed → search → Document objects | ❌ |
| 7 | `src/services/agents/nodes/utils.py` | get_latest_query, get_latest_context, create_langfuse_span, end_langfuse_span | ❌ |
| 8 | `src/services/agents/nodes/guardrail_node.py` | ainvoke_guardrail_step: structured output GuardrailScoring, broader scope (any science), fallback=50 | ❌ |
| 9 | `src/services/agents/nodes/out_of_scope_node.py` | Polite rejection | ❌ |
| 10 | `src/services/agents/nodes/retrieve_node.py` | Create AIMessage with tool calls, increment attempts | ❌ |
| 11 | `src/services/agents/nodes/grade_documents_node.py` | Binary relevance grading with routing | ❌ |
| 12 | `src/services/agents/nodes/rewrite_query_node.py` | LLM-based query rewriting with fallback | ❌ |
| 13 | `src/services/agents/nodes/generate_answer_node.py` | Generate answer with [Author, Year] citations | ❌ |
| 14 | `src/services/agents/agentic_rag.py` | AgenticRAGService: _build_graph (7 nodes, conditional edges), ask (validate→trace→invoke→extract) | ❌ |
| 15 | `src/services/agents/factory.py` | make_agentic_rag_service() | ❌ |
| 16 | `src/routers/agentic_ask.py` | POST /ask-agent endpoint | ❌ |
| 17 | `src/services/telegram/bot.py` | Telegram bot interface | ❌ |
| 18 | `src/services/telegram/factory.py` | make_telegram_bot() | ❌ |

#### Track B — Frontend Week 6 (Finish)

| # | Task | Status |
|---|---|---|
| 1 | Run `npm test` — all tests pass | ❌ |
| 2 | `docker compose up` — frontend at localhost:3000 | ❌ |
| 3 | End-to-end smoke test through Nginx proxy | ❌ |

#### Track C — Argo CD GitOps

| # | Task | Status |
|---|---|---|
| 1 | Install Argo CD on K8s | ❌ |
| 2 | Create `argocd/paperlens-app.yaml` Application | ❌ |
| 3 | Configure auto-sync + self-heal | ❌ |
| 4 | CI updates image tag in Git → Argo CD auto-deploys | ❌ |
| 5 | Configure Argo Rollouts for canary (20%→50%→80%→100%) | ❌ |

---

### Calendar Week 14

#### Track A — Backend Week 7 (Finish): Agent Tests

| # | File | Purpose | Status |
|---|---|---|---|
| 19 | `tests/unit/services/agents/test_agentic_rag.py` | Agent service tests | ❌ |
| 20 | `tests/unit/services/agents/test_models.py` | Model tests | ❌ |
| 21 | `tests/unit/services/agents/test_nodes.py` | Node tests | ❌ |
| 22 | `tests/unit/services/agents/test_tools.py` | Tool tests | ❌ |
| 23 | `tests/api/routers/test_agentic_ask.py` | Endpoint tests | ❌ |
| 24 | `tests/unit/services/test_telegram.py` | Telegram tests | ❌ |

#### Track B — No Frontend Work

#### Track C — Ragas Evaluation + Evidently Drift

| # | Task | Status |
|---|---|---|
| 1 | `tests/evaluation/test_rag_quality.py` — Ragas with golden dataset (faithfulness, relevancy, context precision/recall) | ❌ |
| 2 | Add RAG quality gates to CI (faithfulness ≥ 0.7, relevancy ≥ 0.6) | ❌ |
| 3 | `src/services/monitoring/drift_detector.py` — Evidently drift monitoring | ❌ |
| 4 | `airflow/dags/paper_ingestion/monitoring.py` — Weekly drift task | ❌ |
| 5 | Generate HTML drift report | ❌ |

---

### Calendar Week 15

#### Track A — Backend Week 8: PaperLens Extensions

> **Goal**: Cross-paper synthesis, contradiction detection, critic reflection loop, persistent research memory.

| # | File | Purpose | Status |
|---|---|---|---|
| 1 | `src/services/agents/prompts.py` | Add 4 prompts: SYNTHESIS (themes, agreements, gaps), CONTRADICTION (paper_a vs paper_b, nature, reason), CRITIC (faithfulness/completeness/citation/coherence/contradiction scores, pass if ≥0.7), MEMORY_CONTEXT (integrate prior research) | ❌ |
| 2 | `src/services/agents/models.py` | Add: SynthesisResult (key_themes, agreements, gaps, summary), Contradiction (paper_a, paper_b, nature, possible_reason), CriticResult (scores, overall_score, passed, feedback), MemoryEntry (session_id, query, summary, themes, sources, timestamp, tags) | ❌ |
| 3 | `src/services/memory/client.py` | ResearchMemoryClient: Redis-backed, store_memory (key=memory:{session_id}:{ts}, TTL=90d), retrieve_relevant_memories (keyword + LLM scoring, top_k=5), get_session_memories, clear_session | ❌ |
| 4 | `src/services/memory/factory.py` | make_memory_client() | ❌ |
| 5 | `src/services/agents/nodes/synthesis_node.py` | ainvoke_synthesis_step: group chunks by paper → format with metadata → LLM → SynthesisResult, fallback to concatenation | ❌ |
| 6 | `src/services/agents/nodes/contradiction_node.py` | ainvoke_contradiction_step: uses chunks + synthesis → LLM → List[Contradiction], skip if <2 papers, fallback to empty list | ❌ |
| 7 | `src/services/agents/nodes/critic_node.py` | ainvoke_critic_step: LLM scores answer → CriticResult, route to memory_node if passed OR attempts≥2, else back to generate_answer. continue_after_critic() routing function | ❌ |
| 8 | `src/services/agents/nodes/memory_node.py` | ainvoke_memory_step: Phase 1 retrieve prior context, Phase 2 store new finding. Fallback: skip silently if Redis unavailable | ❌ |
| 9 | `src/services/agents/state.py` | Update: add synthesis_result, contradictions, critic_score, critic_feedback, critic_attempts, memory_context, session_id | ❌ |
| 10 | `src/services/agents/agentic_rag.py` | Update graph: grade_documents→synthesis→contradiction→generate_answer→critic→conditional(memory/retry)→memory→END | ❌ |
| 11 | `src/services/agents/context.py` | Update: add memory_client | ❌ |
| 12 | `src/schemas/api/ask.py` | Add: SynthesisAskRequest (query, model, top_k=5, session_id), SynthesisAskResponse (synthesis, contradictions, critic_score, memory_used, trace_id) | ❌ |
| 13 | `src/routers/synthesis.py` | POST /api/v1/synthesize → extended agentic_rag.ask() with synthesis mode | ❌ |

**Extended Agent Graph (W8):**
```
START → guardrail → [in-scope?]
  ├─ NO → out_of_scope → END
  └─ YES → retrieve → tool_retrieve → grade_documents
                                         ├─ irrelevant → rewrite_query → retrieve (loop max 2)
                                         └─ relevant → synthesis_node → contradiction_node
                                                          → generate_answer → critic_node → [quality OK?]
                                                                                ├─ YES → memory_node → END
                                                                                └─ NO → generate_answer (retry max 2)
```

#### Track B — No Frontend Work

#### Track C — AI Safety (Presidio) + Model Cards

| # | Task | Status |
|---|---|---|
| 1 | `src/services/safety/pii_redactor.py` — Presidio PII detection/redaction (PERSON, EMAIL, PHONE) | ❌ |
| 2 | Integrate PII redaction into RAG pipeline | ❌ |
| 3 | `src/services/safety/output_filter.py` — Prompt injection defense + quality filter | ❌ |
| 4 | `docs/model-cards/paperlens-rag.md` — PaperLens RAG model card | ❌ |
| 5 | `paper-classifier/docs/model-card.md` — Classifier model card | ❌ |

---

### Calendar Week 16

#### Track A — Backend Week 8 (Finish): Tests + Evaluation + Gradio

| # | File | Purpose | Status |
|---|---|---|---|
| 14 | `src/gradio_app.py` | Update: add "Literature Synthesis" tab | ❌ |
| 15 | `tests/unit/services/agents/test_synthesis_node.py` | Synthesis tests | ❌ |
| 16 | `tests/unit/services/agents/test_contradiction_node.py` | Contradiction tests | ❌ |
| 17 | `tests/unit/services/agents/test_critic_node.py` | Critic tests | ❌ |
| 18 | `tests/unit/services/agents/test_memory_node.py` | Memory tests | ❌ |
| 19 | `tests/unit/services/test_memory_client.py` | Memory client tests | ❌ |
| 20 | `tests/api/routers/test_synthesis.py` | Synthesis endpoint tests | ❌ |
| 21 | `tests/evaluation/test_synthesis_quality.py` | Quality evaluation: citation coverage, contradiction detection, critic improvement | ❌ |
| 22 | `tests/evaluation/ragas_eval.py` | RAGAS metrics (faithfulness, relevancy, context precision/recall) | ❌ |

**Verification**: Full e2e — query → retrieve → synthesize → contradictions → critique → remember → respond.

#### Track B — No Frontend Work

#### Track C — Portfolio Polish + Interview Prep

| # | Task | Status |
|---|---|---|
| 1 | GitHub Profile README (featured projects, skills table) | ❌ |
| 2 | PaperLens README.md polish (architecture diagram, demo, badges) | ❌ |
| 3 | Paper Classifier README.md polish | ❌ |
| 4 | CONTRIBUTING.md for both repos | ❌ |
| 5 | CI badges (build, coverage, security) | ❌ |
| 6 | Architecture diagrams (Mermaid/Draw.io) | ❌ |
| 7 | System design practice: PaperLens e2e, ML pipeline, CI/CD flow | ❌ |
| 8 | Interview prep: K8s, CI/CD, MLOps, IaC, Security, Monitoring, RAG | ❌ |

---

## 12. Backend Deep Dives (Weeks 1-8)

### Backend Week 1 — Infrastructure & Skeleton

**Config pattern:** BaseConfigSettings → frozen instances, `env_nested_delimiter="__"`. Top-level fields use single underscore env vars. Nested settings classes use double underscore. Validator ensures `postgresql://` or `postgresql+asyncpg://` prefix.

**DB pattern:** `BaseDatabase(ABC)` → `PostgreSQLDatabase`. Uses `create_async_engine` + `async_sessionmaker`. Table creation bridges sync via `await conn.run_sync(Base.metadata.create_all)`. Session as `@asynccontextmanager` with auto-rollback.

**Schema pattern:** `SemanticScholarPaper` (raw API shape, `alias="paperId"`, `populate_by_name=True`) → `PaperBase` (flattened snake_case) → `PaperCreate` (+ PDF fields, all Optional) → `PaperResponse` (+ id, timestamps, `from_attributes=True`).

**Repository pattern:** Takes `AsyncSession` in constructor. Uses `select() + execute() + scalar_one_or_none() / scalars().all()`. `upsert()` uses `model_dump(exclude_unset=True)`.

### Backend Week 2 — Data Ingestion

**S2 Client:** REST JSON API. `GET /paper/search?query=&fields=&offset=&limit=`. `POST /paper/batch` for up to 500 papers. Rate limiting via async sleep. PDF caching (skip if exists). API key as `x-api-key` header.

**MetadataFetcher:** Coordinates S2 → PDF download → Docling parse → DB store. `max_concurrent_downloads=5`, `max_concurrent_parsing=1`. Returns stats dict. Stores TLDR from API. Only downloads open-access PDFs.

**Airflow DAG:** Schedule `0 6 * * 1-5`. Task chain: setup → fetch → index → report → cleanup. Retries=2, 30min delay. Uses `publicationDate` range for incremental fetching.

### Backend Week 3 — Keyword Search (BM25)

**Index mapping:** text fields with boosts (title 3x, abstract 2x, tldr 1.5x), keyword fields, integer fields, dense vector (1024d cosinesimil) — configured now, used from W4. English analyzer with stopwords.

**QueryBuilder:** Multi-match across title/abstract/chunk_text/tldr. Terms filter for fields_of_study. Range filter for citation_count/year. Sort by publication_date for latest. Highlighting config.

**OpenSearchClient:** verify_certs=False for dev, security-disabled mode. Health → cluster green/yellow. Setup → create index + RRF pipeline. Unified search interface (BM25 now, hybrid later).

### Backend Week 4 — Hybrid Search

**TextChunker:** Word-based (600w, 100w overlap, 100w minimum). Section-aware: 100-800w → single chunk, <100w → merge, >800w → split with overlap. Fallback to sliding window. Each chunk gets `chunk_id = f"{paper_id}_chunk_{index}"`.

**Jina client:** Async httpx with Bearer token. `embed_passages` (task=retrieval.passage, batch_size=100) for indexing. `embed_query` (task=retrieval.query) for search. Model: jina-embeddings-v3, dim: 1024.

**HybridIndexingService:** chunk → embed (batch_size=50) → bulk index. `index_paper`, `index_papers_batch`, `reindex_paper`.

### Backend Week 5 — RAG System

**Prompt engineering:** RAGPromptBuilder loads system prompt, formats query + chunks. ResponseParser handles JSON + regex fallback.

**OllamaClient:** health_check (GET /api/version), list_models, generate, generate_rag_answer, generate_rag_answer_stream (AsyncGenerator). usage_metadata: prompt_tokens, completion_tokens, latency_ms.

**Endpoints:** POST /ask (standard RAG), POST /stream (SSE via StreamingResponse — first metadata, then tokens, then completion signal).

### Backend Week 6 — Observability & Caching

**LangfuseTracer:** Wraps v3 SDK. Callback handler for LangChain/LangGraph. Graceful disable if keys not configured.

**RAGTracer:** Purpose-built context managers per stage: request → embedding → search → prompt → generation.

**CacheClient:** Exact-match. Key = SHA256(query+model+top_k+hybrid+FoS), prefix "exact_cache:". O(1) GET/SET with configurable TTL (6h default). 150-400x speedup for repeated queries.

### Backend Week 7 — Agentic RAG & Telegram

**Graph:** 7 nodes, conditional edges. `START → guardrail → [in-scope?] → retrieve → tool_retrieve → grade → [relevant?] → generate / rewrite (loop max 2)`.

**Guardrail:** Broader scope ("any scientific research question"). Rejects cooking, dating, sports. Fallback score=50.

**AgenticRAGService:** `_build_graph()` builds CompiledGraph. `ask()` validates → traces → invokes → extracts.

### Backend Week 8 — PaperLens Extensions

**Synthesis node:** Groups chunks by paper, formats with metadata, LLM generates SynthesisResult (key_themes, agreements, gaps, summary). Fallback to concatenation.

**Contradiction node:** Detects conflicting findings/methods/conclusions. Skips if <2 papers. Returns List[Contradiction] with paper_a, paper_b, nature, possible_reason.

**Critic node:** LLM scores on faithfulness, completeness, citation accuracy, coherence, contradiction handling (each 0-10). Overall score 0.0-1.0. Pass if ≥0.7. Routes back to generate_answer (max 2 retries) or forward to memory_node.

**Memory node:** Phase 1 retrieves relevant prior memories. Phase 2 stores current finding. Redis-backed with session_id prefix. TTL=90 days. Graceful skip if Redis unavailable.

---

## 13. Frontend Deep Dives (Weeks 1-6)

### Frontend Week 1 — React Foundations

**React concepts learned:** JSX, Components, Props, Children, Import/Export, className, List rendering (.map() + key)

**Setup:** `npm create vite@latest frontend -- --template react`, Tailwind v4 CSS-first config (no tailwind.config.js needed, just `@import "tailwindcss"` in CSS and `@tailwindcss/vite` plugin).

**Folder structure:** `src/{api, components/{layout,health,search,chat,agent,synthesis,memory,common}, context, hooks, pages, utils, styles}`

### Frontend Week 2 — API Integration & Health

**React concepts:** useState, useEffect, Conditional rendering, Async/await in effects, Prop drilling, Lifting state up

**Pattern:** Centralized API client (apiGet, apiPost) → feature-specific wrappers (fetchHealth) → components receive data as props

**useEffect rules:** Empty [] = run once on mount. [var1, var2] = run when vars change. No array = every render (avoid). Return cleanup function for subscriptions/timers.

**Vite proxy:** `/api` → `http://localhost:8585` to avoid CORS in development. Nginx does the same in production.

### Frontend Week 3 — Search Interface

**React concepts:** Controlled components, Event handling (onChange, onSubmit, onClick), Lifting state up, useCallback, e.preventDefault()

**Smart/presentational pattern:** SearchPage (smart, manages state + logic) → SearchBar, PaperCard, etc. (presentational, receive props, render UI)

### Frontend Week 4 — Chat & Streaming

**React concepts:** useRef (auto-scroll, EventSource ref), useReducer (complex chat state), Custom hooks (useChat), SSE/ReadableStream, Cleanup functions

**useReducer vs useState:** Chat state has many interrelated pieces. Reducer makes transitions explicit + debuggable + testable.

**SSE with fetch:** EventSource only supports GET, backend uses POST for /stream, so use fetch + ReadableStream + TextDecoder to parse SSE format (`data: {...}\n\n`).

### Frontend Week 5 — Routing, Agent & Synthesis

**React concepts:** React Router (createBrowserRouter, Link, Outlet, useLocation, useNavigate), Context (createContext, Provider, useContext), useLocalStorage

**Context vs prop drilling:** When 3+ levels deep, Context avoids passing props through intermediaries. Only 2-3 global pieces (settings, theme).

### Frontend Week 6 — Production Polish

**React concepts:** Error Boundaries (class component, componentDidCatch), React.lazy + Suspense (code splitting), React Testing Library (user-centric DOM testing)

**Docker:** Multi-stage: Node build stage → Nginx serve stage. nginx.conf handles SPA routing (`try_files $uri /index.html`) + API proxy + SSE support (disable buffering).

---

## 14. Agentic RAG Architecture (W7+W8)

### Week 7 Graph (Base — 7 nodes)

```
START → guardrail → [in-scope?]
                       ├─ NO → out_of_scope → END
                       └─ YES → retrieve → [tool_call?]
                                              ├─ NO → END (direct answer)
                                              └─ YES → tool_retrieve → grade_documents
                                                                          ├─ relevant → generate_answer → END
                                                                          └─ irrelevant → rewrite_query → retrieve (loop max 2)
```

### Week 8 Extended Graph (11 nodes)

```
START → guardrail → [in-scope?]
  ├─ NO → out_of_scope → END
  └─ YES → retrieve → tool_retrieve → grade_documents
                                         ├─ irrelevant → rewrite_query → retrieve (loop max 2)
                                         └─ relevant → synthesis_node → contradiction_node
                                                          → generate_answer → critic_node → [quality ≥ 0.7?]
                                                                                ├─ YES → memory_node → END
                                                                                └─ NO → generate_answer (retry max 2)
```

### Node Descriptions

| Node | Purpose | Input | Output |
|---|---|---|---|
| **guardrail** | Is this scientific research? Score 0-100 | query | GuardrailScoring |
| **out_of_scope** | Polite rejection | query | message |
| **retrieve** | Create tool call for retrieval | query | AIMessage with tool_call |
| **tool_retrieve** | Execute retrieval (embed → search) | tool_call | Document objects |
| **grade_documents** | Binary relevance grading | documents | relevant/irrelevant routing |
| **rewrite_query** | LLM-based query improvement | original query | rewritten query |
| **synthesis** (W8) | Cross-paper synthesis | chunks grouped by paper | SynthesisResult |
| **contradiction** (W8) | Detect conflicting findings | chunks + synthesis | List[Contradiction] |
| **generate_answer** | Answer with citations | context + query | answer text |
| **critic** (W8) | Quality evaluation + routing | answer + sources | CriticResult + route |
| **memory** (W8) | Retrieve prior context + store new | session_id | memory integration |

---

## 15. Complete File Inventory

### Track A — Backend (~80+ files)

| Category | Count | Key Files |
|---|---|---|
| Settings | 3 | `settings/config.py`, `settings/logging.py`, `exceptions.py` |
| Database | 4 | `db/interfaces/base.py`, `postgresql.py`, `factory.py`, `__init__.py` |
| Models | 2 | `models/paper.py`, `__init__.py` |
| Schemas | 8+ | `api/{health,search,ask}.py`, `semantic_scholar/paper.py`, `embeddings/jina.py`, `indexing/models.py`, `pdf_parser/models.py` |
| Repositories | 2 | `repositories/paper.py`, `__init__.py` |
| Routers | 6 | `health.py`, `hybrid_search.py`, `ask.py`, `agentic_ask.py`, `synthesis.py`, `__init__.py` |
| Services | 32+ | `semantic_scholar/*`, `cache/*`, `embeddings/*`, `indexing/*`, `langfuse/*`, `ollama/*`, `opensearch/*`, `pdf_parser/*`, `telegram/*`, `memory/*` |
| Agents | 20 | `agentic_rag.py`, `config.py`, `context.py`, `models.py`, `prompts.py`, `state.py`, `tools.py`, `nodes/*` (11 nodes) |
| Application | 5 | `main.py`, `dependencies.py`, `middlewares.py`, `gradio_app.py`, `metrics.py` |
| Safety | 2 | `safety/pii_redactor.py`, `safety/output_filter.py` |
| Monitoring | 1 | `monitoring/drift_detector.py` |
| Infrastructure | 8 | `Dockerfile`, `compose.yml`, `Makefile`, `pyproject.toml`, `.env.example`, `.env.test`, `gradio_launcher.py`, `README.md` |
| Airflow | 10 | `Dockerfile`, `entrypoint.sh`, `requirements-airflow.txt`, `hello_world_dag.py`, `paper_ingestion_dag.py`, `common.py`, `setup.py`, `fetching.py`, `indexing.py`, `reporting.py`, `monitoring.py` |
| Tests | 25+ | Unit (14), API (5), Integration (1), Evaluation (2) |

### Track B — Frontend (~45 files)

| Category | Count | Key Files |
|---|---|---|
| Config | 5 | `package.json`, `vite.config.js`, `.env.example`, `Dockerfile`, `nginx.conf` |
| API layer | 7 | `client.js`, `health.js`, `search.js`, `chat.js`, `agent.js`, `synthesis.js`, `memory.js` |
| Common components | 4 | `LoadingSpinner.jsx`, `ErrorMessage.jsx`, `Badge.jsx`, `ErrorBoundary.jsx` |
| Layout components | 4 | `Navbar.jsx`, `Sidebar.jsx`, `StatusBar.jsx`, `Layout.jsx` |
| Health components | 2 | `ServiceStatusCard.jsx`, `HealthDashboard.jsx` |
| Search components | 5 | `SearchBar.jsx`, `FilterPanel.jsx`, `PaperCard.jsx`, `SearchResults.jsx`, `Pagination.jsx` |
| Chat components | 4 | `ChatPanel.jsx`, `ChatInput.jsx`, `ChatMessage.jsx`, `SourceCard.jsx` |
| Agent components | 1 | `ReasoningTrace.jsx` |
| Synthesis components | 3 | `SynthesisForm.jsx`, `ContradictionCard.jsx`, `FindingsList.jsx` |
| Memory components | 2 | `MemoryCard.jsx`, `MemorySidebar.jsx` |
| Context | 1 | `SettingsContext.jsx` |
| Hooks | 2 | `useChat.js`, `useLocalStorage.js` |
| Pages | 6 | `HomePage.jsx`, `HealthPage.jsx`, `SearchPage.jsx`, `ChatPage.jsx`, `SynthesisPage.jsx`, `NotFoundPage.jsx` |
| Utils | 2 | `constants.js`, `formatters.js` |
| Tests | 9 | Component tests (7) + Hook tests (2) |

### Track C — Infrastructure Files

| Category | Key Files |
|---|---|
| K8s learning | `k8s/learning/01-nginx-pod.yaml` through `05-secret.yaml` |
| K8s base | `k8s/base/postgres-deployment.yaml`, `api-deployment.yaml` |
| Helm chart | `charts/paperlens/Chart.yaml`, `values.yaml`, `values-{dev,prod}.yaml`, `templates/*` |
| GitHub Actions | `.github/workflows/ci.yml`, `.github/workflows/deploy.yml` |
| Terraform | `infra/terraform/modules/{vpc,gke,artifact-registry}/`, `environments/dev/`, `practice/` |
| Argo CD | `argocd/paperlens-app.yaml` |
| Paper Classifier | `paper-classifier/src/{train_basic,train_distilbert,train_lora,export_onnx,serve_bentoml,compare_runs,registry_demo,hyperparameter_search,train_wandb}.py`, `bentofile.yaml` |
| Docs | `docs/model-cards/paperlens-rag.md`, `paper-classifier/docs/model-card.md` |

---

## 16. Testing Strategy

### Backend Test Structure

```
tests/
├── conftest.py                         # Global fixtures
├── api/
│   ├── conftest.py                     # FastAPI TestClient + mock overrides
│   └── routers/
│       ├── test_health.py              # W1
│       ├── test_hybrid_search.py       # W3
│       ├── test_ask.py                 # W5
│       ├── test_agentic_ask.py         # W7
│       └── test_synthesis.py           # W8
├── evaluation/                         # W8
│   ├── test_synthesis_quality.py
│   └── ragas_eval.py
├── integration/
│   └── test_services.py                # Real containers
└── unit/
    ├── test_config.py                  # W1
    ├── schemas/
    │   └── test_search.py              # W3
    └── services/
        ├── test_s2_client.py           # W2
        ├── test_pdf_parser.py          # W2
        ├── test_metadata_fetcher.py    # W2
        ├── test_opensearch_query_builder.py  # W3
        ├── test_telegram.py            # W7
        ├── test_memory_client.py       # W8
        └── agents/
            ├── test_agentic_rag.py     # W7
            ├── test_models.py          # W7
            ├── test_nodes.py           # W7
            ├── test_tools.py           # W7
            ├── test_synthesis_node.py  # W8
            ├── test_contradiction_node.py # W8
            ├── test_critic_node.py     # W8
            └── test_memory_node.py     # W8
```

### Frontend Test Structure

```
frontend/tests/
├── setup.js
├── components/
│   ├── LoadingSpinner.test.jsx
│   ├── Badge.test.jsx
│   ├── PaperCard.test.jsx
│   ├── SearchBar.test.jsx
│   ├── ChatMessage.test.jsx
│   ├── ChatInput.test.jsx
│   └── HealthDashboard.test.jsx
└── hooks/
    ├── useChat.test.js
    └── useLocalStorage.test.js
```

### Testing Principles

| Principle | Backend | Frontend |
|---|---|---|
| Mock externals | Mock OpenSearch, Ollama, Jina, S2 | Mock fetch / API calls |
| DI overrides | `app.dependency_overrides` | Context providers |
| Async | `pytest-asyncio`, `AsyncMock` | — |
| DOM testing | — | React Testing Library (user-centric) |
| Quality gates | Ragas faithfulness ≥ 0.7 | Components render correctly |
| Factory mocking | polyfactory for test data | — |
| Evaluation | RAGAS + custom quality checks | — |

---

## 17. Design Patterns & SOLID Principles

### Patterns Used

| Pattern | Where | Why |
|---|---|---|
| **Factory** | Every service has a `factory.py` | Decouple construction from use; enable DI |
| **Repository** | `PaperRepository` | Isolate DB queries from business logic |
| **Dependency Injection** | FastAPI `Depends()`, LangGraph `Context` | Testability, loose coupling |
| **Strategy** | OpenSearch (BM25 vs hybrid vs vector) | Swap algorithm without changing callers |
| **Abstract Interface** | `BaseDatabase`, `BaseRepository` | DB backend swappable |
| **Singleton** | `@lru_cache` factories | Reuse expensive connections |
| **Context Manager** | DB sessions, Langfuse spans | Guaranteed resource cleanup |
| **Builder** | `RAGPromptBuilder`, `QueryBuilder` | Complex object construction |
| **State Machine** | LangGraph `AgentState` | Explicit workflow transitions |
| **Observer** | Langfuse tracing throughout | Non-intrusive monitoring |
| **Graceful Degradation** | Embeddings → BM25, Cache miss → generate, Memory down → skip | Partial failures don't crash |
| **Evaluator-Optimizer** | Critic node reflection loop | Quality improves iteratively |
| **Memento** | Research memory persistence | Remembers prior state |
| **Composition** | React: components compose, not inherit | UI building blocks |
| **Controlled Components** | React forms | React controls input value |
| **Custom Hooks** | `useChat()`, `useLocalStorage()` | Reusable stateful logic |

### SOLID Principles

| Principle | Example |
|---|---|
| **S** — Single Responsibility | Each agent node handles ONE step |
| **O** — Open/Closed | New nodes via `graph.add_node` without modifying existing |
| **L** — Liskov Substitution | `PostgreSQLDatabase` fully substitutes `BaseDatabase` |
| **I** — Interface Segregation | Minimal abstract methods in base classes |
| **D** — Dependency Inversion | High-level modules depend on abstractions |

---

## 18. Portfolio Outcomes

### Repository 1: PaperLens (Full-Stack Agentic RAG)

- Production agentic RAG system (Backend + React Frontend)
- 11-node LangGraph agent with synthesis, contradiction, critic, memory
- Hybrid search (BM25 + Jina vectors + RRF via OpenSearch)
- Kubernetes deployment with Helm charts
- Terraform IaC for GCP (GKE, Artifact Registry)
- GitHub Actions CI/CD with DevSecOps scanning
- Prometheus + Grafana monitoring dashboards
- Argo CD GitOps continuous deployment
- Ragas evaluation harness + Evidently drift monitoring
- Presidio PII redaction + AI guardrails

### Repository 2: Paper Classifier (MLOps)

- DistilBERT fine-tuned on scientific paper abstracts
- LoRA parameter-efficient fine-tuning (0.45% trainable params)
- MLflow experiment tracking + model registry
- W&B experiment logging
- BentoML model serving (classify + classify_batch APIs)
- ONNX model export + benchmarking (1.5-3x speedup)

### Business Framing

> **PaperLens** reduces systematic literature review time from **60+ hours to under 8 hours**.
>
> Given a research question, it discovers papers, parses full-text PDFs, synthesizes findings across multiple sources, detects contradictions, and self-critiques output quality via a reflection loop — while building persistent research memory across sessions.
>
> **Key metrics:** Sub-100ms cached response time (150-400x speedup), 200M+ paper corpus, 13 Docker services, 80+ source files, full test suite with evaluation harness.

---

## 19. Interview Preparation Map

| Interview Question | Project Source | Key Points |
|---|---|---|
| "Describe your CI/CD pipeline" | PaperLens GitHub Actions | lint → test → scan (Trivy+Snyk) → build → push → deploy |
| "How do you deploy to K8s?" | PaperLens | Helm chart → Argo CD GitOps on GKE |
| "Experience with MLOps?" | Paper Classifier | MLflow tracking, model registry, BentoML serving, ONNX export |
| "How do you handle IaC?" | PaperLens | Terraform: VPC + GKE + Artifact Registry, remote state in GCS |
| "Security practices?" | Both | Trivy, Snyk, SonarCloud, OPA policies, Presidio PII, Sealed Secrets |
| "Monitoring strategy?" | PaperLens | Prometheus metrics, Grafana dashboards, Langfuse traces, Evidently drift |
| "RAG system design?" | PaperLens | Hybrid search (BM25+vector), agentic retrieval with LangGraph, critic loop |
| "React architecture?" | PaperLens | SPA, composition, hooks, Context, lazy loading, SSE streaming |
| "Model optimization?" | Paper Classifier | ONNX export, LoRA (0.45% params), batch inference |
| "Data pipeline?" | PaperLens | Airflow DAG: S2 fetch → PDF parse → chunk → embed → index (daily) |

### System Design Practice (Draw These)

1. **PaperLens end-to-end**: data ingestion → search → RAG → monitoring → deployment
2. **Paper Classifier MLOps**: data → train → evaluate → register → serve → monitor
3. **CI/CD pipeline**: commit → lint → test → scan → build → push → deploy → verify

### Skills Coverage

**85% of JD covered hands-on:** K8s, Helm, CI/CD, Terraform, DevSecOps, Prometheus/Grafana, MLflow, PyTorch, BentoML, ONNX, Argo CD, Ragas, Evidently, Presidio, Docker, FastAPI, RAG/LLM, LangGraph, Airflow, PostgreSQL, OpenSearch, Redis, React

**15% deferred (conceptual for interviews):** KServe, Seldon Core, Triton, Ray Serve, Kubeflow, Kafka, RabbitMQ, Istio, Envoy, Vault, CUDA, Sigstore, Feast, Great Expectations

---

## 20. Progress Summary

### Current Status

| Track | Progress | Files Done | Files Total |
|---|---|---|---|
| Track A (Backend) | ~18% of W1 | 14 | ~80 |
| Track B (Frontend) | 0% | 0 | ~45 |
| Track C (Infra) | 0% | 0 | ~30 |
| **Overall** | **~5%** | **14** | **~170+** |

### Next Steps

1. **Backend W1**: `dependencies.py` → `routers/health.py` → `main.py` (bring the API alive)
2. Then: `Dockerfile` → `compose.yml` → `Makefile` → Airflow files → tests
3. Once Backend W1 complete: start Track C (K8s basics) in parallel

### Phase Status

| Phase | Calendar Weeks | Status | Progress |
|---|---|---|---|
| Phase 1 — Foundations | CW 1-4 | 🟡 In Progress | ~10% |
| Phase 2 — MLOps & Search | CW 5-8 | ❌ Not Started | 0% |
| Phase 3 — Infra & Security | CW 9-12 | ❌ Not Started | 0% |
| Phase 4 — Advanced & Portfolio | CW 13-16 | ❌ Not Started | 0% |
