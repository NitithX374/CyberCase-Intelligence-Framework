# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CyberCase Intelligence Framework** is a full-stack RAG application that analyses cybersecurity incident cases using MITRE ATT&CK intelligence. The case is the aggregate: it owns the documents and narratives it is analysed from, the analysis, the conversation about it, and its reports. An analysis starts with a cheap preflight that asks only what the case is missing; if something is worth asking, the reader is asked and nothing expensive runs. Otherwise one grounded model call follows, which the caller waits for — there is no run row and no queue. Technical context, when the case needs it, comes from an agentic RAG pipeline with hybrid retrieval, cross-lingual support (Thai ↔ English) and self-reflection loops; that pipeline never pauses. The report is deterministic and template-first, built from the analysis that is already stored.

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
- **LLMs**: one `CORE_LLM_PROVIDER` drives reasoning, routing, decomposition and evaluation. Default is `openrouter` → `deepseek/deepseek-v4.1-flash`; set `CORE_LLM_PROVIDER=anthropic` for `claude-haiku-4-5`. The served pipeline is cloud-only

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
    └── Graph expansion (Neo4j, 1 hop in+out from each seed; seeds come
        only from the hits that survive the per-query quota)
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
  __init__.py           deliberately empty — see below
  auth/                 auth_service, credentials (passwords, JWTs), dependencies
                        (current user, and the guard every browser request passes)
  cases/                case CRUD
  document_ingestion/   upload to text: service, files (detect, render pages),
                        parsers (PDF text, DOCX), recognition (Typhoon OCR),
                        contracts (types and errors), provenance
  sources/              documents and the one bundle an analysis reads from
  analysis/             producing an analysis of a case
    pipeline.py         advance_case(): assess first, then analyse only if
                        there is nothing worth asking
    steps/              one file per step, in the order they run
      assess.py             the cheap gaps-only call that runs first
      technical_context.py  ask the RAG service, when the gate says to
      write.py              the one model call that writes the trace
      bind.py               bind the trace to the case; count what did not bind
      quotes.py             finding a quotation in a source (bind.py's helper)
    clarification.py    pure policy: ask the reader, or proceed
    contracts/          trace.py, claims.py (claims, citations, gaps, a
                        follow-up exchange, what the preflight returns)
    mitre_gate/         whether this case needs ATT&CK at all (__init__ picks
                        the gate, llm.py and encoder.py are the gates,
                        sentences.py cuts the case up for the encoder)
    provider.py         call the model for one step, and read what came back
    prompts.py          settings.py  (model, token budget)
  workflow/             the request lifecycle around an analysis
    run_analysis.py     one step of the bounded loop: read, think, write
    analysis_storage.py what a step writes — an assessment that asks, or a
                        finished analysis
    answer_question.py  answering a question about an analysis that exists
    shared.py           what both need
  chat/                 the case conversation, and the follow-up it carries
  reports/              contracts, content (the stored report), display (the
                        document's rows), projection, persistence, render
                        (HTML and PDF from the Jinja2 template)
  llm/                  provider routing and the model registry
  clients/              the RAG service client
experiments/            ablations — imports app/, never imported by it
  analysis_arms.py      direct / verify / revise / split, built from the same
                        steps advance_case runs
  split_analysis.py     the two model calls the split arm needs
```

Two rules this layout exists to keep:

**Package `__init__.py` files stay empty.** Python runs one on any import
below it, so re-exporting there made every import pull the whole package — a
router wanting a JWT helper loaded the PDF renderer and the whole pipeline, and
one bad leaf broke the application. Import from the module that defines the
name. The exceptions hold real code: `models/__init__` registers the tables,
`analysis/contracts/__init__` and `analysis/mitre_gate/__init__` define things.
The same reasoning is why `reports/render.py` imports WeasyPrint inside the PDF
function: WeasyPrint
loads Pango and Cairo through ctypes at import time and raises if they are
missing, so at module level one absent system library would break every
import of `app.services.reports`.

**Production runs one path, and the arms are arguments.** That path is
`advance_case`, which reads top to bottom and has no arm switch:

```python
assessment = await assess_gaps(data)          # one cheap call: what is missing?
decision = decide_followup(assessment.gaps, ...)
if not isinstance(decision, Proceed):
    return AnalysisAdvance(assessment, decision)   # ask, and stop here
artifacts = await retrieve_technical_context(...)  # only now pay for the rest
artifacts = await write_analysis(...)
artifacts = await bind_to_case(...)
```

A round that ends in a question never calls the MITRE gate, the RAG service,
the main model call or the binding step. The `verify` arm in
`experiments/analysis_arms.py` runs those three expensive steps without the
preflight.
`run_case_analysis(pipeline=...)` is how an experiment substitutes a
composition. There is no `CASE_ANALYSIS_ARM` setting.

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
`backend/app/services/analysis/mitre_gate/`:

| Mode | What decides | Notes |
|------|--------------|-------|
| `llm` (default) | one prompt over the whole case | `mitre_gate/llm.py`, model from `CASE_ANALYSIS_MODEL` |
| `encoder` | XLM-R over one sentence at a time | `mitre_gate/encoder.py`; needs `torch`/`transformers`, which are **not** in `backend/requirements.txt` |
| `never` | nothing — always SKIP | the ablation, for measuring what technical context is worth |

Input is split by PyThaiNLP `crfcut` (`mitre_gate/sentences.py`); every sentence is an
exact substring of its source, so the gate's `trigger_text` — which becomes the
RAG query — is grounded by construction. `MITRE_GATE_MODEL_PATH` points at the
weights; `research/mitre_gate/README.md` has the measurements.

### Chat Clarification Boundary

The backend owns bounded clarification in `backend/app/services/chat/`. The analysis decides which gaps are worth asking about and writes the question for each; `followup.py` decides when to ask and what to do with the reply. One question is outstanding at a time, so a reply needs no marking — it answers the question above it. The reply stays a `ChatMessage`, cited as `QA-01`; it is **not** a case source, so answering does not move `source_revision` and does not invalidate the analysis that asked. The case is analysed again only once the round's questions are spent, so a round of three costs one analysis rather than three. `chat_followup_max_rounds` and `chat_followup_gaps_per_round` bound it.

RAG is never called for clarification. It is reached only through the analysis pipeline's technical-context stage, when the MITRE gate says RETRIEVE, and the frontend never calls `rag_service` directly.

A retrieval is reused when the input has not changed. The key is
`{source_revision, followup_answers}`, stored in the `retrieval_context_json`
column beside the context it belongs to. Without it every follow-up round
re-queried the RAG service with a byte-identical query and got a different
answer: one case in the development database holds six analyses at
`source_revision = 1` whose technique tables read 6, 6, 11, 10, 9, 9. The
pipeline behind `/query` is not deterministic, so asking again is neither free
nor neutral.

The frontend loads and generates reports through the case-scoped report endpoints. The backend builds a deterministic template-first report from the stored analysis and its source snapshots, keeps report versions, and exposes HTML and PDF export. There is one renderer: the Jinja2 template in `reports/templates/`, printed to PDF by WeasyPrint. The report is an analysis artifact, not an independent fact-verification system.
## Key Configuration (`rag_service/app/RAG/GraphRAG/config.py`)
- **Embedding model**: `BAAI/bge-m3` (1024-dim, FP16)
- **Reranker**: `BAAI/bge-reranker-v2-m3` (multilingual incl. Thai)
- **Core LLM**: `CORE_LLM_PROVIDER` (`openrouter` default → `deepseek/deepseek-v4.1-flash`, or `anthropic` → `claude-haiku-4-5`) — used for reasoning, routing, decomposition and evaluation
- **Single-call generation**: `SINGLE_CALL_GENERATION=true` — Thai answers are written in one call; set false to restore reason-EN-then-translate
- **`DUAL_QUERY_RETRIEVAL`**: read only by `pipeline/chain.py`, which is evaluation-only. The served agent does no input translation
- **RAGAS eval LLM**: `qwen/qwen-2.5-72b-instruct` via OpenRouter
- **Local models (`evaluation/` only)**: Ollama `qwen2.5:7b` + `gemma3:4b`, `OLLAMA_BASE_URL` (default `http://localhost:11434`). Not reachable from the service
- **Vector top-K**: 10, **Final top-K**: 5 (`FINAL_TOP_K` — graph seeds on the
  single-query path), **Graph expansion**: 1 hop, incoming + outgoing, batched
  into 3 Cypher statements per retrieval. There is no `GRAPH_DEPTH` setting;
  `get_multi_hop_path()` (4 hops) is a standalone utility the pipeline never calls.
  Under `retrieve_multi_quota` the graph seed count is the per-query quota (3),
  not `FINAL_TOP_K`, so a hit the quota drops cannot return as a subgraph
- **Qdrant collections**: `mitre_entities`, `mitre_relationships`

## Secrets & Environment
- **Doppler** is used for secrets management (replaces `.env` files in deployed environments); local dev can use `.env` files
- Backend runtime and online migrations read `POSTGRES_*`; chat also reads `RAG_SERVICE_URL` and `OPENROUTER_CYBERCASE`. `CASE_ANALYSIS_MODEL` selects the model for Main Case Analysis, its chat answers, and the LLM MITRE applicability gate; it accepts a registry alias or full OpenRouter ID and defaults to `deepseek/deepseek-v4.1-flash`. `CHAT_ASK_MODEL` is no longer a backend setting. The backend calls OpenRouter only — there is no provider switch or provider fallback. `CORE_LLM_PROVIDER` belongs to the RAG service alone. `MITRE_GATE_MODE` and `MITRE_GATE_MODEL_PATH` select the applicability gate
- RAG service reads `ANTHROPIC_API_KEY`, `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`, `QDRANT_URL`/`QDRANT_API_KEY`, `OPENROUTER_API_KEY`
- Deployment targets **Railway** platform via GitHub Actions in `.github/workflows/deploy.yml`

## Data Sources
- `Mitre_ATT&CK Doc/` — STIX 2.1 JSON bundles (enterprise, mobile, ICS attack patterns)
- `Documents/` — reference documents and case-analysis knowledge assets

## Windows-Specific Notes
- The project is developed on Windows; `rag_service/app/RAG/GraphRAG/main.py` includes UTF-8 encoding fixes for the console
- Use PowerShell syntax for shell commands
