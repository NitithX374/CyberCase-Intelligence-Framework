# Continuity Ledger

## Snapshot

- 2026-08-23 [USER] Goal: aggressively simplify the demo to raw user-authored messages as authoritative evidence; delete canonical Case State, versions, deltas, extraction, entity/relationship UI, and compatibility schema.
- 2026-08-23 [USER] Preserve initial analysis, clarification, add-information vs ask semantics, external RAG, Main Case Analysis, follow-up, reports, and source traceability.
- 2026-08-23 [USER] Existing demo data and old-schema compatibility may be discarded.
- 2026-08-23 [CODE] Raw evidence includes initial, clarification-answer, and explicit add-information messages; ordinary asks and all assistant/RAG text are excluded.
- 2026-08-23 [CODE] Fresh-evidence runs invoke RAG; ordinary asks reuse the latest completed run-bound RagContext without invoking RAG.
- 2026-08-23 [CODE] `analysis_trace_v2` binds source message IDs, evidence SHA-256, retrieval context, and candidate-only MITRE associations.
- 2026-08-23 [CODE] Report generation is deterministic from raw evidence, latest grounded analysis, matching RagContext, MITRE rows, and unresolved gaps.
- 2026-08-23 [CODE] Persistence is reduced to chat_threads, chat_messages, chat_runs, rag_contexts, and chat_reports.
- 2026-08-23 [CODE] Frontend product routes are Chat and Report only.
- 2026-08-23 [TOOL] Backend tests and compile, frontend tests/lint/build, obsolete-symbol scan, and production file-size scan are green.
- 2026-08-23 [CODE] Follow-up backend package restored after all tracked files appeared as unstaged deletions; raw-evidence inputs and frontend clarification presentation are intact.
- 2026-08-23 [USER] `rag_service/**` remains outside this architecture change.

## Done (recent)

- 2026-08-23 [CODE] Deleted Case State/extraction models, services, migrations, workflow stages, frontend screens, routes, schemas, and obsolete tests.
- 2026-08-23 [CODE] Rebuilt workflow, analysis, reports, schema baseline, and active architecture documentation around raw evidence.
- 2026-08-23 [CODE] Removed the unused `baseline_report_v1` API/schema path; only `preliminary_analysis_report_v1` remains.
- 2026-08-23 [TOOL] Backend: 62 tests plus 2 subtests passed; `compileall` passed.
- 2026-08-23 [TOOL] Frontend: 8 test files/23 tests passed; ESLint and Next.js production build passed after follow-up restoration.
- 2026-08-23 [TOOL] Next.js route manifest contains only `/`, `/chat`, `/chat/[threadId]`, and `/chat/[threadId]/report`.
- 2026-08-23 [CODE] Added a focused rendered follow-up UI regression test covering the question, gap explanation, and enabled answer composer.

## Decisions

- D001 ACTIVE 2026-08-23 [USER] Do not modify `rag_service/**` for this cutover.
- D002 ACTIVE 2026-08-23 [USER] Raw included user messages are the only authoritative incident evidence.
- D003 ACTIVE 2026-08-23 [CODE] RAG/MITRE/model output is analytical context, never reported evidence.
- D004 ACTIVE 2026-08-23 [CODE] Ask reuses the latest durable run-bound RagContext; initial, clarification, and add-info runs perform fresh RAG.
- D005 ACTIVE 2026-08-23 [USER] Do not retain compatibility shims for the deleted Case State architecture.
- D006 ACTIVE 2026-08-23 [CODE] Reports remain deterministic, template-first, provisional, and source-message traceable.

## State (Done/Now/Next)

- 2026-08-23 [TOOL] Done: implementation, focused cleanup, active-doc rewrite, and local backend/frontend validation.
- 2026-08-23 [TOOL] Done: final migration-head, diff-integrity, obsolete-symbol, and production file-size audits.
- 2026-08-23 [TOOL] Next: hand off exact changed boundaries and validation receipts; no commit or push unless requested.

## Open questions

- 2026-08-23 [TOOL] UNCONFIRMED: live Docker/PostgreSQL migration execution; the migration source/model contract is tested locally, but a running demo database has not yet been reset in this turn.
- 2026-08-23 [TOOL] Existing unrelated research, experiment, dependency, Docker, and `rag_service/**` dirty changes remain user-owned and outside this cutover.

## Incident: missing backend follow-up package

- 2026-08-23 [USER] Symptom: follow-up appeared missing after the architecture refactor.
- 2026-08-23 [TOOL] Evidence: all 11 tracked `backend/app/services/followup/*` files were absent and reported as unstaged deletions while frontend and workflow callers remained.
- 2026-08-23 [CODE] Mitigation: restored the tracked package from HEAD, reapplied raw-evidence adaptations, restored modular metadata helpers, and added a rendered UI regression test.
- 2026-08-23 [TOOL] Status: RESOLVED; focused backend tests 8 passed and focused frontend tests 7 passed.

## Working set

- 2026-08-23 [CODE] `backend/app/services/chat/raw_evidence.py`
- 2026-08-23 [CODE] `backend/app/services/workflow/`
- 2026-08-23 [CODE] `backend/app/services/case_analysis/`
- 2026-08-23 [CODE] `backend/app/services/reports/`
- 2026-08-23 [CODE] `backend/app/models/`
- 2026-08-23 [CODE] `backend/alembic/baseline_versions/0001_raw_evidence_chat.py`
- 2026-08-23 [CODE] `frontend/src/components/ChatWorkspace*`
- 2026-08-23 [CODE] `frontend/src/features/chat/`
- 2026-08-23 [CODE] `frontend/src/components/report/`
- 2026-08-23 [CODE] `README.md`, `backend/README.md`, `frontend/README.md`, `docs/`
- 2026-08-23 [USER] `rag_service/**` no-touch boundary

## Receipts

- 2026-08-23 [TOOL] `python -m pytest backend/tests -q --tb=short`: 62 passed, 2 subtests passed; warnings were Starlette deprecation and denied pytest cache creation.
- 2026-08-23 [TOOL] `python -m compileall -q backend/app`: passed.
- 2026-08-23 [TOOL] `npm run test -- --reporter=dot`: 8 files and 23 tests passed.
- 2026-08-23 [TOOL] `npm run lint`: passed.
- 2026-08-23 [TOOL] `npm run build`: passed, including TypeScript and static generation.
- 2026-08-23 [TOOL] Alembic reports single head `0001_raw_evidence_chat`; offline PostgreSQL `upgrade head --sql` emitted the five-table schema and all expected foreign keys.
- 2026-08-23 [TOOL] `git diff --check` passed; obsolete production-symbol scan returned no runtime hits except the intentional validator rejection key.
- 2026-08-23 [TOOL] Production backend/frontend code is within 300 physical lines; larger files found only in pre-existing out-of-scope backend experiment modules.
