# Pragmatic Lean Hotfix Receipt — Case Analysis & Chat Q&A Separation

**Date**: 2026-09-11  
**Author**: Luna / Antigravity Engineering Pair  
**Status**: Verification Complete (Ready for Review; Cutover Frozen Pending Approval)  
**Reference Plan**: [`docs/developer-handover/PRAGMATIC_LEAN_HOTFIX_PLAN.md`](./PRAGMATIC_LEAN_HOTFIX_PLAN.md)  
**Canonical Architecture**: [`docs/research/CURRENT_PROJECT_DIRECTION.md`](../research/CURRENT_PROJECT_DIRECTION.md)

---

## 1. Executive Summary

Under the Pragmatic Lean architecture, we have completed the separation of **Case Analysis** and **Chat Q&A**:
1. **Case-Owned Execution & State**: Case is the sole authority for analysis runs, state transitions, evidence revisions, and snapshots. Chat is an optional Q&A surface for discussing established findings.
2. **In-Process Atomic CAS Execution**: Distributed coordination artifacts (lease renewals, background heartbeats, periodic recovery daemons) were eliminated in favor of atomic in-process compare-and-swap claims with monotonic `attempt_count` fencing.
3. **No Duplicate DB Chat Messages**: Analysis completion writes directly to `case_analysis_results` within a single atomic transaction without publishing redundant synthetic `chat_messages`.
4. **Chat Lead Card Projection**: The chat transcript projects the active validated `CaseAnalysisResult` at the top as an attributed `CaseAnalysisLeadCard`, deduplicating legacy historical duplicate publication rows when identical.
5. **Cache Synthesis Elimination**: Frontend no longer synthesizes artificial `CaseRead` records from `ChatThread` objects (`caseFromChatThread` eliminated from active flow and marked `@deprecated`).
6. **Attempt-Aware Polling**: Frontend run polling keys invalidation on `${runId}:${attemptCount}:${status}`, ensuring retried executions properly trigger cache refreshes.

---

## 2. Gate Verification & Deliverables

### Gate A — Baseline & Runtime Environment
- **Runtime Topology**: Exactly ONE application process/instance accessing the PostgreSQL database.
- **Queue/Worker Architecture**: FastAPI `BackgroundTasks` executed in-process without Redis, RabbitMQ, or external daemon workers.
- **RAG Boundary**: `rag_service/**` remained completely isolated and untouched.

### Gate B — Atomic Run Lifecycle Without Leases
- **Atomic Claim**: `claim_case_run` performs atomic CAS via:
  ```sql
  UPDATE case_runs 
  SET status = 'running', attempt_count = attempt_count + 1, started_at = :now, lease_owner = NULL
  WHERE id = :run_id AND status = 'queued'
  RETURNING id, attempt_count
  ```
- **Attempt Fencing**: Completion (`complete_case_run`) and failure (`fail_case_run`) verify `status = 'running' AND attempt_count = :claimed_attempt`. Stale attempts (e.g., from aborted executions or timed-out tasks) cannot overwrite a newer attempt or publish orphaned results.
- **Single-Transaction Completion**: Run status update, `case_analysis_results` persistence, and Case latest pointer update commit atomically in a single transaction.
- **Q&A Isolation**: Ask completion writes assistant messages to `chat_messages` only and cannot advance evidence revisions or overwrite `CaseAnalysisResult`.

### Gate C — Startup Cleanup, Timeout & Cancellation
- **Startup Cleanup**: Application lifespan startup cleans up any leftover `queued` or `running` runs marked from prior process crashes as `status = 'failed'`, `error_code = 'interrupted_by_restart'`, without touching terminal records.
- **Timeout Management**: Configurable whole-execution timeout (`asyncio.timeout`) bounds provider latency.
- **Daemon Removal**: Deleted heartbeat scheduler (`caseRunHeartbeat.py`) and periodic recovery polling daemon; no background interval tasks remain.

### Gate D — Case-Owned State & Analysis Lead Card
- **Eliminated Cache Synthesis**: `ChatWorkspace.tsx` `cacheUpsertCaseFromChat` now updates only `chatQueryKeys.detail` in TanStack query cache without mutating `upsertCase`.
- **Deprecated Synthesis Helper**: `caseFromChatThread` in `useCaseQueries.ts` marked `@deprecated`.
- **Lead Card Component**: Created `frontend/src/components/conversation/CaseAnalysisLeadCard.tsx` rendering validated analysis summary, badge, and navigation to Case Overview.
- **Deduplication in Transcript**: `ChatTranscript.tsx` filters out historical duplicate publication messages matching `leadResult.id`.
- **Wiring**: Props piped seamlessly across `ChatWorkspaceLayout` -> `WorkspaceChatPanel` -> `ChatPanel` -> `ChatTranscript`.

### Gate E — One Run Observer & Attempt-Aware Polling
- **Key Invalidation**: `useCaseRunPolling.ts` keys invalidation on:
  ```ts
  const attemptCount = query.data?.attempt_count ?? 0;
  const invalidationKey = `${runId}:${attemptCount}:${status}`;
  ```
- Retrying the same run cleanly bumps attempt count and invalidates Case/Chat queries upon reaching terminal states.

---

## 3. Files Modified & Created

### Backend Files
| File Path | Action | Description |
| :--- | :--- | :--- |
| `backend/app/services/workflow/caseAskCompletion.py` | Modified | Row-lock ChatThread prior to validation; eliminate duplicate fetch |
| `backend/app/services/workflow/caseRunCompletion.py` | Modified | Single transaction completion; eliminate duplicate ChatMessage publication |
| `backend/app/services/workflow/caseRunClaim.py` | Modified | Atomic CAS claim with monotonic `attempt_count` return |
| `backend/app/services/workflow/caseRunRecovery.py` | Modified | Startup-only cleanup of orphaned active runs |
| `backend/tests/test_case_answer_postgres.py` | Modified | Assert Analysis no longer generates duplicate ChatMessage; create ChatThread fixture |
| `backend/tests/test_case_native_augmentation_postgres.py` | Modified | Assert analysis completion stores `CaseAnalysisResult` without ChatMessage |
| `backend/tests/test_case_runs_postgres.py` | Modified | Added tests for atomic CAS duplicate prevention and startup cleanup |

### Frontend Files
| File Path | Action | Description |
| :--- | :--- | :--- |
| `frontend/src/components/conversation/CaseAnalysisLeadCard.tsx` | **Created** | Renders validated analysis summary and navigation |
| `frontend/src/components/conversation/ChatTranscript.tsx` | Modified | Accepts `leadResult`, renders lead card, deduplicates historical matching messages |
| `frontend/src/components/conversation/ChatPanel.tsx` | Modified | Forwards `leadResult`, `leadSnapshot`, and `onOpenOverview` to `ChatTranscript` |
| `frontend/src/components/conversation/WorkspaceChatPanel.tsx` | Modified | Forwards `leadResult` and `leadSnapshot` to `ChatPanel` |
| `frontend/src/components/ChatWorkspaceLayout.tsx` | Modified | Passes `nativeAnalysisResult` and `nativeEvidenceSnapshot` to `WorkspaceChatPanel` |
| `frontend/src/components/ChatWorkspace.tsx` | Modified | Replaced `upsertCase(caseFromChatThread)` with query cache update to `chatQueryKeys.detail` |
| `frontend/src/hooks/useCaseQueries.ts` | Modified | Marked `caseFromChatThread` as `@deprecated` |
| `frontend/src/hooks/useCaseRunPolling.ts` | Modified | Attempt-aware invalidation key `${runId}:${attemptCount}:${status}` |
| `frontend/src/components/home/HomeSections.tsx` | Modified | Fixed `react-hooks/set-state-in-effect` lint issue |
| `frontend/src/test/components/chat/CaseAnalysisLeadCard.test.tsx` | **Created** | Vitest suite for `CaseAnalysisLeadCard` and transcript deduplication |

---

## 4. Test Verification Evidence

### Backend Test Suite (PostgreSQL 127.0.0.1:5433)
Command:
```powershell
$env:CYBERCASE_TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/cybercase_framework"
..\env_mitre\Scripts\python.exe -m pytest tests/
```
**Results**:
- **456 passed**, 1 skipped (optional test), **0 failed** in 88.21s.
- Concurrency & Atomic Claim:
  - `test_case_run_atomic_claim_prevents_duplicate_execution` PASSED
  - `test_case_run_timeout_and_startup_preserves_terminal_records` PASSED
  - All 10 `test_case_answer_postgres.py` PASSED
  - All 6 `test_case_native_augmentation_postgres.py` PASSED

### Frontend Test Suite (Vitest)
Command:
```bash
npm test -- --run
```
**Results**:
- **45 test files passed** (45/45).
- **190 tests passed** (190/190), **0 failed** in 27.90s.
- Includes `CaseAnalysisLeadCard.test.tsx` (2/2 passed).

### Frontend Typecheck (`tsc`)
Command:
```bash
npx tsc --noEmit
```
**Results**:
- Exited with code **0** (0 type errors).

### Frontend Lint (`eslint`)
Command:
```bash
npm run lint
```
**Results**:
- Exited with code **0** (0 errors, 4 non-blocking warnings).

### Frontend Production Compile (`next build`)
Command:
```bash
npm run build
```
**Results**:
- Compiled successfully in 9.8s.
- Generated all static and dynamic app routes cleanly.

---

## 5. Limitations & Operational Constraints

1. **Single-Process Constraint**: In-process atomic claims and startup cleanups rely on the single-process deployment contract. Running multiple simultaneous backend instances against the same DB without external coordination is unsupported.
2. **Provider Side Effects on Crash/Restart**: If the process restarts while an external LLM request is executing, startup cleanup marks the run failed. Retrying the run will invoke the LLM again.
3. **Database Columns Preserved**: Nullable `lease_owner` and `lease_expires_at` columns remain in the database schema for backward compatibility and are reset to `NULL`; no destructive drop-column migrations were executed.
4. **Historical Legacy Transcripts**: Historical transcripts with duplicated messages from before the hotfix are deduplicated in UI if matching `analysis_result_id` is present; unmapped legacy messages are safely preserved.

---

## 6. Cutover Readiness

All criteria for Gates A through F are satisfied. Code is clean, verified, and ready for review. Live deployment or cutover will remain frozen until explicit user instruction.
