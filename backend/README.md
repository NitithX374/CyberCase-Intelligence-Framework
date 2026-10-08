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

A report is built once per analysis by `app/reports/display.py` and stored as a display snapshot in `case_reports.structured_report`; the HTML and PDF are rendered from that stored copy. Its findings and Source labels, technical notices, and limitations are assembled by `findings.py`, `technical.py`, and `limitations.py` in the same folder.

## Source flow

A document becomes a `CaseDocument` holding the file and a document `CaseSource` holding the text read from it; the source's `provenance_json` keeps the pages, their offsets into that text, and the warnings from reading it, and the source reads its document's `filename`, `mime_type` and `size_bytes`, which `CaseSourceRead` returns. A narrative becomes a narrative `CaseSource`. Each native source changes the Case `source_revision`.

Clarification answers are different: they are persisted `ChatMessage` rows and loaded as `followup_history` for later analysis. They are not native Case sources and do not change `source_revision`; Reading and binding expose answered text as Evidence Units under synthetic QA identifiers.

A manual analysis request is refused with 409 `analysis_waiting_followup` while a follow-up question awaits an answer. The question remains pending; the Chat answer request asks remaining questions and automatically continues analysis when the round is complete. An answered round whose analysis failed can still be retried through Chat or a new analysis request.

An analysis reads one `CaseSourceBundle(revision, sources)` plus the separate follow-up history. The bundle is passed through assessment, optional technical augmentation, structured analysis, and source binding without database access inside the analysis steps. The workflow stores the result only after model work finishes and refuses to store it if the Case source revision changed meanwhile. The stored result records what it read in `external_context_json`: `sources_read`, the IDs of the sources it read, and `followup_history`, each answered follow-up's QA id, question and answer. The report takes the list of sources from `sources_read` and reads those source rows (`recorded_source_bundle` in `app/reports/generate.py`); a source added later is not included, and a missing one refuses the report with `analysis_source_snapshot_invalid`. `followup_history` is not re-read from chat.

Reading receives every source's exact unit text with local IDs such as `U001`, the unchanged `source_id`, and document/quality metadata. `app/analysis/reading_sources.py` captures revisions before the call and expands selected aliases to canonical IDs before binding; offsets and hashes stay backend-owned. `app/sources/evidence.py` and `app/trace/evidence_binding.py` retain deterministic exact spans, revision checks and document page locators. Stored traces keep full canonical IDs. Units are computed at analysis time and need no table or migration. Historical quote/pointer fields remain readable; new binding uses source-unit IDs without quote recovery.

The Reader returns only `version` and canonical `claims`. The backend resolves
Source-unit IDs to original text/provenance. One prompt-structured LLM call batches
exactly the Claims supplied to Judgement into Parties, Timeline and Impacts.
Both calls run independently in parallel after binding and frozen B1-LR Claim admission; views never enter
Judgement/chat and are not authoritative factual records. The extractor input is
only Claim IDs/text. Schema and nonempty known Claim links are checked; any row
with an unknown ID is dropped and logged. Roles and combined date/time may be
null. Views receive no independent semantic verifier or fabricated offsets/citations. Existing
`bound`/`mixed`/`unbound`/`no_claim` meanings remain structural. Historical extractor
and projection metadata remain readable through generic records. Mandatory B1-LR
checks Claims against selected Source units before either call; its LR boundary
is0.50 with longest-first NLI truncation512. It fails if a pinned model is
unavailable, and abstains if no Claim is admitted. See [the verifier contract](../research/attribution_benchmark/B1_INTEGRATION.md).

`CASE_READING_THINKING_TOKENS` can override Reading reasoning without changing Judgement or assessment. Use 0 to disable, or at least 1,024; absent historical pipeline fields inherit the shared budget. Compose keeps 8,192 following the small matched pilot: faster reasoning-off generations did not consistently satisfy the strict Reader schema. Output limits, retries and production timeouts are unchanged. From `backend`, `python -m experiments.reading_load_pilot --output-dir <new-folder>` measures payload sizes; add `--execute` explicitly to call the configured provider on two prelabelled fixtures. The pilot records raw replies, retries, binding and a separate experiment-only 300-second wall limit; it never writes Cases or calls Judgement, derived-view extraction or RAG.

The `case_views` call reuses the configured analysis model/provider order, with
thinking disabled, output capped at 4,096 tokens and an overall deadline of at most
60 seconds. Bounded transport and invalid/truncated-output retries remain within that
deadline. Schema/provider/timeouts yield empty views and recorded failure status;
Judgement may complete normally. Its failure cancels outstanding extraction.
`view_extraction` records method `llm`, model, input Claims, duration, status,
warning code and dropped-row count. The existing analysis snapshot caches views
for reads/reports. New analysis runs extract again; no second revision system or
cross-analysis cache is introduced. The local extractor service/config/mount,
loader, per-Claim runtime and weight provisioner are removed. Torch/Transformers
are still required by the encoder gate and the pinned Claim verifier and MPNet selector. Existing model assets
and historical diagnostic artifacts are retained.

Every structured model stage (assessment, Reading, Judgement, Views, Chat and
the LLM MITRE gate) specifies JSON in its system prompt. The backend sends no
provider-enforced schema. Pydantic checks the full required shape, nested types,
enums and bounds before the existing DTO validators and grounding checks.
Invalid JSON or a token-limit stop gets at most one generation retry; repeated
failure remains visible. Logs distinguish the outbound `request_max_tokens`
from provider-reported output usage. Input estimates include the JSON contract.

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
