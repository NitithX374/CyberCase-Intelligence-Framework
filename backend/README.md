# CyberCase Backend

The FastAPI backend owns authentication, Case CRUD, document intake, Case sources, request-scoped analysis, deterministic follow-up, Case Ask/Chat, optional technical context, and preliminary reports.

## Current boundary

All application routes use `/api/v1`, one router per resource in `app/routers/`. `tests/test_route_surface.py` asserts the exact surface; it is the authority when this list and the code disagree.

- `/health` — service and database health;
- `/auth/register`, `/login`, `/logout`, `/dev-login`, `/me`, `/session` — cookie session;
- `/cases`, `/cases/{case_id}` — Case lifecycle;
- `/cases/{case_id}/documents`, `/documents/{document_id}/content` — document upload, listing, and extracted content;
- `/cases/{case_id}/sources` — native sources used for analysis;
- `/cases/{case_id}/analysis` — read the latest validated analysis or start a request-scoped analysis;
- `/cases/{case_id}/chat`, `/chat/messages` — Case Ask/Chat and clarification answers;
- `/cases/{case_id}/reports` — report generation, history, HTML, and PDF.

The browser calls only this backend. Authentication and Case ownership are enforced here. Optional MITRE retrieval is called by the backend only when that augmentation is enabled and applicable; external context is not a Case source.

There is no run resource. An analysis and an answer happen inside the request that asked for them. The analysis request may perform a gap assessment, optional technical augmentation, one structured main-analysis call, and deterministic source binding. `app/main.py` therefore refuses to start with more than one application worker.

## Persistence

PostgreSQL stores Cases, documents, native Case sources, analysis results, Case-owned messages, optional retrieval context, and Case reports. The SQLAlchemy models and Alembic migrations are the authority for the persisted shape.

## Source flow

A document becomes a `CaseDocument` holding the file and a document `CaseSource` holding the text read from it; the source's `provenance_json` keeps the pages, their offsets into that text, and the warnings from reading it, and the source carries the file's name as `filename`. A narrative becomes a narrative `CaseSource`. Each native source changes the Case `source_revision`.

Clarification answers are different: they are persisted `ChatMessage` rows and loaded as `followup_history` for later analysis. They are not native Case sources and do not change `source_revision`; the binding layer may expose them to the analysis trace through synthetic QA identifiers.

An analysis reads one `CaseSourceBundle(revision, sources)` plus the separate follow-up history. The bundle is passed through assessment, optional technical augmentation, structured analysis, source binding, and report projection without database access inside the analysis steps. The workflow stores the result only after model work finishes and refuses to store it if the Case source revision changed meanwhile.

## One name per thing

A Case is analysed from **sources**. `case_sources`, `source_revision`, `CaseSource`, `CaseSourceCreate`, `CaseSourceRead`, and `/cases/{case_id}/sources` use the same vocabulary. In prose, “evidence” can describe what a report found, but it is not the identifier for the persisted input object.

The report's `case_evidence` and `evidence_to_examine` sections are separate report concepts: findings produced by the analysis and information that still needs checking.

## Run and verify

```powershell
cd backend
python -m alembic upgrade head
uvicorn app.main:app --reload
..\env_mitre\Scripts\python.exe -m pytest tests -q
```
