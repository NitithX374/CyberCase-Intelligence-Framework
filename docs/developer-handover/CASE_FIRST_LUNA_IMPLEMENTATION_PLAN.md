# Case-first analysis: implementation handoff for Luna

Date: 2026-09-10
Status: DRAFT FOR IMPLEMENTATION; no application changes made by this planning task.
Supersedes: CASE_WORKER_IMPLEMENTATION_PLAN.md. Its message-triggered analysis and deferred document/result persistence are insufficient for the confirmed requirements below.

## 1. Confirmed requirements and authority

The user confirmed:

1. Users add documents and invoke Summarize/Analyze from the Case workspace without sending a Chat message.
2. Chat is optional for using the product; it supports additional questions and answers.
3. Historical evidence/analysis state is retained in the database. Do not implement a frontend history/version selector.
4. Every successful case analysis publishes an assistant analysis-result message automatically. Opening Chat afterwards shows that result even if Chat was never opened before.
5. Workflow manages Case processing. Chat manages messages and clarification conversation.

These requirements supersede the previous plan's restriction against document/evidence/result persistence. They do not authorize changes to RAG algorithms, OCR engines, HTR, NLI, legal reasoning, or an old generic Case State/event-sourcing framework.

Implementation is not authorized by the planning request itself. When the user gives Luna this plan to implement, implement the checkpoints below and report actual validation, not this document's expected results.

## 2. Design decisions proposed for this implementation

The following are engineering recommendations, not additional verbatim user requirements. Use them as the proposed baseline; surface material departures before implementing them.

- Keep the existing monolith, PostgreSQL, SQLAlchemy and worker mechanism. No new broker, microservices or agent framework.
- One Case has zero or one ChatThread. Existing shared UUIDs can remain; new code resolves the relationship explicitly. Case creation does not create Chat. Opening Chat or publishing the first result creates its thread transactionally.
- Keep a single queued/running CaseRun per Case, including ASK, to simplify ordering and context consistency. This limits simultaneous Q&A/analysis; document the tradeoff.
- Allow document/evidence edits while a run is executing. They create new immutable revisions; the running job stays pinned to its original snapshot. Its completed result can be latest-but-stale and must be labelled as such.
- Use one existing analysis operation initially; Summarize/Analyze wording does not imply two new provider pipelines.
- Keep current provider prompts/policies unless their source-reference transport requires a versioned schema change. Do not claim multi-document semantic clustering.
- Case-page clarification answers submit evidence and start a new analysis by an explicit action. They can also be mirrored into Chat as genuine user-authored replies, but must not require a transcript to exist.
- Keep original uploaded bytes in bounded PostgreSQL storage for this first implementation, with content hash, size and MIME metadata. Reuse existing upload limits; derive a storage budget before enabling production use. No public file URLs or original-PDF viewer. If existing storage already solves this, reuse it and document the choice instead of adding parallel storage.
- Historical analysis API access may exist for resolving a transcript message/report; do not expose a browse-history UI. Old analysis messages remain in the transcript as requested by the publication behavior.

## 3. Current code: read before editing

| File/module | Current coupling to remove or adapt |
| --- | --- |
| backend/app/models/case.py; services/cases/case_factory.py | Case currently eagerly owns a same-ID thread |
| backend/app/models/chat.py | ChatThread owns processing status; ChatRun requires a request message and thread |
| services/cases/case_management.py | Case status/timestamps are read from ChatThread |
| services/chat/chat_run_creation.py | Message insert, evidence classification, run creation, idempotency and thread state share one transaction |
| services/chat/raw_evidence.py | Evidence is reconstructed from user messages; first-user-message logic cannot remain the admission rule |
| services/chat/document_provenance.py | Existing exact document/page provenance validation must be retained |
| services/workflow/chat_run_claim.py | Snapshot is reconstructed at claim from message history |
| services/workflow/pipeline_execution.py | ASK and analysis share runner; follow-up branch may return question content rather than the analysis answer |
| services/workflow/chat_run_completion.py | Assistant message is the main persisted output; completion/trace/context/status are atomic |
| services/workflow/chat_run_locks.py; run_heartbeat.py; run_recovery.py | Lease fencing, lock order and interrupted-run behavior |
| services/chat/chat_run_retry.py | Retry is coupled to replaying saved message requests |
| services/case_analysis/state_selector.py | Canonical analysis selected from assistant messages |
| backend/app/models/report.py; services/reports/report_snapshot.py | Report source tied to analysis_message_id and message-based evidence |
| frontend/src/components/ChatWorkspace.tsx | Case views orchestrated through chat selection/messages |
| frontend/src/features/chat/runs/; hooks/use-case-queries.ts | Chat polling/session currently owns processing display |
| frontend/src/components/intake/; lib/case-overview.ts | Preview/import and Overview use current narrative/message contracts |

Inspect latest contents, AGENTS.md, CONTINUITY.md and git status/diff first. The checkout is materially dirty and migration 0005 is already applied locally; preserve earlier work. Dated test results in the ledger are not proof for this implementation.

## 4. Ownership and dependency rules

| Domain | Owns | May call/read |
| --- | --- | --- |
| Case | Identity, owner, evidence revision, latest successful analysis pointer | Domain repositories |
| Materials/Evidence | Documents, extraction revisions, admitted source revisions, immutable snapshots | Existing ingestion/provenance code |
| Analysis | Immutable validated case results and source references | Snapshot, existing analysis/follow-up engines |
| Workflow | CaseRun scheduling, leases, retries, completion transaction | Evidence reader, analysis engine, Chat writer |
| Chat | Transcript, ordinal allocation, user/assistant messages | Case context and workflow submission contracts |
| Clarification | Question lifecycle, answer linkage, origin result/snapshot | Evidence admission and Chat presentation |
| Reporting | Immutable report snapshot tied to analysis result | Analysis result and its exact evidence snapshot |

Case CRUD must not implement worker logic. Workflow coordinates services with one database transaction where required. Leaf writers accept the caller's session and must not commit independently. Analysis code must not require a ChatThread or fabricate ChatMessage objects to satisfy old types.

Suggested modules: services/case_materials/, services/case_evidence/, services/case_analysis/ (extend existing), services/workflow/, services/chat/, services/followup/ (extend existing), services/reports/ (extend existing). Split by responsibility; every new/modified code file must meet the 300-line rule. Keep provider entrypoints stable where feasible.

## 5. Proposed schema and invariants

Resolve exact column names and migration numbering against the current checkout at checkpoint A. The logical relations below are required; combining compatible revision records is acceptable if immutability and provenance remain explicit.

### 5.1 Case and Chat

- Case: id, owner, title, evidence_revision (monotonically increasing), latest_analysis_result_id nullable, timestamps. Processing state is derived from CaseRun, not overwritten by Chat status.
- Expose processing_status (idle/queued/running/failed), analysis freshness (missing/current/stale) and pending clarification separately. A run awaiting a human answer has finished; it holds no worker lease.
- ChatThread: unique Case relationship, next_message_ordinal and timestamps. Preserve existing IDs. CaseRead.chat_thread_id becomes nullable.
- Do not leave two writable processing-status columns. If an old API temporarily returns thread.status, derive it from Case state through a named response adapter, then remove it once consumers migrate.

### 5.2 Documents, extraction and evidence

- CaseDocument: case_id, original filename, MIME, byte size, content hash, bytes/storage reference, created_at, archived_at. Server resolves ownership for every access.
- DocumentExtraction revision: document_id, provider/config/version, raw extracted text, page/region/provenance metadata, warnings, created_at. Re-extraction creates a new row and never overwrites an admitted revision.
- EvidenceSource: case_id and source kind (reviewed_document, narrative, clarification_answer, explicit_chat_addition); optional original message/document/question references.
- EvidenceRevision: source_id, revision number, exact admitted text, exact provenance mapping, text hash, admission timestamp, selected extraction revision. Editing creates a new revision; archiving excludes it from future snapshots only.
- Unreviewed extraction is not admitted evidence. ASK, assistant analysis messages and external context never become EvidenceSource automatically.
- Sources created without Chat have native evidence IDs. Never invent message IDs or insert hidden user messages for documents.

### 5.3 Snapshot

- CaseEvidenceSnapshot: case_id, case evidence_revision, format_version, ordered immutable source-revision manifest, exact analysis input text, canonical hash and created_at.
- Store all data needed to reproduce the input without reading mutable current document state. Manifest includes stable source/revision IDs and provenance hashes, not just combined text.
- Snapshot identity/hash format is versioned and deterministically serialized. Distinguish text hash from manifest hash; unchanged text with changed provenance must not silently reuse a different source binding.
- Build/pin the snapshot within the enqueue transaction under Case lock. Never rebuild it at worker claim or retry from current materials.
- Exceeding input/admission limits must fail clearly or follow the existing explicit selection policy with omission receipts. Never silently truncate documents or source mappings.

### 5.4 Run and AnalysisResult

- CaseRun replaces ChatRun ownership: case_id, operation (analysis/ask), snapshot_id, optional request_message_id, optional context_analysis_result_id, idempotency key/fingerprint, pipeline config, status, attempt/lease fields, timestamps, receipts/errors.
- Analysis runs have no required request_message_id. ASK pins both a context result and its corresponding snapshot; it must not combine latest evidence with an older result without an explicit policy.
- Unique active-run constraint per case; unique case/idempotency key. Fingerprint includes operation, snapshot/revision, request parameters and pipeline config. Same key with different intent returns conflict; retry preserves the saved fingerprint/snapshot.
- CaseAnalysisResult: case_id, run_id UNIQUE, snapshot_id, result schema version, answer/summary, validated structured trace, optional technical context reference, pipeline/model metadata, created_at, immutable result status.
- Successful results are append-only. Failed attempts live in CaseRun/attempt receipts and do not replace latest_analysis_result_id. Keep historical outputs explicitly marked if their validity cannot be established.
- Latest pointer references a successful result belonging to that case. Enforce cross-case consistency in DB constraints where practical and in service validation in all cases.
- Currentness compares the result's snapshot with current admitted evidence revision. ASK completion never updates the latest analysis pointer.

### 5.5 Published messages and clarification

- ChatMessage adds nullable analysis_result_id and a typed message kind. Enforce one analysis publication per result with a partial unique index for kind=analysis_result.
- Store an immutable display copy of the answer plus result reference. Do not invoke an LLM to rewrite it for Chat. Canonical structured analysis remains in CaseAnalysisResult.
- PendingClarification: case_id, origin_analysis_result_id, origin snapshot, stable gap/question identity, question text/metadata, state, answer evidence reference, optional question/answer message IDs. Reuse existing follow-up semantics; this record supplies persistence independent of transcript.
- Answer admission is idempotent; one logical reply is admitted once regardless of Case UI or Chat entrypoint. A stale/superseded question must be explicitly rejected or refreshed, never silently applied to a different result.
- Follow-up decisions and chain reconstruction read durable clarification records for new results. Existing transcript history remains readable for historical records through a bounded migration adapter.

### 5.6 Reports and deletion

- New reports bind to analysis_result_id and that result's snapshot. analysis_message_id becomes optional legacy linkage, not the authority for new report admission.
- Preserve all existing report versions, UUIDs and frozen report payloads. Update joins/FKs after run migration, including RagContext.run_id.
- Do not cascade deletion of a chat message/thread into an analysis result, evidence snapshot, clarification or report. Case deletion is the aggregate delete boundary; document archive is non-destructive to historical snapshots.
- No standalone delete-chat action should imply deleting a Case. Audit existing compatibility DELETE /chats behavior and document/remove it before declaring this separation complete.

## 6. Required transaction flows

### 6.1 Add/review material

Authenticate -> save document -> run existing extraction -> persist untrusted extraction revision -> user reviews/adopts text -> admit EvidenceRevision -> increment Case.evidence_revision.

The database transaction must not remain open during OCR/LLM/network work. Persist extraction failures explicitly; never auto-admit partial results. Use current upload/type/size protections and per-case ownership. Extraction success does not automatically start analysis.

### 6.2 Analyze from Case

POST analysis request -> authenticate/lock Case -> check expected evidence_revision -> resolve idempotency -> enforce no active run -> build immutable snapshot -> insert queued CaseRun -> commit -> dispatch process_case_run(run_id).

No ChatThread or user message is needed here. Client retains the idempotency key across an uncertain network response. If dispatch is lost after commit, the saved queued run remains discoverable; preserve current expired-run recovery and explicit retry semantics rather than claiming a durable broker guarantee.

### 6.3 Worker execution and publication

1. Claim run with row locks/skip-locked and attempt lease fencing. Load the saved snapshot/config only.
2. Release DB transaction; invoke existing analysis and follow-up engines; persist attempt receipts using ownership checks.
3. On success, start one completion transaction, acquire required locks in the defined order, recheck run status/lease owner/attempt/expiry.
4. Insert AnalysisResult, optional technical context, and clarification records. Preserve the actual analysis answer even when a question is generated.
5. Ensure the single Case ChatThread exists. Under its lock allocate ordinals and insert analysis-result assistant message, followed by a separate follow-up-question message if needed.
6. Set latest successful result pointer, mark run completed, clear lease, commit everything together.

If any write fails, all completion writes roll back. A duplicate/stale completion publishes nothing. A result may finish against an old snapshot after a material edit; retain it and return stale=true. Do not hold locks across provider calls.

### 6.4 Ask and clarification

- ASK creates a genuine user ChatMessage and CaseRun atomically, pinned to the chosen latest successful result. Default proposal: permit questions about a stale result while displaying that context is older; never represent it as current evidence.
- ASK creates a Q&A assistant message, not a new CaseAnalysisResult or latest pointer.
- No completed analysis: return a clear precondition error asking the user to analyze from Case first; do not silently run analysis for an ordinary question.
- Clarification answer from Case or Chat admits one EvidenceRevision and pins a new analysis snapshot/run atomically when the user submits the answer for analysis.
- Chat questions, analysis publications and follow-up question text are never admitted evidence. Explicit add-info is a separate user intent.

### 6.5 Lock order and retry

- Adopt a documented common order for paths requiring multiple locks: Case -> ChatThread (when needed) -> CaseRun -> subordinate writes. Case lock serializes lazy thread creation. Find candidate IDs without locking, then acquire/revalidate in order.
- Use one helper/policy for enqueue, claim, completion, heartbeat, recovery, retry and deletion. Do not assume renaming existing helpers preserves order.
- Retry reuses the same logical run, snapshot/config and request; increment attempt at claim. New Analyze is a new run, even for identical evidence.
- Validate stale retry rules for intervening requests/evidence revisions: proposal is reject retry superseded by newer case work and require a new Analyze; do not silently repin the old run.
- Recovery must not overwrite a newer result or publish a stale worker's answer. Browser polling cancellation does not cancel a backend run.

## 7. API and frontend contract

Proposed endpoint names; finalize and lock OpenAPI contracts before UI implementation:

| Operation | Contract |
| --- | --- |
| Case identity | Existing /api/v1/cases CRUD, nullable chat thread |
| Documents | POST/GET /cases/{id}/documents; authenticated content access if needed |
| Extraction | POST /cases/{id}/documents/{document_id}/extractions; read extraction revision/status |
| Evidence admission | POST /cases/{id}/evidence; explicit revision creation/archive operations |
| Analyze | POST /cases/{id}/analyses with idempotency key and expected evidence revision -> 202 CaseRunRead |
| Latest overview | GET /cases/{id}/analysis -> latest successful result plus currentness; null result before first success |
| Run status/retry | GET /cases/{id}/runs/{run_id}; POST corresponding /retry |
| Clarification | GET /cases/{id}/clarifications; POST /{question_id}/answers |
| Optional conversation | Idempotent POST /cases/{id}/chat ensures thread; GET must not create data |
| Chat messages | Existing /chats/{thread_id}/messages for ASK, explicit add-info and linked clarification replies |
| Reports | Adapt existing report service to result/snapshot; expose Case-scoped access in the workspace |

All nested IDs must be checked against both case ownership and parent relation. Do not trust an uploaded snapshot, trace, result ID or admission flag without server validation.

Frontend requirements:

- Case workspace loads Case/materials/latest analysis independently of Chat. Remove the empty-messages gate that currently decides whether Overview can display analysis.
- Intake supports multiple saved documents, extraction/review status and explicit admission. Reuse existing preparation/preview components; no visual redesign needed.
- Analyze works with Chat never opened. A reload during execution restores run status from Case APIs.
- Overview uses latest AnalysisResult, with pending/failed run state separate from retained successful content. Show a small stale indicator when evidence changed; no history selector.
- Lazy Chat panel loads transcript and already-published analysis message. All automatic publications are genuine stored messages, not client-side duplicates.
- Keep one run polling controller and separate Case-result and Chat-message caches. On completion invalidate both safely; preserve selection/abort guards.
- Citation drawer resolves snapshot source revisions rather than depending on source_message_id. Old messages/results use their declared historical source format.
- Report action targets the displayed result explicitly; stale result exports must disclose the snapshot and not mix newer evidence.

## 8. Migration and source-reference strategy: highest-risk checkpoint

Do not rewrite applied migrations 0001-0005. Create new additive migrations against the actual current head; prefer schema expansion -> validated backfill -> application cutover -> constraint tightening/legacy removal.

1. Inventory actual tables, counts, foreign keys, active runs, stored trace versions and source-reference formats. Test on a disposable populated database restored from an appropriate fixture/backup.
2. Add evidence, snapshot, result and clarification tables and nullable linkage columns; preserve original message/report rows.
3. For legacy evidence, preserve exact source text/order and only established evidence roles. Do not classify first-ever ASK as evidence just because of ordinal. Persist migration provenance and source_message_id only where real.
4. Backfill legacy results only when the actual generating run, trigger boundary and evidence hash can be established. Never compute a historical snapshot using today's complete transcript.
5. If a result/run association or source snapshot cannot be proved, preserve original data as legacy_unbound with explicit status. Do not publish it as a validated new result or fabricate IDs. Report counts and examples for review before tightening constraints.
6. Existing assistant analysis messages get result links when established; do not republish duplicates during migration. Some old follow-up messages contain trace data but question content: recover the answer only from a proven stored field, never from generation/guessing.
7. New source references use a typed native evidence ID/revision. Inspect contracts, validators, prompts, trace serializers, citations, gap/follow-up, reports and frontend generated types. If v3 requires source_message_ids semantically, introduce an explicit new trace/transport version and keep historical v3 readers. Never put evidence UUIDs in a field claiming they are message IDs.
8. Provider input adapters carry native evidence references; analysis semantics and exact quote binding remain unchanged. Contract migration is part of this task and must be independently tested.
9. Historical report payloads remain frozen. New report generation reads result.snapshot, not latest message history. Validate null technical context still works.
10. Before cutover stop intake of new jobs and drain workers. Take a backup, migrate, deploy matching backend/frontend, then smoke-test. No old worker process may write the new schema.
11. Rollback: restore matching application and database backup during the maintenance window. After new data is written, prefer forward repair; a destructive downgrade is not an acceptable automatic rollback.

## 9. Checkpoint implementation order

| Checkpoint | Deliverables | Exit gate |
| --- | --- | --- |
| A: audit/contracts | Baseline diff inventory; schema, state and source-reference ADR; endpoint/type inventory; fixture strategy | Every confirmed requirement mapped; no undecided ownership or fake message ID shortcut |
| B: materials/snapshots | Persist documents/extractions/admitted revisions; immutable snapshot builder; no Chat dependency | Multiple documents, edits, archive, hashes, ownership and provenance tests pass |
| C: workflow/results | CaseRun, request-message optional, pinned snapshots, result repository, lease/retry/recovery | Analysis with zero thread/messages succeeds; PostgreSQL race tests pass |
| D: Chat publication/follow-up | Atomic result/message publication, lazy thread, explicit clarification state and replies, ASK context | Exactly one publication; question never replaces answer; replies work from Case and Chat |
| E: readers/UI/reports | Native-source citations; Overview independent of messages; Case polling; report result binding | Reload, stale/failure display, citations, transcript and report integration pass |
| F: migration/cutover | Proven backfill, legacy readers, obsolete callers removed, docs updated, coordinated runtime build | Populated migration audit and end-to-end synthetic smoke pass |

Stages are dependency checkpoints, not separate deployable releases unless a temporary compatibility boundary has explicit tests. Do not deploy after B/C while the frontend still relies on old thread state.

At each checkpoint Luna must report changed modules, actual tests, remaining invariants and unresolved failures. If a gate fails, fix within that checkpoint before broadening changes. Keep mechanical renames separate from behavior changes in reviewable diffs; no automatic staging/commit/push unless requested.

## 10. Mandatory acceptance scenarios

| ID | Scenario | Required assertion |
| --- | --- | --- |
| T01 | Create Case, upload/admit two documents, Analyze without Chat | No synthetic user messages; correct snapshot sources; completed result |
| T02 | Open Chat after T01 | One persisted assistant analysis message with exact result link/content |
| T03 | Generate clarification during analysis | Analysis message plus separate question; both linked correctly |
| T04 | Repeat submit with same idempotency key | One logical run; conflicting payload returns conflict |
| T05 | Two workers complete same run / expired worker returns | One result/publication; stale worker writes nothing |
| T06 | Inject failure between result and message inserts | Whole completion transaction rolls back; recoverable run state |
| T07 | Edit/admit document while run executes | Result uses old snapshot, freshness stale, historical bytes unchanged |
| T08 | Second analysis succeeds; third fails | Both successes preserved; latest remains second; third failure visible separately |
| T09 | Ask after analysis | No new evidence/result pointer; answer pinned to explicit result context |
| T10 | First Chat message is ASK | Never classified as initial case narrative; no analysis -> explicit precondition error |
| T11 | Submit same clarification answer from both UIs | One admission/run; correct question linkage; stale question rejected |
| T12 | Retry interrupted run after newer work | Reject superseded retry; no message duplication or snapshot repinning |
| T13 | Archive document / remove conversation | Past snapshots/results/reports survive; Case delete remains explicit aggregate operation |
| T14 | Cross-case nested document/run/result/question IDs | Authorization failure and zero writes/data leakage |
| T15 | Reload/switch Case during polling | Correct persisted progress; late response cannot overwrite another case |
| T16 | Historical fixture migration | IDs/counts/FKs/hashes preserved; unresolved legacy records reported, not invented |
| T17 | Exact quote repeated across documents; edited OCR text | Resolve by declared source/revision; ambiguous page binding fails closed |
| T18 | Report after new evidence or failed run | Uses selected successful result's snapshot only; optional MITRE remains optional |
| T19 | Lazy thread creation races with user opening Chat | Single thread and unique ordered messages |
| T20 | Queued job dispatch lost / process restarted | Saved run recoverable under declared policy; no false success |

Use real disposable PostgreSQL for constraints, locking, migration and atomicity tests. SQLite/mocks cannot certify these. Use fake providers for deterministic pipeline tests and only synthetic material for optional real-provider smoke. No paid calls without existing task authorization.

Then run backend regressions, frontend tests, generated OpenAPI/type drift, TypeScript, scoped lint, build and diff checks. Existing unrelated lint failures must be recorded separately, not silently fixed or reported as passing. UI smoke must exercise the actual Case-first path with Chat closed, not only an HTTP 200 route shell.

## 11. Complexity, risk and estimates

Planning estimate, not measured implementation time: high complexity, 5/5. This is a persistence/domain refactor, substantially larger than worker renaming. Budget roughly 8-15 focused engineer-days including review, migration rehearsal and integration testing; legacy backfill/source-schema surprises can extend this. Tentative footprint 60-100 production/test/generated files; checkpoint A must replace this range with a concrete inventory.

| Risk | Likelihood / impact | Prevention / release gate |
| --- | --- | --- |
| Evidence IDs stuffed into message-ID fields | High / critical | Typed versioned source schema; T01/T10/T17 |
| Historical snapshots fabricated from latest data | High / critical | Proven run boundary/hash; explicit legacy_unbound; T16 |
| Result overwritten or points at wrong snapshot | Medium / critical | Append-only rows, snapshot FK, pinned config; T07/T08 |
| Follow-up question replaces analysis output | High / high | Separate result/analysis message/question contracts; T03 |
| Duplicate result/message after retries | High / high | DB unique indexes and lease fencing; T04/T05/T06 |
| Chat removal cascades into case history | Medium / critical | Audit all FKs/deletes; T13 |
| Locks deadlock or leave partial state | Medium / critical | One documented lock order and transaction owner; PostgreSQL tests |
| Report mixes current material with old result | High / high | Read only result snapshot; T18 |
| UI still infers analysis from message count | High / high | Independent Case reads; T01/T02/T15 |
| Multi-document input silently truncated | Medium / high | Explicit budgets/omission receipts and input tests |
| DB file storage causes growth/backup pressure | Medium / high | Bounded uploads, no base64 in JSON, capacity/backup measurement |
| Broad rewrite changes research pipeline behavior | Medium / high | Keep provider semantics; compare golden fixtures and receipts |
| Optional Chat becomes a mandatory follow-up gate | Medium / high | Case-page clarification path; T11 |
| Dirty checkout changes overwritten | Medium / high | Baseline inventory and scoped diffs at each checkpoint |

The highest-risk review checkpoints are B (source/provenance schema), C/D (transactions and publication) and F (legacy migration). Review those independently before runtime cutover. Passing a large unit suite does not replace migration and race tests.

## 12. Luna execution instructions

Read this document, AGENTS.md, CONTINUITY.md and the linked current code. Treat confirmed user requirements as authoritative over older scope exclusions. Begin at checkpoint A. Use existing modules/libraries; keep code modular below 300 lines; avoid empty catches, silent fallbacks and source fabrication.

Do not implement a frontend analysis-history browser, generic event sourcing, new queue platform, separate RAG service changes, OCR model changes, automatic fact admission from Q&A, or an assistant-written consolidation promoted to evidence.

The consolidated representation is the versioned AnalysisResult derived from an evidence snapshot. Source revisions/snapshots preserve evidence; model-produced claims/results remain derived analysis. Do not feed prior summaries back as authoritative source material.

Update root route-boundary documentation, CURRENT_PROJECT_DIRECTION.md's implementation-status sections and CONTINUITY.md when implementation actually changes these facts. Preserve old dated receipts as historical. Regenerate API types and symbol index after final code changes.

If a required legacy mapping cannot be verified, stop migration promotion of those records and report the exact blocker. Do not delete them, weaken validation or make an LLM reconstruct history. Continue independent implementation/tests that do not depend on that mapping.

Final handoff must include checkpoint status, exact migration head and mapping counts, real pass/skip/fail test results, evidence of Case-only analysis and automatic Chat publication, known limitations, and whether Docker was actually rebuilt. Do not report this plan as implemented.
