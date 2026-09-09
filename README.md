# CyberCase Intelligence Framework

CyberCase is an evidence-first full-stack system for **General Case Summarization and Grounded Analysis**. The admitted user narratives and reviewed case document transcripts serve as authoritative case evidence. The backend decomposes case evidence into atomic claims with exact literal span provenance, applies deterministic selection, generates factually grounded case findings, optionally requests bounded clarifications, and conditionally augments findings with external MITRE ATT&CK intelligence.

> For complete research questions, design principles, and confirmed architecture, see [`docs/research/CURRENT_PROJECT_DIRECTION.md`](docs/research/CURRENT_PROJECT_DIRECTION.md).

## Trust boundary & Source-Role Isolation

- **Included Evidence**: Initial case narratives, user clarification answers, and reviewed document transcripts. Only admitted case evidence can support case facts, timelines, and findings.
- **Excluded Evidence**: Assistant text, RAG output, MITRE ATT&CK descriptions, and general model knowledge.
- **External Knowledge Isolation**: External knowledge provides technical threat actor context; it **never** becomes an admitted case fact.
- **Provenance Invariant**: Every reported claim binds exact character spans in the admitted raw evidence snapshot (`source_message_ids` + SHA-256 hash).

## Runtime flow

```text
CASE MATERIAL (User Narrative / Reviewed Document)
      ↓
Claim-Anchored Case Analysis
  [ Extraction → Provenance Binding → Selection → Constrained Generation ]
      ↓
Grounded Case Findings (AnalysisTraceV3)
      ↓ (conditional on cyber threat indicators)
Optional Technical Augmentation (rag_service STIX 2.1)
      ↓
Persisted Assistant Message + Chat-Scoped Report
```

Ordinary `ask` runs reuse the latest durable case analysis context for focused question-answering. Report generation is deterministic and template-first; it reads persisted case findings and optional technical appendices without re-querying RAG.

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
