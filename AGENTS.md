# AGENTS.md — CyberCase Intelligence Framework

This file provides system architecture, rules, guidelines, and commands for AI coding assistants and developers working on the CyberCase Intelligence Framework repository.

## 🌟 Project Overview & Identity

> [!IMPORTANT]
> **Canonical Source of Truth**: For confirmed research questions, design philosophy, and product scope, always consult [`docs/research/CURRENT_PROJECT_DIRECTION.md`](docs/research/CURRENT_PROJECT_DIRECTION.md).

**CyberCase Intelligence Framework** is a full-stack prototype for **General Case Summarization and Case Analysis**. It processes investigative case materials, produces structured summaries and material gaps, and conditionally augments technical cases with MITRE ATT&CK context:

* **Core Task**: General Case Summarization and Case Analysis using one direct structured Main Analysis call.
* **Role of MITRE ATT&CK**: **Conditional external technical augmentation only**. External threat intelligence (`rag_service` with STIX 2.1) is retrieved only when applicable, isolated in a separate technical appendix, and never treated as incident evidence.
* **Flow**:
  ```text
  CASE SOURCES → MAIN ANALYSIS → DETERMINISTIC FOLLOW-UP POLICY → PRELIMINARY REPORT
                             ↘ CONDITIONAL MITRE AUGMENTATION ↗
  ```
* **Vocabulary**: a thing the case knows is a **source** — a narrative, an extracted
  document, or an answer to a clarification question. Do not name identifiers
  `evidence` or `material`; "evidence" belongs in prose, not in code. The table is
  `case_sources`, the revision coordinate is `Case.source_revision`, the route is
  `/cases/{case_id}/sources`.
* **No run row**: an analysis and a Case Ask happen inside the request that asks for
  them. There is no job table, no claiming and no polling.
* **Design Principles**:
  * *Semantic analysis and language generation* $\to$ LLM.
  * *Validation, state, routing, priority, and stopping rules* $\to$ deterministic backend.
  * *External technical knowledge* $\to$ conditional, isolated augmentation.
* **Storage & Persistence**: Single-user workspace backed by PostgreSQL — users, cases, documents and their extractions, case sources, chat messages, analysis results, and reports bound to the analysis they came from.

---

## 🛠️ Tech Stack & Key Configurations
- **Frontend**: Next.js 16.2.10 (App Router) + React 19.2.4 + Tailwind CSS 4 + TypeScript
- **Backend API**: FastAPI + SQLAlchemy (Async) + PostgreSQL + Alembic
- **Agentic Pipeline**: LangGraph (State Machine) + LangChain message/LLM abstractions. The LCEL chain is evaluation-only (`pipeline/chain.py`)
- **Graph Database**: Neo4j (Enterprise/Community)
- **Vector Database**: Qdrant (1024-dim, BGE-M3 embeddings)
- **Primary LLM Models** (`rag_service/app/RAG/GraphRAG/config.py` & `backend/app/config.py`):
  - **OpenRouter Default**: `openai/gpt-5.6-luna` (alias: `luna`)
  - **Ready-Selection Aliases**:
    - `luna` $\to$ `openai/gpt-5.6-luna` (Default)
    - `4o-mini` $\to$ `openai/gpt-4o-mini`
    - `oss` $\to$ `openai/gpt-oss-120b`
    - `sonnet` $\to$ `anthropic/claude-3.5-sonnet`
    - `haiku` $\to$ `anthropic/claude-3.5-haiku`
    - `4o` $\to$ `openai/gpt-4o`
  - **Embedding**: `BAAI/bge-m3` (FP16 on CUDA, FP32 on CPU, 1024-dim)
  - **Reranker**: `BAAI/bge-reranker-v2-m3` (the mmarco cross-encoder is commented-out legacy in `config.py`)
  - **RAGAS Evaluator**: `qwen/qwen-2.5-72b-instruct` (via OpenRouter)

---

## 📂 Key Project Structure & Paths
```
Cybercase Framework/
├── backend/                  # FastAPI API for cases, analysis, chat and reports
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint (one worker, by refusal)
│   │   ├── models/           # SQLAlchemy models (case, sources, analysis, chat, report, user)
│   │   ├── routers/          # One file per resource + errors.py
│   │   ├── schemas/          # Domain request/response schemas
│   │   ├── services/         # Domain service modules:
│   │   │   ├── auth/         # Sessions, passwords, browser-request guard
│   │   │   ├── cases/        # Case CRUD
│   │   │   ├── document_ingestion/ # Upload to text: parsers, OCR, provenance
│   │   │   ├── sources/      # Documents and the bundle an analysis reads
│   │   │   ├── case_analysis/# The analysis: prompts, contracts/, mitre_gate/, pipeline
│   │   │   ├── technical_context/ # The MITRE retrieval a stage asks RAG for
│   │   │   ├── case_workflow/# Running an analysis, answering a question about one
│   │   │   ├── chat/         # The case conversation and its follow-up questions
│   │   │   ├── clients/      # HTTP service clients (GraphRAG API client)
│   │   │   ├── llm/          # LLM provider routing & model registry
│   │   │   └── reports/      # Template-first report, HTML & PDF rendering
│   │   └── database.py       # Async engine and session management
│   └── alembic/              # Async PostgreSQL migrations
├── rag_service/              # Standalone GraphRAG FastAPI service
│   └── app/RAG/GraphRAG/
│       ├── ingestion/         # Parse STIX JSON and ingest into Neo4j + Qdrant
│       ├── pipeline/          # LangGraph, context builder, and evaluator
│       ├── retrieval/         # Dense + graph retrieval and fusion
│       ├── evaluation/        # RAG evaluation tools
│       ├── model_registry.py  # Central OpenRouter presets & alias resolver
│       └── config.py          # RAG settings and model routing
├── frontend/                 # Next.js 16 Web Application
│   └── src/
│       ├── app/case/         # Case workspace: overview, sources, chat, report
│       └── components/       # Tailwind v4 reusable UI blocks
├── Documents/                # Reference documents and case-analysis knowledge assets
├── Mitre_ATT&CK Doc/         # STIX 2.1 JSON enterprise, mobile, ICS attack patterns
└── docker-compose.yml        # PostgreSQL, backend, rag-service, and frontend
```

---

## 💻 Common Commands

### Virtual Environment & Backend Setup (Windows)
```bash
# Activate virtual environment (Windows MSYS Bash / Git Bash)
source env_mitre/Scripts/activate  # Or in Cmd/PowerShell: .\env_mitre\Scripts\activate

# Install dependencies for all services
python install_deps.py

# Run FastAPI backend with Doppler secret management
cd backend
doppler run -- uvicorn app.main:app --reload

# Upgrade the single-head DB migration graph
python -m alembic upgrade head
```

### RAG Pipeline CLI & Interactivity
```bash
cd rag_service/app

# Display available OpenRouter models catalog
python -m RAG.GraphRAG.main --list-models

# Ingest all STIX 2.1 bundle data into Qdrant & Neo4j
python -m RAG.GraphRAG.main --ingest

# Run interactive RAG playground with default GPT-OSS model
python -m RAG.GraphRAG.main

# Run with specific model alias (e.g. Sonnet, GPT-OSS, GPT-4o)
python -m RAG.GraphRAG.main --model sonnet
python -m RAG.GraphRAG.main --model oss
python -m RAG.GraphRAG.main --model 4o

# Run pipeline in LangGraph Agentic mode
python -m RAG.GraphRAG.main --agent

# Run RAGAS metrics evaluation
python -m RAG.GraphRAG.evaluation.eval_runner
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev     # Run Dev server on http://localhost:3000
npm run lint    # ESLint checking
npm run test    # Vitest suite
npm run build   # Production compile
```

### Docker Infrastructure
```bash
# Start PostgreSQL, backend, rag-service, and frontend
doppler run -- docker compose up --build
```

---

## 📝 Coding Guidelines & Standards

### Python & FastAPI
1. **Async Everywhere**: Use `async def` and await async DB operations (`SQLAlchemy` or `Motor`/`Redis` calls). Never block the main FastAPI thread.
2. **Type-Safety & Pydantic**: Ensure all incoming requests and response payloads are strictly typed using Pydantic models.
3. **Database Sessions**: Obtain the async DB session through the existing `get_db` FastAPI dependency.

### LangGraph Agentic Loops
1. **State Immutability**: Ensure state updates in `agent_graph.py` return a modified state dictionary instead of modifying keys in-place.
2. **Confidence checks**: The RAG evaluator returns `SUFFICIENT` or `INSUFFICIENT`; an insufficient result selects a bounded recovery strategy such as `BROADEN_SEARCH` or `ACKNOWLEDGE_LIMIT`. It does not pause for user input.
3. **Grace Limit**: Limit loop iterations strictly. Never let self-reflection run for more than 2-3 iterations to avoid infinite API cost.

### Next.js & React
1. **React 19 & Tailwind v4**: Use utility-first styling with native Tailwind v4 class names. Use React 19 primitives.
2. **Strict TypeScript**: Avoid `any`. Define interfaces for all props, states, and API return values.

---

## 🔄 Analysis Module & External Technical Augmentation

### Main Case Analysis Pipeline
The core analysis module (`backend/app/services/case_analysis/`) executes on admitted case evidence:
1. **Direct Analysis**: One structured LLM call returns a summary, key findings, material gaps, and lightweight source references.
2. **Validation**: The backend validates identifiers and supplied source references without adding a second semantic analysis pipeline.
3. **Follow-up Policy**: Deterministic rules filter answered or explicitly unknown gaps, apply priority and round limits, and select one gap.
4. **Question Realization**: No extra model call. The analysis already wrote the question for each gap it raised; the follow-up policy only picks which one to ask.

### Conditional Technical Augmentation (`rag_service`)
When admitted case findings describe cyber threat activity, the backend conditionally gates retrieval to `rag_service` (STIX 2.1 ATT&CK):
1. **Dense Vector Search**: Embeds technical query using `BAAI/bge-m3` $\to$ matches vectors in Qdrant.
2. **Graph Expansion**: Performs 2-hop depth Cypher queries in Neo4j (techniques, mitigations, groups).
3. **Fusion (RRF)**: Merges results using Reciprocal Rank Fusion + Cross-Encoder reranking.
4. **Source-Role Isolation**: The retrieved technical context is rendered strictly as an analytical appendix, never as an admitted case fact.

### Clarification Gating
The Main Analysis emits material unresolved gaps. The backend deterministically selects at most one eligible gap and persists a focused clarification question. The reply becomes a Case source bound to that gap, and the Case is analysed again only once the round's questions are spent — a round of three costs one analysis, not three. The retired separate Gap Analysis LLM is not part of the production Case path.

### Backend Route Boundary

Everything is `/api/v1`, one router per resource, and `backend/tests/test_route_surface.py` asserts the exact set: `/health`, the `/auth` session routes, and authenticated Case routes for the case itself, its documents, its sources, its analysis, its chat and its reports. Messages belong to the Case directly — there is no thread resource and no `/api/v1/chats`. There is no run resource either: an analysis and an answer each happen in the request that asked for them, which is why `main.py` refuses to start with more than one worker. Do not add top-level `/api/v1/reports`, public upload/OCR, or standalone RAG-proxy endpoints. Chat messages, assistant analysis publications, and external RAG context are not authoritative Case sources; native citations resolve Case source revisions and snapshots.
