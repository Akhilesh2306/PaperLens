<p align="center">
  <h1 align="center">🔬 PaperLens</h1>
  <p align="center">
    <strong>Production-Grade Agentic Literature Review Engine</strong>
  </p>
  <p align="center">
    <em>Discover papers. Synthesize findings. Detect contradictions. Remember everything.</em>
  </p>
  <p align="center">
    <a href="#architecture"><img src="https://img.shields.io/badge/Architecture-8_Layers-blue?style=flat-square" alt="Architecture"></a>
    <a href="#tech-stack"><img src="https://img.shields.io/badge/Docker_Services-6_·_13_planned-green?style=flat-square" alt="Docker Services"></a>
    <a href="#agent-graph"><img src="https://img.shields.io/badge/Agent_Nodes-11-red?style=flat-square" alt="Agent Nodes"></a>
    <a href="#implementation-roadmap"><img src="https://img.shields.io/badge/Build_Plan-8_Weeks-orange?style=flat-square" alt="Build Plan"></a>
    <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
  </p>
</p>

---

**PaperLens** reduces systematic literature review time from **60+ hours to under 8 hours**.

Given a research question, it automatically discovers papers from Semantic Scholar's 200M+ corpus, parses full-text PDFs, synthesizes findings across multiple sources, detects contradictions between studies, and self-critiques output quality via a reflection loop — while building persistent research memory across sessions.

```
You ask: "What is the current evidence on transformer architectures for time-series forecasting?"

PaperLens automatically:
  1. Discovers relevant papers from Semantic Scholar (200M+ papers, all disciplines)
  2. Downloads & parses full-text PDFs using Docling (tables, sections, references)
  3. Indexes with hybrid search (BM25 keywords + 1024-dim Jina embeddings + RRF)
  4. Retrieves the most relevant chunks — rewrites bad queries automatically
  5. Synthesizes findings across papers — themes, agreements, gaps
  6. Detects contradictions — "Paper A says X, Paper B says Y, possibly because..."
  7. Self-critiques the answer (re-generates if quality < 0.7)
  8. Remembers your prior research — next query builds on what you already explored
```

## Table of Contents

- [The Problem](#the-problem)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Agent Graph](#agent-graph)
- [Implementation Roadmap](#implementation-roadmap)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Design Patterns](#design-patterns)
- [Testing Strategy](#testing-strategy)
- [License](#license)

## The Problem

Researchers in 2026 juggle 4-5 fragmented tools for a single literature review — Semantic Scholar, Elicit, Scite, NotebookLM, Obsidian — **none of which talk to each other.**

| Pain Point | Today's Reality | PaperLens |
|---|---|---|
| **Paper discovery** | Manual search across 3+ databases | Automated daily ingestion via Airflow |
| **Reading 50+ papers** | 60+ hours of manual review | Hybrid search surfaces relevant chunks |
| **Finding contradictions** | Read every paper end-to-end | Contradiction detection identifies conflicts |
| **Synthesizing findings** | Copy-paste quotes into docs | Cross-paper synthesis with citations |
| **Losing context** | Start from scratch each session | Persistent research memory across sessions |
| **Quality assurance** | Re-read and manually verify | Critic agent scores & improves output iteratively |

## Architecture

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
                        │  Redis (Cache + Memory) │
                        │  Langfuse (Tracing)     │
                        │  LangGraph (Agent)      │
                        │  ┌────────────────────┐ │
                        │  │ PaperLens Nodes    │ │
                        │  │ Synthesis          │ │
                        │  │ Contradiction      │ │
                        │  │ Critic (Reflection)│ │
                        │  │ Memory             │ │
                        │  └────────────────────┘ │
                        └─────────────────────────┘
```

**Nine decoupled layers** — each independently testable and replaceable:

| Layer | Components | Purpose |
|-------|-----------|---------|
| **Clients** | Gradio, Telegram, curl | User interaction |
| **API** | FastAPI routers | REST endpoints (`/search`, `/ask`, `/synthesize`) |
| **Agentic (W7)** | LangGraph 7-node state machine | Guardrail → Retrieve → Grade → Rewrite → Generate |
| **Synthesis (W8)** | 4 new agent nodes | Cross-paper synthesis, contradictions, critic, memory |
| **LLM + Embeddings** | Ollama (llama3.2), Jina v3 | Generation + 1024-dim vectors |
| **Storage** | PostgreSQL, OpenSearch, Redis | Metadata, hybrid search, cache + memory |
| **Ingestion** | Airflow DAG | Fetch → Parse (Docling) → Chunk → Embed → Index |
| **Observability** | Langfuse v3, RAGAS | Tracing, quality metrics, evaluation harness |
| **Infrastructure** | Docker Compose (6 now, 13 at completion) | One-command deployment |

## Tech Stack

### Core

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | **Python 3.12+** | Application code |
| Package Manager | **UV** | Fast dependency management |
| Web Framework | **FastAPI ≥0.115** | Async REST API |
| ORM | **SQLAlchemy 2.0** | Database abstraction |
| Validation | **Pydantic ≥2.12** | Data validation & settings |

### Infrastructure (Docker Compose)

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL 17** | 5432 | Paper metadata storage |
| **OpenSearch 3** | 9200 | BM25 + KNN hybrid search |
| **OpenSearch Dashboards** | 5601 | Search visualization |
| **Ollama** | 11434 | Local LLM (llama3.2) |
| **Apache Airflow** | 8080 | Workflow orchestration |
| **Redis 7** | 6379 | Response cache + research memory |
| **Langfuse v3** | 3001 | LLM observability & tracing |
| **ClickHouse** | — | Langfuse analytics |
| **MinIO** | 9090 | Langfuse blob storage |

### AI/ML

| Library | Purpose |
|---------|---------|
| **LangGraph ≥0.2** | Agentic workflow state machine (11 nodes) |
| **LangChain ≥0.3** | LLM abstractions & tool framework |
| **Docling ≥2.43** | PDF parsing with table extraction + OCR |
| **Jina AI v3** | 1024-dim embeddings (passage/query) |
| **Gradio ≥4.0** | Web UI |
| **python-telegram-bot ≥21** | Telegram bot interface |

### Data Source

| | |
|---|---|
| **API** | Semantic Scholar Graph API v1 |
| **Coverage** | 200M+ papers, all disciplines |
| **Auth** | Optional API key (free) |
| **Rate Limit** | 1 req/s (free) · 10 req/s (with key) |
| **Geo** | Global — works everywhere |

## Agent Graph

PaperLens uses a **LangGraph state machine** with 11 nodes — 7 core nodes (Week 7) + 4 extension nodes (Week 8):

```
START → guardrail ─── score < 60 ──→ out_of_scope → END
            │
        score ≥ 60
            │
            ▼
        retrieve → tool_retrieve → grade_documents
                                        │
                    ┌───────────────────┤
                    │                   │
              irrelevant            relevant
                    │                   │
                    ▼                   ▼
            rewrite_query        🔬 synthesis_node      ← NEW (W8)
            (loop max 2)              │
                    │                 ▼
                    └──→        ⚔️ contradiction_node   ← NEW (W8)
                                      │
                                      ▼
                               generate_answer
                                      │
                                      ▼
                               🎯 critic_node           ← NEW (W8)
                                      │
                        ┌─────────────┤
                        │             │
                    score < 0.7   score ≥ 0.7
                    (max 2 retries)   │
                        │             ▼
                        └──→    🧠 memory_node          ← NEW (W8)
                                      │
                                      ▼
                                     END
```

**Week 8 nodes explained:**

| Node | What it does |
|------|-------------|
| **Synthesis** | Groups chunks by paper, identifies themes, agreements, and research gaps across multiple papers |
| **Contradiction** | Detects conflicting conclusions, methodological disagreements; explains *why* papers disagree |
| **Critic** | Scores answer quality (0-1) on faithfulness, completeness, citation accuracy, coherence. Retriggers generation if < 0.7. *Creates the measurable metric: "Improved faithfulness from X% to Y%"* |
| **Memory** | Retrieves prior research context for the session; stores current synthesis for future sessions. Redis-backed, 90-day TTL |

## Implementation Roadmap

The project is built incrementally over **8 weeks**. Weeks 1-7 mirror production RAG patterns. Week 8 adds novel extensions.

| Week | Focus | Key Deliverable | Status |
|------|-------|----------------|--------|
| **1** | Infrastructure & Skeleton | FastAPI + Docker Compose (6 services) + health checks + tests | ✅ Complete |
| **2** | Data Ingestion | Semantic Scholar client + Docling PDF parsing + Airflow DAG | 🟡 In Progress |
| **3** | Keyword Search (BM25) | OpenSearch index + multi-field boosted search + filtering | Planned |
| **4** | Hybrid Search + Embeddings | Jina 1024-dim embeddings + RRF fusion + section-aware chunking | Planned |
| **5** | Complete RAG System | Ollama LLM + streaming SSE + Gradio UI + prompt engineering | Planned |
| **6** | Observability & Caching | Langfuse tracing + Redis cache (150-400x speedup) | Planned |
| **7** | Agentic RAG & Telegram | LangGraph 7-node graph + Telegram bot | Planned |
| **8** | **PaperLens Extensions** | Synthesis + Contradiction + Critic + Memory + RAGAS eval | Planned |

> See [`static/PAPERLENS_MASTER_PLAN.md`](static/PAPERLENS_MASTER_PLAN.md) for the complete file-by-file coding guide.
>
> Open [`static/PAPERLENS_MASTER_STORYBOOK.html`](static/PAPERLENS_MASTER_STORYBOOK.html) in a browser for an interactive visual walkthrough.

## Project Structure

```
paperlens/
├── src/
│   ├── settings/
│   │   ├── config.py                      # Pydantic Settings (all config)
│   │   └── logging.py                     # Centralized logging setup
│   ├── exceptions.py                      # Custom exception hierarchy
│   ├── main.py                            # FastAPI app + lifespan
│   ├── dependencies.py                    # DI definitions
│   ├── middlewares.py                     # Request logging
│   ├── db/
│   │   ├── interfaces/
│   │   │   ├── base.py                    # Abstract BaseDatabase
│   │   │   └── postgresql.py              # PostgreSQL implementation
│   │   └── factory.py                     # Database factory
│   ├── models/
│   │   └── paper.py                       # SQLAlchemy ORM (S2 fields)
│   ├── repositories/
│   │   └── paper.py                       # PaperRepository (CRUD)
│   ├── schemas/
│   │   ├── api/                           # ask.py, health.py, search.py
│   │   ├── semantic_scholar/paper.py      # S2Paper schema
│   │   ├── embeddings/jina.py             # Embedding schemas
│   │   ├── indexing/models.py             # Chunk schemas
│   │   └── pdf_parser/models.py           # PDF content schemas
│   ├── routers/
│   │   ├── health.py                      # GET /health
│   │   ├── hybrid_search.py               # POST /hybrid-search
│   │   ├── ask.py                         # POST /ask + POST /stream
│   │   ├── agentic_ask.py                 # POST /ask-agentic
│   │   └── synthesis.py                   # POST /synthesize (W8)
│   └── services/
│       ├── semantic_scholar/              # S2 API client + factory
│       ├── pdf_parser/                    # Docling wrapper + factory
│       ├── opensearch/                    # Client, query builder, index config
│       ├── embeddings/                    # Jina client + factory
│       ├── indexing/                      # Text chunker, hybrid indexer
│       ├── ollama/                        # LLM client, prompts, factory
│       ├── langfuse/                      # Tracer, RAG tracer, factory
│       ├── cache/                         # Redis cache client
│       ├── memory/                        # Research memory client (W8)
│       ├── telegram/                      # Telegram bot + factory
│       └── agents/
│           ├── agentic_rag.py             # Main AgenticRAGService
│           ├── config.py                  # GraphConfig
│           ├── state.py                   # AgentState (TypedDict)
│           ├── context.py                 # Runtime Context (dataclass)
│           ├── models.py                  # Structured LLM outputs
│           ├── prompts.py                 # All prompt templates
│           ├── tools.py                   # Retriever tool factory
│           └── nodes/
│               ├── guardrail_node.py      # Scope validation (0-100)
│               ├── out_of_scope_node.py   # Polite rejection
│               ├── retrieve_node.py       # Tool call creation
│               ├── grade_documents_node.py# Binary relevance
│               ├── rewrite_query_node.py  # Query optimization
│               ├── generate_answer_node.py# Answer with citations
│               ├── synthesis_node.py      # Cross-paper synthesis (W8)
│               ├── contradiction_node.py  # Conflict detection (W8)
│               ├── critic_node.py         # Reflection loop (W8)
│               └── memory_node.py         # Persistent memory (W8)
├── airflow/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements-airflow.txt
│   └── dags/
│       ├── health_dag.py                  # API + DB connectivity check
│       ├── paper_ingestion/               # Ingestion modules (W2+)
├── tests/
│   ├── conftest.py
│   ├── unit/                              # 14 files — config, schemas, services, agents
│   ├── api/                               # 5 files — all router endpoints
│   ├── integration/                       # 1 file — real service connectivity
│   └── evaluation/                        # 2 files — RAGAS + quality metrics (W8)
├── static/
│   ├── PAPERLENS_MASTER_PLAN.md            # Complete file-by-file coding guide
│   ├── PAPERLENS_MASTER_STORYBOOK.html    # Interactive visual walkthrough
│   ├── PAPERLENS_QUESTION_BANK.html       # Concept revision & interview prep
│   └── contexts/SESSION_CONTEXT.md        # Session bootstrap context
├── Dockerfile                             # Multi-stage API build
├── compose.yml                            # Docker services (6 now, 13 at completion)
├── Makefile                               # Developer commands
├── pyproject.toml                         # UV project config
├── .env.example                           # Environment template
└── gradio_launcher.py                     # UI entry point
```

## Getting Started

### Prerequisites

- **Docker Desktop** (8GB+ RAM, 20GB+ disk)
- **Python 3.12+**
- **UV**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Jina AI API key** (free): https://jina.ai/
- **Semantic Scholar API key** (free, optional): https://www.semanticscholar.org/product/api#api-key

### Quick Start

```bash
# Clone
git clone https://github.com/<your-username>/PaperLens.git
cd PaperLens

# Install dependencies
uv sync

# Copy environment config
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker compose up --build -d

# Verify
curl http://localhost:8585/api/v1/health
```

### Makefile Commands

```bash
make start       # Start all Docker services
make stop        # Stop all services
make restart     # Restart everything
make logs        # Tail service logs
make health      # Check service health
make test        # Run test suite
make lint        # Run ruff linter
make format      # Run ruff formatter
make cleanup     # Remove containers, volumes, caches
```

## Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| **Factory** | Every service has `factory.py` | Decouple construction from use; enable DI |
| **Repository** | `PaperRepository` | Isolate DB queries from business logic |
| **Dependency Injection** | FastAPI `Depends()`, LangGraph `Context` | Testability, loose coupling |
| **Strategy** | OpenSearch (BM25 / hybrid / vector) | Swap search algorithm without changing callers |
| **Abstract Interface** | `BaseDatabase`, `BaseRepository` | DB backend swappable |
| **Singleton** | `@lru_cache` factories | Reuse expensive connections |
| **Context Manager** | DB sessions, Langfuse spans | Guaranteed resource cleanup |
| **State Machine** | LangGraph `AgentState` | Explicit workflow transitions with typed state |
| **Graceful Degradation** | Embeddings→BM25, Cache→generate, Memory→skip | Partial failures never crash the system |
| **Evaluator-Optimizer** | Critic node reflection loop (W8) | Iterative quality improvement with feedback |
| **Memento** | Research memory persistence (W8) | System remembers prior state across sessions |

## Testing Strategy

```
tests/
├── unit/           14 files — Config, schemas, services, agents, memory
├── api/             5 files — All router endpoints (mocked deps)
├── integration/     1 file  — Real service connectivity
└── evaluation/      2 files — RAGAS metrics + quality assertions (W8)
```

| Tier | What | How |
|------|------|-----|
| **Unit** | Business logic, parsing, query building, node logic | `pytest` + `AsyncMock`, all external services mocked |
| **API** | FastAPI endpoints with dependency overrides | `httpx.AsyncClient` + `app.dependency_overrides` |
| **Integration** | Real Semantic Scholar, OpenSearch, PostgreSQL | Run against live Docker containers |
| **Evaluation** | Synthesis faithfulness, citation accuracy, contradiction detection | RAGAS metrics + custom quality assertions |

## Status

🚧 **Under active development** — Building week by week following the [implementation plan](static/PAPERLENS_MASTER_PLAN.md).

**Current release: v0.1.0** — Infrastructure & project skeleton complete. Async FastAPI app, PostgreSQL, OpenSearch, Ollama, and Airflow running in Docker Compose. Health endpoint, dependency injection, test framework with mocked async DB sessions.

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built from scratch as a production-grade portfolio project demonstrating multi-agent orchestration, hybrid search, reflection loops, and production engineering patterns.</sub>
</p>