# CyberCase Intelligence Framework

CyberCase is a full-stack prototype for general case summarization and preliminary case analysis. It accepts user-authored narratives and uploaded documents, extracts document text, identifies unresolved information gaps, produces a structured analysis, binds supported claims back to Case sources, and assembles a deterministic report.

The current production path is source-bounded and domain-neutral. MITRE ATT&CK retrieval is an optional external technical augmentation; it is not required for the core case-analysis path and is never treated as a Case source.

For the current product direction and research boundaries, see [`docs/research/CURRENT_PROJECT_DIRECTION.md`](docs/research/CURRENT_PROJECT_DIRECTION.md).

## Trust boundary and source roles

- **Case sources**: user narratives and extracted text from uploaded documents. These are the only sources that can support case facts, timelines, entities, and findings.
- **Follow-up history**: answers to clarification questions are persisted as Case chat messages. They are passed to later analysis and can be referenced with QA identifiers, but they are not native `CaseSource` rows and do not increment `source_revision`.
- **External context**: assistant responses, MITRE descriptions, RAG retrieval, and general model knowledge are not Case sources and cannot establish incident facts.
- **Traceability**: structured claims may carry source identifiers and exact quotes. The backend verifies those references against the source bundle and records unresolved bindings.

## Runtime flow

```text
CASE SOURCES + FOLLOW-UP HISTORY
              ↓
Gap-only assessment (case_assessment_v1)
              ↓
Deterministic follow-up policy
       ┌──────┴──────┐
       │             │
       Ask           Proceed
       │             ↓
Persist assessment   Optional MITRE augmentation
and focused question          ↓
       │             Structured main analysis
       │              (main_case_analysis_v1)
       │                         ↓
       └──────────────→ Deterministic source binding
                                  ↓
                         Validated analysis → Report
```

The assessment may stop the request before technical augmentation, the main analysis call, and binding. When the case proceeds, the main analysis is one structured LLM call. Analysis and Case Ask operations are request-scoped; there is no run resource, job queue, or polling workflow.

Report generation is separate, deterministic, and template-first. It reads a selected validated analysis and the source revision associated with that analysis; it does not require a new report-generation LLM call.

## Components

- `frontend/`: Next.js 16, React 19, Tailwind CSS 4, TypeScript
- `backend/`: FastAPI, async SQLAlchemy, PostgreSQL, Alembic
- `rag_service/`: optional standalone GraphRAG service backed by Qdrant and Neo4j

The browser calls only the backend. Authentication and per-user Case ownership are enforced by the backend.

## Persistence

PostgreSQL stores Cases, documents and extraction records, native Case sources, the Case source revision, analysis results, Case-owned chat messages, optional technical retrieval context, and reports. An analysis result can have `status="assessment"` while a clarification question is pending or `status="validated"` after full analysis and source binding.

There is no `CaseRun` table. The backend reads a source bundle, releases the database transaction during model or external-service work, and stores the result in a later short transaction. A result is rejected if the Case source revision changed while the request was running.

## API boundary

All application routes use `/api/v1`. The primary surface is authenticated Case CRUD, document upload and extraction, Case sources, request-scoped analysis, Case chat, and Case reports. There is no public upload/OCR route, top-level report route, run-status route, or browser-to-`rag_service` route.

## Development conventions

- Python backend modules use `snake_case`; frontend functions and variables use `camelCase`, with PascalCase React components.
- Keep production modules small and modular; the repository contract limits code files to 300 lines.
- Keep LLM semantics in analysis steps and keep validation, routing, persistence, stopping rules, and report assembly deterministic.

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

Open `http://localhost:3000/case`; backend OpenAPI is at `http://localhost:8000/docs`.

## Checks

```powershell
.\env_mitre\Scripts\python.exe -m pytest backend\tests -q
cd frontend
npm run test
npm run lint
npm run build
```
