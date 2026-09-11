# Chat / Case Analysis Separation Receipt

Date: 2026-09-11  
Scope: Chat Q&A and Case Analysis separation, backend/frontend application code and tests  
Decision: safe application changes are ready for parent review; PostgreSQL integration verification is blocked by the unavailable required test port. No deployment or cutover is certified.

## Boundary implemented

- Case owns evidence, snapshots, analysis results, clarifications, and `CaseRun` worker execution.
- Chat is an optional transcript and Q&A surface. An ordinary composer message is always an `ask` operation and never silently admits evidence or starts Case Analysis.
- Clarification admission remains explicit through the Case Overview clarification action and the persisted `add_case_info` intent. A pending retry preserves its stored `kind` and `action`.
- A Chat ASK loads one validated, Case-owned analysis result and its pinned evidence snapshot, then invokes only the dedicated answer stage. It does not extract claims, create quotes, invoke RAG/MITRE, admit evidence, or create another analysis result.
- The answer publication is a response-scoped assistant message with an answer receipt. It is not authoritative Case evidence and does not mutate the pinned result or snapshot.
- Exact citation validation remains the existing strict validator. The Q&A loader revalidates the pinned native trace against the admitted source registry and fails closed for invalid bindings.

## Changes in this continuation

Backend:

- `backend/app/services/chat/case_answer.py`: validates missing/corrupt trace, metadata, augmentation table, evidence hash, pipeline configuration, answer context shape, request message binding, and bounded history before provider execution. Cross-case result/snapshot bindings fail closed. No provenance or historical snapshot is fabricated.
- `backend/tests/test_case_answer_postgres.py`: added real-PostgreSQL scenarios for missing result context, empty/malformed trace, invalid metadata, cross-case pinned result, and history isolation. Provider calls are mocked only at the HTTP boundary.

Frontend:

- `frontend/src/features/chat/workspace/use-workspace-submission-actions.ts`: ordinary composer submissions always use `message`; only an already persisted retry can retain `followup` intent.
- `frontend/src/features/chat/runs/use-chat-submission.ts`: ordinary messages resolve to `ask` regardless of stale persisted `postAnswerAction`; explicit follow-up retries retain `add_case_info`.
- `frontend/src/components/conversation/ChatPanel.tsx`: shows Q&A-specific copy, disables Chat before a validated Case analysis, and directs pending clarification answers to Case Overview.
- `frontend/src/components/conversation/WorkspaceChatPanel.tsx`, `frontend/src/components/ChatWorkspaceLayout.tsx`, `frontend/src/components/ChatWorkspace.tsx`, and `frontend/src/features/chat/workspace/chat-workspace-types.ts`: pass the validated analysis-context boundary and remove obsolete Chat action controls from the active panel.
- `frontend/src/test/components/chat/ChatPanelFollowUp.test.tsx`, `frontend/src/test/features/chat/chat-submission-retry.test.tsx`, and `frontend/src/test/features/chat/workspace-submission-actions.test.tsx`: cover the UI boundary, stale action isolation, explicit clarification retry, and ordinary composer behavior.

## Verification evidence

Passed:

```text
backend: python -m compileall -q app tests
backend: ruff check app tests --target-version py311 --output-format concise
backend non-PostgreSQL: 407 passed, 2 skipped, 37 deselected, 1 warning, 2 subtests passed
frontend focused boundary: 3 files, 12 tests passed
frontend full suite: 44 files, 181 tests passed
frontend: npx tsc --noEmit
frontend: npm run check:api-types
frontend: npm run build
frontend scoped ESLint: 0 errors, 0 warnings on the boundary/test file set
```

The focused PostgreSQL command was run with the required URL:

```powershell
$env:CYBERCASE_TEST_DATABASE_URL='postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/cybercase_framework'
& '..\env_mitre\Scripts\python.exe' -m pytest -q --disable-warnings tests/test_case_chat_postgres.py tests/test_case_answer_postgres.py tests/test_case_chat_retry_postgres.py --tb=short
```

Result: `15 failed` during disposable-schema setup with `ConnectionRefusedError [WinError 1225]` at `127.0.0.1:5433`. The full backend attempt with the same URL produced `38 failed, 407 passed, 1 skipped, 2 subtests passed`; the failures were the PostgreSQL-dependent tests unable to open that connection. No `:5432` result is used as evidence for this receipt, and Docker was not started or rebuilt.

The new PostgreSQL tests collected successfully as 15 tests. Their database execution is not certified in this continuation because the required PostgreSQL service was unavailable. A prior handoff reported focused PostgreSQL passes before this hardening; that earlier result is not treated as proof for the current modified test set.

## Limitations and blockers

- Real PostgreSQL execution of the Q&A success, failure, cross-case, corruption, history, retry, and concurrency scenarios must be rerun against the required disposable `:5433` target before this gate can be marked passed.
- No live worker drain, admission freeze, Docker restart/rebuild, deploy, migration, or live database mutation was performed.
- HTTP provider behavior was tested with `httpx.MockTransport`; no paid/live LLM, RAG, or MITRE provider call was made.
- Authenticated browser E2E was not run. The production build and component tests do not prove browser routing or live API behavior.
- Full frontend lint remains blocked by unrelated pre-existing `react-hooks/set-state-in-effect` errors in `frontend/src/components/auth/AccountForm.tsx` and `frontend/src/components/home/HomeSections.tsx`. The scoped boundary lint is clean.
- Historical Chat compatibility remains read-only where no proven Case relation exists. No UUID coincidence, silent relink, synthetic Case, or fabricated historical provenance was introduced.

## Ownership protection

- Existing dirty and untracked work was preserved. No reset, stage, commit, push, destructive migration, or file-wide cleanup was performed.
- `rag_service/**`, report redesign, migrations, parent plan/review documents, and `CONTINUITY.md` were not edited for this continuation.

Final status: implemented application boundary, pending parent review and required real-PostgreSQL verification; not a cutover certification.
