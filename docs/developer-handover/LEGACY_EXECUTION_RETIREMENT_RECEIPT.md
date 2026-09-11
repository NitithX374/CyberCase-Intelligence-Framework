# Legacy Execution Retirement Receipt

Date: 2026-09-10  
Scope: backend and frontend application code/tests only  
Decision: application changes and verification are complete for the safe scope; Checkpoint D and live cutover are not certified or authorized.

This receipt records the implementation and independent verification of `LEGACY_EXECUTION_RETIREMENT_PLAN.md`. It does not authorize a deployment, Docker restart, database mutation, historical relinking, or deletion of retained tables/migrations.

## Invariants preserved

- `Case` owns new evidence, snapshots, analysis results, clarification history, reports, and worker execution.
- `Chat` remains an optional transcript and Q&A/publication surface. A new Chat message for a Case dispatches a `CaseRun`; it does not create a `ChatRun`.
- User-authored admitted Case evidence is authoritative. Assistant output, analyst ASK messages, and MITRE/RAG output are not evidence.
- Native citations continue to resolve through Case evidence source revisions and exact spans/page metadata. No synthetic historical snapshot or provenance binding was created.
- MITRE remains conditional augmentation through the existing applicability gate, RAG client, and mapping boundary. `rag_service/**` was not changed.
- Historical ChatRun/report readers, models, schemas, migrations, and compatibility API symbols remain available where their data/history dependency is real.
- No files were staged, committed, pushed, broadly deleted, or moved. No live application rows were mutated.

## Baseline and ownership protection

Checkpoint A baseline was captured before retirement edits in `F:\Cybercase Framework`:

| Item | Receipt |
|---|---|
| Git HEAD | `e4f179192f812840dc99ea3c1e914f7b5507af86` |
| `git status --porcelain=v1` | 257 entries at implementation baseline; all pre-existing dirty/untracked paths were preserved |
| Dirty-tree hash manifest | `319dd50e7bf513c3935d7a29bc258e368b2dbc8de049fa1bea82c0bd0124f1e1` |
| Parent files | `AGENTS.md`, `CONTINUITY.md`, and `LEGACY_EXECUTION_RETIREMENT_PLAN.md` were read and not edited by this implementation |

The parent-file SHA-256 values at final receipt time are:

```text
AGENTS.md                                             1F30842A5F13552ABFADC335C8C25C9212D48E5B6DF1EEECE557EBD59CB5F0F5
CONTINUITY.md                                         7DB5C9940752A8966EDDB200D04C8F3349A121C818973ED8626B66B9B8C4630D
docs/developer-handover/LEGACY_EXECUTION_RETIREMENT_PLAN.md
                                                       D376CD77B099CC4283EB26F8C7B2166FDE10AF920A26AB3C6C8D3A301F06CA84
docs/developer-handover/LEGACY_EXECUTION_RETIREMENT_VERIFICATION.md
                                                       AA74F9977A57254762D5B9424C55C537BA3338A9E69CFE7C5760A241E82129EA
```

The baseline's dirty and untracked work was retained. The parent-owned ledger has its current hash above and was not edited by this implementation; its hash is not used as a claim that the parent did not make an independent update. Luna-reported totals were not used as proof; the checks below were rerun independently in this checkout.

The final working tree has 266 `git status --short` entries. The increase from the 257-entry baseline is the scoped application/test/receipt work listed below; no baseline path was reset or discarded, and nothing was staged.

## Checkpoint A — baseline and inventory

Status: PASS for the application inventory and read-only census.

The inventory covered backend routers, services, models, schemas, lifespan/recovery, tests, migrations, frontend routes/layouts, hooks, API clients/types, storage, components, and tests. Candidate deletion was decided from callers and data dependencies, not from the word `legacy` in a filename.

The read-only Docker PostgreSQL census was point-in-time and did not dump case contents:

| Relation/state | Count |
|---|---:|
| Alembic head | `0010_preserve_chat_reports` |
| Cases | 2 |
| Chat threads | 2 |
| Unlinked Chat threads | 0 |
| Chat messages | 0 |
| Chat runs | 0 |
| Active Chat runs | 0 |
| Case runs | 0 |
| Active Case runs | 0 |
| Case results | 0 |
| Clarifications | 0 |
| Evidence snapshots | 0 |
| Chat reports | 0 |
| RAG contexts | 0 |

Foreign-key/orphan checks in the census reported no violations. This is not a freeze-window or deployment receipt; it only describes the observed database state at the time of the read.

The pre-edit regression receipts were captured before deleting the old execution-only tests: backend `459 passed, 1 skipped, 2 subtests` and frontend `168 tests` across the then-current frontend suite. They are baseline evidence, not a claim that every old execution path remains supported. The final current-checkout verification is recorded under Checkpoint F.

## Checkpoint B — native capability and conditional MITRE parity

Status: PASS for native worker-to-report verification at the provider boundary; live provider verification not performed.

The active path is:

```text
CaseRun -> case_run_execution -> native case analysis
        -> source-bound findings and exact evidence validation
        -> conditional MITRE applicability gate
        -> existing RAG client and Case MITRE mapping
        -> one Case-owned result/publication
```

| Capability | Native owner | Evidence |
|---|---|---|
| General summary/analysis | `backend/app/services/workflow/case_run_execution.py`, `backend/app/services/case_analysis/case_native_*` | Native CaseRun tests and full backend suite |
| Optional Chat Q&A/ASK | `backend/app/services/chat/case_chat.py`, `case_ask_completion.py` | Case Chat and retry PostgreSQL tests |
| Clarification continuation | `backend/app/services/followup/case_clarification.py`, Case clarification routes/history | Clarification and CaseRun tests |
| Conditional MITRE | `case_analysis/mitre_applicability_gate.py`, `workflow/case_mitre_augmentation.py`, `clients/rag_client.py` | 56 focused tests, 6 native PostgreSQL integration scenarios, and 2 subtests |
| Retry, lease, cancellation, recovery | `workflow/case_run_service.py`, `case_run_claim.py`, `case_run_heartbeat.py`, `case_run_recovery.py` | PostgreSQL retry/recovery/concurrency tests |
| Reports/source inspection | `case_reports.py`, `case_report_*`, retained report serializers | Case report PostgreSQL tests and full suite |

The focused command was:

```powershell
cd F:\Cybercase Framework\backend
..\env_mitre\Scripts\python.exe -m pytest -q tests/test_case_mitre_augmentation.py tests/test_case_native_validation.py tests/test_chat_rag_client.py tests/test_mitre_applicability_provider.py tests/test_mitre_applicability_validation.py tests/test_source_citations.py tests/test_claim_anchored_pipeline.py --tb=short
```

Result: `56 passed, 2 subtests passed in 4.15s`.

The tests exercise nontechnical skip, technical retrieval, ambiguous/invalid gate results, empty retrieval, transport failure, case-claim support, retrieved ATT&CK support, and exact source-role validation at the mocked HTTP boundary. No paid or live provider call was made. Browser/provider success must not be inferred from these mocks.

The native integration command was:

```powershell
cd F:\Cybercase Framework\backend
$env:CYBERCASE_TEST_DATABASE_URL='postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/cybercase_framework'
..\env_mitre\Scripts\python.exe -m pytest -q --disable-warnings tests/test_case_native_augmentation_postgres.py
```

Result: `6 passed in 6.33s`. This uses the real CaseRun execution, conditional augmentation, PostgreSQL result/publication persistence, and Case report/PDF rendering while mocking only the provider boundary. It covers not-applicable skip, technical mappings, empty/insufficient retrieval, transport failure, partial mappings, and no supported match. The failure scenario also mutates the persisted result after report creation and verifies that the immutable report snapshot and rendered PDF retain the original failure outcome. Only trace-validated Case associations are rendered as mappings; unmapped retrieved rows are separately labeled retrieved-only and have no Case evidence sources.

## Checkpoint C — writers, readers, and frontend callers

Status: native writer cutover and relation-aware reader PASS; final compatibility/cutover approval BLOCKED by an unresolved historical policy decision.

Backend behavior:

- `POST /api/v1/chats/{thread_id}/messages` resolves the owning Case. For a linked thread it calls `create_case_chat_message_and_run`, commits the Case-owned message/run, and schedules `process_case_run`.
- `GET /api/v1/chats/{thread_id}/case-link` returns the proven relation's actual Case ID, or `historical_unavailable` when no relation exists; it never treats a Chat thread ID as a Case ID.
- An unlinked historical thread returns HTTP `410` with `legacy_chat_execution_retired`; it is read-only and cannot enter the old worker.
- `GET /api/v1/chats/{thread_id}/runs/{run_id}` remains a historical ChatRun reader for preserved records.
- Application lifespan recovery starts only `recover_expired_case_runs` and `monitor_case_runs`.
- No production caller remains for `process_chat_run`, the old ChatRun creation/retry writer, or old ChatRun recovery.

Frontend behavior:

- `ChatWorkspace` and `ChatWorkspaceLayout` use the Case as the active workspace and keep Chat as an optional panel.
- Case intake/materials/analysis use native Case contracts. The active Case workspace does not submit through the retired Chat writer or poll a ChatRun.
- The `/chat` layout resolves the relation endpoint before routing. A linked thread goes to the actual Case route; an unlinked thread goes to an explicit historical-unavailable state, and an unavailable/unauthorized lookup goes to an explicit unavailable state. The leaf route remains a framework compatibility route.
- Native pending submission identity is account-scoped browser state and restores a lost-response retry without using historical `retry_request` metadata.
- Completion refreshes the Chat detail so a persisted assistant analysis publication appears when the user opens Chat.
- Native technical context separates validated Case mappings from retrieved-only rows and renders explicit outcomes for skip, insufficient/empty, no supported match, failure, and invalid trace. It does not infer a historical augmentation status or fabricate Case provenance.

The relation-aware route tests were run with:

```powershell
cd F:\Cybercase Framework\backend
& '..\env_mitre\Scripts\python.exe' -m pytest -q --disable-warnings tests/test_chat_case_link.py tests/test_route_surface.py
```

Result: `7 passed, 1 warning in 2.45s`, including linked threads whose Case ID differs from the Chat thread ID, unlinked historical threads, missing threads, and ownership rejection.

The unresolved policy is arbitrary old unlinked Chat IDs/deep links. The current database has zero unlinked threads, but there is no approved historical relation-mapping/backfill contract. No UUID coincidence, silent relink, synthetic Case, or fabricated snapshot was introduced. The `410` behavior is therefore implemented as a safe retirement boundary, but it must be explicitly accepted before a production compatibility cutover.

## Checkpoint D — drain and concurrency rehearsal

Status: BLOCKED. The required scoped mixed-worker/admission-freeze evidence was not established; no live drain or cutover was authorized.

The available rehearsal used a disposable PostgreSQL schema created by `backend/tests/run_recovery_support.py`. It populated queued, running, failed legacy ChatRuns and an expired native CaseRun. A test-local retirement helper marked only queued/running legacy rows as `failed/chat_run_interrupted`, left the already-failed row historical, and ran native CaseRun recovery concurrently. It asserted that the native run became `failed/case_run_interrupted` and that no ChatRun was created for the native Case. This is supporting policy/concurrency evidence only: it does not exercise an old application worker racing a native worker, an admission-freeze barrier, lease/publication conflict across worker versions, or a scoped drain controller.

```powershell
cd F:\Cybercase Framework\backend
$env:CYBERCASE_TEST_DATABASE_URL='postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/cybercase_framework'
..\env_mitre\Scripts\python.exe -m pytest -q tests/test_legacy_execution_drain_postgres.py tests/test_legacy_execution_retirement.py tests/test_case_auth_transaction_postgres.py tests/test_case_chat_postgres.py tests/test_case_chat_retry_postgres.py tests/test_case_run_retry_postgres.py tests/test_case_reports_postgres.py --tb=short
```

Result: `12 passed in 20.80s`.

The gate remains blocked despite that result. The live census observed zero queued/running ChatRuns, but no admission freeze, old-version drain, deployment restart, backup/restore rehearsal, or future-window observation was authorized or performed. Failed legacy work remains historical/read-only; it is not converted to a native run. A future cutover must add a bounded admission-freeze and mixed-worker/lease/publication race rehearsal on disposable PostgreSQL before any live action is considered.

## Checkpoint E — evidence-based deletion

Status: PASS for the verified execution-only candidates. Historical readers and migrations were retained.

### Deleted backend execution modules

| Deleted file | Last supported caller | Replacement | Data policy |
|---|---|---|---|
| `backend/app/services/chat/analysis_run_config.py` | old ChatRun execution configuration | CaseRun configuration carried by native run contracts | Do not rewrite stored historical payloads |
| `backend/app/services/chat/chat_run_creation.py` | old Chat message -> ChatRun writer | `chat/case_chat.py` and `workflow/case_run_service.py` | Preserve ChatMessage/ChatRun rows for reading |
| `backend/app/services/chat/chat_run_retry.py` | old ChatRun retry writer | native CaseRun retry/supersession policy | No old retry admission; no data conversion |
| `backend/app/services/chat/document_provenance.py` | old execution-only provenance adapter | native Case evidence source/revision binding | Never manufacture old snapshots/bindings |
| `backend/app/services/workflow/analysis_execution_receipt.py` | old ChatRun execution receipt | native CaseRun execution receipt | Historical JSON remains readable where its reader is retained |
| `backend/app/services/workflow/analysis_pipeline_context.py` | old ChatRun pipeline context | `case_run_execution.py` native context | No historical context rewrite |
| `backend/app/services/workflow/chat_run_claim.py` | old worker claim | `case_run_claim.py` | Existing ChatRun rows are not claimed by native worker |
| `backend/app/services/workflow/chat_run_completion.py` | old ChatRun completion | `case_run_completion.py` / `case_ask_completion.py` | Preserve historical terminal records |
| `backend/app/services/workflow/chat_run_contracts.py` | old ChatRun execution constants/contracts | native CaseRun contracts | Retain schema/API readers elsewhere |
| `backend/app/services/workflow/chat_run_failure.py` | old ChatRun failure writer | `case_run_failure.py` | Historical failures are read-only |
| `backend/app/services/workflow/chat_run_locks.py` | old ChatRun lock path | Case lock/lease ownership | No live old worker lock path remains |
| `backend/app/services/workflow/chat_run_store.py` | old ChatRun persistence store | native CaseRun services | Existing ChatRun data is not deleted |
| `backend/app/services/workflow/outcome.py` | old result coercion/response path | native result coercion in CaseRun execution/client boundary | Preserve report/history readers |
| `backend/app/services/workflow/pipeline_execution.py` | `process_chat_run` execution path | `process_case_run` -> `execute_case_run` | No old execution fallback |
| `backend/app/services/workflow/question_execution.py` | old ChatRun question path | native Case ASK completion | Chat messages remain transcript, not evidence |
| `backend/app/services/workflow/rag_routing.py` | old ChatRun RAG routing | native applicability gate/client/mapping | External RAG remains non-evidence context |
| `backend/app/services/workflow/run_heartbeat.py` | old ChatRun lease heartbeat | `case_run_heartbeat.py` | Do not alter historical leases |
| `backend/app/services/workflow/run_recovery.py` | old ChatRun startup/monitor recovery | `case_run_recovery.py` | No live old recovery mutation |

### Deleted obsolete execution tests

These tests exercised only the retired ChatRun writer/worker/recovery paths and were removed after replacement coverage was verified:

```text
backend/tests/test_analysis_retirement_postgres.py
backend/tests/test_chat_raw_pipeline.py
backend/tests/test_claim_anchored_postgres.py
backend/tests/test_claim_anchored_workflow.py
backend/tests/test_mitre_applicability_pipeline.py
backend/tests/test_optional_rag_pipeline.py
backend/tests/test_run_recovery_postgres.py
backend/tests/test_stateful_clarification_domains.py
backend/tests/test_stateful_clarification_pipeline.py
```

Replacement coverage is retained in `test_case_runs_postgres.py`, `test_case_chat_postgres.py`, `test_case_chat_retry_postgres.py`, `test_case_run_retry_postgres.py`, `test_case_mitre_augmentation.py`, `test_case_native_validation.py`, `test_case_followup_history_postgres.py`, `test_case_reports_postgres.py`, `test_legacy_execution_drain_postgres.py`, `test_legacy_execution_retirement.py`, and the existing claim/binding/selection/citation suites.

### Deleted frontend execution state

```text
frontend/src/features/chat/workspace/chat-retry-request.ts
```

The old retry restoration path was replaced with account-scoped native pending Case Chat state in `use-chat-draft.ts`. Generated `ChatRetryRequest` and historical response fields remain because they are read/compatibility schema, not active execution.

The explicitly authorized obsolete dialog was also deleted:

```text
frontend/src/components/common/DeleteChatDialog.tsx
```

No production import remains; sign-out confirmation uses the shared confirmation dialog, and case deletion uses `DeleteCaseDialog`.

### Retirement-scoped changed files

Backend runtime and exports:

```text
backend/app/main.py
backend/app/routers/chat.py
backend/app/services/chat/__init__.py
backend/app/services/chat/chat_management.py
backend/app/services/chat/chat_message.py
backend/app/services/clients/__init__.py
backend/app/services/clients/rag_client.py
backend/app/services/followup/__init__.py
backend/app/services/reports/report_persistence.py
backend/app/services/workflow/__init__.py
backend/app/services/workflow/pipeline.py
```

Backend test adaptations/additions:

```text
backend/tests/run_recovery_support.py
backend/tests/test_account_persistence.py
backend/tests/test_analysis_pipeline_versioning.py
backend/tests/test_canonical_analysis_state.py
backend/tests/test_chat_rag_client.py
backend/tests/test_document_narrative_handoff.py
backend/tests/test_gap_claim_transport.py
backend/tests/test_raw_evidence_workflow.py
backend/tests/test_source_citations.py
backend/tests/test_stateful_clarification_metadata.py
backend/tests/test_case_reports_postgres.py
backend/tests/test_legacy_execution_drain_postgres.py
backend/tests/test_legacy_execution_retirement.py
```

Frontend runtime and transport:

```text
frontend/src/app/chat/[threadId]/chat/page.tsx
frontend/src/app/chat/layout.tsx
frontend/src/components/ChatWorkspace.tsx
frontend/src/components/ChatWorkspaceLayout.tsx
frontend/src/components/technical/TechnicalContextView.tsx
frontend/src/features/chat/routing/chat-route.ts
frontend/src/features/chat/runs/chat-polling.ts
frontend/src/features/chat/runs/use-chat-submission.ts
frontend/src/features/chat/workspace/chat-workspace-types.ts
frontend/src/features/chat/workspace/use-chat-draft.ts
frontend/src/features/chat/workspace/use-chat-thread-selection.ts
frontend/src/features/chat/workspace/use-workspace-submission-actions.ts
frontend/src/hooks/use-case-run-polling.ts
frontend/src/lib/api-client.ts
frontend/src/lib/technical-context.ts
```

Frontend test adaptations/additions:

```text
frontend/src/test/features/chat/ChatWorkspaceIntake.test.tsx
frontend/src/test/features/chat/chat-interrupted-retry.test.tsx
frontend/src/test/features/chat/chat-polling.test.ts
frontend/src/test/features/chat/chat-route.test.ts
frontend/src/test/features/chat/chat-session-selection.test.tsx
frontend/src/test/features/chat/chat-session-test-support.tsx
frontend/src/test/features/chat/chat-submission-retry.test.tsx
```

### Follow-up remediation after independent review

The following paths were changed after the independent FIX-THEN-SHIP review. They are listed separately from the earlier Luna retirement inventory so the follow-up scope is auditable:

Backend:

```text
backend/app/services/case_analysis/contracts.py
backend/app/schemas/message_metadata.py
backend/app/schemas/chat.py
backend/app/routers/chat.py
backend/app/services/chat/chat_management.py
backend/app/services/reports/case_report_persistence.py
backend/tests/test_case_native_augmentation_postgres.py
backend/tests/test_chat_case_link.py
backend/tests/test_case_native_validation.py
backend/tests/test_route_surface.py
```

Frontend:

```text
frontend/scripts/generate-api-types.mjs
frontend/src/lib/generated/ChatCaseLinkRead.ts
frontend/src/lib/generated/MessageMetadata.ts
frontend/src/lib/api-types.ts
frontend/src/lib/api-client.ts
frontend/src/app/chat/layout.tsx
frontend/src/app/chat-unavailable/page.tsx
frontend/src/features/chat/routing/chat-route.ts
frontend/src/features/chat/routing/LegacyChatRouteStateView.tsx
frontend/src/lib/technical-context.ts
frontend/src/components/technical/TechnicalContextView.tsx
frontend/src/test/lib/technical-context.test.ts
frontend/src/test/components/technical/TechnicalContextView.test.tsx
frontend/src/test/features/chat/chat-route.test.ts
```

The existing dirty changes in `AccountForm.tsx` and `HomeSections.tsx` were preserved and are not counted as follow-up retirement fixes; their pre-existing full-lint findings remain documented below.

### Retained by evidence

The following are intentionally not deleted:

- `backend/app/models/chat.py`, `schemas/chat.py`, and `models/rag_context.py`: ORM/API/history contracts, including ChatRun and persisted context readers.
- `backend/app/services/chat/chat_history.py`, `chat_message.py`, `chat_management.py`, `raw_evidence.py`, and `clarification_chain.py`: historical reads, shared raw-evidence/citation semantics, ownership, and transcript access. `chat_message.py` is reader-only after this retirement.
- `backend/app/services/reports/report_generation.py`, `report_snapshot.py`, `report_persistence.py`, and `ChatReportService`: historical serialization/read/PDF/report compatibility. Native Case report code uses retained serializers where required.
- `backend/alembic/versions/0001` through `0010` and `backend/alembic/baseline_versions/0005` through `0010`: no migration or table was deleted and no historical transformation was performed.
- `frontend/src/lib/api-client.ts` exports `createChatMessage` and `getChatRun` for compatibility; no active production component calls either symbol. Generated Chat contracts and `ChatRetryRequest` remain for historical payloads.
- `frontend/src/components/report/ChatReportView.tsx` and its tests: not mounted by the active Case workspace; retained pending an explicit historical UI policy.
- `frontend/src/components/intake/CaseIntakeView.tsx`: its historical projection branch remains, while the active workspace always supplies the native Case intake path.
- `frontend/src/app/chat/**` compatibility routes and `features/chat/routing/chat-route.ts`: framework discovery and safe redirects remain; no UUID-based historical relation is invented.
- `rag_service/**`, report redesign, file regrouping, scratch datasets, and all unrelated dirty work: unchanged or preserved.

## Checkpoint F — final verification

Status: code verification PASS with known unrelated lint findings; production cutover BLOCKED.

### Backend commands

```powershell
cd F:\Cybercase Framework
& 'C:\Users\kkham\.local\bin\ruff.exe' check backend/app backend/tests --target-version py311 --output-format concise
```

Result: `All checks passed!`

```powershell
cd F:\Cybercase Framework\backend
& '..\env_mitre\Scripts\python.exe' -m compileall -q app tests
```

Result: passed.

```powershell
$env:CYBERCASE_TEST_DATABASE_URL='postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/cybercase_framework'
& '..\env_mitre\Scripts\python.exe' -m pytest -q --disable-warnings
```

Result: `434 passed, 1 skipped, 1 warning, 2 subtests passed in 43.51s` on the real PostgreSQL target. The tests create disposable schemas through the PostgreSQL helper; one test remains skipped, so this is not a claim of zero skips. The provider boundary is mocked; no paid or live LLM/RAG/MITRE call was made.

Import and route catalog:

```powershell
..\env_mitre\Scripts\python.exe -c "import hashlib,json; from app.main import app; inner=app.app; paths=sorted(inner.openapi()['paths']); payload=json.dumps(paths,separators=(',',':')).encode(); print('openapi-paths',len(paths)); print('openapi-sha256',hashlib.sha256(payload).hexdigest()); print('\\n'.join(paths))"
```

Result: 36 paths; OpenAPI path SHA-256 `86adeffc050b1f638ca2a9cf5713cccd9f63aef21f3b6c75f09c1a4766cb0630`. The catalog contains Case routes, optional Chat/history/report routes including the relation-aware `case-link` reader, auth, health, and document-ingestion routes; no top-level standalone RAG/report execution route was added.

### Frontend commands

```powershell
cd F:\Cybercase Framework\frontend
npm test -- --run
npx tsc --noEmit
npm run check:api-types
npm run build
```

Results: Vitest `43 files, 177 tests passed`; TypeScript passed; API-type drift check passed; Next.js production build passed with Next.js `16.2.10`/Turbopack.

The retirement-scoped ESLint invocation passed. Full `npm run lint` still reports only the known pre-existing errors in `src/components/auth/AccountForm.tsx:48` and `src/components/home/HomeSections.tsx:128`, plus the existing `<img>` warning at `HomeSections.tsx:232`; those files were not changed for this retirement.

```powershell
cd F:\Cybercase Framework
git diff --check
```

Result: exit 0. Git emitted Windows LF/CRLF normalization warnings for dirty files; no whitespace error was reported.

## Limitations and approval blockers

1. Live cutover is not authorized and was not performed. No Docker rebuild/restart, admission freeze, old-worker drain, deployment, or volume/data operation was run for this retirement.
2. The zero-active-run live census is point-in-time evidence only. It is not proof of no future old admission or a completed freeze window.
3. The unlinked historical Chat policy needs explicit contract approval. Current behavior is safe read-only/HTTP 410, with no conversion or silent relink; arbitrary historical deep-link resolution remains unconfirmed.
4. Authenticated browser E2E was not run. The available browser state was not an authenticated session, so Case intake -> analysis with Chat closed -> publication -> Q&A -> report/source inspection is not certified here.
5. No live paid LLM/RAG/MITRE provider call was made. Conditional MITRE behavior is verified at the mocked HTTP boundary only.
6. Backup/restore readiness and rollback against a deployed application version were not tested. Rollback must be an explicit application/version decision; do not roll back to a version that cannot read newly created native Case data, and do not auto-transform or drop old tables.
7. Native pending lost-response retry is account-scoped browser storage, not a new database retry table. The database still owns CaseRun request identity/status, but another browser or cleared storage cannot restore the local draft automatically.

## Final decision

The verified code change retires the old ChatRun execution writers, worker, recovery, and active frontend execution branches while preserving historical readers, API compatibility, Case evidence provenance, conditional MITRE isolation, and native CaseRun concurrency behavior. It is ready for parent review as an application change, but it is **not a complete retirement/cutover certification**: Checkpoint D remains blocked, and the unlinked-history policy plus a separately authorized live drain/deployment/rollback procedure still require approval.
