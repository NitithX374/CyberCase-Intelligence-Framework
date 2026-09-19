# CyberCase Backend

The FastAPI backend owns authentication, Case CRUD, document intake, Case sources,
analysis, deterministic follow-up, the Case Ask/Chat panel, optional MITRE context,
and preliminary reports.

## Current boundary

All application routes use `/api/v1`, one router per resource in `app/routers/`.
`tests/test_route_surface.py` asserts the exact set; it is the authority when this
list and the code disagree.

- `/health` — the service and its database;
- `/auth/register`, `/login`, `/logout`, `/dev-login`, `/me`, `/session` — cookie session;
- `/cases`, `/cases/{case_id}` — Case lifecycle;
- `/cases/{case_id}/documents`, `/documents/{document_id}/content` — upload, list, read back;
- `/cases/{case_id}/sources` — what the Case is analysed from;
- `/cases/{case_id}/analysis` — read the latest analysis, or run one;
- `/cases/{case_id}/chat`, `/chat/messages` — the Case Ask/Chat panel;
- `/cases/{case_id}/reports` — report generation, history, HTML, and PDF.

The browser calls only this backend. Authentication and Case ownership are enforced
here. External MITRE retrieval is performed by the backend when the analysis gate
requires it; external context is not a Case source.

There is no run resource. An analysis and an answer are each one model call the
caller waits for, made in the request that asked for it — which is why
`app/main.py` refuses to start with more than one application worker.

## Persistence

PostgreSQL stores Cases, documents, extraction records, Case sources, analysis
results, Case-owned messages, optional RAG context, and Case reports. The
SQLAlchemy models and Alembic migrations are the authority for the persisted shape.

## Source flow

Documents become `CaseDocument` and `DocumentExtraction` records, then a document
source. Narratives and follow-up answers are also persisted as Case sources. Active
sources are loaded as one `CaseSourceBundle(revision, sources)`; analysis,
validation, Chat, MITRE augmentation, and reports derive their local views from that
bundle. A Case carries the revision its bundle was read at, so an analysis whose
sources changed underneath it is refused rather than stored.

## One name per thing

A Case is analysed from **sources**. `case_sources`, `source_revision`,
`CaseSource`, `CaseSourceCreate`, `CaseSourceRead` and `/cases/{case_id}/sources`
all say the same word, and `0006_source_vocabulary` is the migration that made
them agree. Prose that still says "evidence" or "material" for that thing is using
an older name for it.

The report's `case_evidence` and `evidence_to_examine` sections are a different
thing, and keep their names: what the analysis found, and what an investigator
should still look at.

## Run and verify

```powershell
cd backend
python -m alembic upgrade head
uvicorn app.main:app --reload
..\env_mitre\Scripts\python.exe -m pytest tests -q
```
