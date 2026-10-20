# CyberCase Intelligence Framework

CyberCase is a full-stack prototype for general case summarization and preliminary case analysis. It accepts user-authored narratives and uploaded documents, extracts document text, identifies unresolved information gaps, produces a structured analysis, binds supported claims back to Case sources, and assembles a deterministic report.

The current production path is source-bounded and domain-neutral. MITRE ATT&CK retrieval is an optional external technical augmentation; it is not required for the core case-analysis path and is never treated as a Case source.

## Repository map

The system is three services, each in its own folder.

| Folder | What it holds |
|---|---|
| `frontend/` | The Next.js web app: pages in `src/app/`, one folder per feature in `src/features/`, unit tests in `src/test/` and browser tests in `e2e/`. [`frontend/README.md`](frontend/README.md) gives the rules its folders keep. |
| `backend/` | The FastAPI API: one folder per feature in `app/`, tests in `tests/`, database migrations in `alembic/`, and in `scripts/` the scripts that copy the local model weights into `backend/models/` (not in git) and export the OpenAPI schema. [`backend/ARCHITECTURE.md`](backend/ARCHITECTURE.md) describes the analysis and the claim verifier. |
| `rag_service/` | The ATT&CK retrieval service: the GraphRAG pipeline and its evaluation in `app/RAG/GraphRAG/`, the legal lookup in `app/RAG/legal_reference/`, and a fine-tuning module in `finetune/`. [`rag_service/ARCHITECTURE.md`](rag_service/ARCHITECTURE.md) describes it. |

Around them:

| Path | What it holds |
|---|---|
| `docker-compose.yml` | The three services and PostgreSQL, for running the system locally. |
| `docker-compose.selfhosted.yml`, `deploy/selfhosted/` | The same stack with the models on self-hosted vLLM servers. [`deploy/selfhosted/README.md`](deploy/selfhosted/README.md) has the steps. |
| `Mitre_ATT&CK Doc/` | The MITRE ATT&CK data in STIX 2.1, which the retrieval service ingests. |
| `Documents/` | Reference PDFs, not read by the code: Thai laws on computer crime, electronic transactions, cybersecurity and personal data, the Criminal Code, and a summary of the system flow. |
| `docs/design/` | The logo and two draw.io diagrams. |
| `research/` | Studies run beside the system, listed below. The services do not import them. |
| `.github/workflows/deploy.yml` | Builds and pushes the Docker images on every push to `main`. |
| `install_deps.py` | Installs the backend and retrieval-service requirements into the active Python. |
| `AGENTS.md`, `CLAUDE.md`, `.claude/` | Instructions and skills for the coding agents used in development. |

| Research folder | What it holds |
|---|---|
| `research/nli_grounding/` | The experiment that chose the claim verifier, B1-LR. Section 5.4.3 of the thesis book reports it. |
| `research/attribution_benchmark/` | Benchmark runs and audits of that verifier. Sections 5.4.1, 5.4.2 and 5.4.4 of the thesis book and the paper report them. |
| `research/traceability_properties/` | Measurements of the source units on public ThaiSum and AttributionBench text: losslessness, determinism, revision safety and segmentation cost. The paper reports them. |
| `research/segmenter_comparison/` | Why the backend splits sentences with SaT and not PyThaiNLP crfcut: how the two cut the same 200 XL-Sum articles, and how fast they are. Section 5.4.5 of the thesis book reports it. The article text is not stored. |
| `research/attack_applicability_search/` | A survey of released cybersecurity datasets for deciding whether ATT&CK applies to a case; none of them is labelled for that decision. The folder holds the survey and its receipts, not the datasets. |
| `research/ocr_downstream/` | The OCR error study that the appendix of the thesis book reports: scripts, protocol and scores on 100 ThaiSum crime articles (MIT licence), with an OCR error bank built from ThaiOCRBench (CC BY-SA 4.0). The article text and the raw model outputs are not included. |
| `research/notes/USABILITY_PROTOCOL.md` | The protocol of the usability test, which the paper cites. |

A study that runs against an older backend names its commit in `pinned/<commit>/COMMIT`. The tag `pre-squash-2026-10-19` keeps those commits. Studies that neither the thesis book nor the paper reports were removed on 2026-10-20; commit `3b9ea357` still has them.

## Trust boundary and source roles

- **Case sources**: user narratives and extracted text from uploaded documents. Case sources and answered follow-ups (below) are the only inputs that can support case facts, timelines, entities, and findings.
- **Follow-up history**: answers to clarification questions are persisted as Case chat messages. A later analysis may cite an answer as `QA-nn` to support a claim, the same way it cites a source (`followup_registry_items` in `backend/app/trace/bind.py` puts each answered follow-up beside the sources, in the reading input and in the binding index). An answer is still not a `CaseSource` row and does not increment `source_revision`.
- **External context**: assistant responses, MITRE descriptions, RAG retrieval, and general model knowledge are not Case sources and cannot establish incident facts.
- **Traceability**: each claim cites the source units it rests on by ID. The backend resolves those IDs to the exact text and offsets of the source bundle and the answered follow-ups, and records a reference it cannot resolve as invalid.

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
       ↓             ↓
Persist assessment   Optional MITRE augmentation
and focused question ↓
(request ends)       Reading: claims citing source units
                     ↓
                     Deterministic source binding
                     ↓
                     Judgement, views and claim check, side by side
                     ↓
                     Validated analysis → Report
```

The assessment may stop the request before technical augmentation, the analysis calls, and binding. When the case proceeds, a reading call writes the claims, each citing the source units it rests on, and the backend binds those units to the source text. Then three things run at once: a judgement call writes the summary and gaps over the checked claims, a views call lists the parties, timeline and impacts, and the claim check labels each claim. The ATT&CK associations are not written by a model: the backend lists the techniques the RAG service tied to a sentence of the case, with that sentence. Analysis and Case Ask operations are request-scoped; there is no run resource, job queue, or polling workflow.

Report generation is separate, deterministic, and template-first. It reads a selected validated analysis and what that analysis recorded when it was stored: the sources it read and the follow-up answers it had. Each analysis gets at most one report. The report is stored as a display snapshot, and the HTML and PDF are rendered from that stored copy. No model is called.

## Components

- `frontend/`: Next.js 16, React 19, Tailwind CSS 4, TypeScript
- `backend/`: FastAPI, async SQLAlchemy, PostgreSQL, Alembic
- `rag_service/`: optional standalone GraphRAG service backed by Qdrant and Neo4j

The browser calls only the backend. Authentication and per-user Case ownership are enforced by the backend.

## Persistence

PostgreSQL stores Cases, uploaded documents, native Case sources (narratives, and the text extracted from each document with its pages and warnings in `provenance_json`), the Case source revision, analysis results, Case-owned chat messages, optional technical retrieval context, and reports. The schema is created by the Alembic migrations in `backend/alembic/versions/`: `0001_initial_schema.py`, and `0002_source_deactivation.py`, which lets a source be turned off. An analysis result can have `status="assessment"` while a clarification question is pending or `status="validated"` after full analysis and source binding.

There is no `CaseRun` table. The backend reads a source bundle, releases the database transaction during model or external-service work, and stores the result in a later short transaction. A result is rejected if the Case source revision changed while the request was running.

## API boundary

All application routes use `/api/v1`. The primary surface is authenticated Case CRUD, document upload and extraction, Case sources, request-scoped analysis, Case chat, and Case reports. There is no public upload/OCR route, top-level report route, run-status route, or browser-to-`rag_service` route.

## Development conventions

- Python backend modules use `snake_case`; frontend functions and variables use `camelCase`, with PascalCase React components.
- There is no line-count limit. Split a file when that makes it easier to read, test or own (see `AGENTS.md`).
- Keep LLM semantics in analysis steps and keep validation, routing, persistence, stopping rules, and report assembly deterministic.

## Run

```powershell
doppler run -- docker compose up --build
```

Or run services separately. `install_deps.py` installs `backend/requirements-dev.txt` (the backend plus its test tools) and `rag_service/requirements.txt` into the active Python environment:

```powershell
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

The backend's PostgreSQL tests are skipped unless `CYBERCASE_TEST_DATABASE_URL` points at a test database.

```powershell
cd backend
python -m pytest -q
cd ..\frontend
npm run test
npm run lint
npm run build
```
