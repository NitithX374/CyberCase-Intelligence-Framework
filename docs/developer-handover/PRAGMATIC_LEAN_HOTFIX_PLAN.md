# Pragmatic Lean hotfix — Luna implementation contract

Date: 2026-09-11
Authorization: user requests implementation by Luna, combining Gemini's Pragmatic Lean proposal with the parent's safeguards. This hotfix supersedes the paused naming/consolidation task as the active implementation priority. Do not resume broad renames.

## Outcome

Keep in-process FastAPI BackgroundTasks and PostgreSQL Run/result persistence. Remove periodic lease renewal and recovery scanning. Preserve minimal concurrency protection, evidence integrity and optional Chat UX. Use one frontend Run observer and project analysis results into Chat without new duplicate analysis messages.

This is a bounded architectural hotfix, not a cosmetic change or zero-risk patch. No Redis, RabbitMQ, new worker service or scheduling framework. rag_service/** stays unchanged. Report redesign remains deferred.

## Non-negotiable boundaries

- Preserve all existing dirty/untracked changes, including partially completed camelCase moves and Gemini flow changes. Resolve current paths rather than restoring old filenames from this plan.
- Coordinate overlapping files before edits. If ownership remains uncertain, stop the affected batch and report the conflict; do not assume another agent finished.
- No deployment, Docker restart/rebuild, paid provider calls, commit/stage/push or live DB mutation. PostgreSQL tests may create disposable schemas/databases through the established helpers only.
- Parent owns CONTINUITY.md and this plan. Luna owns application/tests and PRAGMATIC_LEAN_HOTFIX_RECEIPT.md.
- Maintain readable logical blank lines and expanded control flow. Cohesive files around 400–500 lines are acceptable; do not manufacture tiny modules or compress code for LOC.
- Case evidence, revisions, immutable snapshots, quote validation and source-role isolation remain intact. No fuzzy citation repair, invented provenance or reconstructed historical snapshots.
- Native Q&A remains separate from main analysis. Ordinary Chat never admits evidence, answers clarification implicitly, or starts analysis when context is absent.

## A. Baseline and supported runtime gate

Read root AGENTS.md, current ledger and prior Chat separation/naming receipts. Inventory git status, current relevant file paths and modified sections before work. Capture baseline focused tests, OpenAPI schema and existing DB constraints. Do not overwrite other agent fixes.

Supported Lean runtime is exactly ONE application process/instance accessing this CaseRun database, without rolling overlap. One machine/container is not enough if it runs multiple workers. Verify launcher/Compose configuration, document this deployment contract and reject explicitly configured unsupported worker counts where detectable. Do not claim a local setting proves no external replica exists. Production single-instance verification remains a cutover gate.

Startup recovery completes before accepting requests. A live old version must be stopped before the new version starts. Existing code already runs BackgroundTasks; do not describe this as a migration from an external queue.

Exit A: coherent baseline and released write scope; exact file list; runtime assumptions and known failures recorded. No deployment performed.

## B. Atomic run lifecycle without leases

Likely working set (resolve post-rename paths): workflow/caseRunClaim.py, caseRunExecution.py, caseRunCompletion.py, caseAskCompletion.py, caseRunService.py, failure helpers, models/caseRun.py, relevant routers.

### Admission

1. Commit a queued CaseRun before scheduling a background task.
2. Preserve idempotency key/fingerprint rules and same-key/different-payload rejection.
3. Preserve one active run per Case if that is the current rule, including requests with DIFFERENT keys. An existing Case row lock or proven constraint can remain. Atomic claim per run does not protect cross-run admission.
4. Existing terminal receipts must not execute again; duplicate scheduling of a queued run must be harmless.

### Claim

Use a short transaction containing UPDATE WHERE id=:id AND status='queued', setting running/started_at and incrementing attempt_count. RETURNING must include the attempt number as well as run id. Commit before provider work. Zero returned rows means no-op.

Capture the returned attempt number locally as claimedAttempt. This is a monotonic attempt fence, not a lease; no periodic renewal. Preserve snapshot hash/manifest validation when replacing claimCaseRun. Invalid inputs fail the claimed attempt without provider calls.

### Completion/failure

Every success/failure/timeout write checks run id, status='running' AND attempt_count=claimedAttempt. Never reset attempt_count on retry. Retry is permitted only for terminal failed work, not arbitrary live running work.

In ONE transaction: conditionally acquire completion rights, insert result (or ASK assistant message), update Case latest result if applicable, and mark Run completed. If the attempt predicate fails, do not persist any output. If any insert/update fails, rollback all writes, including the status transition. Do not commit Result before checking completion rights. Keep unique-result invariants and relevant constraints.

ASK success writes conversation output only; it must not create CaseAnalysisResult or increment evidence revisions. Timeout/failure from an old attempt must not mark a newer attempt failed. Preserve active-run admission locking; do not claim all SELECT FOR UPDATE is unnecessary.

Exit B: PostgreSQL same-key and different-key concurrent admission tests, duplicate execution test, stale-success/stale-failure tests and injected completion rollback pass. Provider side effects cannot be guaranteed exactly once across crashes; document potential repeated provider cost after retry.

## C. Lifecycle: startup cleanup, timeout and cancellation

Working set: main.py, caseRunRecovery.py, caseRunExecution.py, config.py and applicable launcher docs.

- Replace the lease-expiry scan with a startup-only cleanup of prior queued/running runs, marking failed/interrupted_by_restart with finished_at. Do not wait for old lease expiry. Preserve completed/failed results and other users' non-Run data.
- Run cleanup transaction before yielding application lifespan. If DB cleanup fails, fail startup rather than accepting traffic with unknown state.
- Remove recovery daemon and heartbeat scheduling. Delete caseRunHeartbeat.py only after all callers and tests are migrated.
- Set a documented configurable whole-execution timeout, covering context loading and pipeline work; retain provider HTTP timeouts. Cancellation is cooperative, not a hard kill. No swallowed CancelledError or untracked fire-and-forget subtasks.
- Handle timeout and ordinary exceptions through attempt-fenced failure persistence. Handle application shutdown cancellation with best-effort bounded cleanup and re-raise cancellation; startup cleanup is the fallback after process death.
- Completion must have explicit transaction/cancellation semantics: cancellation before commit rolls back; an already committed completion must not later be overwritten as failed. No DB locks held while waiting on LLM.
- If DB failure prevents failure persistence, log run/attempt identifiers without case contents and fail visibly; do not promise guaranteed recovery without a functioning DB or restart.
- Preserve manual retry; this design does not resume provider execution mid-call. Document the acceptance gap between queued commit and task start: process restart recovers abandoned jobs; no durable queue/resume guarantee is claimed.

Schema strategy for this hotfix: stop using lease_owner/lease_expires_at but retain nullable columns initially to avoid unnecessary destructive migration. Check existing constraints; if a constraint requires lease fields for running rows, use the smallest reviewed additive/constraint migration with isolated PostgreSQL upgrade tests. Do not drop historical columns/FKs blindly. ASK request_message_id remains meaningful; Analysis may have no Chat message. Defer physical lease column removal to a separate approved cleanup.

Exit C: startup tests for recent queued/running work (not just expired), terminal preservation, cleanup failure, runtime timeout, cancellation and late result suppression. No periodic heartbeat/recovery tasks remain in application startup or runtime.

## D. Case-owned state and analysis projection in Chat

Working set: Case serialization, Chat readers/completion, frontend Chat workspace/transcript, native result/snapshot readers.

1. Native Case state derives from Case data, run operation/state and analysis freshness, not ChatThread.status. Eliminate frontend caseFromChatThread synthesis into Case cache. Chat reads update Chat cache, and invalidate Case only when needed.
2. Preserve meaningful distinction between ASK processing/failure and main-analysis state. An ASK failure must not replace a valid analysis or make it appear that main analysis failed.
3. Stop creating NEW analysis-result ChatMessage copies. Locate real publication code in completion helpers rather than assuming a ChatPublicationService class exists.
4. Render latest validated CaseAnalysisResult as an explicitly identified assistant analysis Lead Card in Chat, using its pinned evidence snapshot for citations. No fabricated message id or ordinal. No analysis means a clear no-analysis state, not automatic execution.
5. Keep each Q&A's context_analysis_result_id and snapshot binding. If latest result changes A→B, prior Q&A must remain labeled as based on A; retain source inspection against A, not silently substitute B. It is acceptable to show only latest analysis as the lead card, provided older answer context remains explicit.
6. Deduplicate historical publication messages only when an exact analysis_result_id relation proves duplication. Do not delete historical DB records or hide unmapped legacy messages. Avoid two rendered copies of the same result.
7. Clarification remains an explicit Case action; do not reinterpret normal Chat as an answer or authoritative evidence. Keep pending clarification display/functionality after removing analysis publication writes.
8. Preserve Chat creation/opening behavior unless an actual dependency requires adjustment. Do not delete all CaseRun→Chat foreign keys to make the diagram look independent.

Exit D: Analysis completes with Chat closed; opening Chat shows the result and valid citations without a new analysis-result message row. A→B reanalysis preserves older Q&A attribution, historical duplicates are handled conservatively, no-analysis Chat refuses without a run, explicit clarification still works.

## E. One frontend Run observer

Replace independent Case polling and Chat session network loops with one query/observer keyed by Case id + Run id. Both consumers use it. Do not replace two loops with two instances of another custom network loop.

- Poll only Run while queued/running. Keep selection cancellation and saved pending request/idempotency data.
- On terminal state, invalidate/refetch appropriate Case and Chat data once per observed (runId, attempt_count, terminalStatus), coordinated across consumers. Fetching messages after ASK completion is necessary; it is not a second polling loop.
- Retry on the same Run id must restart observation and allow terminal refresh for its new attempt.
- Query remount must still get current data; do not introduce a permanent dedupe set that suppresses required fresh reads. Assert coordinated transitions rather than promising exactly one network request across all remounts/cache policies.
- Current Chat polling reads thread after terminal status, not every tick. The duplication to remove is the independent Run observers and repeated completion refresh logic.
- A failed run refreshes status and displays the backend error without automatically starting a new run. Closing Chat does not cancel Case analysis; switching Cases must not apply stale UI updates.

Exit E: frontend tests verify both consumers observing one run, same-run retry, changed selection, refresh, lost receipt, completion/failed states and Chat message refresh. Preserve native API type generation and query-key semantics or migrate callers explicitly.

## F. Verification and handoff

Run focused regressions first, then full suites where feasible. Do not use pytest -k case_run alone: camelCase renames and Q&A/publication tests may be missed.

Required PostgreSQL cases:

1. Same key concurrent requests → one logical run and one provider call within the attempt.
2. Same key different intent → conflict; different keys same Case → existing active-run policy preserved.
3. Two scheduled tasks claim same run → only one executes.
4. Attempt 1 late success AND late failure cannot modify attempt 2 or insert orphan output.
5. Result insertion/latest-pointer failure rolls back completion atomically.
6. Recent queued/running work cleaned on startup; completed results unchanged.
7. Runtime timeout/cancellation without restart → bounded handling, no successful late write.
8. ASK does not mutate evidence/main result; snapshot and ownership checks remain strict.
9. Any required constraint migration upgrades against disposable PostgreSQL and preserves historical records.

Required frontend/integration cases: no-analysis refusal; Analysis with Chat closed; lead card citations; no duplicated result rows/cards; A→B old Q&A labels; explicit clarification; shared polling/attempt-aware invalidation; refresh/retry and selection cancellation.

Commands: use actual environment paths and verified PostgreSQL port (previous local Docker 127.0.0.1:5433), established isolated-schema helpers, backend pytest/compile/Ruff, frontend Vitest/tsc/API-type check/build/scoped lint, final diff and import review. Mock provider boundaries; no paid/live calls. Use synthetic test fixtures, never real case contents in new logs.

Browser/process-kill verification should use an isolated test environment only. If unavailable, report unverified explicitly. Lack of visible errors is not proof of no races. No live cutover is authorized.

Receipt must list completed checkpoints, changed paths, actual commands/results, unsupported configurations, remaining gaps and whether restart/migration/browser scenarios were simulated or exercised. No claim of 100% concurrency safety or identical historical UX. Parent performs independent review before any deployment discussion.
