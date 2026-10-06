# CyberCase Backend

The FastAPI backend owns authentication, Case CRUD, document intake, Case sources, request-scoped analysis, deterministic follow-up, Case Ask/Chat, optional technical context, and preliminary reports.

## Current boundary

All application routes use `/api/v1`, one `routes.py` per feature folder (`app/auth/`, `app/cases/`, `app/sources/`, `app/analysis/`, `app/chat/`, `app/reports/`). `tests/test_route_surface.py` asserts the exact surface; it is the authority when this list and the code disagree.

- `/health` — service and database health;
- `/auth/register`, `/login`, `/logout`, `/session` — cookie session;
- `/cases`, `/cases/{case_id}` — Case lifecycle;
- `POST /cases/{case_id}/documents`, `GET /cases/{case_id}/documents/{document_id}/content` — document upload and the original file; there is no document list, because each document is listed through its source;
- `/cases/{case_id}/sources` — native sources used for analysis;
- `/cases/{case_id}/analysis` — read the latest validated analysis or start a request-scoped analysis;
- `/cases/{case_id}/chat`, `/chat/messages` — Case Ask/Chat and clarification answers;
- `/cases/{case_id}/reports` — report generation, history, HTML, and PDF.

The browser calls only this backend. Authentication and Case ownership are enforced here. Optional MITRE retrieval is called by the backend only when that augmentation is enabled and applicable; external context is not a Case source.

There is no run resource. An analysis and an answer happen inside the request that asked for them. The analysis request may perform a gap assessment, optional technical augmentation, two structured analysis calls (a reading, then a judgement), and deterministic source binding. `app/main.py` therefore refuses to start with more than one application worker.

## Persistence

PostgreSQL stores Cases, documents, native Case sources, analysis results, Case-owned messages, optional retrieval context, and Case reports. The SQLAlchemy models in `app/models/` are the authority for the persisted shape. `alembic/versions/0001_initial_schema.py` is the one migration that builds it, and `tests/test_database_schema_parity_alembic.py` checks that the two match.

A report is built once per analysis by `app/reports/display.py` and stored as a display snapshot in `case_reports.structured_report`; the HTML and PDF are rendered from that stored copy.

## Source flow

A document becomes a `CaseDocument` holding the file and a document `CaseSource` holding the text read from it; the source's `provenance_json` keeps the pages, their offsets into that text, and the warnings from reading it, and the source reads its document's `filename`, `mime_type` and `size_bytes`, which `CaseSourceRead` returns. A narrative becomes a narrative `CaseSource`. Each native source changes the Case `source_revision`.

Clarification answers are different: they are persisted `ChatMessage` rows and loaded as `followup_history` for later analysis. They are not native Case sources and do not change `source_revision`; Reading and binding expose answered text as Evidence Units under synthetic QA identifiers.

An analysis reads one `CaseSourceBundle(revision, sources)` plus the separate follow-up history. The bundle is passed through assessment, optional technical augmentation, structured analysis, and source binding without database access inside the analysis steps. The workflow stores the result only after model work finishes and refuses to store it if the Case source revision changed meanwhile. The stored result records what it read in `external_context_json`: `sources_read`, the IDs of the sources it read, and `followup_history`, each answered follow-up's QA id, question and answer. The report takes the list of sources from `sources_read` and reads those source rows (`recorded_source_bundle` in `app/reports/generate.py`); a source added later is not included, and a missing one refuses the report with `analysis_source_snapshot_invalid`. `followup_history` is not re-read from chat.

Reading receives all sources as deterministic, exact-offset Evidence Units from `app/sources/evidence.py`. Claims select `source_id` plus `evidence_unit_ids`; `app/trace/evidence_binding.py` reproduces original source text and page locators without searching for model-written quotes. Units are computed at analysis time and need no table or migration. Existing quote matching and advisory recovery remain available for legacy citations and unresolved pointers.

The Reader returns only `version` and canonical `claims`. Each claim selects source-unit citations; the backend derives its source-ID lists and resolves original text and provenance. Local GLiNER2 derives Parties, Timeline and Impacts from claims with resolved supporting citations for Details and reports. Selected fields have original Claim offsets and backend-assigned claim links; unselected roles are null and full Claim context is retained. Judgement receives only those claims, answered follow-up history and optional external MITRE context. It generates the summary, gaps and associations without the extracted views. No projection-specific NLI verifier runs; GLiNER2 extraction is not semantic verification. Generic NLI still serves legacy advisory meaning recovery. Historical structured views and stored verdicts remain readable. Binding states (`bound`, `mixed`, `unbound`, `no_claim`) indicate resolvable support, not semantic confirmation. See [the grounding contract and examples](../docs/architecture/evidence-unit-grounding.md).

Provision local Claim-view weights from `backend` with `python scripts/copy_case_view_weights.py` before running analysis. The pinned `gliner2==1.3.2` dependency is in `requirements-encoder.txt`. Weights are ignored and mounted read-only by Compose; runtime never downloads them. `CASE_VIEW_MODEL_PATH=gliner_case_views`, `CASE_VIEW_DEVICE=cpu` and `CASE_VIEW_THRESHOLD=0.5` are the defaults. Missing weights or invalid spans produce explicit errors. Trace `view_extraction` records model/revision, device/threshold, eligible/excluded claims and elapsed time.

## One name per thing

A Case is analysed from **sources**. `case_sources`, `source_revision`, `CaseSource`, `CaseSourceCreate`, `CaseSourceRead`, and `/cases/{case_id}/sources` use the same vocabulary. An Evidence Unit addresses content inside a source; its ID does not replace the persisted source identity.

The report template's `case_evidence` and `evidence_to_examine` sections (`app/reports/templates/case_report.html.j2`) are section ids in the template, not inputs: they print the snapshot's `findings` and its `gaps`, the information that still needs checking.

## Run and verify

```powershell
cd backend
pip install -r requirements-dev.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
python -m pytest -q
```

`requirements-dev.txt` adds the test tools to `requirements.txt`. The PostgreSQL tests skip unless `CYBERCASE_TEST_DATABASE_URL` is set.
