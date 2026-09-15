# CyberCase Backend

The FastAPI backend owns authentication, Case CRUD, document/material intake, Case sources, analysis runs/results, deterministic follow-up, Case-owned Ask/Chat messages, optional MITRE context, and preliminary reports.

## Current boundary

All application routes use `/api/v1`. The main route groups are:

- `/cases` and `/cases/{case_id}` for Case lifecycle;
- `/cases/{case_id}/documents` and document content routes;
- `/cases/{case_id}/evidence` for received Case sources;
- `/cases/{case_id}/analysis` and `/cases/{case_id}/runs/{run_id}` for analysis state;
- `/cases/{case_id}/clarifications` for focused follow-up answers;
- `/cases/{case_id}/chat` for the Case Ask/Chat panel;
- `/cases/{case_id}/reports` for report generation, history, HTML, and PDF.

The browser calls only this backend. Authentication and Case ownership are enforced here. External MITRE retrieval is performed by the backend when the current analysis gate requires it; external context is not Case evidence.

## Persistence

PostgreSQL stores Cases, documents, extraction records, Case sources, CaseRuns, analysis results, Case-owned messages, optional RAG context, and Case reports. The current SQLAlchemy models and Alembic migrations are the authority for the persisted shape.

## Source flow

Documents become `CaseDocument` and `DocumentExtraction` records, then a document source. Narratives and follow-up answers are also persisted as Case sources. Active sources are loaded as one `CaseSourceBundle(revision, sources)` for a `CaseRun`; analysis, validation, Chat, MITRE augmentation, and reports derive their local views from that bundle.

## Compatibility names

Application code uses `CaseSource`, `CaseSourceCreate`, and `CaseSourceRead`. The existing `/evidence` HTTP paths and generated schema names `CaseEvidenceCreate` and `EvidenceSourceRead` remain unchanged for frontend compatibility. The physical `case_evidence_sources` table, `exact_text` source column, and `evidence_revision` fields also remain unchanged until a separately reviewed migration.

## Run and verify

```powershell
cd backend
python -m alembic upgrade head
uvicorn app.main:app --reload
..\env_mitre\Scripts\python.exe -m pytest tests -q
```
