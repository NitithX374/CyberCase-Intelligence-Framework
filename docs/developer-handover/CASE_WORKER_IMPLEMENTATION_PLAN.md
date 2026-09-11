# Case-owned worker and chat interaction implementation plan

2026-09-10 [USER] SUPERSEDED by [CASE_FIRST_LUNA_IMPLEMENTATION_PLAN.md](CASE_FIRST_LUNA_IMPLEMENTATION_PLAN.md): Case-only document analysis, database history and automatic assistant result publication require independent evidence/result persistence. Do not implement this older plan as the current target.

2026-09-10 [USER] Draft only: Case owns worker/run management; Chat owns message submission and follow-up conversation.

2026-09-10 [CODE] Based on the current dirty checkout. This document proposes changes; no application implementation or database migration is performed by this planning task.

## Target ownership

| Responsibility | Owner |
| --- | --- |
| Run creation, idempotency, active-run exclusion, dispatch, lease, completion, failure, retry and recovery | Case workflow |
| Message content, ordering, transcript, follow-up question/answer linkage | Chat |
| Evidence admission and snapshot assembled from submitted source messages | Case evidence service, reading Chat through an explicit adapter |
| Analysis, gap evaluation, decision to request clarification | Existing analysis/follow-up services invoked by Case workflow |
| Display and persistence of generated answers and follow-up questions | Chat message writer invoked inside workflow transaction |
| Provider prompts, exact source binding, analysis selection policy | Existing analysis implementation |

Case remains related to one ChatThread. Shared UUIDs remain valid, but new contracts carry explicit case_id and request_message_id and resolve the related thread rather than deriving ownership from UUID equality.

## Current coupling confirmed in source

- `backend/app/services/chat/chat_run_creation.py`: message insert, run insert, idempotency, active-run check, follow-up linkage and thread status changes share one transaction.
- `backend/app/services/workflow/pipeline.py` and `pipeline_execution.py`: process_chat_run selects ASK or fresh analysis and invokes ChatRunWorker.
- `chat_run_claim.py`: reads ordered ChatMessage history through the triggering message ordinal, builds the evidence snapshot and reconstructs clarification history.
- `chat_run_completion.py`: stores assistant message, trace, retrieval context and terminal run/thread status atomically.
- `chat_run_locks.py`, `run_heartbeat.py`, `run_recovery.py`, and `chat/chat_run_retry.py`: locks and recovery are thread/run scoped. Expired runs are marked failed for explicit retry, not automatically re-executed.
- `backend/app/services/cases/case_management.py`: CaseRead.status and updated_at currently come from ChatThread.
- `frontend/src/features/chat/runs/chat-polling.ts`: polls thread status and reads getChatRun; stopping browser polling does not cancel backend execution.

## Proposed contracts and storage

1. Rename the ORM model ChatRun to CaseRun and physical table chat_runs to case_runs using a new migration after 0005. Preserve every run UUID, request payload, attempt, receipt, timestamp and source reference.
2. Add/backfill case_id as a non-null FK to cases. Replace run ownership by thread_id with case_id; retain request_message_id as provenance/trigger linkage to ChatMessage. Validate that the message's thread belongs to the same Case before enqueue/claim. Inspect and update dependent FK names, ORM joins and indexes, including RagContext and report-related readers.
3. Move the existing workflow status to Case.processing_status, preserving current values for this cutover. CaseRun.status remains queued/running/completed/failed. awaiting_followup is a Case processing outcome even though the question is presented in Chat.
4. Keep ChatThread.next_message_ordinal in Chat. Remove thread workflow status as a writable authority; any retained Chat API status field is a read projection from Case. Case status/updated_at serialization and ordering must use Case consistently.
5. Enforce one queued/running run per case with a partial unique index and case-scoped idempotency uniqueness. Keep the current request fingerprint algorithm stable during migration.
6. Introduce CaseRunRead and ClaimedCaseRun with explicit ownership. ChatMessageAccepted returns the saved message plus CaseRunRead, so message acceptance remains one client operation.

## Implementation sequence

### A. Contracts and invariant tests

- Define CaseRunRead, ClaimedCaseRun, CaseRunCommand and a typed outcome. The command includes case identity, saved trigger message, existing action, evidence boundary and pinned analysis configuration.
- Define a Chat writer that accepts the caller's AsyncSession and never commits independently. Define an evidence/chat-history reader bounded by the trigger message ordinal.
- Specify ownership checks, status projections and retry behavior before mechanical renames.

### B. Database migration and model ownership

- Add a new migration; do not rewrite the already-applied 0005 migration.
- Backfill Case processing state from its thread, rename run storage, backfill case ownership and update constraints/relationships.
- Preflight detects missing Case/thread/message links and conflicting active runs; fail explicitly on invalid data.
- Preserve historical report, trace and retrieval IDs. Audit delete cascades in both Case and legacy Chat delete paths.
- Deploy backend/schema/frontend as a coordinated cutover after active workers finish. Take a database backup and verify restore instructions. Do not run old and new workers together against the migrated schema.

### C. Case workflow services

- Move worker contracts/store, claim, locks, completion/failure and retry into `backend/app/services/cases/runs/`, using small modules below 300 lines.
- Keep the existing `services/workflow/` pipeline assembly location; expose process_case_run and use CaseRunWorker. Update all callers, logging and error consumers without retaining unused Python aliases.
- Case run creation owns active-run/idempotency checks. Chat submission calls it with the shared transaction after preparing the source message.
- Use a consistent lock order whenever multiple locks are needed: Case -> ChatThread -> CaseRun. Claims can read candidate IDs first, then acquire/recheck in this order; preserve skip-locked behavior and lease fencing.
- Case completion calls the Chat writer and commits message, trace/context, Case status and CaseRun terminal status together. An expired worker cannot publish an answer.
- Recovery continues to mark interrupted work failed for explicit retry. Retry preserves the existing run/message IDs and rejects requests superseded by newer messages or another active case run.

### D. Chat and follow-up integration

- Chat owns message validation, ordinal assignment, question/answer linkage and transcript persistence.
- Split the current create_message_and_run implementation into Chat preparation and Case enqueue operations within one outer transaction. Dispatch only after commit, using the existing background-task mechanism.
- Keep gap reasoning and follow-up policy in their current services. The Case pipeline invokes them and passes the resulting question to Chat for persistence.
- A clarification answer references the originating question/run; Case builds the admitted evidence snapshot and schedules fresh analysis under the existing action semantics.
- ASK remains a CaseRun operation triggered by Chat, sharing case-level execution exclusion. ASK and assistant/RAG content must not become incident evidence.
- Move evidence projection/configuration ownership out of the Chat service package where appropriate, without introducing document tables or a new analysis-representation store.

### E. API and frontend cutover

- Keep POST `/api/v1/chats/{thread_id}/messages` for initial material, ASK, add-info and follow-up replies.
- Add GET `/api/v1/cases/{case_id}/runs/{run_id}` and POST `/api/v1/cases/{case_id}/runs/{run_id}/retry` with Case ownership validation. Retry reuses the saved request rather than inserting another chat message.
- Migrate frontend run polling/retry to the Case client and CaseRunRead. Keep composer, transcript and clarification UI in Chat.
- Use one polling controller with both identities. Refresh Case status and Chat detail after settlement, with selection/abort guards so an old response cannot update another case.
- Update generated API types, tests, handover references and the root route-boundary documentation.
- After all in-repo callers are migrated, remove the old chat-run read route and unused internal ChatRun exports. Verify any external consumers before removing a public route; no automatic compatibility alias is proposed.

### F. Verification and local deployment

- PostgreSQL migration fixture from the old schema: counts, UUIDs, payloads, FKs, status, report/retrieval references and cascade behavior.
- Concurrent same-key submissions yield one message/run; different active submissions are rejected per Case; unauthorized case/run/message combinations fail.
- Lease expiry, heartbeat loss, competing workers, retry after newer messages and deletion during execution produce no duplicate answers, orphan records or partial completion.
- Failure injected between message insertion and run insertion rolls back both. Failure during completion rolls back answer and terminal status together.
- Follow-up question -> reply -> next result retains question/run linkage, source IDs, evidence hash semantics and pinned pipeline configuration.
- ASK preserves evidence exclusion and the latest canonical overview. Existing report read/generation behavior remains valid after run model migration.
- Frontend: submit, follow-up, reload during processing, interrupted retry, case switching and deletion with a late polling response.
- Run focused PostgreSQL/API tests, then backend/frontend regressions, generated API-type check, TypeScript, scoped lint and production build. Record skipped tests explicitly.
- Rebuild application services and verify migration head, Case CRUD, message acceptance, run polling, follow-up and report access. Use synthetic material for smoke tests.

## Complexity and risk estimate

2026-09-10 [ASSUMPTION] Medium-high overall complexity (4/5). Roughly 30-50 backend files and 10-20 frontend/schema/test files may be affected; these are planning ranges, not a counted patch inventory. Estimated 4-6 focused engineer-days including migration, concurrency tests and review, assuming the current dirty baseline is stable. A naming-only change would not satisfy the ownership requirement.

| Area | Complexity | Main risk | Mitigation |
| --- | --- | --- | --- |
| Worker/module rename | Low-medium | Missed imports/error consumers | Trace all callers, remove unused exports, static checks |
| Model/schema and historical references | High | Broken FKs, cascades or data links | New migration, preserved UUIDs, populated PostgreSQL fixture |
| Locks, completion and retry | High | Deadlock, duplicate reply, partial write | Uniform lock order, one transaction, lease fencing, race tests |
| Case vs Chat status | Medium-high | Two writable states diverge | Case authority, Chat read projection, cache integration tests |
| Follow-up/evidence linkage | High impact, medium change volume | Answer linked to wrong question or evidence altered | Preserve ordinals/IDs and existing policy, end-to-end chain tests |
| Frontend polling | Medium | Stale response or stuck processing UI | One controller, explicit IDs, selection guards |
| Deployment | Medium-high | Mixed schema/worker versions | Drain active work, backup, coordinated cutover |

## Acceptance boundary

- Case owns run creation and all worker lifecycle state in both code and schema.
- Chat owns messages and follow-up conversation; it does not own leases or retries.
- No duplicate writable processing status or reliance on UUID equality for authorization.
- Existing saved messages, reports and source references survive migration.
- Provider algorithms and follow-up decision rules remain behaviorally equivalent in regression tests.
- Separate persistent documents/evidence, a dedicated queue platform and a standalone consolidated representation are subsequent scopes; this plan changes execution ownership only.
