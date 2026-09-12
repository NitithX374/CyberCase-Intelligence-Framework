# Case and CaseRun ownership audit

2026-09-12 [USER/CODE] Scope: read-only schema/runtime audit and migration proposal against `gemini/canonical-dev-cleanup` at `9325e40`. No migration, application change, live database mutation, or history rewrite performed. The older continuity entries describe another checkout state.

## Canonical contract

Case owns persistent case state. CaseRun owns durable processing state and processing artifacts. A reference is not ownership. SQL `async def` does not imply a durable job. Ownership cascade remains subject to references from retained records: a Run need not be independently deletable merely because its artifacts use CASCADE.

## Ownership map: all 14 product tables

| Table | Canonical owner now | Current ownership edge | Assessment |
| --- | --- | --- | --- |
| users | Account root | None | Outside Case execution lifecycle |
| cases | Account/workspace retention policy | user_id: ORM CASCADE, baseline SET NULL | Policy/schema mismatch; resolve explicitly |
| chat_threads | Case | case_id CASCADE; ORM delete-orphan | Correct |
| chat_messages | ChatThread | thread_id CASCADE; ORM delete-orphan | Correct; analysis_result_id SET NULL is a reference |
| case_documents | Case | case_id CASCADE | Correct |
| document_extractions | CaseDocument while extraction is request-scoped | document_id CASCADE | Correct for current lifecycle; no durable extraction job exists |
| case_evidence_sources | Case | case_id CASCADE | Correct; document_id/origin_message_id SET NULL are optional origin references |
| case_evidence_revisions | EvidenceSource | source_id CASCADE | Correct; extraction_id SET NULL preserves admitted text after extraction removal |
| case_evidence_snapshots | Case | case_id CASCADE | Correct; consumed by Runs/results/reports through RESTRICT references |
| case_runs | Case | case_id CASCADE | Correct; currently analysis/ask only |
| case_analysis_results | CaseRun | run_id UNIQUE RESTRICT, but Run relationship delete-orphan | Explicit ORM/SQL ownership contradiction |
| rag_contexts | CaseRun | case_run_id NOT NULL UNIQUE CASCADE | SQL ownership correct; runtime retry and ORM ownership incomplete |
| case_reports | Case for current synchronous template generation | case_id CASCADE | No durable report job today; retain until lifecycle changes |
| case_clarifications | Case, proposed persistent clarification history | case_id CASCADE plus origin_analysis_result_id CASCADE | Origin reference currently deletes the clarification; choose durable history and use RESTRICT |

`Case.analysis_results` and `Case.rag_contexts` currently also have `delete-orphan`. Their direct case_id columns may remain useful for scoping/querying, but collection membership should not provide a second independent artifact-deletion owner. Keep case navigation without delete-orphan; Run is the immediate artifact owner. Direct case_id CASCADE can remain for aggregate teardown, with same-Case consistency checks.

## Findings and evidence

### 1. Retrieval persistence does not implement retry reuse

`backend/app/services/workflow/caseRunService.py:172` requeues the same failed Run. `caseRunExecution.py:255` persists retrieval early, looking up by provider retrieval_context_id. `caseMitreAugmentation.py:108` calls retrieval again on execution; no existing context is loaded by case_run_id before that request. `caseRunCompletion.py:282` also looks up by retrieval ID.

If attempt A commits context X and later fails, attempt B can produce Y for the same Run. Early persistence of Y violates UNIQUE(case_run_id); the callback exception is logged and swallowed. Completion may then try to insert Y again. This is a code-path finding, not a reproduced live-provider failure in this audit.

Minimal fix: load context by run ID before retrieval, validate its Case/snapshot binding, and reuse it. Persist only validated retrieval outputs. Fence early persistence by current lease owner and attempt count inside the transaction, matching completion fencing. On concurrent insertion, reload the winning same-Run context and use that artifact, rather than silently continuing with an unpersisted ID. A new Analyze Again request with a new idempotency key creates a new Run and its own retrieval artifact. Do not weaken the existing unique constraint.

### 2. AnalysisResult ownership differs between ORM and SQL

`backend/app/models/caseRun.py` declares Run.analysis_result with delete-orphan/passive_deletes, while result.run_id is RESTRICT in both ORM metadata and the baseline. Loaded ORM deletion and unloaded/raw SQL deletion can therefore behave differently. Proposed ownership FK: CASCADE. Keep result.snapshot_id and result.retrieval_context_id as RESTRICT references.

Changing this one FK does not prove that deleting a Run or Case works. A report referencing its result, or another Run referencing that result, can legitimately protect it. Also, two artifacts of the same Run can reference one another: deleting the Run cascades to both result and RagContext while result->RagContext is RESTRICT. Exercise this complete graph; do not infer correctness from individual FK labels.

### 3. Baseline and ORM drift precedes the ownership migration

`backend/alembic/baseline_versions/0001_canonical_case_system.py` differs from models:

- cases.user_id: baseline SET NULL versus ORM CASCADE.
- case_runs.context_analysis_result_id: baseline SET NULL versus ORM RESTRICT.
- case_evidence_revisions: baseline created_at versus ORM admitted_at and archived_at; associated indexes/unique names also differ.
- Chat message kind constraint and some indexes differ.

The deployed catalog was not inspected here. ORM-only tests cannot certify migration-created schema. Inspect actual alembic_version and catalog before selecting a migration parent or claiming a production FK value.

### 4. Clarifications span processing and persistent case history

`caseClarification.py` persists a pending question, later answer links/fingerprint and answered/superseded state. An answer becomes Case-owned evidence. `services/followup/caseClarification.py` admits the answer and enqueues operation=analysis with clarification_id. This is a coherent implementation: no extra clarification Run is needed for recording an answer; the resulting analysis is the durable job.

Recommended ownership: Case owns clarification history; origin_analysis_result_id is a required reference protected with RESTRICT. Keep optional message/answer-source links SET NULL and origin_snapshot RESTRICT. This prevents deleting a producing result from erasing answered clarification history. If intentionally treating questions as disposable artifacts instead, retain CASCADE, but document that distinct retention policy before migration.

### 5. Report and extraction are conditional future migrations

`services/reports/case_report_persistence.py:296` builds and persists a report inside one transaction; `case_report_template.py:22` uses a deterministic template and validator. There is no queued/running report lifecycle. Keep Case ownership and references to result/context/snapshot.

`routers/caseMaterials.py` awaits ingestion during upload, then persists document plus extraction. A process crash can lose in-flight work, but no durable job contract is currently offered. Moving OCR into a recoverable worker is a separate feature, not a prerequisite for this ownership repair.

If either becomes durable: introduce the corresponding operation and producer run_id then, not now. `operation` currently has length 16, so `document_extraction` requires widening. Mandatory snapshot_id also needs an operation-aware rule because extraction may precede evidence admission. Retain the current one-active-Run-per-Case policy until a real concurrency requirement justifies changing it.

### 6. Generic job fields do not require erasing typed input references

Current Run already holds lifecycle/idempotency/request fields; output lives in separate tables. snapshot_id, request_message_id, context_analysis_result_id, clarification_id and pinned pipeline_config are input/provenance references or execution configuration. Keep them for this pass. Moving IDs into request_payload solely to make the table generic loses FK enforcement and adds a migration without a product benefit.

The independent case_id/snapshot_id/run_id/context IDs do not themselves enforce same-Case identity. Audit writers and existing data. Composite FKs are a possible subsequent enforcement step if required; avoid expanding this small ownership repair into a universal polymorphic job framework.

## Minimal implementation and migration proposal

1. Compare ORM metadata, a database created from the baseline, and the deployed catalog. Resolve the account deletion policy and existing drift first; do not rewrite an applied baseline or synthesize historical Runs.
2. Fix retrieval reuse and attempt-fenced persistence under the existing schema. Preserve UNIQUE(case_run_id).
3. Add a successor migration changing `fk_case_analysis_results_run_id` to CASCADE and, under the proposed persistent clarification policy, `fk_case_clarifications_origin_result_id` to RESTRICT. Align Run context_result reference to RESTRICT where the catalog currently uses SET NULL. Align ORM ownership collections in the same change.
4. Verify aggregate deletion and retained references on PostgreSQL. Existing `CaseService.deleteCase` expunges ORM state and issues a direct Case DELETE; it relies on the database graph. If RESTRICT ordering prevents aggregate teardown, explicitly delete Case-owned dependents in tested dependency order within one transaction. Do not globally replace protective references with CASCADE. Deferred NO ACTION is an alternative only when end-of-transaction validation is the chosen policy.
5. Add no operations, report job table, extraction job table, or generic artifact table in this pass. Keep synchronous CRUD as CRUD.

## Required acceptance checks for implementation

- Baseline-created schema and migrated schema agree with ORM columns, FK actions and constraints.
- Retry after persisted retrieval reuses exactly one context; a new logical Run gets a new context; stale workers cannot write artifacts.
- Deleting an unreferenced Run removes its result/context but preserves its input snapshot and chat messages.
- Retained reports, consuming Runs and clarification history block deletion of required inputs.
- Whole-Case deletion succeeds for a populated graph, including a result/context pair, reports, clarification, and later consuming Run, without deleting another Case.
- Test loaded ORM relationships, unloaded ORM relationships and raw SQL deletion separately.
- Simple Case edits, evidence admission and conversation persistence do not create gratuitous Runs.

No application or migration implementation is included in this audit. Live schema parity and deletion behavior remain unverified until these checks are run on PostgreSQL.
