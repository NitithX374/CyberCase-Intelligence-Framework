# Independent legacy-retirement verification

Date: 2026-09-10
Verdict: Follow-up application verification PASS within the reviewed scope; retirement/cutover remains BLOCKED at checkpoint D. Application code not modified during either parent review.

## Follow-up independent verification — 2026-09-10

- [CODE] Earlier MITRE presentation finding addressed: `frontend/src/lib/technical-context.ts` builds mapped cards from validated trace associations, separates retrieved-only rows, and exposes failure/invalid-trace outcomes.
- [CODE] Earlier report outcome finding addressed: `case_report_snapshot.py` validates and persists augmentation status, query hash and trace binding; `case_report_template.py` distinguishes absent historical metadata without inventing an outcome.
- [CODE] Legacy layout now resolves the authenticated `case-link` reader before redirecting, with explicit unavailable/historical-unavailable UI. Different-ID relation coverage is a mocked service contract, not proof of a migrated database relationship; current ORM uses the shared primary-key Case relationship. Historical policy approval remains separate.
- [TOOL] Fresh full backend suite against Docker PostgreSQL at 127.0.0.1:5433: **434 passed, 1 skipped, 1 warning, 2 subtests passed**, 86.78 seconds. PostgreSQL helper uses disposable UUID schemas with teardown, not public application rows. The skipped account-persistence scenario is not certified.
- [TOOL] Fresh frontend suite: **43 files, 177 tests passed**. TypeScript, API-type drift check, Next.js production build, and git diff --check passed. Diff check emitted line-ending warnings. No tracked rag_service diff.
- [CODE/TOOL] `test_case_native_augmentation_postgres.py` exercises native execution through result persistence, assistant publication and report/PDF, including skip, empty retrieval, failure, partial mapping and no supported match. Provider callables are mocked; this does not test real provider transport or quality.
- [TOOL] Receipt commands cite port 5432; the observed Docker mapping is 5433. This review used 5433 explicitly. Agent-reported command provenance should be corrected before using the receipt as an exact reproduction guide.
- [CODE] Checkpoint D is honestly blocked: the test-local drain simulation does not exercise mixed old/new workers, an admission-freeze barrier or publication/lease races across versions. Passing tests do not close that gate.
- [TOOL] Not performed: authenticated browser E2E, fresh migration upgrade/rollback rehearsal, full lint/Ruff rerun, live provider calls, live admission freeze/drain, backup/restore or deployment. No authorization inferred for these actions. Report redesign and contract harmonization remain deferred.

## Previous review findings (historical; superseded above where addressed)

## Findings

### P1: Retrieved rows appear as Case-relevant techniques without validated associations

frontend/src/lib/technical-context.ts:36 iterates every retrieved row. Line 46 uses association.reason OR raw row.reason. nativeMitreRows at line 279 reads the raw MITRE table without checking augmentation status or association membership. A mapping failure retains retrieval context in case_mitre_augmentation._failed; a successful mapping with zero supported associations also retains rows. Both therefore render cards with no supported Case association. This defeats the purpose of a separately validated mapping stage.

Required: render mapped cards only from validated associations; if showing retrieved-but-unmapped context, label it separately with no asserted Case relevance. Preserve explicit failed/no-supported-match state. Add native UI tests for mapping failure, zero associations, partial mapping and invalid trace. Current catch-to-empty also conceals invalid source/trace data as ordinary absence.

### P2: Report loses technical augmentation outcome

backend/app/services/reports/case_report_snapshot.py:35-51 copies trace and retrieval ID but not technical_augmentation status/failure metadata. case_report_template.py:39 collapses empty associations into one not-called-or-no-results message. A timed-out retrieval and genuinely not-applicable case cannot be distinguished in the persisted/exported report. This violates checkpoint B's explicit outcome contract, even though the base summary remains available.

Required: preserve proven outcome in report snapshot and limitations; render failed, not_applicable and no-supported-match distinctly. Test generation and PDF data path from persisted failed augmentation, not just the augmentation helper.

### P2: Legacy deep link still assumes Chat ID equals Case ID

frontend/src/features/chat/routing/chat-route.ts:45-47 constructs /case/{same ID} without resolving ownership/relation. /chat layout no longer mounts old workspace, which is correct, but unlinked historical threads have no deliberate historical destination. Receipt acknowledges policy unresolved; this is not a completed compatibility gate. Do not infer safety from a previous zero-row census.

Required: approve historical policy and resolve mapping or present explicit read-only historical state; test linked, unlinked, missing and unauthorized IDs. No automatic relink/backfill.

### Verification gap: native MITRE integration and drain are not proven end-to-end

backend/tests/test_case_runs_postgres.py:128 calls execute_case_run without applicability_gate/rag_request, so its conditional augmentation branch is skipped. test_case_mitre_augmentation.py tests the helper directly. These checks do not prove CaseRun -> augmentation -> DB result -> publication -> UI/report parity together.

backend/tests/test_legacy_execution_drain_postgres.py:77 defines its own _retire_legacy_runs which simply marks rows failed; line 101 runs that helper concurrently with native recovery. It does not exercise old-writer admission freeze, old worker lease/publication races or a production drain operation. Useful isolation check, not evidence checkpoint D's race gate passed.

Required: integration test through actual native orchestration with only provider boundary mocked, plus genuine mixed-worker/freeze rehearsal or keep cutover explicitly blocked. Preserve prior coverage when deleting old-path tests; passing a smaller suite is not parity evidence.

## Independently executed checks

- Backend: CYBERCASE_TEST_DATABASE_URL set to local Docker PostgreSQL port 5433; ../env_mitre/Scripts/python.exe -m pytest -q --tb=short from backend. 418 passed, 1 skipped, 2 subtests passed, one upstream deprecation warning, 58.36s. Inspected isolated_database helper: UUID-named test schemas created/dropped; no public-case fixtures written by that helper.
- Skipped test: test_registered_accounts_persist_private_chats requires a separately migrated cybercase_auth_verification_* database. Do not call this full migrated account-flow verification.
- Frontend: npm test -- --maxWorkers=2: 43 files, 167 tests passed, 75.26s.
- npx tsc --noEmit: exit 0.
- npm run check:api-types: exit 0.
- npm run build: exit 0; compiled, TypeScript and static route generation passed.
- git diff --numstat -- rag_service: no tracked changes shown.

No live provider calls, authenticated browser checks, live freeze/drain, backup/restore or deployment performed. Full lint/Ruff and migration rehearsal not rerun in this review. Existing dirty work retained. All findings above are source-path evidence; no adversarial fixture was added or run for the newly identified UI/report defects in this review.
