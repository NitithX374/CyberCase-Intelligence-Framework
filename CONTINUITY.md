# Continuity Ledger

## Snapshot

- 2026-09-17 [USER] SUPERSEDED: build adaptive Case Gap clarification first with LangChain structured model calls and LangGraph workflow/checkpoint state; ordinary Case Q&A was deferred at that point.
- 2026-09-17 [TOOL] Branch `audiit` started at `779e88b0ad8dcf71c7d8daa233e8b018b53ceda4`; current work is uncommitted.
- 2026-09-17 [USER] SUPERSEDED: new architecture preserved Case/Postgres evidence semantics, introduced LangGraph only for adaptive gap workflow, and kept ordinary Chat out of that phase.
- 2026-09-17 [USER] Main Analysis must use LangChain structured output while retaining exact quote, claim/source, MITRE, gap, and persistence validation.
- 2026-09-17 [USER] Clarification state is workflow-only: bounded questions/answers, pending question, attempts, resolution, and committed source IDs; authoritative facts remain normal CaseSource rows.
- 2026-09-18 [USER] Continue a read-only dead-legacy audit focused on necessity, over-engineering, redundancy, and the concurrent CaseRun contract: multiple active runs, retry beside newer runs, and the requested partial index migration.
- 2026-09-18 [USER] New attached request starts a frontend-wide simplification audit; Phase 1 is audit only and must not edit frontend production code.
- 2026-09-18 [USER] Additional Phase 1 scan requested for statically one-use components and multi-hop prop forwarding.
- 2026-09-18 [USER] New attached interaction-architecture request requires a read-only Phase 1 audit before implementation; target is one persisted Case state shared by Analysis, Chat, and explicit Follow-up workflow.
- 2026-09-18 [CODE] Approved implementation now uses the existing Case aggregate and child rows as the shared context boundary; no child-ID arrays, snapshot tables, or new migration were added.

## Done (recent)

- 2026-09-17 [CODE] Main Case Analysis now uses production LangChain ChatModel structured output while retaining CyberCase trace, quote, source, gap, and MITRE validation.
- 2026-09-17 [CODE] Adaptive Gap Clarification uses typed LangGraph interrupt/resume state, durable PostgreSQL checkpoints, deterministic gap selection, bounded attempts, stale revision checks, and evidence-bound persistence; factual answers alone create deduplicated CaseSource rows and trigger re-analysis.
- 2026-09-17 [CODE] Case Chat supports restored pending questions, answered/unavailable/skipped follow-ups, explicit clarification session identity, empty-source ordinary Ask, and request-keyed optimistic user rendering with a pre-LLM delay.
- 2026-09-17 [TOOL] Playwright E2E passed: 3 tests, including LangChain OpenAI-compatible provider stub, adaptive clarification, PostgreSQL checkpoint, evidence commit, and re-analysis.
- 2026-09-18 [CODE] Completed Pydantic validation architecture audit and simplification: eliminated hidden field mutations in `GapAnswerInterpretation`, `ClarificationResumeAnswer`, and `GapNextStep`; moved text normalization to `@field_validator`; removed dead version injection in `AnalysisPipelineConfig`; explicitly mapped non-answered chat message content in persistence.
- 2026-09-18 [CODE] Completed Report models and versioning simplification: deleted dead speculative version dictionaries (`REPORT_SECTION_IDS_BY_VERSION`, `REPORT_SECTION_HEADINGS_BY_VERSION`); converted internal pipeline models (`CaseReportInput`, `CaseReportTechnicalAugmentation`) to lightweight dataclasses; simplified `StructuredReport` defaults; deleted `validate_augmentation_outcome` and `mitre_table_for_validation` in projection; regenerated frontend API types.
- 2026-09-18 [CODE] Follow-up answers now persist and return an assistant acknowledgement as `reply_message`; the frontend merges it with any next question, renders friendly unavailable/skipped labels, and clears the composer after acceptance.
- 2026-09-18 [CODE] Removed dead legacy follow-up engine: deleted `backend/app/services/followup/decision.py` and `policy.py` (~620 lines); pruned obsolete contracts (`FollowUpDecision`, `FollowUpExchange`, `FollowUpPolicy`, `FollowUpPolicyResult`, `FollowUpResolution`); retained `answer_indicates_unavailable` in `contracts.py` and read-only history endpoint `get_case_followups` in `case_followup.py`.
- 2026-09-18 [CODE] Slimmed `GapClarificationState` to ten workflow fields; question text/target now live in persisted `ChatMessage` metadata and are reloaded by message ID before interrupt/resume.
- 2026-09-18 [CODE] Added in-memory Case Chat context loading from latest analysis, bounded chat messages, active clarification metadata, and run-linked RAG context; ordinary Chat now sends that context through the existing reasoning payload.
- 2026-09-18 [CODE] Removed the obsolete `GapNextStep.reply` action and graph reply node; acknowledgement persistence remains in the answer transaction.
- 2026-09-18 [CODE] Shortened migration `0006` revision to `0006_case_run_active_idx` so it fits Alembic's `version_num varchar(32)` column; added a regression assertion.

## Decisions

- 2026-09-17 [USER] D001 ACTIVE: smallest clear thesis-prototype change; no speculative compatibility or orchestration layers.
- 2026-09-17 [CODE] D029 ACTIVE: source-bundle module owns canonical provider serialization; `request_case_reasoning` owns shared generation; Chat has no separate reasoning adapter.
- 2026-09-17 [USER] D030 ACTIVE: conversation history can resolve references, but only Case sources establish Case facts; ordinary clarification remains conversation-only.
- 2026-09-17 [USER] D031 ACTIVE: formal follow-up remains the only Chat-adjacent path that can create Case evidence and trigger re-analysis.
- 2026-09-17 [CODE] D032 SUPERSEDED: the user-directed adaptive Gap workflow combines the shared reasoning boundary with LangChain transport and LangGraph workflow state; ordinary Q&A redesign remains deferred.
- 2026-09-17 [CODE] D033 ACTIVE: PostgreSQL remains Case truth and LangGraph checkpoint state is workflow-only; no SQL tools or duplicated Case evidence are stored in checkpoints.
- 2026-09-17 [CODE] D034 ACTIVE: production provider calls use LangChain; the explicit HTTP client path exists only for deterministic injected transport fixtures.
- 2026-09-17 [CODE] D035 ACTIVE: ordinary Ask may reason over an empty canonical source bundle to request missing context; only formal Main Analysis and Gap clarification require persisted Case evidence.
- 2026-09-17 [CODE] D036 ACTIVE: `CHAT_ASK_START_DELAY_SECONDS` defaults to 1.0 after user-message commit and before ordinary Q&A reasoning; optimistic cache entries use the request key and are replaced by the persisted receipt.

- 2026-09-18 [USER] D037 ACTIVE: concurrent CaseRuns may be created and failed runs may be requeued beside other runs; the active index must be nonunique and partial, with migration/test parity still required.
- 2026-09-18 [USER] D038 ACTIVE: current prototype accepts the limited concurrency impact because the primary workloads are Chat and analysis; no FIFO scheduler or active-run collection is required.
- 2026-09-18 [USER] D039 ACTIVE: the newest-created analysis run has precedence; a late completion from an older run must not replace the newest Case result pointer.
- 2026-09-18 [USER] D040 PROPOSED: slim `GapClarificationState` to workflow identity/lineage, a gap pointer, transient answer/interpretation, and control/result fields; move DB-derived history and runtime/config values out of checkpoint state.
- 2026-09-18 [CODE] D041 ACTIVE: ordinary Case Chat may read the latest analysis, active clarification, bounded conversation history, and run-linked RAG context from existing Case child rows through an in-memory loader; only Case sources remain factual authority.

## Now / Next

- 2026-09-17 [CODE] Implementation is complete in the working tree and remains uncommitted on branch `audiit`; the empty-Case Chat regression and immediate Ask rendering are fixed and final validation is complete.
- 2026-09-17 [TOOL] Final review confirmed no active production caller for the deleted claims-only Chat adapter, old single-turn submission path, or completion-time evaluator; only read-only follow-up history remains.
- 2026-09-18 [TOOL] Read-only audit report added at `docs/audits/2026-09-18-dead-legacy/dead-legacy-audit.md`; no production implementation was changed by the audit.
- 2026-09-18 [TOOL] SUPERSEDED: an earlier local run had backend collection blocked by missing `asyncpg`; PostgreSQL-backed integration now runs with the installed environment.
- 2026-09-18 [CODE] User-authorized bounded follow-up added `0006_case_run_concurrent_active_index.py` and updated migration/schema/retry expectations; no scheduler or frontend change was added.
- 2026-09-18 [DOC] Frontend Phase 1 report added at `docs/audits/2026-09-18-frontend-simplification/frontend-simplification-audit.md`; all 65 production TS/TSX paths are classified and no frontend cleanup was applied.
- 2026-09-18 [TOOL] Frontend baseline for the simplification audit: API type check and strict TypeScript compile passed; lint passed with the existing `HomeSections.tsx:239` image warning; Vitest had 106 passed and 2 label-contract failures.
- 2026-09-18 [DOC] The frontend report now includes the one-use and prop-hop appendix: 57 static one-use JSX component definitions, one confirmed dead `hasAnalysisContext` prop, and seven traced multi-hop chains.
- 2026-09-18 [CODE] Frontend Phase 2 cleanup removed zero-caller route/hooks/props/icons/exports, removed the preview route exception, centralized run polling in `CaseShellLayout`, and removed the `useCaseChat` session compatibility facade.
- 2026-09-18 [TOOL] Baseline label expectations were committed as `6e0b7aa`; the post-cleanup frontend suite has 109 passing tests and the production build succeeds.
- 2026-09-18 [TOOL] Chat regression validation passed: backend follow-up integration, frontend Vitest, three rendered Playwright flows, strict TypeScript, API types, production build, compileall, and diff check; the full backend suite has one unrelated pypdfium2 concurrent-render crash.
- 2026-09-18 [TOOL] SUPERSEDED: Phase 1 traced Run Analysis, normal Chat, Gap Clarification, revision freshness, current-gap derivation, MITRE persistence, and frontend query ownership; at audit time normal Chat omitted analysis and active clarification context.

## Open questions

- 2026-09-17 [USER] Plugin Management was named without a concrete install/inspect/remove action; no plugin connection changes were made.
- 2026-09-17 [TOOL] Build Web Apps browser/E2E validation covered the adaptive Case UI; the existing image optimization lint warning remains outside this change.
- 2026-09-18 [USER] Newest-run precedence resolves active visibility and result ordering; retry supersession remains a separate choice under D037.
- 2026-09-18 [TOOL] No FIFO scheduler exists, and none is required by D038; current route scheduling dispatches an explicit run ID through FastAPI background tasks.
- 2026-09-18 [TOOL] The requested partial active-run index has no traced current status-filtered consumer after guard removal; validate scheduler/recovery/monitoring use before carrying the index cost.
- 2026-09-18 [TOOL] Run lifecycle coverage now proves child cache observers read seeded runs without fetching; no browser run-lifecycle smoke was performed in this pass.
- 2026-09-18 [TOOL] Audit found a contained minimal path: assemble a typed read-only Chat context from existing CaseSource/CaseAnalysisResult/ChatMessage/CaseRun/RagContext rows, extend the existing reasoning payload, and add focused tests; no DB migration is needed unless literal immutable snapshot tables are required.
- 2026-09-18 [CODE] Completed the contained Chat context path and focused tests; production behavior now follows D041 without adding persisted projections.
- 2026-09-18 [TOOL] Current checkout has no normalized Gap/Question/Answer tables: gaps are validated from `CaseAnalysisResult.trace_json`, while questions/answers are `ChatMessage` rows plus metadata; any `gap_id`-only state refactor must derive the gap from the source analysis and preserve message metadata without inventing new tables.
- 2026-09-18 [USER] Case context may be rooted at the existing `Case` aggregate; prefer existing child foreign keys and relationships, with only justified singular current pointers, over arrays of child IDs or a new persisted projection.

## Working set

- 2026-09-18 [DOC] `docs/audits/2026-09-18-frontend-simplification/frontend-simplification-audit.md`
- 2026-09-18 [CODE] `frontend/src/app/case/[caseId]/layout.tsx`
- 2026-09-18 [CODE] `frontend/src/app/case/[caseId]/intake/page.tsx`
- 2026-09-18 [CODE] `frontend/src/app/case/[caseId]/report/page.tsx`
- 2026-09-18 [CODE] `frontend/src/components/overview/CaseOverviewView.tsx`
- 2026-09-18 [CODE] `frontend/src/components/conversation/WorkspaceChatPanel.tsx`
- 2026-09-18 [CODE] `frontend/src/components/common/icons.tsx`
- 2026-09-18 [CODE] `frontend/src/components/auth/AccountGate.tsx`
- 2026-09-18 [CODE] `frontend/src/hooks/useCaseQueries.ts`
- 2026-09-18 [CODE] `frontend/src/features/chat/useCaseChat.ts`
- 2026-09-18 [CODE] `frontend/src/features/chat/useChatDraft.ts`
- 2026-09-18 [CODE] `frontend/src/test/hooks/use-case-run-polling.test.tsx`

## Receipts

- 2026-09-17 [TOOL] LangGraph PostgreSQL migrations and Windows SelectorEventLoop E2E setup were verified; earlier empty-source and optimistic Ask regressions passed their focused backend/frontend/Playwright checks.
- 2026-09-18 [TOOL] Audit inventory: 416 tracked code files; 242 current production files; 400 backend and 392 RAG-app Python function definitions; 980 TypeScript function-like nodes.
- 2026-09-18 [TOOL] `npm test -- --reporter=dot` passed: 29 files and 108 tests; `npm run check:api-types` passed.
- 2026-09-18 [TOOL] Backend pytest collection stopped at missing `asyncpg`; Ruff bounded F401/F811/F841 scan reported 19 findings.
- 2026-09-18 [TOOL] `git diff --check` passed with only Git line-ending warnings; the working tree remains intentionally dirty from the ongoing implementation.
- 2026-09-18 [TOOL] Migration chain test passed 2 tests and changed migration/test files compile; route-surface collection remains blocked by missing `asyncpg`.
- 2026-09-18 [TOOL] Frontend inventory counted 65 production TS/TSX files at 9,115 lines and 32 test TS/TSX files at 3,464 lines.
- 2026-09-18 [TOOL] Current Vitest failures are `AnalysisEvidenceReferences.test.tsx` and `TechnicalContextView.test.tsx`; both expect old `Source source-1` labels while the dirty tree renders `Case narrative`.
- 2026-09-18 [TOOL] TypeScript JSX scan found 57 named components with one static JSX call; map-rendered cards and stateful feature boundaries were retained, while small pure wrappers were marked for possible inlining.
- 2026-09-18 [TOOL] Prop trace identified the deepest chains in findings source chips and chat evidence drawers; `WorkspaceChatPanelProps.hasAnalysisContext` is declared and passed but never read.
- 2026-09-18 [TOOL] Post-cleanup validation: Vitest 29 files/109 tests, strict TypeScript, API type check, lint with one existing warning, Next production build, and `git diff --check` passed.
- 2026-09-18 [TOOL] Residual scan found `useCaseRunPolling` only in the case shell and focused lifecycle tests/comments; no deleted compatibility symbol or preview route reference remains.
- 2026-09-18 [TOOL] Pydantic architecture cleanup validation: backend pytest passed 187 tests, 10 skipped, 2 subtests passed (with Python 3.12.2 / `env_mitre`); `git diff --check` passed.
- 2026-09-18 [TOOL] Report simplification validation: backend pytest passed 189 tests, 10 skipped (0 failures); Vitest passed 29 files / 109 tests; API types regenerated and verified; `git diff --check` passed.
- 2026-09-18 [TOOL] Follow-up fix regression: before the patch the PostgreSQL route returned `assistant_message: null`; after it the focused backend test passed, full frontend Vitest passed 29 files/109 tests, and Playwright passed Ask, answered follow-up, and unavailable follow-up with visible acknowledgement and empty composer.
- 2026-09-18 [TOOL] Full backend pytest reached 198 passed but failed on unrelated `tests/test_document_ingestion.py::test_concurrent_ocr_is_bounded_by_semaphore` due a pypdfium2 access violation; excluding that file, 185 passed with 2 subtests and targeted Chat tests remain green.
- 2026-09-18 [TOOL] Streaming audit found no SSE/WebSocket/ReadableStream or LangChain/LangGraph stream path; Chat waits on `ainvoke`, analysis exposes only run polling and post-completion execution receipts.
- 2026-09-18 [TOOL] Context implementation validation passed PostgreSQL-backed Chat/reasoning integration (6 tests including the new aggregate-context case), backend tests excluding the known pypdfium2 crash file (186 passed, 2 subtests), frontend Vitest (112 passed), strict TypeScript, API type check, Ruff, compileall, and diff check.
- 2026-09-18 [TOOL] PostgreSQL logs traced recurring `unexpected EOF ... open transaction` to the backend restart loop caused by migration `0006` string truncation; after the slug fix, migration applied and backend/PostgreSQL remained up without new EOFs during verification.
- 2026-09-18 [USER] SUPERSEDED: work was paused before hotfix after a new Case Sources → Analysis → sufficiency/gaps flow sketch; implementation resumed after the user's approval to follow the original plan.
