# PaperLens — Complete Implementation Plan

> **Goal**: Build a production-grade Agentic Literature Review Engine from scratch, line by line.
> PaperLens helps researchers (academic & industry) discover, analyze, and synthesize scientific papers — using the same production architecture as the arXiv RAG course, extended with cross-paper synthesis, contradiction detection, reflection loops, and persistent research memory.

---

## Table of Contents

1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Technology Stack](#2-technology-stack)
3. [Prerequisites & Environment Setup](#3-prerequisites--environment-setup)
4. [Week 1 — Infrastructure & Project Skeleton](#4-week-1--infrastructure--project-skeleton)
5. [Week 2 — Data Ingestion Pipeline (Semantic Scholar + PDF Parsing + Airflow)](#5-week-2--data-ingestion-pipeline)
6. [Week 3 — Keyword Search with OpenSearch (BM25)](#6-week-3--keyword-search-with-opensearch-bm25)
7. [Week 4 — Hybrid Search (Chunking + Embeddings + RRF)](#7-week-4--hybrid-search-chunking--embeddings--rrf)
8. [Week 5 — Complete RAG System (LLM + Streaming + Gradio)](#8-week-5--complete-rag-system-llm--streaming--gradio)
9. [Week 6 — Observability & Caching (Langfuse + Redis)](#9-week-6--observability--caching-langfuse--redis)
10. [Week 7 — Agentic RAG (LangGraph) & Telegram Bot](#10-week-7--agentic-rag-langgraph--telegram-bot)
11. [Week 8 — PaperLens Extensions (Synthesis · Contradiction · Critic · Memory)](#11-week-8--paperlens-extensions)
12. [Testing Strategy](#12-testing-strategy)
13. [Design Patterns & Principles Reference](#13-design-patterns--principles-reference)

---

## 1. Project Overview & Architecture

### The Problem

Researchers in 2026 juggle 4-5 fragmented tools to complete a single literature review: Semantic Scholar for discovery, Elicit for extraction, Scite for citation verification, NotebookLM for synthesis, and Obsidian for knowledge storage. **None of these tools talk to each other.** 46.3% of researchers struggle with synthesizing large volumes of data and 41.3% can't identify patterns across different sources. Systematic reviews cost £13,825–£35,781 on average and take 60+ hours of manual effort.

No existing AI tool handles **cross-paper synthesis** — they summarize individual papers but fail at detecting contradictions, methodological differences, and research gaps across a corpus. NotebookLM can't cross-reference notebooks. Elicit doesn't synthesize. No tool builds persistent research memory across sessions.

### What We're Building

**PaperLens** — an agentic literature review engine that:
- **Discovers** scientific papers daily from Semantic Scholar (all disciplines, 200M+ papers)
- **Downloads & parses** full-text PDFs using Docling (tables, sections, references extraction)
- **Indexes** papers with both keyword (BM25) and semantic (vector) search via OpenSearch
- **Answers** research questions using a local LLM with hybrid retrieval (RAG)
- **Synthesizes** findings across multiple papers (cross-paper analysis)
- **Detects contradictions** between papers (conflicting findings, methods, conclusions)
- **Self-critiques** via a reflection loop that scores and iteratively improves output quality
- **Remembers** prior research sessions (persistent knowledge base across queries)
- **Reasons** intelligently about when and how to retrieve documents (Agentic RAG)
- **Monitors** everything with distributed tracing and caches repeated queries
- **Serves** users via REST API, Gradio web UI, and Telegram bot

### Who This Serves

- **Graduate students & postdocs** conducting literature reviews as a core part of their work
- **Industry R&D professionals** tracking state-of-the-art in their domain
- **Independent researchers** who need to process hundreds of papers efficiently
- **Anyone** who asks: _"What is the current evidence on [topic] and where do the studies disagree?"_

### The Pain PaperLens Solves

| Pain Point | Today's Reality | PaperLens |
|---|---|---|
| Paper discovery | Manual search across 3+ databases | Automated daily ingestion from Semantic Scholar |
| Reading 50+ papers | 60+ hours of manual review | Hybrid search surfaces the most relevant chunks |
| Finding contradictions | Read every paper end-to-end | Contradiction detection node identifies conflicts |
| Synthesizing findings | Copy-paste quotes into docs | Cross-paper synthesis with citations |
| Losing context | Start from scratch each session | Persistent research memory across sessions |
| Quality assurance | Re-read and manually verify | Critic agent scores and improves output iteratively |

### System Components

```
┌──────────────────┐    ┌─────────────────────────┐    ┌───────────────────┐
│    Data Source    │    │  Data Processing (DAG)  │    │     Storage       │
│ Semantic Scholar  │───▶│  Airflow: Fetch → Parse │───▶│ PostgreSQL (meta) │
│       API        │    │  → Chunk → Embed → Index │    │ OpenSearch (search)│
└──────────────────┘    └─────────────────────────┘    └───────────────────┘
                                                              │
┌──────────────────┐    ┌─────────────────────────┐           │
│     Clients      │    │      API Layer          │◀──────────┘
│  Gradio UI       │◀──▶│  FastAPI + Routers      │
│  Telegram Bot    │    │  /search /ask /ask-agent │
│  curl / HTTP     │    │  /synthesize /memory     │
└──────────────────┘    └──────────┬──────────────┘
                                   │
                        ┌──────────▼──────────────┐
                        │      Core Services      │
                        │  Ollama (LLM)           │
                        │  Jina (Embeddings)      │
                        │  Redis (Cache)          │
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
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Semantic Scholar API** | Free, global (works in India), 200M+ papers, structured metadata, rate-limited (perfect for Airflow) |
| **BM25 before vectors** | Professional RAG starts with keyword search (proven 90% baseline), then adds vectors |
| **Hybrid search with RRF** | Reciprocal Rank Fusion combines BM25 precision + semantic recall |
| **Local LLM (Ollama)** | No API keys needed for LLM; runs privately; cost-free |
| **Factory pattern everywhere** | Decouples configuration from construction; enables testing |
| **Pydantic Settings** | Type-safe config with env-var loading and nested prefixes |
| **Abstract DB interface** | Swap PostgreSQL for any backend without touching business logic |
| **LangGraph for agentic** | State machine approach: guardrail → retrieve → grade → rewrite loop |
| **Graceful degradation** | Embeddings fail? BM25 still works. Cache down? Skip it. |
| **Week 8 extensions build ON TOP** | Learn the core patterns first (Weeks 1-7), then extend with advanced nodes |

### PaperLens vs arXiv RAG Course — What Changes

| Component | arXiv RAG (Course) | PaperLens (Your Project) |
|---|---|---|
| **Data source** | arXiv API (CS/AI only) | Semantic Scholar API (all disciplines, 200M+ papers) |
| **Paper model fields** | arxiv_id, categories | paper_id (S2), fields_of_study, citation_count, year, venue, is_open_access, tldr |
| **Domain guardrail** | "Is this CS/AI/ML?" | "Is this a scientific research question?" (broader) |
| **Prompts/templates** | arXiv-specific citations | Semantic Scholar citations with DOI, year, venue |
| **Airflow DAG** | arXiv XML parsing | S2 JSON parsing, bulk download |
| **Agent nodes (W7)** | 7 nodes (guardrail → generate) | Same 7 nodes |
| **Agent nodes (W8)** | — | +4 nodes: synthesis, contradiction, critic, memory |
| **Config settings** | ArxivSettings | SemanticScholarSettings |
| **Everything else** | Identical | Identical (OpenSearch, Jina, Ollama, Redis, Langfuse, Docker, patterns) |

~85% of code is identical. ~15% changes for domain adaptation. Week 8 is entirely new.

---

## 2. Technology Stack

### Core Application
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.12+ | Application code |
| Package Manager | UV | latest | Fast dependency management |
| Web Framework | FastAPI | ≥0.115 | REST API with async support |
| ORM | SQLAlchemy | ≥2.0 | Database abstraction |
| Validation | Pydantic | ≥2.11 | Data validation & settings |
| HTTP Client | httpx | ≥0.28 | Async HTTP requests |

### Infrastructure (Docker Compose)
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| PostgreSQL | postgres:16-alpine | 5432 | Paper metadata storage |
| OpenSearch | opensearchproject/opensearch:2.19.0 | 9200 | Search engine (BM25 + KNN) |
| OpenSearch Dashboards | opensearchproject/opensearch-dashboards:2.19.0 | 5601 | Search visualization |
| Ollama | ollama/ollama:0.11.2 | 11434 | Local LLM server |
| Apache Airflow | Custom (Python 3.12) | 8080 | Workflow orchestration |
| Redis | redis:7-alpine | 6379 | Response caching + research memory store |
| Langfuse (Web + Worker) | langfuse/langfuse:3 | 3001 | Observability & tracing |
| ClickHouse | clickhouse-server:24.8-alpine | — | Langfuse analytics backend |
| MinIO | minio/minio | 9090 | Langfuse blob storage |

### AI/ML Libraries
| Library | Purpose |
|---------|---------|
| LangGraph (≥0.2) | Agentic workflow state machine |
| LangChain (≥0.3) | LLM abstractions & tool framework |
| langchain-ollama | Ollama LLM integration |
| Docling (≥2.43) | PDF parsing with table extraction |
| Jina AI Embeddings API | 1024-dim vectors (retrieval.passage/query) |
| python-telegram-bot (≥21) | Telegram bot interface |
| Gradio (≥4.0) | Web UI for RAG interaction |

### Data Source
| Service | Details |
|---------|---------|
| Semantic Scholar API | Base URL: `https://api.semanticscholar.org/graph/v1` |
| Rate Limit | 1 request/second (unauthenticated) or 10 req/s (with API key) |
| Coverage | 200M+ papers across all disciplines |
| Auth | Optional API key (free, recommended for higher rate limits) |
| Key Endpoints | `/paper/search`, `/paper/{paper_id}`, `/paper/batch` |

---

## 3. Prerequisites & Environment Setup

### Required Tools
- **Docker Desktop** with Docker Compose (8GB+ RAM allocated, 20GB+ disk)
- **Python 3.12+**
- **UV package manager**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git**
- **A Jina AI API key** (free tier): https://jina.ai/ (needed from Week 4)
- **A Semantic Scholar API key** (free, optional but recommended): https://www.semanticscholar.org/product/api#api-key
- **A Telegram Bot Token** (optional, Week 7): talk to @BotFather on Telegram

### Initial Project Setup (Do This First)

```bash
# 1. Create project directory
mkdir paperlens && cd paperlens

# 2. Initialize UV project
uv init --python 3.12

# 3. Create the directory structure
mkdir -p src/{db/interfaces,models,repositories,routers,schemas/{api,semantic_scholar,common,database,embeddings,indexing,pdf_parser,telegram},services/{agents/nodes,semantic_scholar,cache,embeddings,indexing,langfuse,ollama/prompts,opensearch,pdf_parser,telegram,memory}}
mkdir -p tests/{api/routers,integration,unit/{schemas,services/agents}}
mkdir -p airflow/{dags/paper_ingestion,plugins}
mkdir -p notebooks/week{1,2,3,4,5,6,7,8}
mkdir -p static data/scholar_pdfs

# 4. Create all __init__.py files
find src tests -type d -exec touch {}/__init__.py \;
```

---

## 4. Week 1 — Infrastructure & Project Skeleton

> **Goal**: FastAPI app running in Docker with PostgreSQL, OpenSearch, Airflow, and Ollama — all health-checked.

### Step-by-Step Coding Order

#### Step 1.1: `pyproject.toml` — Project Configuration

Create the project manifest with all dependencies. Start with only Week 1 dependencies; we'll add more each week.

```
File: pyproject.toml
```

**Key points:**
- Project name: `paperlens`
- Use `uv sync` to install dependencies (creates `uv.lock`)
- Dev dependencies separated via `[dependency-groups]`
- Ruff for linting, pytest for testing, mypy for type checking

#### Step 1.2: `.env.example` and `.env`

```
File: .env.example
File: .env  (copy from .env.example and fill in real values)
```

**Key changes from arXiv course:**
- Replace `ARXIV__*` env vars with `SEMANTIC_SCHOLAR__*`
- Add `SEMANTIC_SCHOLAR__API_KEY` (optional, for higher rate limits)
- Add `SEMANTIC_SCHOLAR__BASE_URL=https://api.semanticscholar.org/graph/v1`
- All other service URLs use Docker container hostnames (e.g., `postgres:5432`)
- Nested settings use `__` delimiter

#### Step 1.3: `src/config.py` — Centralized Configuration

This is the **first source file** to write. Everything depends on it.

```
File: src/config.py
```

**What to implement:**
- `BaseConfigSettings` — base class using `pydantic_settings.BaseSettings` with frozen=True, env_nested_delimiter="__"
- `SemanticScholarSettings` — env_prefix="SEMANTIC_SCHOLAR__":
  - `base_url: str = "https://api.semanticscholar.org/graph/v1"`
  - `api_key: Optional[str] = None`
  - `max_results: int = 100`
  - `rate_limit_delay: float = 1.0` (1s unauthenticated, 0.1s with key)
  - `pdf_cache_dir: str = "data/scholar_pdfs"`
  - `fields_of_study: List[str] = ["Computer Science", "Mathematics"]` (default filter)
  - `paper_fields: str = "paperId,title,abstract,authors,year,venue,citationCount,fieldsOfStudy,isOpenAccess,openAccessPdf,tldr,publicationDate"`
- `PDFParserSettings` — env_prefix="PDF_PARSER__", max_pages, OCR toggle
- `ChunkingSettings` — env_prefix="CHUNKING__", chunk_size=600, overlap=100
- `OpenSearchSettings` — env_prefix="OPENSEARCH__", host, index names, vector dimension
- `LangfuseSettings` — env_prefix="LANGFUSE__", keys, host, flush settings
- `RedisSettings` — env_prefix="REDIS__", host, port, TTL
- `TelegramSettings` — env_prefix="TELEGRAM__", bot_token, enabled flag
- `MemorySettings` — env_prefix="MEMORY__":
  - `max_memories_per_session: int = 50`
  - `relevance_threshold: float = 0.7`
  - `ttl_days: int = 90`
- `Settings` — root class composing all sub-settings, plus postgres_database_url, ollama_host, jina_api_key
- `get_settings()` function that returns a Settings instance

**Design pattern:** Pydantic Settings with nested configuration, frozen (immutable) instances, env file loading.

#### Step 1.4: `src/exceptions.py` — Custom Exception Hierarchy

```
File: src/exceptions.py
```

Define all custom exceptions up front:
- `RepositoryException` → `PaperNotFound`, `PaperNotSaved`
- `ParsingException` → `PDFParsingException` → `PDFValidationError`
- `PDFDownloadException` → `PDFDownloadTimeoutError`
- `OpenSearchException`
- `SemanticScholarAPIException` → `SemanticScholarTimeoutError`, `SemanticScholarRateLimitError`
- `MetadataFetchingException` → `PipelineException`
- `LLMException` → `OllamaException` → `OllamaConnectionError`, `OllamaTimeoutError`
- `SynthesisException` → `ContradictionDetectionError`, `CriticLoopError`
- `MemoryException` → `MemoryStoreError`, `MemoryRetrievalError`
- `ConfigurationError`

#### Step 1.5: `src/db/` — Database Abstraction Layer

Write in this order:

1. **`src/db/interfaces/base.py`** — Abstract base classes
   - `BaseDatabase(ABC)`: `startup()`, `teardown()`, `get_session()` → ContextManager[Session]
   - `BaseRepository(ABC)`: `create()`, `get_by_id()`, `update()`, `delete()`, `list()`

2. **`src/db/interfaces/postgresql.py`** — PostgreSQL implementation
   - `PostgreSQLDatabase(BaseDatabase)`:
     - `startup()`: Create engine with connection pooling (`pool_pre_ping=True`), test connection with `SELECT 1`, create all ORM tables via `Base.metadata.create_all()`
     - `teardown()`: Dispose engine
     - `get_session()`: Context manager yielding `Session` with auto-rollback on exception
   - Export `Base = declarative_base()` from here

3. **`src/db/interfaces/__init__.py`** — Export `BaseDatabase`, `BaseRepository`, `PostgreSQLDatabase`

4. **`src/db/factory.py`** — Factory function
   - `make_database() → BaseDatabase`: Get settings, create `PostgreSQLDatabase`, call `startup()`, return

5. **`src/database.py`** — Standalone database access (for Airflow tasks)
   - Global `_database` singleton with `get_database()` and `get_db_session()` context manager

#### Step 1.6: `src/models/paper.py` — ORM Model

```
File: src/models/paper.py
```

SQLAlchemy model for the `papers` table:
- `id`: UUID primary key (uuid4 default)
- `paper_id`: unique string (Semantic Scholar corpus ID, e.g., "649def34f8be52c8b66281af98ae884c09aef38b")
- `title`: string
- `authors`: JSON (list of `{"authorId": "...", "name": "..."}`)
- `abstract`: text
- `year`: integer
- `venue`: string (journal/conference name)
- `citation_count`: integer
- `fields_of_study`: JSON (e.g., `["Computer Science", "Mathematics"]`)
- `is_open_access`: boolean
- `pdf_url`: string (from openAccessPdf)
- `publication_date`: date
- `tldr`: text (Semantic Scholar's auto-generated TLDR)
- `doi`: string (optional)
- `raw_text`: text (extracted PDF content)
- `sections`: JSON (structured sections from Docling)
- `references`: JSON (extracted references)
- `parser_used`: string
- `parser_metadata`: JSON
- `pdf_processed`: boolean (default False)
- `pdf_processing_date`: datetime (nullable)
- `created_at`, `updated_at`: auto-managed timestamps

**Important:** Import `Base` from `src/db/interfaces/postgresql.py` so the model registers with the declarative registry.

#### Step 1.7: `src/schemas/` — Pydantic Schemas

Create the following in order:

1. **`src/schemas/database/config.py`** — `PostgreSQLSettings(BaseModel)` with database_url, echo_sql, pool_size, max_overflow
2. **`src/schemas/semantic_scholar/paper.py`** — `S2Paper`, `PaperBase`, `PaperCreate`, `PaperResponse`, `PaperSearchResponse`
   - `S2Paper` maps the Semantic Scholar API response:
     - `paperId`, `title`, `abstract`, `authors` (list of dicts), `year`, `venue`, `citationCount`, `fieldsOfStudy`, `isOpenAccess`, `openAccessPdf` (optional dict with `url`), `tldr` (optional dict with `text`), `publicationDate`
3. **`src/schemas/api/health.py`** — `HealthResponse`, `ServiceHealth`
4. **`src/schemas/common/__init__.py`** — Empty (placeholder for shared schemas)

#### Step 1.8: `src/repositories/paper.py` — Data Access Layer

```
File: src/repositories/paper.py
```

`PaperRepository` class:
- Takes `Session` in constructor
- Methods: `create()`, `get_by_paper_id()` (was get_by_arxiv_id), `get_by_id()`, `update()`, `upsert()`, `get_all()`, `get_processed_papers()`, `get_unprocessed_papers()`, `get_papers_with_raw_text()`, `get_count()`, `get_processing_stats()`, `get_by_field_of_study(field: str)`, `get_highly_cited(min_citations: int)`

#### Step 1.9: `src/middlewares.py` — Simple Logging

```
File: src/middlewares.py
```

Two simple functions: `log_request()` and `log_error()`. Placeholder for future middleware.

#### Step 1.10: `src/routers/ping.py` — Health Check Endpoint

```
File: src/routers/ping.py
```

`GET /health` endpoint:
- Checks database (SELECT 1), OpenSearch (health_check()), Ollama (health_check())
- Returns `HealthResponse` with overall status ("ok" / "degraded") and individual service statuses
- Uses FastAPI dependency injection for all services

#### Step 1.11: `src/dependencies.py` — FastAPI Dependency Injection

```
File: src/dependencies.py
```

Dependency functions retrieving services from `request.app.state`:
- `get_settings()`, `get_database()`, `get_db_session()`, `get_opensearch_client()`, `get_s2_client()`, etc.
- Type-annotated dependency aliases: `SettingsDep`, `DatabaseDep`, `SessionDep`, `OpenSearchDep`, etc.

#### Step 1.12: `src/main.py` — FastAPI Application

```
File: src/main.py
```

- `lifespan()` async context manager: initializes all services on startup, cleans up on shutdown
- `app = FastAPI(...)` with title="PaperLens", description="Agentic Literature Review Engine", version
- Include routers with prefixes (`/api/v1`)
- For Week 1: only `ping.router`

#### Step 1.13: `Dockerfile` — API Container

```
File: Dockerfile
```

Multi-stage build:
1. **Base stage**: UV image (`ghcr.io/astral-sh/uv:python3.12-bookworm`), install deps with `uv sync --frozen --no-dev`
2. **Final stage**: `python:3.12.8-slim`, copy `/app` from base, expose 8000, run `uvicorn`

#### Step 1.14: `compose.yml` — Docker Compose (Week 1 Services)

Start with only essential services:
- `api` (our FastAPI app)
- `postgres` (PostgreSQL 16)
- `opensearch` (OpenSearch 2.19)
- `opensearch-dashboards`
- `ollama`

Add health checks, volumes, networks (`paperlens-network`). The remaining services (Redis, Langfuse, Airflow, etc.) will be added in later weeks.

#### Step 1.15: `Makefile` — Developer Experience

```
File: Makefile
```

Commands: `start`, `stop`, `restart`, `status`, `logs`, `health`, `setup`, `format`, `lint`, `test`, `clean`

#### Step 1.16: `airflow/` — Basic Airflow Setup

1. **`airflow/Dockerfile`** — Python 3.12 slim, install Airflow 2.10.3 with PostgreSQL backend, create airflow user
2. **`airflow/entrypoint.sh`** — Kill stale processes, `airflow db init`, create admin user, start webserver + scheduler
3. **`airflow/requirements-airflow.txt`** — httpx, sqlalchemy, pydantic, docling, opensearch-py, psycopg2-binary
4. **`airflow/dags/hello_world_dag.py`** — Simple "Hello World" DAG that checks API and DB connectivity

Add the `airflow` service to `compose.yml`.

#### Step 1.17: Verify Week 1

```bash
docker compose up --build -d
curl http://localhost:8000/api/v1/health
# Expected: {"status": "ok", "services": {"database": "healthy", ...}}
```

### Week 1 File Checklist

| # | File | Purpose |
|---|------|---------|
| 1 | `pyproject.toml` | Project config & dependencies |
| 2 | `.env.example` / `.env` | Environment configuration |
| 3 | `src/config.py` | Centralized settings (Pydantic) |
| 4 | `src/exceptions.py` | Custom exception classes |
| 5 | `src/db/interfaces/base.py` | Abstract DB interface |
| 6 | `src/db/interfaces/postgresql.py` | PostgreSQL implementation |
| 7 | `src/db/interfaces/__init__.py` | DB interface exports |
| 8 | `src/db/factory.py` | Database factory |
| 9 | `src/database.py` | Standalone DB access |
| 10 | `src/models/paper.py` | Paper ORM model |
| 11 | `src/models/__init__.py` | Model exports |
| 12 | `src/schemas/database/config.py` | DB config schema |
| 13 | `src/schemas/semantic_scholar/paper.py` | Paper schemas |
| 14 | `src/schemas/api/health.py` | Health check schema |
| 15 | `src/repositories/paper.py` | Paper repository |
| 16 | `src/repositories/__init__.py` | Repository exports |
| 17 | `src/middlewares.py` | Simple logging |
| 18 | `src/routers/ping.py` | Health endpoint |
| 19 | `src/routers/__init__.py` | Router exports |
| 20 | `src/dependencies.py` | DI definitions |
| 21 | `src/main.py` | FastAPI application |
| 22 | `Dockerfile` | API container |
| 23 | `compose.yml` | Docker Compose |
| 24 | `Makefile` | Dev commands |
| 25 | `airflow/Dockerfile` | Airflow container |
| 26 | `airflow/entrypoint.sh` | Airflow startup |
| 27 | `airflow/requirements-airflow.txt` | Airflow deps |
| 28 | `airflow/dags/hello_world_dag.py` | Test DAG |
| 29 | `tests/conftest.py` | Test configuration |
| 30 | `tests/unit/test_config.py` | Config tests |
| 31 | `tests/api/conftest.py` | API test fixtures |
| 32 | `tests/api/routers/test_ping.py` | Health test |

---

## 5. Week 2 — Data Ingestion Pipeline

> **Goal**: Automated pipeline that fetches papers from Semantic Scholar, downloads open-access PDFs, parses them with Docling, and stores everything in PostgreSQL. Orchestrated by Airflow.

### Step-by-Step Coding Order

#### Step 2.1: `src/schemas/pdf_parser/models.py` — PDF Parser Schemas

- `PDFContent(BaseModel)`: raw_text, sections (list of dicts), references, tables, figures, page_count
- `PDFMetadata(BaseModel)`: file_size_bytes, parsing_time_seconds, parser_used, page_count

#### Step 2.2: `src/services/pdf_parser/` — PDF Parsing Service

1. **`src/services/pdf_parser/docling.py`** — Docling wrapper
   - Parse PDF files using `docling` library
   - Extract text, sections, tables, figures
   - Handle OCR fallback for scanned documents

2. **`src/services/pdf_parser/parser.py`** — `PDFParserService` class
   - `parse_pdf(pdf_path: Path) → PDFContent`
   - `validate_pdf(pdf_path: Path) → bool` — file size check, extension check
   - Configurable max_pages, max_file_size, OCR toggle

3. **`src/services/pdf_parser/factory.py`** — `make_pdf_parser_service()`

#### Step 2.3: `src/services/semantic_scholar/` — Semantic Scholar API Client

1. **`src/services/semantic_scholar/client.py`** — `SemanticScholarClient`

   **Key differences from arXiv client:**
   - REST JSON API (not XML). Responses are structured JSON.
   - Uses `GET /paper/search?query={query}&fields={fields}&offset={offset}&limit={limit}`
   - Uses `POST /paper/batch` for bulk fetching by paper IDs
   - Rate limiting: 1 req/s unauthenticated, 10 req/s with API key
   - API key sent as `x-api-key` header (optional)
   - Pagination via `offset` + `limit` (max 100 per request)

   Methods:
   - `async search_papers(query, limit, offset, fields_of_study, year_range, min_citation_count) → List[S2Paper]`
   - `async get_paper(paper_id) → S2Paper` — single paper by S2 ID or DOI
   - `async get_papers_batch(paper_ids) → List[S2Paper]` — up to 500 papers per request
   - `async get_paper_citations(paper_id, limit) → List[S2Paper]`
   - `async get_paper_references(paper_id, limit) → List[S2Paper]`
   - `async download_pdf(pdf_url, paper_id) → Optional[Path]` with retry logic
   - PDF caching: skip download if file already exists
   - `_rate_limit()` — async sleep based on config rate_limit_delay

   **Response parsing:**
   ```python
   # S2 response structure (JSON, not XML):
   {
     "total": 10000,
     "offset": 0,
     "data": [
       {
         "paperId": "649def34...",
         "title": "Attention Is All You Need",
         "abstract": "...",
         "authors": [{"authorId": "123", "name": "Vaswani"}],
         "year": 2017,
         "venue": "NeurIPS",
         "citationCount": 85000,
         "fieldsOfStudy": ["Computer Science"],
         "isOpenAccess": true,
         "openAccessPdf": {"url": "https://..."},
         "tldr": {"text": "..."},
         "publicationDate": "2017-06-12"
       }
     ]
   }
   ```

2. **`src/services/semantic_scholar/factory.py`** — `make_s2_client()`

#### Step 2.4: `src/services/metadata_fetcher.py` — Pipeline Orchestrator

`MetadataFetcher` class:
- Coordinates: SemanticScholarClient → PDF download → PDF parsing → DB storage
- `async fetch_and_process_papers(...)` — main entry point
- Concurrent downloads with semaphore (`max_concurrent_downloads=5`)
- Concurrent parsing with semaphore (`max_concurrent_parsing=1` — Docling is CPU-heavy)
- Returns statistics dict: papers_fetched, pdfs_downloaded, pdfs_parsed, papers_stored, errors
- Stores TLDR from S2 API response (free summary without needing to parse PDF)
- Only attempts PDF download for `is_open_access=True` papers

#### Step 2.5: `airflow/dags/paper_ingestion/` — DAG Task Modules

1. **`common.py`** — `get_cached_services()` (LRU cached) → returns tuple of all initialized services
2. **`setup.py`** — `setup_environment()` → verify DB, OpenSearch health, create indices
3. **`fetching.py`** — `fetch_daily_papers(**context)` → search recent papers by configured fields_of_study, store to DB
4. **`indexing.py`** — `index_papers_hybrid(**context)` → chunk, embed, index (placeholder for Week 4)
5. **`reporting.py`** — `generate_daily_report(**context)` → aggregate stats from XCom

#### Step 2.6: `airflow/dags/paper_ingestion_dag.py` — Production DAG

- Schedule: `0 6 * * 1-5` (weekdays 6 AM UTC)
- Task chain: `setup_environment → fetch_daily_papers → index_papers_hybrid → generate_daily_report → cleanup_temp_files`
- Retries: 2 with 30-minute delay
- Catchup: False
- Uses Semantic Scholar's `publicationDate` range filter for incremental fetching

#### Step 2.7: Update `src/main.py`

Add `s2_client` and `pdf_parser` to lifespan initialization.

### Week 2 New Files

| # | File | Purpose |
|---|------|---------|
| 1 | `src/schemas/pdf_parser/models.py` | PDF parsing schemas |
| 2 | `src/services/pdf_parser/docling.py` | Docling wrapper |
| 3 | `src/services/pdf_parser/parser.py` | PDF parser service |
| 4 | `src/services/pdf_parser/factory.py` | PDF parser factory |
| 5 | `src/services/semantic_scholar/client.py` | Semantic Scholar API client |
| 6 | `src/services/semantic_scholar/factory.py` | S2 client factory |
| 7 | `src/services/metadata_fetcher.py` | Pipeline orchestrator |
| 8 | `airflow/dags/paper_ingestion/common.py` | Shared service init |
| 9 | `airflow/dags/paper_ingestion/setup.py` | Environment setup task |
| 10 | `airflow/dags/paper_ingestion/fetching.py` | Paper fetching task |
| 11 | `airflow/dags/paper_ingestion/indexing.py` | Indexing task (stub) |
| 12 | `airflow/dags/paper_ingestion/reporting.py` | Report generation task |
| 13 | `airflow/dags/paper_ingestion_dag.py` | Main DAG definition |
| 14 | `tests/unit/services/test_s2_client.py` | S2 client tests |
| 15 | `tests/unit/services/test_pdf_parser.py` | PDF parser tests |
| 16 | `tests/unit/services/test_metadata_fetcher.py` | Metadata fetcher tests |

---

## 6. Week 3 — Keyword Search with OpenSearch (BM25)

> **Goal**: Production BM25 search with filtering, highlighting, pagination, and multi-field boosted scoring.

### Step-by-Step Coding Order

#### Step 3.1: `src/services/opensearch/index_config_hybrid.py` — Index Configuration

Define the OpenSearch index mapping as a Python dictionary:
- **Text fields**: `title` (3x boost), `abstract` (2x boost), `chunk_text` (1x), `content` (1x), `tldr` (1.5x boost)
- **Keyword fields**: `paper_id`, `fields_of_study`, `section_name`, `venue`
- **Integer fields**: `citation_count`, `year`
- **Date field**: `publication_date`
- **Dense vector field**: `embedding` (1024 dim, cosinesimil) — configured now, used from Week 4
- **Analyzers**: English analyzer with stopwords

```python
PAPERS_CHUNKS_MAPPING = {
    "settings": { ... },
    "mappings": {
        "properties": { ... }
    }
}
```

#### Step 3.2: `src/services/opensearch/query_builder.py` — Query Construction

`QueryBuilder` class (static methods):
- `build_bm25_query(query, size, from_, fields_of_study, min_citations, year_range, latest_papers)` → OpenSearch query DSL
- Multi-match across title, abstract, chunk_text, tldr with field boosts
- Optional `terms` filter for fields_of_study
- Optional `range` filter for citation_count and year
- Optional sort by `publication_date` for latest papers
- Highlighting configuration for matched fields

#### Step 3.3: `src/services/opensearch/client.py` — OpenSearch Client

`OpenSearchClient`:
- Constructor: host, settings, creates `OpenSearch` client (verify_certs=False for dev, http_auth disabled for security-disabled mode)
- `health_check() → bool` — cluster health green/yellow
- `get_index_stats() → Dict` — document count, size
- `setup_indices(force) → Dict` — create index + RRF pipeline
- `search_papers(query, size, from_, fields_of_study, year_range, min_citations, latest) → Dict` — BM25 search
- `search_unified(...)` — unified interface (BM25 now, hybrid added in Week 4)

#### Step 3.4: `src/services/opensearch/factory.py` — Factory

- `make_opensearch_client()` (LRU cached singleton)
- `make_opensearch_client_fresh()` — non-cached for testing

#### Step 3.5: `src/schemas/api/search.py` — Search Schemas

- `HybridSearchRequest(BaseModel)`: query (1-500 chars), size (1-50, default 10), from_ (≥0, default 0), fields_of_study, min_citations, year_range, latest_papers, use_hybrid, min_score
- `SearchHit(BaseModel)`: paper_id, title, authors, abstract, year, venue, citation_count, fields_of_study, pdf_url, score, highlights, chunk_text, section_name, tldr
- `SearchResponse(BaseModel)`: query, total, hits, size, from_, search_mode, error

#### Step 3.6: `src/routers/hybrid_search.py` — Search Endpoint

`POST /hybrid-search/`:
- Accepts `HybridSearchRequest`
- Generates query embeddings (graceful fallback to BM25 if embeddings fail)
- Calls `opensearch_client.search_unified()`
- Maps results to `SearchHit` objects
- Returns `SearchResponse`

#### Step 3.7: Update `src/main.py`

- Add OpenSearch initialization to lifespan (health check + index setup)
- Include `hybrid_search.router`

#### Step 3.8: Backfill Existing Papers

Update the Airflow DAG's indexing task to index paper metadata (title, abstract, tldr) into OpenSearch for BM25 search.

### Week 3 New Files

| # | File | Purpose |
|---|------|---------|
| 1 | `src/services/opensearch/index_config_hybrid.py` | Index mapping config |
| 2 | `src/services/opensearch/query_builder.py` | Query DSL builder |
| 3 | `src/services/opensearch/client.py` | OpenSearch client |
| 4 | `src/services/opensearch/factory.py` | Client factory |
| 5 | `src/schemas/api/search.py` | Search request/response |
| 6 | `src/routers/hybrid_search.py` | Search endpoint |
| 7 | `tests/unit/services/test_opensearch_query_builder.py` | Query builder tests |
| 8 | `tests/api/routers/test_hybrid_search.py` | Search endpoint tests |
| 9 | `tests/unit/schemas/test_search.py` | Schema validation tests |

---

## 7. Week 4 — Hybrid Search (Chunking + Embeddings + RRF)

> **Goal**: Intelligent document chunking, Jina AI embeddings, and hybrid BM25+vector search with Reciprocal Rank Fusion.

### Step-by-Step Coding Order

#### Step 4.1: `src/schemas/indexing/models.py` — Chunking Schemas

- `ChunkMetadata(BaseModel)`: chunk_index, total_chunks, section_name, start_char, end_char, word_count, overlap_with_previous, overlap_with_next
- `TextChunk(BaseModel)`: chunk_id, paper_id, chunk_text, title, abstract, metadata

#### Step 4.2: `src/services/indexing/text_chunker.py` — Text Chunker

`TextChunker` class:
- Word-based chunking with configurable size (600 words), overlap (100 words), minimum (100 words)
- **Section-aware chunking**: If document has parsed sections, use them as natural boundaries
  - Sections 100-800 words → single chunk
  - Sections < 100 words → merge with adjacent
  - Sections > 800 words → split with overlap
- **Fallback**: Traditional word-based sliding window for unstructured text
- Each chunk gets: `chunk_id = f"{paper_id}_chunk_{index}"`, title, abstract context

#### Step 4.3: `src/schemas/embeddings/jina.py` — Embeddings Schemas

- `EmbeddingRequest(BaseModel)`: texts (List[str]), model, task ("retrieval.passage" or "retrieval.query"), dimensions
- `EmbeddingResponse(BaseModel)`: embeddings (List[List[float]]), model, usage

#### Step 4.4: `src/services/embeddings/jina_client.py` — Jina Embeddings Client

`JinaEmbeddingsClient`:
- Async httpx client with Bearer token auth
- `async embed_passages(texts, batch_size=100) → List[List[float]]` — for indexing (task="retrieval.passage")
- `async embed_query(query) → List[float]` — for search (task="retrieval.query")
- Model: `jina-embeddings-v3`, dimensions: 1024
- Batch processing for large document sets
- Async context manager support

#### Step 4.5: `src/services/embeddings/factory.py`

- `make_embeddings_service()` / `make_embeddings_client()` — creates fresh JinaEmbeddingsClient

#### Step 4.6: `src/services/indexing/hybrid_indexer.py` — Hybrid Indexing Service

`HybridIndexingService`:
- Orchestrates: chunk → embed → index
- `async index_paper(paper_data) → Dict[str, int]`
  1. Chunk paper text using `TextChunker`
  2. Generate embeddings for all chunks (batch_size=50)
  3. Prepare documents with embedding vectors
  4. Bulk index into OpenSearch
- `async index_papers_batch(papers, replace_existing) → Dict`
- `async reindex_paper(paper_id, paper_data) → Dict`

#### Step 4.7: `src/services/indexing/factory.py`

- `make_hybrid_indexing_service()` — creates TextChunker + JinaClient + OpenSearchClient + HybridIndexingService

#### Step 4.8: Update OpenSearch Client for Hybrid Search

Add to `OpenSearchClient`:
- `_create_rrf_pipeline()` — Reciprocal Rank Fusion search pipeline
- `search_chunks_vector(query_embedding, size, fields_of_study)` — pure KNN search
- `_search_hybrid_native(query, query_embedding, size, fields_of_study, min_score)` — BM25 + KNN with RRF
- Update `search_unified()` to route between BM25-only and hybrid based on embedding availability

#### Step 4.9: Update Airflow Indexing Task

Implement the actual `index_papers_hybrid()` function in `airflow/dags/paper_ingestion/indexing.py`:
- Query papers from DB
- Convert to dicts with raw_text and sections
- Call `indexing_service.index_papers_batch()`
- Push stats to XCom

#### Step 4.10: Update Search Router

Modify `hybrid_search.py` to:
- Generate query embeddings via `EmbeddingsDep`
- Pass embedding to `search_unified()` for hybrid search
- Gracefully fall back to BM25 if embedding generation fails

### Week 4 New Files

| # | File | Purpose |
|---|------|---------|
| 1 | `src/schemas/indexing/models.py` | Chunk schemas |
| 2 | `src/services/indexing/text_chunker.py` | Text chunker |
| 3 | `src/schemas/embeddings/jina.py` | Embedding schemas |
| 4 | `src/services/embeddings/jina_client.py` | Jina embeddings client |
| 5 | `src/services/embeddings/factory.py` | Embeddings factory |
| 6 | `src/services/indexing/hybrid_indexer.py` | Hybrid indexing service |
| 7 | `src/services/indexing/factory.py` | Indexing factory |

---

## 8. Week 5 — Complete RAG System (LLM + Streaming + Gradio)

> **Goal**: Full RAG pipeline — user asks a question, system retrieves relevant chunks, LLM generates an answer citing sources. Plus streaming and a web UI.

### Step-by-Step Coding Order

#### Step 5.1: `src/services/ollama/prompts.py` — Prompt Engineering

1. `RAGPromptBuilder`:
   - Loads system prompt from `src/services/ollama/prompts/rag_system.txt`
   - `create_rag_prompt(query, chunks) → str` — formats query + context chunks
   - `create_structured_prompt(query, chunks) → Dict` — returns prompt with JSON schema

2. `ResponseParser`:
   - `parse_structured_response(response) → Dict` — parse JSON from LLM
   - `_extract_json_fallback(response) → Dict` — regex-based JSON extraction

3. **`src/services/ollama/prompts/rag_system.txt`** — System prompt:
   - "You are PaperLens, a research literature assistant."
   - "Only use provided paper excerpts"
   - "Limit to 200 words"
   - "Cite with [S2:paper_id] or [Author, Year] format"
   - "If papers disagree, note the contradiction"

#### Step 5.2: `src/services/ollama/client.py` — Ollama LLM Client

`OllamaClient`:
- `async health_check() → Dict` — check /api/version
- `async list_models() → List[Dict]` — available models
- `async generate(model, prompt, stream, **kwargs) → Dict` — text generation
- `async generate_rag_answer(query, chunks, model) → Dict` — RAG-specific generation
- `async generate_rag_answer_stream(query, chunks, model) → AsyncGenerator` — streaming tokens
- Response includes `usage_metadata`: prompt_tokens, completion_tokens, latency_ms
- Error handling: `OllamaConnectionError`, `OllamaTimeoutError`

#### Step 5.3: `src/services/ollama/factory.py`

- `make_ollama_client()` — LRU-cached singleton

#### Step 5.4: `src/schemas/api/ask.py` — RAG Schemas

- `AskRequest(BaseModel)`: query (1-1000 chars), top_k (1-10, default 3), use_hybrid (default True), model (default "llama3.2:1b"), fields_of_study
- `AskResponse(BaseModel)`: query, answer, sources (List[Dict]), chunks_used, search_mode, model, execution_time
- `FeedbackRequest(BaseModel)`: trace_id, score (1-5), comment
- `FeedbackResponse(BaseModel)`: success, message

#### Step 5.5: `src/routers/ask.py` — RAG Endpoints

Two endpoints:

1. **`POST /ask`** — Standard RAG:
   - Retrieve chunks from OpenSearch (hybrid search with fallback)
   - Build prompt with RAGPromptBuilder
   - Generate answer with Ollama
   - Return AskResponse with sources

2. **`POST /stream`** — Streaming RAG:
   - Same retrieval as /ask
   - Returns Server-Sent Events (SSE) via `StreamingResponse`
   - First sends metadata (sources, chunks_used)
   - Then streams tokens as generated
   - Finally sends completion signal

Helper: `_prepare_chunks_and_sources()` — shared retrieval logic

#### Step 5.6: `src/gradio_app.py` — Web UI

Gradio interface:
- Chat-style interface for asking questions
- Model selection dropdown
- Top-K and hybrid search toggles
- Fields of study filter
- Shows sources with Semantic Scholar links (https://www.semanticscholar.org/paper/{paper_id})
- Streaming responses
- Calls the FastAPI `/ask` or `/stream` endpoint

#### Step 5.7: `gradio_launcher.py` — Entry Point

Simple launcher: adds `src/` to path, imports and runs `main()` from `gradio_app`.

#### Step 5.8: Update `src/main.py`

- Add Ollama initialization to lifespan
- Include `ask_router` and `stream_router`

### Week 5 New Files

| # | File | Purpose |
|---|------|---------|
| 1 | `src/services/ollama/prompts/rag_system.txt` | System prompt template |
| 2 | `src/services/ollama/prompts.py` | Prompt builder & parser |
| 3 | `src/services/ollama/client.py` | Ollama LLM client |
| 4 | `src/services/ollama/factory.py` | Ollama factory |
| 5 | `src/schemas/api/ask.py` | Ask request/response |
| 6 | `src/routers/ask.py` | RAG endpoints |
| 7 | `src/gradio_app.py` | Gradio web interface |
| 8 | `gradio_launcher.py` | Gradio launcher |
| 9 | `tests/api/routers/test_ask.py` | RAG endpoint tests |

---

## 9. Week 6 — Observability & Caching (Langfuse + Redis)

> **Goal**: End-to-end tracing of every RAG request with Langfuse. Redis caching for 150-400x faster repeated queries.

### Step-by-Step Coding Order

#### Step 6.1: `src/services/langfuse/client.py` — Langfuse Tracer Wrapper

`LangfuseTracer`:
- Wraps Langfuse v3 SDK
- `get_callback_handler(trace_name, user_id, ...) → CallbackHandler` — for LangChain/LangGraph
- `trace_langgraph_agent(name, user_id, ...) → (trace_ctx, callback_handler)` — context manager
- `get_trace_id(trace) → Optional[str]`
- Graceful disable if public_key/secret_key not configured

#### Step 6.2: `src/services/langfuse/tracer.py` — RAG-Specific Tracer

`RAGTracer`:
- Purpose-built for the RAG pipeline stages
- Context managers for each stage:
  - `trace_request(user_id, query)` — overall request
  - `trace_embedding(trace, query)` — embedding generation
  - `trace_search(trace, query, top_k)` — search operation
  - `trace_prompt_construction(trace, chunks)` — prompt building
  - `trace_generation(trace, model, prompt)` — LLM generation
- End methods for updating spans with results

#### Step 6.3: `src/services/langfuse/factory.py`

- `make_langfuse_tracer()` — LRU-cached singleton

#### Step 6.4: `src/services/cache/client.py` — Redis Cache Client

`CacheClient`:
- Exact-match caching strategy
- `_generate_cache_key(request: AskRequest) → str` — SHA256 hash of (query, model, top_k, use_hybrid, fields_of_study), prefixed with "exact_cache:"
- `async find_cached_response(request) → Optional[AskResponse]` — O(1) Redis GET
- `async store_response(request, response) → bool` — O(1) Redis SET with TTL
- Configurable TTL (default 6 hours)

#### Step 6.5: `src/services/cache/factory.py`

- `make_redis_client(settings) → redis.Redis` — with connection pooling and retry
- `make_cache_client(settings) → CacheClient`

#### Step 6.6: Update `src/routers/ask.py`

Add caching and tracing to both endpoints:
- **Cache check first** — return immediately if exact match found
- **Wrap each stage** with Langfuse tracing spans
- **Cache storage** after successful generation

#### Step 6.7: Add Langfuse + Redis to `compose.yml`

Add services: `redis`, `langfuse-web`, `langfuse-worker`, `langfuse-postgres`, `langfuse-redis`, `langfuse-minio`, `clickhouse`

#### Step 6.8: Update `.env.example`

Add Langfuse keys, Redis host, and Langfuse server configuration variables.

### Week 6 New Files

| # | File | Purpose |
|---|------|---------|
| 1 | `src/services/langfuse/client.py` | Langfuse tracer wrapper |
| 2 | `src/services/langfuse/tracer.py` | RAG-specific tracing |
| 3 | `src/services/langfuse/factory.py` | Langfuse factory |
| 4 | `src/services/cache/client.py` | Redis cache client |
| 5 | `src/services/cache/factory.py` | Cache factory |

---

## 10. Week 7 — Agentic RAG (LangGraph) & Telegram Bot

> **Goal**: Intelligent agent that decides *when* and *how* to retrieve, grades document relevance, rewrites queries, and provides transparent reasoning. Plus a Telegram bot for mobile access.

### Architecture: LangGraph State Machine

```
START → guardrail → [in-scope?]
                       ├─ NO → out_of_scope → END
                       └─ YES → retrieve → [tool_call?]
                                              ├─ NO → END (direct answer)
                                              └─ YES → tool_retrieve → grade_documents
                                                                          ├─ relevant → generate_answer → END
                                                                          └─ irrelevant → rewrite_query → retrieve (loop)
```

### Step-by-Step Coding Order

#### Step 7.1: `src/services/agents/config.py` — Agent Configuration

`GraphConfig(BaseModel)`:
- `max_retrieval_attempts: int = 2`
- `guardrail_threshold: int = 60`
- `model: str = "llama3.2:1b"`
- `temperature: float = 0.0`
- `top_k: int = 3`
- `use_hybrid: bool = True`
- `enable_tracing: bool = True`
- `settings: Settings`

#### Step 7.2: `src/services/agents/models.py` — Pydantic Models

Structured outputs for LLM calls:
- `GuardrailScoring`: score (0-100), reason
- `GradeDocuments`: binary_score ("yes"/"no"), reasoning
- `SourceItem`: paper_id, title, authors, year, venue, url, citation_count, relevance_score, `to_dict()`
- `ToolArtefact`: tool_name, tool_call_id, content, metadata
- `RoutingDecision`: route ("retrieve"/"out_of_scope"/"generate_answer"/"rewrite_query"), reason
- `GradingResult`: document_id, is_relevant, score, reasoning
- `ReasoningStep`: step_name, description, metadata

#### Step 7.3: `src/services/agents/state.py` — LangGraph State

`AgentState(TypedDict)`:
- `messages: Annotated[list[AnyMessage], add_messages]` — append-only message history
- `original_query`, `rewritten_query` — query tracking
- `retrieval_attempts: int` — attempt counter
- `guardrail_result: Optional[GuardrailScoring]`
- `routing_decision: Optional[RoutingDecision]`
- `sources`, `relevant_sources`, `relevant_tool_artefacts`
- `grading_results: List[GradingResult]`
- `metadata: Dict[str, Any]`

#### Step 7.4: `src/services/agents/context.py` — Runtime Context

`Context(dataclass)`:
- Holds all clients: `ollama_client`, `opensearch_client`, `embeddings_client`, `langfuse_tracer`
- Tracing state: `trace`, `langfuse_enabled`
- Config: `model_name`, `temperature`, `top_k`, `max_retrieval_attempts`, `guardrail_threshold`

#### Step 7.5: `src/services/agents/prompts.py` — LLM Prompts

Seven prompt templates:
1. `GUARDRAIL_PROMPT` — "Is this a scientific research question? Score 0-100" (broader than CS/AI)
2. `DECISION_PROMPT` — Should we RETRIEVE or RESPOND directly?
3. `GRADE_DOCUMENTS_PROMPT` — Are these documents relevant? yes/no
4. `REWRITE_PROMPT` — Rewrite query for better retrieval
5. `GENERATE_ANSWER_PROMPT` — Generate answer from context, cite as [Author, Year]
6. `SYSTEM_MESSAGE` — "You are PaperLens, an agentic literature review assistant"
7. `DIRECT_RESPONSE_PROMPT` — Polite out-of-scope response

#### Step 7.6: `src/services/agents/tools.py` — Retriever Tool

`create_retriever_tool()` factory:
- Creates a `@tool`-decorated async function `retrieve_papers(query)`
- Inside: embed query → search OpenSearch → convert to LangChain `Document` objects
- Closures capture: `opensearch_client`, `embeddings_client`, `top_k`, `use_hybrid`

#### Step 7.7: `src/services/agents/nodes/utils.py` — Shared Utilities

Helper functions used across nodes:
- `get_latest_query(state) → str`
- `get_latest_context(state) → str`
- `create_langfuse_span(context, name, input_data) → Optional[span]`
- `end_langfuse_span(span, output_data)`

#### Step 7.8: Node Implementations (one file per node)

1. **`nodes/guardrail_node.py`** — `ainvoke_guardrail_step(state, runtime)`
   - Format `GUARDRAIL_PROMPT` with query
   - Use `llm.with_structured_output(GuardrailScoring)`
   - Broader scope: any scientific research question (not just CS/AI)
   - Rejects: cooking recipes, dating advice, sports scores, etc.
   - Fallback: score=50 if LLM fails

2. **`nodes/out_of_scope_node.py`** — polite rejection

3. **`nodes/retrieve_node.py`** — create AIMessage with tool calls, increment attempts

4. **`nodes/grade_documents_node.py`** — binary relevance grading with routing

5. **`nodes/rewrite_query_node.py`** — LLM-based query rewriting with fallback

6. **`nodes/generate_answer_node.py`** — generate answer with [Author, Year] citations

#### Step 7.9: `src/services/agents/agentic_rag.py` — Main Service

`AgenticRAGService`:

**`_build_graph() → CompiledGraph`**: 7 nodes, conditional edges, compile.

**`async ask(query, user_id, model) → Dict`**: validate → trace → invoke → extract results.

**Visualization**: `get_graph_mermaid()`, `get_graph_visualization()`, `get_graph_ascii()`

#### Step 7.10 - 7.14: Factory, schemas, router, Telegram bot

Same as arXiv course — adapted naming only.

### Week 7 New Files

| # | File | Purpose |
|---|------|---------|
| 1 | `src/services/agents/config.py` | Agent configuration |
| 2 | `src/services/agents/models.py` | Pydantic models |
| 3 | `src/services/agents/state.py` | LangGraph state |
| 4 | `src/services/agents/context.py` | Runtime context |
| 5 | `src/services/agents/prompts.py` | LLM prompts |
| 6 | `src/services/agents/tools.py` | Retriever tool |
| 7 | `src/services/agents/nodes/utils.py` | Node utilities |
| 8 | `src/services/agents/nodes/guardrail_node.py` | Guardrail node |
| 9 | `src/services/agents/nodes/out_of_scope_node.py` | Out-of-scope node |
| 10 | `src/services/agents/nodes/retrieve_node.py` | Retrieve node |
| 11 | `src/services/agents/nodes/grade_documents_node.py` | Grade documents node |
| 12 | `src/services/agents/nodes/rewrite_query_node.py` | Rewrite query node |
| 13 | `src/services/agents/nodes/generate_answer_node.py` | Generate answer node |
| 14 | `src/services/agents/agentic_rag.py` | Main agent service |
| 15 | `src/services/agents/factory.py` | Agent factory |
| 16 | `src/routers/agentic_ask.py` | Agentic endpoint |
| 17 | `src/services/telegram/bot.py` | Telegram bot |
| 18 | `src/services/telegram/factory.py` | Telegram factory |
| 19 | `tests/unit/services/agents/test_agentic_rag.py` | Agent service tests |
| 20 | `tests/unit/services/agents/test_models.py` | Model tests |
| 21 | `tests/unit/services/agents/test_nodes.py` | Node tests |
| 22 | `tests/unit/services/agents/test_tools.py` | Tool tests |
| 23 | `tests/api/routers/test_agentic_ask.py` | Endpoint tests |
| 24 | `tests/unit/services/test_telegram.py` | Telegram tests |

---

## 11. Week 8 — PaperLens Extensions

> **Goal**: This is where PaperLens goes beyond the base course. Add four advanced agent nodes that transform single-paper Q&A into a true literature review engine: cross-paper synthesis, contradiction detection, a critic/reflection loop, and persistent research memory.

### Extended Architecture: LangGraph State Machine (Week 8)

```
START → guardrail → [in-scope?]
                       ├─ NO → out_of_scope → END
                       └─ YES → retrieve → tool_retrieve → grade_documents
                                                             ├─ irrelevant → rewrite_query → retrieve (loop max 2)
                                                             └─ relevant → synthesis_node
                                                                             │
                                                                             ▼
                                                                   contradiction_node
                                                                             │
                                                                             ▼
                                                                   generate_answer
                                                                             │
                                                                             ▼
                                                                       critic_node → [quality OK?]
                                                                             ├─ YES → memory_node → END
                                                                             └─ NO → generate_answer (retry, max 2)
```

### New State Fields (extend AgentState)

Add these to `AgentState(TypedDict)`:

```python
# Week 8 extensions
synthesis_result: Optional[Dict]       # Cross-paper synthesis output
contradictions: List[Dict]             # Detected contradictions between papers
critic_score: Optional[float]          # 0.0 - 1.0 quality score
critic_feedback: Optional[str]         # What to improve
critic_attempts: int                   # How many revision loops
memory_context: Optional[str]          # Retrieved prior research context
session_id: Optional[str]             # For persistent memory grouping
```

### Step-by-Step Coding Order

#### Step 8.1: `src/services/agents/prompts.py` — New Prompt Templates

Add four new prompts:

1. **`SYNTHESIS_PROMPT`** — Cross-paper synthesis
   ```
   You are analyzing multiple research papers to synthesize findings.
   
   Research question: {query}
   
   Paper excerpts:
   {chunks_with_metadata}
   
   Instructions:
   1. Identify the key findings from each paper
   2. Find common themes and patterns across papers
   3. Note where findings reinforce each other
   4. Identify gaps — what topics are NOT covered?
   5. Organize findings by theme, not by paper
   
   Output a structured synthesis with:
   - key_themes: list of themes with supporting papers
   - agreements: findings that multiple papers support
   - gaps: areas where no paper provides coverage
   - summary: 2-3 paragraph synthesis narrative with citations
   ```

2. **`CONTRADICTION_PROMPT`** — Detect conflicting findings
   ```
   You are comparing findings across research papers.
   
   Research question: {query}
   
   Paper excerpts:
   {chunks_with_metadata}
   
   Identify any CONTRADICTIONS between papers:
   - Different conclusions about the same question
   - Conflicting experimental results
   - Disagreements on methodology effectiveness
   - Different population/context leading to different outcomes
   
   For each contradiction:
   - paper_a: which paper and what it claims
   - paper_b: which paper and what it claims
   - nature: what type of conflict (methodological, findings, scope)
   - possible_reason: why they might disagree (different populations, timeframes, methods)
   
   If no contradictions are found, return an empty list with a note.
   ```

3. **`CRITIC_PROMPT`** — Quality evaluation
   ```
   You are a quality reviewer evaluating a research synthesis answer.
   
   Original question: {query}
   Generated answer: {answer}
   Source papers used: {sources}
   
   Evaluate on these criteria (score each 0-10):
   1. Faithfulness: Does the answer accurately reflect the source papers?
   2. Completeness: Are all relevant findings from the sources included?
   3. Citation accuracy: Are citations correct and sufficient?
   4. Coherence: Is the synthesis well-organized and logical?
   5. Contradiction handling: Are disagreements between papers noted?
   
   Output:
   - scores: dict of criterion → score
   - overall_score: float 0.0 - 1.0 (weighted average)
   - pass: boolean (true if overall_score >= 0.7)
   - feedback: specific improvements needed (empty if pass is true)
   ```

4. **`MEMORY_CONTEXT_PROMPT`** — Integrate prior research
   ```
   The user has prior research context from previous sessions:
   
   Previous findings:
   {memory_context}
   
   Current question: {query}
   Current synthesis: {synthesis}
   
   If the previous findings are relevant, integrate them:
   - Note connections to prior research
   - Highlight what's new vs. what was already known
   - Flag any contradictions with prior findings
   
   If not relevant, return the synthesis unchanged.
   ```

#### Step 8.2: `src/services/agents/models.py` — New Pydantic Models

Add:

```python
class SynthesisResult(BaseModel):
    key_themes: List[Dict[str, Any]]  # [{"theme": "...", "papers": [...], "finding": "..."}]
    agreements: List[Dict[str, Any]]  # [{"finding": "...", "papers": [...]}]
    gaps: List[str]                    # ["No study covers X"]
    summary: str                       # Narrative synthesis

class Contradiction(BaseModel):
    paper_a: Dict[str, str]           # {"paper_id": "...", "title": "...", "claim": "..."}
    paper_b: Dict[str, str]           # {"paper_id": "...", "title": "...", "claim": "..."}
    nature: str                        # "methodological" | "findings" | "scope"
    possible_reason: str               # Why they disagree

class CriticResult(BaseModel):
    scores: Dict[str, float]          # {"faithfulness": 8, "completeness": 7, ...}
    overall_score: float               # 0.0 - 1.0
    passed: bool                       # True if >= 0.7
    feedback: str                      # What to improve

class MemoryEntry(BaseModel):
    session_id: str
    query: str
    synthesis_summary: str
    key_themes: List[str]
    sources_used: List[str]            # paper_ids
    timestamp: datetime
    relevance_tags: List[str]          # For retrieval
```

#### Step 8.3: `src/services/memory/client.py` — Research Memory Store

`ResearchMemoryClient`:
- Uses Redis as the persistent store (with configurable TTL, default 90 days)
- Stores memories as JSON with session_id prefix

Methods:
- `async store_memory(session_id, entry: MemoryEntry) → bool`
  - Key: `memory:{session_id}:{timestamp}`
  - Value: JSON-serialized MemoryEntry
  - TTL: configurable (default 90 days)

- `async retrieve_relevant_memories(query, session_id, top_k=5) → List[MemoryEntry]`
  - Scans memories for the session
  - Uses keyword matching + LLM-based relevance scoring
  - Returns most relevant prior research

- `async get_session_memories(session_id) → List[MemoryEntry]`
  - All memories for a session (chronological)

- `async clear_session(session_id) → int`
  - Delete all memories for a session

#### Step 8.4: `src/services/memory/factory.py`

- `make_memory_client(settings) → ResearchMemoryClient`

#### Step 8.5: Node Implementations

1. **`src/services/agents/nodes/synthesis_node.py`** — `ainvoke_synthesis_step(state, runtime)`

   **What it does:**
   - Takes the relevant document chunks from grading
   - Groups chunks by paper (paper_id → chunks)
   - Formats chunks with paper metadata (title, year, venue, citation count)
   - Calls LLM with SYNTHESIS_PROMPT
   - Parses structured output into `SynthesisResult`
   - Updates state: `synthesis_result = SynthesisResult`

   **Fallback:** If LLM fails, returns a basic concatenation of chunk summaries

   **Langfuse tracing:** Traces input chunks, synthesis output, and latency

2. **`src/services/agents/nodes/contradiction_node.py`** — `ainvoke_contradiction_step(state, runtime)`

   **What it does:**
   - Uses the same chunks + synthesis result
   - Calls LLM with CONTRADICTION_PROMPT
   - Parses output into `List[Contradiction]`
   - Updates state: `contradictions = [...]`

   **Fallback:** If LLM fails, returns empty contradictions list with note "Unable to analyze contradictions"

   **Key insight:** Only runs if >= 2 unique papers found. For single-paper results, skips with empty list.

3. **`src/services/agents/nodes/critic_node.py`** — `ainvoke_critic_step(state, runtime)`

   **What it does:**
   - Takes the generated answer (from generate_answer node)
   - Calls LLM with CRITIC_PROMPT
   - Parses output into `CriticResult`
   - **Routing decision:**
     - If `critic_result.passed == True` OR `critic_attempts >= 2`: route to memory_node
     - If `critic_result.passed == False` AND `critic_attempts < 2`:
       - Append feedback as system message
       - Route back to generate_answer for revision
       - Increment `critic_attempts`
   - Updates state: `critic_score`, `critic_feedback`, `critic_attempts`

   **Routing function:** `continue_after_critic(state) → Literal["memory_node", "generate_answer"]`

   **Fallback:** If LLM fails scoring, default to passed=True (don't block the pipeline)

   **Measurability:** "Reflection loop improved synthesis faithfulness from X% to Y%" — this is the metric you'll track in Langfuse.

4. **`src/services/agents/nodes/memory_node.py`** — `ainvoke_memory_step(state, runtime)`

   **What it does (two phases):**

   **Phase 1 — Retrieve prior context (before generation):**
   - Check if session_id is set
   - Call `memory_client.retrieve_relevant_memories(query, session_id)`
   - If relevant memories found, append to state as `memory_context`

   **Phase 2 — Store new finding (after generation):**
   - Create `MemoryEntry` from current synthesis
   - Call `memory_client.store_memory(session_id, entry)`
   - Update state: `memory_stored = True`

   **Fallback:** If Redis unavailable, skip silently (graceful degradation)

   **Integration:** The memory context is injected into the generate_answer prompt via MEMORY_CONTEXT_PROMPT

#### Step 8.6: Update `src/services/agents/state.py`

Add Week 8 fields to `AgentState`:
```python
# Week 8 extensions
synthesis_result: Optional[Dict]
contradictions: List[Dict]
critic_score: Optional[float]
critic_feedback: Optional[str]
critic_attempts: int
memory_context: Optional[str]
session_id: Optional[str]
```

#### Step 8.7: Update `src/services/agents/agentic_rag.py` — Extended Graph

Modify `_build_graph()` to add the new nodes and edges:

```python
# Extended graph (Week 8)
graph.add_node("synthesis_node", ainvoke_synthesis_step)
graph.add_node("contradiction_node", ainvoke_contradiction_step)
graph.add_node("critic_node", ainvoke_critic_step)
graph.add_node("memory_node", ainvoke_memory_step)

# Updated edges:
# grade_documents → synthesis_node (instead of generate_answer)
# synthesis_node → contradiction_node
# contradiction_node → generate_answer
# generate_answer → critic_node (instead of END)
# critic_node → conditional(continue_after_critic) → {memory_node, generate_answer}
# memory_node → END
```

Also update the `ask()` method return value to include:
- `synthesis_result`, `contradictions`, `critic_score`, `critic_attempts`, `memory_stored`

#### Step 8.8: Update `src/services/agents/context.py`

Add `memory_client: ResearchMemoryClient` to the Context dataclass.

#### Step 8.9: `src/schemas/api/ask.py` — Extended Response Schemas

Add/update:
```python
class SynthesisAskRequest(BaseModel):
    query: str  # 1-1000 chars
    model: str = "llama3.2:1b"
    top_k: int = 5  # Higher default for synthesis
    use_hybrid: bool = True
    session_id: Optional[str] = None  # For persistent memory
    fields_of_study: Optional[List[str]] = None

class SynthesisAskResponse(BaseModel):
    query: str
    answer: str
    synthesis: Optional[Dict]
    contradictions: List[Dict]
    sources: List[Dict]
    reasoning_steps: List[Dict]
    retrieval_attempts: int
    critic_score: Optional[float]
    critic_attempts: int
    memory_used: bool
    search_mode: str
    rewritten_query: Optional[str]
    execution_time: float
    trace_id: Optional[str]
```

#### Step 8.10: `src/routers/synthesis.py` — Synthesis Endpoint

New router:
- `POST /api/v1/synthesize` → delegates to extended `agentic_rag.ask()` with synthesis mode enabled
- Returns `SynthesisAskResponse`
- Accepts `session_id` for persistent memory

#### Step 8.11: Update Gradio App (`src/gradio_app.py`)

Add a new tab for "Literature Synthesis" mode:
- Larger input area for research questions
- Session ID input (for persistent memory)
- Results display with:
  - Synthesis narrative
  - Contradictions panel (if any)
  - Critic score badge
  - Source papers table
  - Memory indicator ("Building on 3 prior research sessions")

#### Step 8.12: Evaluation Harness

Create `tests/evaluation/` with:

1. **`tests/evaluation/test_synthesis_quality.py`** — Automated quality checks
   - Does the answer cite all retrieved papers?
   - Are contradictions identified when test papers disagree?
   - Does the critic loop improve scores? (run with/without)
   - Does memory retrieval surface relevant prior context?

2. **`tests/evaluation/ragas_eval.py`** — RAGAS metrics (optional integration)
   - Faithfulness: Is the answer grounded in sources?
   - Answer relevancy: Does it address the query?
   - Context precision: Are retrieved chunks relevant?
   - Context recall: Are important chunks retrieved?

### Week 8 New Files

| # | File | Purpose |
|---|------|---------|
| 1 | `src/services/agents/nodes/synthesis_node.py` | Cross-paper synthesis |
| 2 | `src/services/agents/nodes/contradiction_node.py` | Contradiction detection |
| 3 | `src/services/agents/nodes/critic_node.py` | Reflection/quality loop |
| 4 | `src/services/agents/nodes/memory_node.py` | Persistent research memory |
| 5 | `src/services/memory/client.py` | Redis memory store |
| 6 | `src/services/memory/factory.py` | Memory factory |
| 7 | `src/routers/synthesis.py` | Synthesis endpoint |
| 8 | `tests/unit/services/agents/test_synthesis_node.py` | Synthesis tests |
| 9 | `tests/unit/services/agents/test_contradiction_node.py` | Contradiction tests |
| 10 | `tests/unit/services/agents/test_critic_node.py` | Critic tests |
| 11 | `tests/unit/services/agents/test_memory_node.py` | Memory tests |
| 12 | `tests/unit/services/test_memory_client.py` | Memory client tests |
| 13 | `tests/api/routers/test_synthesis.py` | Synthesis endpoint tests |
| 14 | `tests/evaluation/test_synthesis_quality.py` | Quality evaluation tests |
| 15 | `tests/evaluation/ragas_eval.py` | RAGAS metrics (optional) |

---

## 12. Testing Strategy

### Test Organization

```
tests/
├── conftest.py            # Global test config + fixtures
├── api/
│   ├── conftest.py        # FastAPI TestClient + mock overrides
│   └── routers/
│       ├── test_ping.py
│       ├── test_hybrid_search.py
│       ├── test_ask.py
│       ├── test_agentic_ask.py
│       └── test_synthesis.py        # Week 8
├── evaluation/                       # Week 8
│   ├── test_synthesis_quality.py
│   └── ragas_eval.py
├── integration/
│   └── test_services.py   # Real service connectivity
└── unit/
    ├── test_config.py
    ├── schemas/
    │   └── test_search.py
    └── services/
        ├── test_s2_client.py
        ├── test_metadata_fetcher.py
        ├── test_opensearch_query_builder.py
        ├── test_pdf_parser.py
        ├── test_telegram.py
        ├── test_memory_client.py            # Week 8
        └── agents/
            ├── test_agentic_rag.py
            ├── test_models.py
            ├── test_nodes.py
            ├── test_tools.py
            ├── test_synthesis_node.py       # Week 8
            ├── test_contradiction_node.py   # Week 8
            ├── test_critic_node.py          # Week 8
            └── test_memory_node.py          # Week 8
```

### Testing Principles

| Principle | Implementation |
|-----------|---------------|
| **Mocking external services** | All tests mock OpenSearch, Ollama, Jina, Semantic Scholar APIs |
| **Dependency override** | API tests use FastAPI's `app.dependency_overrides` |
| **Async testing** | `pytest-asyncio` with `AsyncMock` for async services |
| **Flexible assertions** | Accept multiple status codes (200/500/503) for resilience |
| **Fixture hierarchy** | conftest.py at each level provides scoped fixtures |
| **Factory-based mocking** | polyfactory for generating test data |
| **Evaluation harness** | Week 8 adds RAGAS metrics for measurable quality |

### When to Write Tests

- **Week 1**: test_config.py, test_ping.py
- **Week 2**: test_s2_client.py, test_pdf_parser.py, test_metadata_fetcher.py
- **Week 3**: test_opensearch_query_builder.py, test_hybrid_search.py, test_search.py
- **Week 5**: test_ask.py
- **Week 7**: test_agentic_rag.py, test_models.py, test_nodes.py, test_tools.py, test_agentic_ask.py, test_telegram.py
- **Week 8**: test_synthesis_node.py, test_contradiction_node.py, test_critic_node.py, test_memory_node.py, test_memory_client.py, test_synthesis.py, test_synthesis_quality.py
- **Integration**: test_services.py (run against real containers)

---

## 13. Design Patterns & Principles Reference

### Patterns Used Throughout

| Pattern | Where | Why |
|---------|-------|-----|
| **Factory** | Every service has a factory.py | Decouple construction from use; enable DI |
| **Repository** | `PaperRepository` | Isolate DB queries from business logic |
| **Dependency Injection** | FastAPI `Depends()`, LangGraph `Context` | Testability, loose coupling |
| **Strategy** | OpenSearch (BM25 vs hybrid vs vector) | Swap search algorithm without changing callers |
| **Abstract Interface** | `BaseDatabase`, `BaseRepository` | DB backend swappable |
| **Singleton** | `@lru_cache` factories | Reuse expensive connections |
| **Context Manager** | DB sessions, Langfuse spans | Guaranteed resource cleanup |
| **Builder** | `RAGPromptBuilder`, `QueryBuilder` | Complex object construction |
| **State Machine** | LangGraph AgentState | Explicit workflow transitions |
| **Observer** | Langfuse tracing throughout pipeline | Non-intrusive monitoring |
| **Graceful Degradation** | Embeddings → BM25 fallback, Cache miss → generate, Memory down → skip | Partial failures don't crash system |
| **Evaluator-Optimizer** | Critic node reflection loop | Quality improves iteratively via feedback |
| **Memento** | Research memory persistence | System remembers prior state across sessions |

### SOLID Principles Applied

| Principle | Example |
|-----------|---------|
| **S** — Single Responsibility | Each node handles ONE step (guard, retrieve, grade, synthesize, critique, remember) |
| **O** — Open/Closed | New agent nodes via graph.add_node without modifying existing nodes |
| **L** — Liskov Substitution | `PostgreSQLDatabase` fully substitutes for `BaseDatabase` |
| **I** — Interface Segregation | Minimal abstract methods in base classes |
| **D** — Dependency Inversion | High-level modules depend on abstractions (BaseDatabase, not PostgreSQLDatabase) |

---

## Complete File Inventory (All Weeks)

### Source Files (~80 files)

| Category | Count | Key Files |
|----------|-------|-----------|
| Configuration | 4 | config.py, exceptions.py, middlewares.py, database.py |
| Database | 4 | base.py, postgresql.py, factory.py, __init__.py |
| Models | 2 | paper.py, __init__.py |
| Schemas | 16 | api/{ask,health,search}, semantic_scholar/paper, database/config, embeddings/jina, indexing/models, pdf_parser/models + __init__.py files |
| Repositories | 2 | paper.py, __init__.py |
| Routers | 6 | ping.py, hybrid_search.py, ask.py, agentic_ask.py, synthesis.py, __init__.py |
| Services | 32 | semantic_scholar/*, cache/*, embeddings/*, indexing/*, langfuse/*, ollama/*, opensearch/*, pdf_parser/*, telegram/*, memory/* |
| Agents | 20 | agentic_rag.py, config, context, factory, models, prompts, state, tools, nodes/* (11 nodes including Week 8) |
| Application | 3 | main.py, dependencies.py, gradio_app.py |

### Infrastructure Files (8 files)

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project dependencies |
| `Dockerfile` | API container |
| `compose.yml` | All services |
| `Makefile` | Developer commands |
| `gradio_launcher.py` | UI launcher |
| `.env.example` | Config template |
| `.env.test` | Test config |
| `README.md` | Documentation |

### Airflow Files (8 files)

| File | Purpose |
|------|---------|
| `airflow/Dockerfile` | Airflow container |
| `airflow/entrypoint.sh` | Startup script |
| `airflow/requirements-airflow.txt` | Dependencies |
| `airflow/dags/hello_world_dag.py` | Test DAG |
| `airflow/dags/paper_ingestion_dag.py` | Production DAG |
| `airflow/dags/paper_ingestion/common.py` | Service init |
| `airflow/dags/paper_ingestion/fetching.py` | Fetch task |
| `airflow/dags/paper_ingestion/indexing.py` | Index task |
| `airflow/dags/paper_ingestion/reporting.py` | Report task |
| `airflow/dags/paper_ingestion/setup.py` | Setup task |

### Test Files (~25 files)

| Category | Count | Key Files |
|----------|-------|-----------|
| `tests/conftest.py` | 2 | Global + API fixtures |
| `tests/unit/` | 14 | Config, schemas, services, agents, memory |
| `tests/api/` | 5 | All router endpoints including synthesis |
| `tests/integration/` | 1 | Service connectivity |
| `tests/evaluation/` | 2 | Quality metrics + RAGAS |

---

## Business Framing (For Portfolio README)

> **PaperLens** reduces systematic literature review time from **60+ hours to under 8 hours**.
>
> Given a research question, it automatically discovers papers, parses full-text PDFs, synthesizes findings across multiple sources, detects contradictions between studies, and self-critiques output quality via a reflection loop — while building persistent research memory across sessions.
>
> **Key metrics:**
> - Synthesis faithfulness improved from X% to Y% via critic reflection loop
> - Contradiction detection precision: Z% against manually annotated test set
> - 200M+ paper corpus via Semantic Scholar API
> - Sub-100ms cached response time (150-400x speedup)
> - 13 Docker services, 80+ source files, full test suite with evaluation harness
