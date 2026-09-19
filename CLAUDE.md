# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CyberCase Intelligence Framework** is a full-stack RAG application that analyses cybersecurity incident cases using MITRE ATT&CK intelligence. The case is the aggregate: it owns the documents and narratives it is analysed from, the analysis, the conversation about it, and its reports. An analysis is one grounded model call the caller waits for — there is no run row and no queue — and what it could not settle it asks the reader about, one question at a time. Technical context, when the case needs it, comes from an agentic RAG pipeline with hybrid retrieval, cross-lingual support (Thai ↔ English) and self-reflection loops; that pipeline never pauses. The report is deterministic and template-first, built from the analysis that is already stored.

## Service Layout

The platform is split into three services (see `docker-compose.yml`):

| Service | Path | Port | Role |
|---------|------|------|------|
| Frontend | `frontend/` | 3000 | Next.js UI |
| Backend API | `backend/` | 8000 | FastAPI: auth, cases, documents, sources, analysis, chat and reports + PostgreSQL. Calls the RAG service over HTTP (`RAG_SERVICE_URL`) when the MITRE gate asks for context |
| RAG Service | `rag_service/` | 8001 | FastAPI service hosting the GraphRAG pipeline; serves `/query`, `/health`, `/retrieval-contexts/{id}` |

The RAG pipeline code lives at `rag_service/app/RAG/GraphRAG/` (it was migrated out of `backend/` — backend no longer contains any RAG code). `rag_service/finetune/` holds the MITRE ATT&CK specialist fine-tune module (cloud QLoRA training + A/B compare; see its `README.md`).

## Common Commands

### Install Dependencies
```bash
# Installs backend/requirements.txt + rag_service/requirements.txt into the active Python
python install_deps.py
```

### Backend API (FastAPI, port 8000)
```bash
cd backend
doppler run -- uvicorn app.main:app --reload   # with Doppler secrets
# or with a local .env file:
uvicorn app.main:app --reload

# Run database migrations
python -m alembic upgrade head

# Formatting and linting (configured in backend/pyproject.toml)
python -m ruff format .
python -m ruff check .
```

### RAG Service (FastAPI, port 8001)
```bash
cd rag_service
uvicorn app.main:app --port 8001 --reload
```
Startup loads BGE-M3 + reranker models once and connects to Neo4j/Qdrant — first boot is slow.

### RAG Pipeline (CLI)
The CLI must be run as a module from `rag_service/app` (the code uses relative imports — `python main.py` will not work):
```bash
cd rag_service/app

python -m RAG.GraphRAG.main --ingest        # Ingest STIX data into Neo4j + Qdrant
python -m RAG.GraphRAG.main --test          # Run test queries
python -m RAG.GraphRAG.main                 # Interactive mode (agent)
python -m RAG.GraphRAG.main --retrieve-only # Debug retrieval only
python -m RAG.GraphRAG.main --fast          # Single retrieve → one answer call
python -m RAG.GraphRAG.main --ultrafast     # Vector-only retrieve → terse answer
```
The CLI has no `--local` flag — Ollama is offline-tooling only, see RAG Evaluation
below. `--agent` still parses but is a no-op: the agent is the only pipeline.

### RAG Evaluation
```bash
cd rag_service/app/RAG/GraphRAG

python -m evaluation.eval_runner --dataset evaluation/eval_dataset.json --mode retriever
python -m evaluation.eval_runner --dataset evaluation/eval_dataset.json --mode generation
python -m evaluation.eval_runner --dataset evaluation/eval_dataset.json --mode full
# Options: --local (Ollama models), --output results.md, --max-samples N
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev    # Development server on http://localhost:3000
npm run lint          # ESLint
npm run format        # Prettier (config in .prettierrc.json)
npm run format:check  # what CI would check
npm run build  # Production build
```

### Docker
```bash
doppler run -- docker compose up --build   # PostgreSQL (host port 5433) + backend + rag-service + frontend
```
Neo4j and Qdrant are cloud-hosted — no local containers for them.

## Architecture

### High-Level Stack
- **Frontend**: Next.js 16.2.10 + React 19.2.4 + Tailwind CSS 4
- **Backend API**: FastAPI + SQLAlchemy (async) + PostgreSQL — owns chat threads/messages/runs, background work, and clarification policy; calls the RAG service via HTTPX
- **RAG Engine**: LangGraph for orchestration (the agentic state machine) plus LangChain for the LLM and message abstractions (`langchain_core.messages`, `langchain_anthropic.ChatAnthropic`), hosted in `rag_service`. LangGraph is a separate library, not part of LangChain. No LCEL — the LCEL chain is evaluation-only (`pipeline/chain.py`)
- **Vector DB**: Qdrant (BGE-M3 embeddings, 1024-dim, FP16)
- **Graph DB**: Neo4j (MITRE ATT&CK STIX entities + relationships)
- **LLMs**: one `CORE_LLM_PROVIDER` drives reasoning, routing, decomposition and evaluation. Default is `openrouter` → `openai/gpt-5.6-luna`; set `CORE_LLM_PROVIDER=anthropic` for `claude-haiku-4-5`. The served pipeline is cloud-only

### Agentic RAG Pipeline (`rag_service/app/RAG/GraphRAG/pipeline/`)

The pipeline is a LangGraph state machine in `agent_graph.py`:

```
User Input (Thai/English)
    ↓
[ROUTER] Classifies, but the result is currently discarded — the graph edge is
    hard-wired to the incident path, so general-explanation is unreachable
    ↓
[PREPARE] Detect response language only. NO input translation — BGE-M3 is
    multilingual and retrieves on the Thai text as-is
    ↓
[DECOMPOSE] Incident → atomic per-technique sub-queries, in the incident's
    own language (query_decomposer.py)
    ↓
[HYBRID RETRIEVAL] retrieve_multi_quota — per-query quota, round-robin
    interleaved so every sub-query's technique survives the trim
    ├── Dense vector search (Qdrant + BGE-M3) + rerank
    └── Graph expansion (Neo4j, 2 hops)
    ↓
[EVALUATOR] Context sufficiency check (evaluator.py)
    ├── SUFFICIENT → proceed
    └── INSUFFICIENT → BROADEN_SEARCH: the agent rewrites the query itself and
        loops retrieval (max 2x). Budget spent → answer with the best context
        available, or return the evaluator's ACKNOWLEDGE_LIMIT message.
    ↓
[REASONING LLM] Generate answer (single-call Thai by default)
    ↓
[TRANSLATION LLM] Skipped on the normal Thai path (single-call already wrote
    Thai). Still runs for an ACKNOWLEDGE_LIMIT message, and for the whole
    answer if SINGLE_CALL_GENERATION=false
    ↓
END → AgentResponse(status="completed", answer)
```

The pipeline never pauses for user input.

### API Endpoints

Backend (`backend/app/routers/`, prefix `/api/v1`), one router per resource. `tests/test_route_surface.py` asserts this exact set, so it is the authority when this list and the code disagree:
- `GET /health` — backend and database health (`health.py`)
- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `POST /auth/dev-login`, `GET /auth/me`, `GET /auth/session` — cookie session (`auth.py`)
- `GET`, `POST /cases`; `GET`, `PATCH`, `DELETE /cases/{case_id}` — case lifecycle (`cases.py`)
- `GET /cases/{case_id}/chat`, `POST /cases/{case_id}/chat/messages` — the Ask/Chat panel (`chat.py`)
- `GET`, `POST /cases/{case_id}/documents`, `GET /cases/{case_id}/documents/{document_id}/content` — upload and read back (`documents.py`)
- `GET`, `POST /cases/{case_id}/sources` — what the case is analysed from (`sources.py`)
- `GET`, `POST /cases/{case_id}/analysis` — read the latest analysis, or run one (`analysis.py`)
- `POST`, `GET /cases/{case_id}/reports`, `GET /cases/{case_id}/reports/{report_id}/pdf`, `.../html` — report versions and export (`reports.py`)

Every case route is authenticated and ownership-scoped. There are no top-level `/api/v1/reports`, `/users`, or RAG-proxy routes, and no `/runs/{run_id}` — the analysis happens in the request that asked for it, which is why `main.py` refuses to start with more than one worker.

RAG service (`rag_service/app/main.py`, port 8001, no prefix): `GET /health`, `POST /query`, `GET /retrieval-contexts/{context_id}`.

### Backend Layout (`backend/app/`)

```
routers/                one file per resource; errors.py turns service errors into HTTP
schemas/                request/response contracts
models/                 SQLAlchemy tables
services/
  auth/                 sessions, passwords, the guard every browser request passes
  cases/                case CRUD
  document_ingestion/   upload to text: parsers, OCR recognition, provenance
  sources/              documents and the one bundle an analysis reads from
  case_analysis/        the analysis itself: prompts, provider call, validation
    contracts/          what a trace, a claim and a source citation are
    mitre_gate/         whether this case needs ATT&CK at all (__init__ picks
                        the gate, llm.py and encoder.py are the gates,
                        sentences.py cuts the case up for the encoder)
    pipeline.py         the stages one analysis runs through
  technical_context/    the MITRE retrieval a stage asks the RAG service for
  case_workflow/        running an analysis (analysis.py) and answering a
                        question about one (answering.py), with what both
                        need in shared.py
  chat/                 the case conversation, and the follow-up it carries
  reports/              contracts, content, assembly, display, render_html,
                        render_pdf
  llm/                  provider routing and the model registry
  clients/              the RAG service client
```

### Key Modules (under `rag_service/app/RAG/GraphRAG/`)
| Module | Path | Purpose |
|--------|------|---------|
| Agent graph | `pipeline/agent_graph.py` | LangGraph state machine, main pipeline orchestration |
| Hybrid retriever | `retrieval/hybrid_retriever.py` | Vector + graph search with RRF fusion |
| Context builder | `pipeline/context_builder.py` | Format retrieved context for LLM |
| Evaluator | `pipeline/evaluator.py` | Assess context sufficiency, drive self-reflection |
| Config | `config.py` | All RAG settings (models, topK, DB URLs) |
| Ingestion | `ingestion/` | Parse STIX JSON, populate Neo4j + Qdrant |

### MITRE Applicability Gate (backend)

Before a case is analysed the backend decides whether ATT&CK is relevant at
all. `MITRE_GATE_MODE` picks between three gates, which live together in
`backend/app/services/case_analysis/mitre_gate/`:

| Mode | What decides | Notes |
|------|--------------|-------|
| `llm` (default) | one prompt over the whole case | `mitre_gate/llm.py`, model from `CHAT_ASK_MODEL` |
| `encoder` | XLM-R over one sentence at a time | `mitre_gate/encoder.py`; needs `torch`/`transformers`, which are **not** in `backend/requirements.txt` |
| `never` | nothing — always SKIP | the ablation, for measuring what technical context is worth |

Input is split by PyThaiNLP `crfcut` (`mitre_gate/sentences.py`); every sentence is an
exact substring of its source, so the gate's `trigger_text` — which becomes the
RAG query — is grounded by construction. `MITRE_GATE_MODEL_PATH` points at the
weights; `research/mitre_gate/README.md` has the measurements.

### Chat Clarification Boundary

The backend owns bounded clarification in `backend/app/services/chat/`. The analysis decides which gaps are worth asking about and writes the question for each; `followup.py` decides when to ask and what to do with the reply. One question is outstanding at a time, so a reply needs no marking — it answers the question above it and becomes a case source bound to that gap. The case is analysed again only once the round's questions are spent, so a round of three costs one analysis rather than three. `chat_followup_max_rounds` and `chat_followup_gaps_per_round` bound it.

RAG is never called for clarification. It is reached only through the analysis pipeline's technical-context stage, when the MITRE gate says RETRIEVE, and the frontend never calls `rag_service` directly.

The frontend loads and generates reports through the case-scoped report endpoints. The backend builds a deterministic template-first report from the stored analysis and its source snapshots, keeps report versions, and exposes HTML and PDF export. The report is an analysis artifact, not an independent fact-verification system.
## Key Configuration (`rag_service/app/RAG/GraphRAG/config.py`)
- **Embedding model**: `BAAI/bge-m3` (1024-dim, FP16)
- **Reranker**: `BAAI/bge-reranker-v2-m3` (multilingual incl. Thai)
- **Core LLM**: `CORE_LLM_PROVIDER` (`openrouter` default → `openai/gpt-5.6-luna`, or `anthropic` → `claude-haiku-4-5`) — used for reasoning, routing, decomposition and evaluation
- **Single-call generation**: `SINGLE_CALL_GENERATION=true` — Thai answers are written in one call; set false to restore reason-EN-then-translate
- **`DUAL_QUERY_RETRIEVAL`**: read only by `pipeline/chain.py`, which is evaluation-only. The served agent does no input translation
- **RAGAS eval LLM**: `qwen/qwen-2.5-72b-instruct` via OpenRouter
- **Local models (`evaluation/` only)**: Ollama `qwen2.5:7b` + `gemma3:4b`, `OLLAMA_BASE_URL` (default `http://localhost:11434`). Not reachable from the service
- **Vector top-K**: 10, **Graph depth**: 2 hops, **Final top-K**: 5
- **Qdrant collections**: `mitre_entities`, `mitre_relationships`

## Secrets & Environment
- **Doppler** is used for secrets management (replaces `.env` files in deployed environments); local dev can use `.env` files
- Backend runtime and online migrations read `POSTGRES_*`; chat also reads `RAG_SERVICE_URL` and `OPENROUTER_CYBERCASE`. `CASE_ANALYSIS_MODEL` picks the model the case analysis and its chat answers run on; `CHAT_ASK_MODEL` picks the one the MITRE applicability gate runs on. Both take a registry alias (`luna`, `mini`, `oss`, `sonnet`, `haiku`, `4o`) or a full OpenRouter id. The backend calls OpenRouter only — there is no provider switch and no fallback; the default model is `openai/gpt-5.6-luna`. `CORE_LLM_PROVIDER` belongs to the RAG service alone. `MITRE_GATE_MODE` and `MITRE_GATE_MODEL_PATH` select the applicability gate
- RAG service reads `ANTHROPIC_API_KEY`, `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`, `QDRANT_URL`/`QDRANT_API_KEY`, `OPENROUTER_API_KEY`
- Deployment targets **Railway** platform via GitHub Actions in `.github/workflows/deploy.yml`

## Data Sources
- `Mitre_ATT&CK Doc/` — STIX 2.1 JSON bundles (enterprise, mobile, ICS attack patterns)
- `Documents/` — reference documents and case-analysis knowledge assets

## Windows-Specific Notes
- The project is developed on Windows; `rag_service/app/RAG/GraphRAG/main.py` includes UTF-8 encoding fixes for the console
- Use PowerShell syntax for shell commands
