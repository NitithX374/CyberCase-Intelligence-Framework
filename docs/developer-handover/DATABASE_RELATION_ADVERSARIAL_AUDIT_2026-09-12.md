# Database relationship and ownership audit

2026-09-12. Target: `gemini/canonical-dev-cleanup`, HEAD and remote both `d73a62fb133a757fb8a604dcf6bab9f47138903c`. Clean initial worktree. This supersedes the ownership audit at 9325e40. Proposal only; no application or migration implementation.

## Verdict

The 13-table model is sufficient. Deriving ASK context through its request message is valid only after all message writers persist the historical analysis FK and request-message deletion is protected. Today ASK user/assistant messages and follow-up answers omit that FK. Their metadata currently compensates for the missing relation.

Use one cascade ownership path per entity and ordinary, non-deferrable NO ACTION for retained references. Remove manual child deletion from the Case service after validating the complete proposed graph. No standalone Clarification or Gap table is needed.

## A/E. Every current FK and proposed policy

Current actions below are verified in ORM, baseline and running PostgreSQL public catalog. Nullable values are from ORM/baseline. Targets use id unless explicitly stated. Types: O=OWNS (target owns source), S=SCOPES, R=REQUIRED REFERENCE when populated, P=OPTIONAL REFERENCE whose target may disappear. Nullable does not necessarily imply disposable reference.

| Source column | Target | Nullable | Current | Type / runtime purpose | Proposed |
| --- | --- | --- | --- | --- | --- |
| cases.user_id | users.id | yes | SET NULL | P: account association, current DB retains Case | SET NULL |
| cases.latest_analysis_result_id | case_analysis_results.id | yes | SET NULL | P: current-result pointer | SET NULL |
| chat_threads.case_id | cases.id | no | CASCADE | O: conversation lifecycle | CASCADE |
| chat_messages.thread_id | chat_threads.id | no | CASCADE | O: message history | CASCADE |
| chat_messages.analysis_result_id | case_analysis_results.id | yes | SET NULL | R: historical analytical context; may be absent before analysis | NO ACTION |
| chat_messages.in_reply_to_message_id | chat_messages.id | yes | SET NULL | R: exact answered question | NO ACTION |
| case_documents.case_id | cases.id | no | CASCADE | O: original material | CASCADE |
| document_extractions.document_id | case_documents.id | no | CASCADE | O: extraction revision, request-scoped processing | CASCADE |
| case_evidence_sources.case_id | cases.id | no | CASCADE | O: admitted evidence source | CASCADE |
| case_evidence_sources.document_id | case_documents.id | yes | SET NULL | P: optional document origin; evidence text retained | SET NULL |
| case_evidence_sources.origin_message_id | chat_messages.id | yes | SET NULL | P: optional conversational origin | SET NULL |
| case_evidence_revisions.source_id | case_evidence_sources.id | no | CASCADE | O: admitted revisions | CASCADE |
| case_evidence_revisions.extraction_id | document_extractions.id | yes | SET NULL | P: extraction origin; exact admitted text retained | SET NULL |
| case_evidence_snapshots.case_id | cases.id | no | CASCADE | O: immutable Case input | CASCADE |
| case_runs.case_id | cases.id | no | CASCADE | O: execution history | CASCADE |
| case_runs.snapshot_id | case_evidence_snapshots.id | no | RESTRICT | R: pinned execution input | NO ACTION |
| case_runs.request_message_id | chat_messages.id | yes | SET NULL | R: request; mandatory for ASK, optional for analysis | NO ACTION |
| case_runs.context_analysis_result_id | case_analysis_results.id | yes | RESTRICT | R: current ASK context source | REMOVE |
| case_analysis_results.case_id | cases.id | no | CASCADE | S: direct Case query/filter | NO ACTION |
| case_analysis_results.run_id | case_runs.id | no | CASCADE | O: producing analysis Run, UNIQUE | CASCADE |
| case_analysis_results.snapshot_id | case_evidence_snapshots.id | no | RESTRICT | R: result evidence binding | NO ACTION |
| case_analysis_results.retrieval_context_id | rag_contexts.retrieval_context_id | yes | RESTRICT | R: optional augmentation, retained once bound | NO ACTION |
| rag_contexts.case_id | cases.id | no | CASCADE | S: direct Case query/filter | NO ACTION |
| rag_contexts.case_run_id | case_runs.id | no | CASCADE | O: producing Run, UNIQUE | CASCADE |
| rag_contexts.evidence_snapshot_id | case_evidence_snapshots.id | no | RESTRICT | R: retrieval input provenance | NO ACTION |
| case_reports.case_id | cases.id | no | CASCADE | O: report history, no durable report job | CASCADE |
| case_reports.analysis_result_id | case_analysis_results.id | no | RESTRICT | R: report source | NO ACTION |
| case_reports.evidence_snapshot_id | case_evidence_snapshots.id | no | RESTRICT | R: frozen report evidence | NO ACTION |
| case_reports.retrieval_context_id | rag_contexts.retrieval_context_id | yes | RESTRICT | R: retained augmentation source | NO ACTION |

All proposed NO ACTION constraints are NOT DEFERRABLE. They reject deleting a referenced target while its consumer survives, but permit a single parent DELETE whose cascading effects remove both. SET NULL remains only for references where loss is legitimate. Stronger original-document retention would be a separate policy change.

User is deliberately an account association rather than Case's lifecycle owner under current SET NULL semantics. `User.cases` nevertheless uses delete-orphan: ORM account deletion differs from SQL account deletion. Recommendation: preserve DB retention behavior and remove ORM delete/delete-orphan, passive_deletes='all'. If account deletion must destroy Cases, explicitly choose that alternative policy; do not silently infer it from a tree drawing.

## B/D. Canonical ownership matrix and final model

The owner/children columns define the complete ownership graph; the FK table defines its cross references. Each row has one immediate lifecycle owner.

| Table | Lifecycle owner | Case scope | Owned children | Required references when present | Disposable optional references |
| --- | --- | --- | --- | --- | --- |
| users | root | none | none under retained-Case policy | none | none |
| cases | workspace root | self | threads, documents, sources, snapshots, runs, reports | none | user, latest result |
| chat_threads | Case | direct | messages | none | none |
| chat_messages | Thread | via Thread | none | analytical result, reply question | none |
| case_documents | Case | direct | extractions | none | none |
| document_extractions | Document | via Document | none | none | none |
| case_evidence_sources | Case | direct | revisions | none | document, origin message |
| case_evidence_revisions | EvidenceSource | via Source | none | none | extraction |
| case_evidence_snapshots | Case | direct | none | none | none |
| case_runs | Case | direct | result, retrieval context | snapshot, request message | none |
| rag_contexts | Run | direct scope + via Run | none | snapshot | none |
| case_analysis_results | Run | direct scope + via Run | none | snapshot, retrieval context | none |
| case_reports | Case | direct | none | result, snapshot, retrieval context | none |

Cardinality: Case->Thread 0..1; Thread->Messages many; Document->Extractions many; Source->Revisions many; Case->Snapshots/Runs/Reports many; Run->Result 0..1 and Run->RagContext 0..1. Keep the existing one-active-Run-per-Case constraint.

Scope FKs do not guarantee scope consistency with the owner FK. Validate result.case_id == run.case_id; context.case_id == run.case_id; all snapshots and message threads belong to that Case; report references bind the selected result's snapshot/context. Existing independent FKs permit contradictory pairs. Add negative writer tests and migration preflight queries. Composite scope constraints can strengthen this later but are not required merely to resolve deletion timing.

## C. ASK identity and historical binding

Actual path:

- `services/chat/caseChat.py:createCaseAsk`: selects latest validated result under Case lock; creates user message with context ID in metadata, NOT analysis_result_id; duplicates context ID in request_payload and Run FK. Snapshot ID is also copied into payload and metadata.
- `services/chat/caseAnswer.py:loadCaseAnswerContext`: loads Run.context_analysis_result_id; checks Case/snapshot/trace; filters previous conversation using metadata context ID. It also incorrectly requires message.thread_id == run.case_id, instead of joining Thread.case_id. Distinct Thread and Case UUIDs break this path.
- `services/workflow/caseAskCompletion.py:completeCaseAsk`: reloads Run context FK and writes assistant context metadata, NOT the historical FK.
- `caseRunService.py:case_run_fingerprint_matches`: ASK hash verifies saved payload/snapshot/config; it does not independently compare the Run context FK with the payload context ID. Thus duplicated values are not even one enforced identity.
- Retry uses the original Run/payload and rejects stale evidence/newer work. Preserve these current retry admission rules; removing duplication does not authorize relaxing them.

Proposed authority: message.analysis_result_id. At ASK enqueue assign A1 to the user message; derive context through Run.request_message_id; at completion assign the SAME A1 to the assistant message, never current Case.latest. At follow-up-answer enqueue copy the question's bound result A1; subsequent analysis may set latest=A2 without rebinding either message. Pre-analysis messages remain NULL.

Remove Run.context_analysis_result_id, metadata.context_analysis_result_id and payload.context_analysis_result_id. Also remove payload.context_snapshot_id where redundant with Run.snapshot_id. Recompute a versioned fingerprint from immutable message content, its analysis_result_id, request intent/language, pinned snapshot and pipeline config. Persist the HASH and fingerprint format version; the context scalar can be derived for validation and need not be duplicated. Request idempotency lookup must resolve the original request before looking at latest analysis. Failed attempts must reject altered message content or analytical binding.

This design requires protecting request-message lifetime: SET NULL would discard the only context path. Proposed NO ACTION blocks independent deletion of a referenced request/Thread; whole Case deletion removes both Run and messages. `chatService.deleteThread` currently permits deletion independent from Case. Return a clear conflict for referenced conversation history, or choose a separate archival UX later. If independent destructive Chat deletion must preserve executable ASK history, the proposed simplification is NOT sufficient; an independent immutable execution context would be required. Do not both remove it and keep SET NULL.

An answer receipt may retain call hashes, history message IDs, costs and generated claim references as an execution record. Eliminate its duplicated context scalar if no export contract needs it; ephemeral model-call context IDs are not redundant database relations. Do not mistake request language/config/content used for reproducibility for duplicate domain outputs.

## Main-analysis isolation

`caseRunService.enqueue_case_analysis` writes operation=analysis and context_analysis_result_id=None. `caseRunExecution._execute_claimed_work` invokes the main analysis with claimed input_text, snapshot registry, pipeline config, question=None. Only operation=ask invokes loadCaseAnswerContext. Prior follow-up exchanges are loaded for subsequent follow-up selection/history, not supplied as previous result facts to main analysis. No path inspected feeds a prior AnalysisResult summary/claims into normal main-analysis generation. Add a sentinel regression proving this separately from follow-up policy behavior.

## Follow-up and gap duplication

CaseClarification ORM/table are gone. Legacy names remain in `schemas/caseClarifications.py`, `schemas/chat.py`, `schemas/caseRuns.py`, `services/followup/caseClarification.py`, `caseChat.py`, Run payload/fingerprints and tests. `create_pending_clarification` and `supersede_prior_clarifications` are no-op compatibility functions. Canonical runtime intent/kind should be followup_answer; remove clarification_answer aliases and clarification_id where they duplicate a question message ID. No entity should be restored.

Keep in_reply_to_message_id. A single CURRENT pending question cannot identify which OLD question an idempotent replay answered. Current code queries answers by self-FK, reconstructs histories through it and computes pending status from unanswered questions. It also accepts any same-result question found by ID; no database single-pending-question constraint exists, and supersede is a no-op. The claimed invariant is not a sufficient replacement for the historical link. Validate same-thread, assistant question/user answer roles, supersession and one accepted answer under the Case lock. Historical NULL-link inference should be removed for disposable data.

Actual newly persisted question metadata comes from `caseRunCompletion.build_followup_message_metadata`: selected_gap_detail, kind=clarification, action=ask_followup, duplicated result/snapshot/question IDs and gap_key. It does not copy the entire gap_analysis field in that function; the full gap_analysis structure exists in followup metadata/policy schemas and other processing paths. Distinguish transient policy input from persisted copies.

Use question.analysis_result_id + metadata.gap_id to resolve trace.gaps[]. Retain reason_code, round and policy version if actually needed. Preserve exact question content. Remove selected_gap_detail, duplicated analysis_result_id/clarification_id/in_reply_to_message_id, and kind/action fields inferable from message_kind. Update policy readers and frontend API serialization adapters together; frontend redesign is unnecessary, but silently deleting fields still read by existing clients is not a complete change. Evidence provenance copies that make immutable snapshots self-contained are a separate concern, not automatically redundant metadata.

Additional failure: existing-answer replay falls back to latest CaseRun if the request-linked Run is missing (`submit_clarification_answer`). Remove that fallback; it can return/requeue unrelated work. Also its existing-answer fingerprint is rebuilt without the original response_language; preserve request identity through the Run fingerprint rather than fabricated defaults.

## F. Case deletion execution and ORM

Current `CaseService.deleteCase` performs manual ordered DELETE/UPDATE statements, then a parent DELETE; it does not demonstrate database aggregate ownership. Most owner collections use cascade='all, delete-orphan', passive_deletes=True. Loaded children may still be deleted by SQLAlchemy. Case.analysis_results/rag_contexts no longer have delete-orphan, but passive_deletes=True can still null loaded children on ORM parent deletion. User.cases has the inconsistent ORM cascade described above.

Proposed service: authorize and lock Case using a minimal query, issue only `DELETE FROM cases WHERE id=:id`, commit. Database cascades Case->Thread->Messages, Document->Extractions, Source->Revisions, Snapshots, Runs->Results/Contexts, Reports. Non-deferrable NO ACTION checks protect any consumer still remaining after that statement. Scope FKs use NO ACTION so Runs remain the unique artifact lifecycle owners. A second Case's invalid reference must block deletion, not cascade into that Case.

Align ownership relationships to DB-controlled deletion: remove ORM delete/delete-orphan and set passive_deletes='all' for owner collections where parent deletion must emit no child DML; same for Case scope collections, preferably read-only navigation if unnecessary for writes. Keep explicit creation via db.add and immutable owner FKs. Do not combine passive_deletes='all' with delete-orphan. Test loaded/unloaded ORM parent deletion as well as direct service SQL. Cross-reference relationships must not propagate delete cascades.

No DEFERRABLE constraint is proposed. A PostgreSQL temporary-table experiment on this host verified a parent cascade removing both an artifact and its NO ACTION consumer in one statement (remaining counts 0/0, ROLLBACK). This proves the mechanism, not the full proposed product graph; populated migration tests remain an approval gate.

## G. Exact minimal change plan, after approval

1. Remove only CaseRun.context_analysis_result_id and its FK/relationship. Keep run.snapshot_id, artifact/report provenance references and message self-FK. Keep scope columns.
2. Change actions exactly as A/E: seven retained RESTRICT references to NO ACTION; two artifact scope CASCADE FKs to NO ACTION; three historical/input SET NULL references to NO ACTION. Drop the redundant Run context FK. Keep other actions unchanged.
3. Apply DB-owned ORM policy from F, including User retention parity. Preserve one-to-one uniqueness for Run artifacts.
4. Modify createCaseAsk, loadCaseAnswerContext, completeCaseAsk, follow-up answer creation, history filters, Run serializers/fingerprint validation and deleteCase. Fix Thread UUID validation. Preserve ASK claim-based generation and main-analysis isolation.
5. Remove duplicated IDs and gap detail payloads listed in C/follow-up section; update serializers and existing clients' transport adapters without UI redesign. Keep useful execution receipts.
6. Use a successor Alembic revision for an applied database. Inventory/reconcile historical ASK bindings before dropping the FK: compare Run/payload/metadata, bind request/assistant messages only where unambiguous; fail preflight on conflicting identities. If disposable data reset is chosen, make it an explicit implementation operation, not an implicit migration fallback. Version/recompute fingerprints deliberately. Do not rewrite an applied baseline to pretend existing databases migrated.
7. Tests: realistic graph with ASK Run and report.retrieval_context_id; one SQL parent delete; loaded/unloaded ORM paths; survivor Case assertions; individual required-target deletion blocked; optional pointers SET NULL; baseline->successor upgrade parity for every FK; A1/A2 message history; ASK derive/retry/idempotency with distinct Thread UUIDs; main-analysis sentinel; follow-up replay/supersession; stale retrieval attempt fencing.

## Verification and limits

- Live FK catalog: all 29 FK targets/actions match current ORM and inspected baseline. No claim of complete column/index/type parity from this check.
- Existing schema/deletion/parity tests: `env_mitre/Scripts/python.exe -m pytest backend/tests/test_database_schema.py backend/tests/test_case_aggregate_deletion_postgres.py backend/tests/test_database_schema_parity_alembic.py -q` -> 8 passed, 4 skipped (test DB URL unavailable to this invocation).
- Deletion fixture omits ASK Run and report.retrieval_context_id, uses Case UUID as Thread UUID, and lacks loaded-ORM deletion coverage. Service pass would certify manual deletion, not one-parent deletion.
- Existing parity test checks column presence/nullability and selected FKs/uniques; it is not exhaustive schema-drift certification.
- Retrieval retry reuse is now implemented (unlike the older audit), but early persistence still lacks attempt/lease fencing and checks run ID OR retrieval ID without proving ownership of a matched row. Keep this as a focused execution-provenance fix.
- No application changes, new tables, migration, deployment, commit or push in this audit.
