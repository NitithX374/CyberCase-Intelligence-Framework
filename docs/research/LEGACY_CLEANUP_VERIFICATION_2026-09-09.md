# Legacy cleanup verification — 2026-09-09

Follow-up to the supplied Gemini cleanup report. Existing attribute-first and cleanup edits preserved; no rag_service changes, commits, deployment, or production database writes.

## Corrections

- Canonical backend selection now stops at the newest overview record by ordinal. Retired, malformed, unsupported, or invalid/stale v3 records cannot expose an older validated overview. Ordinary assistant messages and explicit ASK/response-scoped records do not supersede the overview.
- Frontend uses the same scope exclusions and ordinal ordering. Retired v2/unversioned records receive a re-analysis notice; invalid v3 and unsupported formats receive an unavailable/unsupported notice instead of an incorrect legacy label. No citations or findings are fabricated.
- ASK run claiming cannot bypass the selection barrier through the legacy RAG-context lookup when an overview record exists. The old context path remains for historical runs without an overview record. PostgreSQL regression tests verify both branches.
- Updated the former backend characterization test that deliberately retained an older overview after an invalid replacement. Its expected behavior now matches the retirement boundary; the test was retained.

## Verification

- Backend full suite against a disposable native PostgreSQL 18 instance on loopback port 55442: 405 passed, 2 subtests passed, no skips; one upstream FastAPI/Starlette httpx deprecation warning. Instance stopped in finally; existing database service untouched.
- Frontend: 158 tests passed in 37 files; ESLint, API type consistency and tsc --noEmit passed.
- Ruff F/I for changed backend selector, worker and new tests passed. Changed code/test files at most 227 lines. git diff --check passed; rag_service status empty.
- Next.js production build passed, including TypeScript and page generation.
- No live model calls, browser E2E, or inventory/migration of production v2 records. Historical scenarios were exercised with synthetic persisted PostgreSQL fixtures.

## Working files

- backend/app/services/case_analysis/state_selector.py
- backend/app/services/workflow/chat_run_claim.py
- frontend/src/lib/case-overview.ts
- backend/tests/test_canonical_analysis_state.py
- backend/tests/test_analysis_retirement_selection.py
- backend/tests/test_analysis_retirement_postgres.py
- frontend/src/test/lib/analysis-retirement.test.ts
