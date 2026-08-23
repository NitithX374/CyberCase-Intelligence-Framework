# CyberCase Intelligence Framework

CyberCase is a persisted-chat application for cybersecurity incident analysis. The accumulated raw user-authored incident messages are the authoritative case evidence. The backend combines that evidence with external MITRE ATT&CK retrieval, produces a source-traceable analysis, optionally asks a bounded clarification question, and stores a chat-scoped report.

## Trust boundary

- Included evidence: the initial incident message, clarification answers, and messages explicitly submitted as added case information.
- Excluded evidence: ordinary `ask` messages, assistant text, RAG output, MITRE descriptions, and model knowledge.
- External knowledge can support analysis and candidate MITRE mappings, but it never becomes an incident fact.
- Reported claims carry `source_message_ids`; the persisted analysis trace also binds the exact raw-evidence SHA-256 and retrieval context.

There is no canonical Case State, extraction layer, entity graph, relationship graph, state version, or delta workflow in the product runtime.

## Runtime flow

```text
user message -> ChatRun -> raw evidence projection
                         -> rag_service /query for initial, clarification, and add-info runs
                         -> Main Case Analysis
                         -> bounded follow-up decision
                         -> assistant message + run-bound RagContext

ordinary ask -> reuse latest durable RagContext -> question-answer analysis
```

The deterministic report workflow reads raw source messages, the latest grounded analysis, its persisted retrieval context, and admitted MITRE rows. Report generation does not call RAG again.

## Components

- `frontend/`: Next.js 16, React 19, Tailwind CSS 4, TypeScript
- `backend/`: FastAPI, async SQLAlchemy, PostgreSQL, Alembic
- `rag_service/`: standalone GraphRAG service backed by Qdrant and Neo4j

The browser calls only the backend. Chat is currently single-user and has no authentication or per-user ownership boundary.

## Persistence

The demo baseline contains five application tables: `chat_threads`, `chat_messages`, `chat_runs`, `rag_contexts`, and `chat_reports`. It intentionally discards compatibility with older demo schemas and data.

## API boundary

All application routes use `/api/v1`: health; chat list/create/read/rename/delete; message submission; run status; and chat-scoped report create/list/read/PDF download. There are no standalone case routes, top-level report routes, upload/OCR routes, or frontend-facing RAG proxy routes.

## Run

```powershell
doppler run -- docker compose up --build
```

Or run services separately:

```powershell
.\env_mitre\Scripts\Activate.ps1
python install_deps.py
cd backend
doppler run -- python -m alembic upgrade head
doppler run -- uvicorn app.main:app --reload
```

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000/chat`; backend OpenAPI is at `http://localhost:8000/docs`.

## Checks

```powershell
.\env_mitre\Scripts\python.exe -m pytest backend\tests -q
cd frontend
npm run test
npm run lint
npm run build
```
