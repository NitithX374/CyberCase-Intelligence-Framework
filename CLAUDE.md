# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CyberCase Intelligence Framework** is a full-stack RAG application that analyses cybersecurity incident cases using MITRE ATT&CK intelligence. The case is the aggregate: it owns the documents and narratives it is analysed from, the analysis, the conversation about it, and its reports. An analysis starts with a cheap preflight that asks only what the case is missing; if something is worth asking, the reader is asked and nothing expensive runs. Otherwise the analysis follows in two grounded model calls, which the caller waits for — a reading that writes the claims, parties, timeline and impacts with their quotations, a check of those quotations against the sources, then a judgement that writes the summary, gaps and ATT&CK associations over the checked claims. The reading runs without grammar-constrained decoding: its JSON is described in the prompt, validated after decoding and asked at most twice. Every other call keeps the provider's JSON-schema grammar. There is no run row and no queue. Technical context, when the case needs it, comes from an agentic RAG pipeline with hybrid retrieval, cross-lingual support (Thai ↔ English) and self-reflection loops; that pipeline never pauses. The report is deterministic and template-first, built from the analysis that is already stored.

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
# Installs backend/requirements-dev.txt (requirements.txt plus the test tools) +
# rag_service/requirements.txt into the active Python
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

# Tests (backend/pytest.ini); the PostgreSQL tests skip unless
# CYBERCASE_TEST_DATABASE_URL points at a test database
python -m pytest -q
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
npm run test          # Vitest
npm run generate:api-types  # regenerate src/lib/api/generated/openapi.ts from the backend schema
npm run check:api-types     # fails when that file is stale
npm run build  # Production build
```
The frontend's folders and the rules they keep are in `frontend/README.md`.

### Docker
```bash
doppler run -- docker compose up --build   # PostgreSQL (host port 5433) + backend + rag-service + frontend, all published on 127.0.0.1 only
```
Neo4j and Qdrant are cloud-hosted — no local containers for them.

## Architecture

### High-Level Stack
- **Frontend**: Next.js 16.2.10 + React 19.2.4 + Tailwind CSS 4
- **Backend API**: FastAPI + SQLAlchemy (async) + PostgreSQL — owns cases, sources, the analysis, the case conversation and the clarification policy; the analysis's technical-context step calls the RAG service via HTTPX. There are no runs, threads or queues: an analysis starts in the request that asked for it, and when that request streams its progress the analysis runs in a task of its own, which finishes and is stored even if the browser leaves
- **RAG Engine**: LangGraph for orchestration (the agentic state machine) plus LangChain for the LLM and message abstractions (`langchain_core.messages`, `langchain_anthropic.ChatAnthropic`), hosted in `rag_service`. LangGraph is a separate library, not part of LangChain. No LCEL — the LCEL chain is evaluation-only (`pipeline/chain.py`)
- **Vector DB**: Qdrant (BGE-M3 embeddings, 1024-dim; FP16 on CUDA only)
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
    ├── Dense + sparse search fused by Qdrant's RRF (BGE-M3), then rerank
    └── Graph expansion (Neo4j, 1 hop in+out from each seed; seeds come
        only from the hits that survive the per-query quota)
    ↓
[EVALUATOR] Context sufficiency check (evaluator.py)
    ├── SUFFICIENT → proceed
    └── INSUFFICIENT → BROADEN_SEARCH: the agent rewrites the query itself and
        loops retrieval (max 2x). Budget spent → answer with the best context
        available. ACKNOWLEDGE_LIMIT returns the evaluator's note on its own
        only on the first pass; after a broaden round the note is appended to
        the answer.
    ↓
[REASONING LLM] One call writes the final answer in the query's language
    (Thai for a Thai case file). Nothing is translated. An ACKNOWLEDGE_LIMIT
    note is returned as the evaluator wrote it (in the query's language)
    ↓
END → AgentResponse(status="completed", answer)
```

The pipeline never pauses for user input.

### API Endpoints

Backend (prefix `/api/v1`), one `routes.py` per feature folder. `tests/test_route_surface.py` asserts this exact set, so it is the authority when this list and the code disagree:
- `GET /health` — backend and database health (`health.py`)
- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/session` — cookie session (`auth/routes.py`)
- `GET`, `POST /cases`; `GET`, `PATCH`, `DELETE /cases/{case_id}` — case lifecycle (`cases/routes.py`)
- `GET /cases/{case_id}/chat`, `POST /cases/{case_id}/chat/messages` — the Ask/Chat panel (`chat/routes.py`)
- `POST /cases/{case_id}/documents`, `GET /cases/{case_id}/documents/{document_id}/content` — upload and read back (`sources/routes.py`, `document_router`). There is no document list: a document is listed through its source, and `CaseSourceRead` carries `filename`, `mime_type` and `size_bytes`
- `GET`, `POST /cases/{case_id}/sources` — what the case is analysed from (`sources/routes.py`)
- `GET`, `POST /cases/{case_id}/analysis` — read the latest analysis, or run one (`analysis/routes.py`)
- **Progress stream.** `POST /cases/{case_id}/analysis` and `POST /cases/{case_id}/chat/messages` answer a request sent
  with `Accept: text/event-stream` with a Server-Sent Events stream on the same request, instead of one JSON body
  (`analysis/stream.py`):
  - a `step` event as the analysis reaches each step (`assess`, `gate`, `retrieve` only when the RAG service is asked,
    `read`, `bind`, `judge`), with the seconds since it began;
  - a `: heartbeat` comment every 15 seconds of quiet, so the browser can tell a slow step from a lost connection;
  - then `result`, holding the JSON body a plain request gets, or `error`, holding its status and `detail`.
  - The analysis runs in a task of its own, so it finishes and is stored even if the browser leaves. Without that
    header both routes answer exactly as before.
- `POST`, `GET /cases/{case_id}/reports`, `GET /cases/{case_id}/reports/{report_id}/pdf`, `.../html` — report versions and export (`reports/routes.py`)

Every case route is authenticated and ownership-scoped; ownership is one check, `owned_case` in `cases/ownership.py`, which answers 404 for a case the user does not own. There are no top-level `/api/v1/reports`, `/users`, or RAG-proxy routes, and no `/runs/{run_id}` — the analysis happens in the request that asked for it, which is why `main.py` refuses to start with more than one worker.

RAG service (`rag_service/app/main.py`, port 8001, no prefix): `GET /health`, `POST /query`, `GET /retrieval-contexts/{context_id}`.

### Backend Layout (`backend/app/`)

```
main.py                 the app: one worker only, the browser guard, and the
                        one handler that turns AppError into HTTP
errors.py               AppError, the one service error (code, message,
                        status), and its two kinds: CaseAnalysisFailure (a
                        model stage failed) and CaseWorkflowError
health.py               GET /health
models/                 SQLAlchemy tables, one per file: case, source,
                        document, analysis_result, chat_message, report, user
llm/                    calling a model
  request.py            request_stage: the one transport every model call
                        takes, the LLM gate's included. grammar=False (the
                        reading) sends no output_config: the reply is
                        validated after decoding, asked at most twice
  settings.py           model, providers, output and thinking budgets
  openrouter.py         the OpenRouter target; registry.py (model aliases),
                        schema.py (the structured-output schema)
trace/                  what the analysis, chat and reports share
  claims.py             claims, citations, gaps, a follow-up exchange, what
                        the preflight returns
  trace.py              the trace: summary, parties, timeline, impacts, claims
  quotes.py             finding a quotation in a source
  bind.py               bind a written trace to the case; count what did not bind;
                        bound_claims checks the reading's quotations before the
                        judgement, and bound_references checks the judgement's
                        claim IDs and techniques after it;
                        a "reported" claim left with no verified quote becomes
                        "not_confirmed"; a quote with an ellipsis in the middle is
                        stored as one citation per piece when every piece occurs
                        once in the source, and otherwise as the one span the
                        pieces stretch over; either way it counts as one written
                        quote
  messages.py           what a chat message carries: the trace attached to it,
                        an answer's units and its suggestion
followup/               the bounded clarification the analysis and chat share
  clarification.py      pure policy: ask the reader, or proceed
  conversation.py       what the loop reads from the conversation (asked gaps,
                        rounds, the answered history, the pending question)
                        and the messages it writes into it
auth/                   routes, schemas, service (register, log in),
                        credentials (passwords, JWTs), guard (current user,
                        and the guard every browser request passes)
cases/                  routes, schemas, service (case CRUD and whether the
                        latest analysis is current), and ownership.py:
                        owned_case, the one ownership check
sources/                routes (sources and documents), schemas, service, and
                        bundle.py: the one bundle an analysis reads from
  ingestion/            upload to text: service, files (detect, render pages),
                        parsers (PDF text, DOCX), recognition (Typhoon OCR),
                        contracts (types and errors), provenance
analysis/               producing an analysis of a case; routes, schemas
  run.py                one step of the bounded loop: read, think, write
  store.py              what a step writes: an assessment that asks, or a
                        finished analysis
  latest.py             the read side: the latest analysis and the technical
                        context it recorded
  pipeline.py           advance_case(): assess first, then analyse only if
                        there is nothing worth asking
  assess.py             the cheap gaps-only call that runs first
  write.py              write_trace: a reading call (claims, parties, timeline,
                        impacts, with quotations; JSON from the prompt, no
                        grammar), the check of its quotations (bound_claims),
                        then a judgement call (summary, gaps, ATT&CK
                        associations) over the checked claims
  language.py           which language to write in: Thai when any source has
                        a Thai character; a chat question in its own language
  progress.py           announce(step): the steps write, retrieve and the
                        pipeline report, heard only by a request that listens
  stream.py             the progress stream: steps, heartbeats, then the result
  prompts.py            the analysis prompts
  technical_context/    whether and how the case gets ATT&CK context
    contracts.py        the augmentation and applicability records, and the
                        RAG service's request and response
    retrieve.py         run the gate, then ask the RAG service when it says to
    gate.py             picks the gate; gate_llm.py and gate_encoder.py are
                        the gates, sentences.py cuts the case up for the encoder
    rag_client.py       the RAG service client
chat/                   the case conversation; routes, schemas
  reply.py              routes a message: a follow-up answer or a question
  answer.py             answering a chat question: read the case, compose,
                        store the reply
  compose.py            the chat model call: request, verify citations, units
  prompts.py            CHAT_PROMPT
  contracts.py          the answer compose returns
reports/                routes, schemas, contracts, generate.py (one report
                        per analysis, from what it recorded), display.py (the
                        snapshot a report stores and prints), render.py (HTML
                        and PDF from the Jinja2 template in templates/)
experiments/            ablations — imports app/, never imported by it; only
                        __init__.py and this file are tracked; the rest
                        is local
  analysis_arms.py      direct / verify / revise / single, built from the same
                        steps advance_case runs; single is the one-call writer
                        production used before the reading/judgement split,
                        kept as the ablation
tests/                  every backend test and the helpers they share
```

The rules this layout exists to keep:

**One folder per thing the case does.** A feature's routes, schemas and logic
sit together: open its `routes.py` and follow the function each route calls.
Only what several features share has a folder of its own: `llm/`, `trace/` and
`followup/`. No feature imports another that imports it back.

**Data shapes live in contract files, never in a step.** `contracts.py`,
`trace/claims.py` and `trace/trace.py` hold types only, so a module that needs a
type does not import the step that uses it: reports read the technical-context
record without loading the MITRE gate or the model transport.

**Package `__init__.py` files stay empty.** Python runs one on any import
below it, so re-exporting there made every import pull the whole package — a
router wanting a JWT helper loaded the PDF renderer and the whole pipeline, and
one bad leaf broke the application. Import from the module that defines the
name. The one exception is `models/__init__`, which registers the tables.
The same reasoning is why `reports/render.py` imports WeasyPrint inside the PDF
function: WeasyPrint
loads Pango and Cairo through ctypes at import time and raises if they are
missing, so at module level one absent system library would break every
import of `app.reports`.

**Tests sit in a test folder, never beside the code they test.** Every backend
test is in `backend/tests/`, and `tests/test_layout.py` fails when a test file
appears under `app/`. Every frontend test is in `frontend/src/test/`, at the
path of the file it tests, and `npm run lint` fails on a test file anywhere
else.

**Production runs one path, and the arms are arguments.** That path is
`advance_case`, which reads top to bottom and has no arm switch:

```python
assessment = await assess_gaps(data)          # one cheap call: what is missing?
decision = decide_followup(assessment.gaps, ...)
if not isinstance(decision, Proceed):
    return AnalysisAdvance(assessment, decision)   # ask, and stop here
artifacts = await retrieve_technical_context(...)  # only now pay for the rest
artifacts = await write_analysis(...)              # reading, quote check, judgement
artifacts = await bind_to_case(...)                # the judgement's references
```

A round that ends in a question never calls the MITRE gate, the RAG service,
the reading and judgement calls or the binding step. The `verify` arm in
`experiments/analysis_arms.py` runs those three expensive steps without the
preflight.
The arms in `experiments/analysis_arms.py` take an `AnalysisInput` directly and
touch no case row. `run_case_analysis(pipeline=...)` also accepts a substitute
composition, as `tests/test_case_followup_postgres.py` does. There is no
`CASE_ANALYSIS_ARM` setting.

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
`backend/app/analysis/technical_context/` (`gate.py` picks one):

| Mode | What decides | Notes |
|------|--------------|-------|
| `llm` (default) | one prompt over the case, each source cut to at most 4,000 characters (20,000 across all sources); `input_truncated` on the record says whether anything was cut | `technical_context/gate_llm.py`, model from `CASE_ANALYSIS_MODEL`, sent through `request_stage` like every other model call |
| `encoder` | XLM-R over one sentence at a time | `technical_context/gate_encoder.py`; needs `torch`/`transformers`, which are **not** in `backend/requirements.txt` |
| `never` | nothing — always SKIP | the ablation, for measuring what technical context is worth |

**Shadow gate.** `MITRE_GATE_SHADOW=encoder` runs the XLM-R gate beside the LLM gate, concurrently.
- Only the LLM gate decides.
- The encoder's decision is stored on the analysis as `shadow_applicability` in the technical-augmentation record, so
  the two can be compared later.
- The shadow runs only when `MITRE_GATE_MODE=llm`.
- If torch, transformers or the weights are missing, it records `SKIP` with `mitre_shadow_unavailable`, and the
  analysis carries on.
- **Where it is on.**
  - Compose turns it on, installs CPU torch and transformers from `backend/requirements-encoder.txt`, and mounts
    `backend/xlmr_ladder_best` read-only.
  - The code default is `off`, so Railway and the tests are unaffected.
  - `tests/conftest.py` keeps it off whatever the local `.env` says.

The `encoder` gate splits its input with PyThaiNLP `crfcut` (`technical_context/sentences.py`);
every sentence is an exact substring of its source, so the encoder's `trigger_text`
is grounded by construction. The `llm` gate does not split sentences: it reads each
source cut to its share of the budget, and the `trigger_text` it returns is checked
instead. `validate_mitre_applicability` keeps a RETRIEVE only if every trigger, after
NFKC normalization, is a substring of a source the gate cited and every cited source
holds a trigger; otherwise it records SKIP with `mitre_applicability_invalid_grounding`.
The RAG query is not the trigger text alone: `retrieval_query` in
`technical_context/retrieve.py` joins the triggers, falls back to the whole source bundle
(`build_rag_query`) when there are none, and appends each answered follow-up's
question and answer. `MITRE_GATE_MODEL_PATH` points at the encoder's weights;
`research/mitre_gate/README.md` has the measurements.

### Chat Clarification Boundary

The backend owns bounded clarification. The analysis decides which gaps are worth asking about and writes the question for each. It checks every case against a fixed 5W1H list, `CASE_CHECKLIST` in `analysis/prompts.py` (who was affected, who was responsible, what, when, where, why, how, how much). A gap on that list takes its key as its `gap_key`, and the follow-up history sent to the model carries the `gap_key` each earlier question was asked under. A gap therefore keeps its key from round to round and is not asked twice. `followup/clarification.py` decides whether to ask one (`decide_followup`, pure policy); `followup/conversation.py` reads what that needs from the conversation (asked gap keys, rounds spent, the answered history) and builds the question and answer messages; `chat/reply.py` routes each message. One question is outstanding at a time, so a reply needs no marking — the backend links it to the question above it through `in_reply_to_message_id`. The reply stays a `ChatMessage`, cited as `QA-01`; it is **not** a case source, so answering does not move `source_revision` and does not invalidate the analysis that asked. The case is analysed again only once the round's questions are spent, so a round of three costs one analysis rather than three. `chat_followup_max_rounds` and `chat_followup_gaps_per_round` bound it. If that analysis fails, the round is not lost: retrying the answer that closed it, or pressing Analyze, runs the round's analysis instead of starting a new round. A retry that arrives while the round is still being analysed only returns what was stored; `analysing` in `analysis/run.py` tracks the analyses in flight, which holds because the backend runs one process.

RAG is never called for clarification. It is reached only through the analysis pipeline's technical-context stage, when the MITRE gate says RETRIEVE, and the frontend never calls `rag_service` directly.

A retrieval is reused when the input has not changed. The key is
`{source_revision, followup_answers}`, stored in the `retrieval_context_json`
column beside the context it belongs to. Without it every follow-up round
re-queried the RAG service with a byte-identical query and got a different
answer: one case in the development database holds six analyses at
`source_revision = 1` whose technique tables read 6, 6, 11, 10, 9, 9. The
pipeline behind `/query` is not deterministic, so asking again is neither free
nor neutral.

The frontend loads and generates reports through the case-scoped report endpoints. The backend builds a deterministic template-first report from the stored analysis and what it recorded, keeps report versions, and exposes HTML and PDF export. `reports/display.py` builds one `CaseReportContent` snapshot when the report is generated, `case_reports.structured_report` stores it, and the HTML and PDF render from that stored copy; a row stored in an older shape is refused with `case_report_outdated`, not rebuilt. A report shows what its analysis read, recorded when the analysis was stored: `external_context_json.sources_read` lists the IDs of the case sources it read (cited or not), and `external_context_json.followup_history` holds each answered follow-up's QA id, question and answer. Both are taken from what the analysis read when it started, never inferred from timestamps. The report takes the list of sources from `sources_read` and reads those source rows: a source added later is not included, and a missing one refuses the report with `analysis_source_snapshot_invalid`. `followup_history` is stored in full and is not re-read from chat. A row without either record is refused, not reported from current data. Each analysis gets at most one report, which is never rewritten; newer answers need a new analysis. There is one renderer: the Jinja2 template in `reports/templates/`, printed to PDF by WeasyPrint. The report is an analysis artifact, not an independent fact-verification system; nothing in `app/` checks it against the trace (that validator belongs to the local `experiments/report_fidelity` experiment).

## Key Configuration (`rag_service/app/RAG/GraphRAG/config.py`)
- **Embedding model**: `BAAI/bge-m3` (1024-dim; FP16 on CUDA only)
- **Reranker**: `BAAI/bge-reranker-v2-m3` (multilingual incl. Thai)
- **Core LLM**: `CORE_LLM_PROVIDER` (`openrouter` default → `deepseek/deepseek-v4.1-flash`, or `anthropic` → `claude-haiku-4-5`) — used for reasoning, routing, decomposition and evaluation
- **Single-call generation**: Thai answers are written in one call; the served agent has no translation stage. Reason-EN-then-translate survives only as an evaluation baseline (`pipeline/chain.py`, `evaluation/crosslingual_generation_benchmark.py`)
- **`DUAL_QUERY_RETRIEVAL`**: read only by `pipeline/chain.py`, which is evaluation-only. The served agent does no input translation
- **RAGAS eval LLM**: `qwen/qwen-2.5-72b-instruct` via OpenRouter
- **Local models (`evaluation/` only)**: Ollama `qwen2.5:7b` + `gemma3:4b`, `OLLAMA_BASE_URL` (default `http://localhost:11434`). Not reachable from the service
- **Vector top-K**: 10, **Final top-K**: 5 (`FINAL_TOP_K` — graph seeds on the
  single-query path), **Graph expansion**: 1 hop, incoming + outgoing, batched
  into 3 Cypher statements per retrieval. There is no `GRAPH_DEPTH` setting;
  `get_multi_hop_path()` (4 hops) is a standalone utility the pipeline never calls.
  Under `retrieve_multi_quota` the graph seed count is the per-query quota (5
  with `TECHNIQUE_POOL`, the default; 3 without), not `FINAL_TOP_K`, so a hit
  the quota drops cannot return as a subgraph
- **Qdrant collections**: `mitre_entities`, `mitre_relationships`

## Secrets & Environment
- **Doppler** is used for secrets management (replaces `.env` files in deployed environments); local dev can use `.env` files
- Backend runtime and online migrations read `POSTGRES_*`, or `DATABASE_URL`, which wins when set. The analysis's technical-context step reads `RAG_SERVICE_URL`; every backend model call reads `OPENROUTER_CYBERCASE`; OCR reads `TYPHOON_API_KEY`; a session cookie needs a `JWT_SECRET_KEY` of at least 32 characters. A chat answer never calls the RAG service. A reply that closes a round runs the analysis, and the analysis's technical-context step may call it. `CASE_ANALYSIS_MODEL` selects the model for every backend model call — the preflight, Main Case Analysis, its chat answers, and the LLM MITRE applicability gate; it accepts a registry alias or full OpenRouter ID and defaults to `deepseek/deepseek-v4.1-flash`. The backend calls OpenRouter only — there is no provider switch or provider fallback. `CASE_ANALYSIS_PROVIDERS` (comma-separated OpenRouter endpoint tags, e.g. `parasail/fp8,coreweave/fp8`) pins every backend model call to those endpoints in that order with `allow_fallbacks: false`; empty lets OpenRouter route, and the tags must serve the configured model. `CORE_LLM_PROVIDER` belongs to the RAG service alone. `MITRE_GATE_MODE` and `MITRE_GATE_MODEL_PATH` select the applicability gate, and `MITRE_GATE_SHADOW` runs the encoder beside it
- RAG service reads `OPENROUTER_CYBERCASE` (or `ANTHROPIC_API_KEY` when `CORE_LLM_PROVIDER=anthropic`), `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`, `QDRANT_URL`/`QDRANT_API_KEY`, and `THANOY_API_URL`/`THANOY_API_KEY` for the legal lookup. `OPENROUTER_API_KEY` is read only by the RAGAS evaluation
- Deployment targets **Railway** platform via GitHub Actions in `.github/workflows/deploy.yml`

## Data Sources
- `Mitre_ATT&CK Doc/` — STIX 2.1 JSON bundles (enterprise, mobile, ICS attack patterns)
- `Documents/` — reference documents and case-analysis knowledge assets

## Windows-Specific Notes
- The project is developed on Windows; `rag_service/app/RAG/GraphRAG/main.py` includes UTF-8 encoding fixes for the console
- Use PowerShell syntax for shell commands
