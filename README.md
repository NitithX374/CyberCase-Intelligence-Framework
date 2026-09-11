# CyberCase Intelligence Framework

CyberCase is a full-stack prototype for **General Case Summarization and Case Analysis**. It analyzes admitted user narratives and reviewed document text in one direct LLM call, identifies material unresolved gaps, optionally asks a focused clarification, and conditionally augments technical cases with MITRE ATT&CK context.

> For complete research questions, design principles, and confirmed architecture, see [`docs/research/CURRENT_PROJECT_DIRECTION.md`](docs/research/CURRENT_PROJECT_DIRECTION.md).

## Trust boundary & Source-Role Isolation

- **Included Evidence**: Initial case narratives, user clarification answers, and reviewed document transcripts. Only admitted case evidence can support case facts, timelines, and findings.
- **Excluded Evidence**: Assistant text, RAG output, MITRE ATT&CK descriptions, and general model knowledge.
- **External Knowledge Isolation**: External knowledge provides technical threat actor context; it **never** becomes an admitted case fact.
- **Source References**: Important findings retain source references and short supporting quotes where practical. Existing snapshots and hashes remain for reproducibility without defining the analysis architecture.

## Runtime flow

```text
CASE MATERIAL (User Narrative / Reviewed Document)
      ↓
Direct Main Analysis LLM
  [ Summary + Findings + Material Gaps + Source References ]
      ↓
Deterministic Follow-up Selection → Optional Question Realization
      ↓ (conditional on cyber threat indicators)
MITRE Applicability Gate → Optional rag_service Retrieval + Mapping
      ↓
Persisted Result + Deterministic Preliminary Report
```

Ordinary `ask` runs reuse the latest durable case analysis context for focused question-answering. Report generation is deterministic and template-first; it reads persisted case findings and optional technical appendices without re-querying RAG.

## Components

- `frontend/`: Next.js 16, React 19, Tailwind CSS 4, TypeScript
- `backend/`: FastAPI, async SQLAlchemy, PostgreSQL, Alembic
- `rag_service/`: standalone GraphRAG service backed by Qdrant and Neo4j

The browser calls only the backend. Authentication and per-user Case ownership are enforced by the backend.

## Persistence

PostgreSQL stores Cases, documents and extraction revisions, admitted evidence, analysis runs/results, clarifications, optional Chat transcripts, RAG context, and preliminary reports.

## API boundary

All application routes use `/api/v1`. The primary surface is authenticated Case CRUD, material/evidence admission, analysis/run status, clarification, and Case report routes. Optional Chat compatibility routes remain; the browser does not call `rag_service` directly.

## Code Style & Naming Conventions

The project enforces **`camelCase`** for function and method names across both Frontend and Backend, integrating the guidelines from `naming-analyzer` and `naming-cheatsheet` (kettanaito standard):
- **Function Naming (`camelCase`)**:
  - Follow the **A/HC/LC Pattern**: `prefix? + action (A) + high context (HC) + low context? (LC)` (e.g. `executeNativeAnalysisPipeline`, `verifyQuoteCoverage`, `determineCaseRunPhase`).
  - Use precise action verbs:
    - `get` (fetch or read data immediately)
    - `set` (declarative state assignment)
    - `reset` (restore initial state)
    - `add` vs `create` (`add` requires a destination collection; `create` creates anew)
    - `remove` vs `delete` (`remove` takes an item from a collection; `delete` erases an entity permanently)
    - `compose` (combine data into new formats)
    - `handle` (event and callback handlers)
  - Eliminate awkward leading underscores (`_`): Encapsulate internal helpers into cohesive domain classes or dedicated modules with explicit exports (`__all__`), rather than procedural `_helper` functions.
  - S-I-D Principle: Names must be **S**hort, **I**ntuitive (natural English, no made-up verbs), and **D**escriptive.
  - Avoid cryptic contractions: use full words (`calculateTotal`, `userConfig`).
- **File Naming**:
  - Frontend: `kebab-case` for utility/type modules (`api-client.ts`, `use-chat.ts`) and `PascalCase` for React components (`ChatWorkspace.tsx`).
  - Backend: Clean `camelCase` modules (`caseMaterials.py`, `pipelineExecution.py`, `evidenceQuoteResolver.py`).
- **Variables & Boolean States**:
  - `camelCase` with standard question-form prefixes (`is*`, `has*`, `can*`, `should*`).
  - Reflect the expected result directly (`isDisabled` instead of `!isEnabled`).

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
