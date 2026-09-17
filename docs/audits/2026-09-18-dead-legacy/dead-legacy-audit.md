# Dead and redundant code audit — 2026-09-18

## Ledger snapshot

- Scope: the current working tree on `audiit`, including the concurrent CaseRun change supplied in this conversation.
- Goal: ask what current route, persistence contract, user-visible behavior, test contract, or operational entrypoint requires each file and function.
- The audit phase was read-only. After the user authorized execution, the bounded follow-up added the CaseRun migration and updated its schema/retry tests; no unrelated production behavior was changed.
- The working tree was already dirty before the audit. Existing changes, including `case_run_service.py` and `case_run.py`, belong to the ongoing implementation and were preserved.

## Method and coverage

I traced router registration from `backend/app/main.py` and `rag_service/app/main.py`, followed package imports and real callers, checked ORM relationships and Alembic files, and searched frontend route imports and hook consumers. I also ran AST inventories rather than treating a filename or a single unused-import warning as deletion proof.

The inventory covered 416 tracked Python/TypeScript/JavaScript source files: 242 current production files (108 backend, 97 frontend, and 37 RAG service files), plus 174 tests, evaluation programs, and support entrypoints. The Python inventory contains 400 backend function definitions and 139 classes, and 392 RAG-app function definitions and 63 classes. The TypeScript symbol pass found 980 function-like nodes, including callbacks; anonymous React callbacks were attributed to their owning component or hook rather than called dead individually. Generated API types were included in the import search but were not proposed for hand editing.

The following classifications are used throughout:

- **Keep** — a current runtime entrypoint, framework callback, persistence boundary, or user-visible feature has been traced.
- **Candidate** — no current production caller was found, but a test, export, dynamic import, migration, or external contract still needs a deliberate decision before deletion.
- **Remove after migration** — the current production path is absent and the remaining caller is a stale test/export or compatibility path; migrate that caller and delete as one bounded change.
- **Do not classify as dead** — static evidence is insufficient or the code is intentionally an evaluation/support path.

## Findings

### A-01 — concurrent CaseRun database contract is now migration-backed

The working-tree model declares the non-unique partial index `ix_case_runs_active_per_case` in [case_run.py](/F:/Cybercase%20Framework/backend/app/models/case_run.py:35), and `enqueue_case_analysis` no longer performs the active-run query in [case_run_service.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_service.py:32). The new [0006_case_run_concurrent_active_index.py](/F:/Cybercase%20Framework/backend/alembic/baseline_versions/0006_case_run_concurrent_active_index.py:1) drops the unique index created by [0002_case_run_active_index.py](/F:/Cybercase%20Framework/backend/alembic/baseline_versions/0002_case_run_active_index.py:13) and creates the requested non-unique partial index. The schema parity and migration-chain tests now expect the new contract.

The migration is now present, but it still requires a PostgreSQL upgrade test before deployment. A downgrade can fail when multiple active rows already exist because recreating the unique index would reject that data; this is the expected consequence of downgrading a concurrent-run schema.

The partial index itself still needs a necessity check after the migration: the existing `ix_case_runs_case_id_created_at` already starts with `case_id`, and `serialize_case` loads the CaseRun relationship instead of issuing a status-filtered query. Keep the requested index if a scheduler, recovery query, or monitoring path will filter `queued`/`running`; otherwise it is an extra index with no traced consumer.

### A-02 — the failed-run “newer work” guard needs to align with run precedence (High)

The explicit active-run guard was removed, but [requeue_failed_case_run](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_service.py:141) still queries any newer CaseRun and raises `case_run_superseded`. Consequently, retrying an old failed idempotency key remains rejected when a newer run exists, including when that newer run is already failed or merely queued. This is different from “allow re-queuing a failed run even if another run exists.”

Keep the evidence-revision check because it protects Case truth. The new policy says a newly created analysis has precedence, so this guard may be retained as an optimization that avoids obsolete retries, but that is different from the requested removal of the active-run guard. If failed retries must still be accepted beside newer work, remove this guard and ensure the older retry can never replace the newer result.

### A-03 — newest-run-only serialization is accepted under the current policy

The current implementation deliberately chooses one `latest_run` with `max(created_at)` in [case_service.py](/F:/Cybercase%20Framework/backend/app/services/cases/case_service.py:23), then exposes only that row as `active_run_id` at line 60. Under the newly accepted policy that a newly created analysis has precedence, run B hiding older active run A is intentional: the UI follows the newest run and does not need an active-run collection.

This remains an operational cost because A may continue consuming resources, but it is not a dead-code or product correctness defect within the current prototype scope. Keep the single-ID contract and test that the newest run remains the visible authority.

### A-04 — completion ordering is nondeterministic when equal-revision runs overlap (High)

`complete_case_run` validates the evidence revision and then assigns `case.latest_analysis_result_id` to the result that commits in [case_run_completion.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_completion.py:36). With two runs created against the same revision, the last transaction to complete wins, regardless of creation time. That contradicts the new policy: an older run may overwrite a newer run that already completed.

Creation order is now authoritative. Completion must compare run timestamps or a monotonic sequence before changing the pointer; a late older completion may remain historical but must not become the latest Case result. Add an out-of-order completion test. The run-local execution code itself does not assume exclusivity and should remain.

### A-05 — no FIFO scheduler exists; the open question is real (Medium)

There is no `claim_next_case_run` or polling loop. [case_analysis.py](/F:/Cybercase%20Framework/backend/app/routers/case_analysis.py:38) schedules `process_case_run(run.id)` with FastAPI `BackgroundTasks`, and [case_run_claim.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_claim.py:16) claims only the explicitly supplied ID. Runs therefore execute in request/background scheduling order, not FIFO. `useCaseRunPolling` polls one selected ID and cannot impose ordering.

This is not dead code. The new policy makes arbitrary execution order acceptable because creation order, rather than completion order, determines authority. Do not add a scheduler solely to create FIFO behavior.

### A-06 — lock order can deadlock idempotent concurrent requests (Medium)

`enqueue_case_analysis` locks the Case and then locks the idempotency row in [case_run_service.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_service.py:39). `claim_case_run` updates/locks the CaseRun first and then locks its Case in [case_run_claim.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_claim.py:24). A duplicate enqueue and the background claim for the same run can therefore hold those two rows in opposite order. The same shape is present in failed-run requeue. The locks are not redundant—they protect idempotency and claim ownership—but their order needs a concurrency test before calling concurrent runs complete.

### A-07 — legacy deterministic follow-up decision and provider policy have no production caller (Remove after migration)

The adaptive graph now owns selection, question generation, interpretation, persistence, and resume. [graph.py](/F:/Cybercase%20Framework/backend/app/services/gap_clarification/graph.py:17) wires the active nodes, while [nodes.py](/F:/Cybercase%20Framework/backend/app/services/gap_clarification/nodes.py:75) and [persistence.py](/F:/Cybercase%20Framework/backend/app/services/gap_clarification/persistence.py:24) are called by that graph.

By contrast, [followup/decision.py](/F:/Cybercase%20Framework/backend/app/services/followup/decision.py:60) (`select_followup_gap`, `evaluate_followup_outcome`, history ranking, metadata builders) has no production importer; its callers are the old selection tests and the package re-export. [followup/policy.py](/F:/Cybercase%20Framework/backend/app/services/followup/policy.py:186) (`AnthropicFollowUpPolicy`, response extraction, policy coercion) is likewise test/package-only. `answer_indicates_unavailable` from [contracts.py](/F:/Cybercase%20Framework/backend/app/services/followup/contracts.py:122) is still used by adaptive `nodes.py`, and `case_followup.py` remains the live read-only history endpoint. Do not delete the whole package: remove the decision/policy contracts and stale tests after preserving that one shared predicate and the history contracts.

### A-08 — small backend compatibility helpers are candidates for removal (Remove after migration)

The following exact definitions have no current production caller after tracing routers, package exports, and tests:

- `lock_case_chat` in [chat/case_chat.py](/F:/Cybercase%20Framework/backend/app/services/chat/case_chat.py:34); the route calls `get_case_chat`, `ask_case`, and `submit_case_followup_answer` directly.
- `split_native_blocks` in [document_ingestion/parsers/pdf_text_parser.py](/F:/Cybercase%20Framework/backend/app/services/document_ingestion/parsers/pdf_text_parser.py:42); ingestion uses `normalize_text` and `inspect_pdf`.
- `image_dimensions` in [document_ingestion/rendering.py](/F:/Cybercase%20Framework/backend/app/services/document_ingestion/rendering.py:55); normalization uses PIL dimensions directly.
- `mitre_table_for_validation` in [reports/case_report_projection.py](/F:/Cybercase%20Framework/backend/app/services/reports/case_report_projection.py:144); report persistence derives MITRE IDs from the validated trace.
- `mitre_table_from_output` in [workflow/case_run_completion.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_completion.py:31); completion reads the technical augmentation object directly.
- `attach_case_augmentation` in [workflow/case_run_context.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_context.py:137); the active execution path uses `resolve_case_technical_context` and `attach_case_augmentation_receipt`.
- `map_rag_response` in [clients/rag_client.py](/F:/Cybercase%20Framework/backend/app/services/clients/rag_client.py:74); active workflow consumes validated `QueryResponse`, and only the old client tests/package export use this mapper.

These are good first cleanup candidates, but deleting them in isolation would leave tests and `__all__` misleading. Migrate/delete their stale tests in the same patch and run the backend suite.

### A-09 — frontend chat hook exposes a duplicated test-era session facade (Candidate)

Production [case layout](/F:/Cybercase%20Framework/frontend/src/app/case/[caseId]/layout.tsx:68) uses the direct fields returned by `useCaseChat`. The hook additionally constructs `sessionObj` and returns a second copy of selection, refresh, suspend, getters, and state at [useCaseChat.ts](/F:/Cybercase%20Framework/frontend/src/features/chat/useCaseChat.ts:168) and line 208. Search found `session.*` callers only in `chat-session-selection.test.tsx` and `chat-submission-retry.test.tsx`. `restoreCaseChat` at line 166 is an empty callback. `getSelection` creates a new `AbortController` signal without a consumer in production.

This is over-engineered compatibility surface, not a dead hook: `useCaseChat` and its direct fields are live. Replace test support with the direct public behavior, then remove the session object, no-op restore, and duplicated getters in a focused frontend change. Keep `selectCaseChat`/`suspendCaseChat` only if a real product caller is added.

### A-10 — `useCaseRun` is exported but has no production consumer (Candidate)

`useCaseRun` at [useCaseQueries.ts](/F:/Cybercase%20Framework/frontend/src/hooks/useCaseQueries.ts:102) is referenced by tests/types only; the layout, intake, report, and overview routes all use `useCaseRunPolling`. It can be removed after test cleanup, or retained as a deliberately supported one-shot query. The polling hook must stay because it drives run settlement and cache invalidation.

### A-11 — RAG `GraphRAGChain` is not a served path, but it is not proven dead (Do not classify as dead)

`POST /query` initializes `GraphRAGAgent` in [rag_service/app/main.py](/F:/Cybercase%20Framework/rag_service/app/main.py:16), and [routers/rag.py](/F:/Cybercase%20Framework/rag_service/app/routers/rag.py:39) calls that agent. The current evaluation runner also creates `GraphRAGAgent` in [evaluation/eval_runner.py](/F:/Cybercase%20Framework/rag_service/app/RAG/GraphRAG/evaluation/eval_runner.py:268). `pipeline/chain.py` explicitly says it is evaluation-only and has no app import, but `rag_service/tests/test_llm_content.py` still imports `GraphRAGChain` to exercise its response parser shape.

The chain can be retired only after removing or migrating that test and deciding whether the historical cross-lingual benchmark is still a deliverable. `cross_lingual.py` itself is not dead merely because the served agent no longer translates input: the chain and benchmark still import it.

### A-12 — the RAG `use_agent` request field is vestigial but contract-bound (Candidate)

`QueryRequest.use_agent` is ignored by the only pipeline in [rag_service/app/schemas/rag.py](/F:/Cybercase%20Framework/rag_service/app/schemas/rag.py:11), yet `backend/app/services/clients/rag_client.py` sends `use_agent=True` and both schemas use `extra="forbid"`. Removing it from one side breaks every current chat request with 422; remove it only as one backend/RAG contract change with regenerated types and route tests.

### A-13 — report rendering split is justified; one validation helper is not

HTML and PDF are separate current API outputs: [case_report_persistence.py](/F:/Cybercase%20Framework/backend/app/services/reports/case_report_persistence.py:79) routes them to `render_case_report_html` and `render_case_report_pdf`, and both share the active `build_case_report_display`. The split is a real output boundary, not redundant files. The uncalled `mitre_table_for_validation` listed in A-08 is the narrow cleanup candidate. Do not merge HTML/PDF renderers merely to reduce file count.

### A-14 — configuration mixins add navigation cost; only a few fields are dead candidates

`Settings` inherits seven one-use `BaseModel` mixins in [config.py](/F:/Cybercase%20Framework/backend/app/config.py:134). The mixins are not independently constructed by production code, so flattening them could reduce indirection, but it is a refactor rather than a safe dead-code deletion. Field-level tracing found `frontend_base_url` and `debug` with no current consumer, and `chat_followup_max_rounds` is used only by the legacy deterministic decision module; `chat_followup_enabled`, database settings, OCR settings, LLM targets, and report settings have live consumers. Remove unused fields only after checking deployment environment contracts.

### A-15 — Tailwind animation tokens are currently unused (Candidate)

The three `float-*` animations and `float` keyframe in [tailwind.config.ts](/F:/Cybercase%20Framework/frontend/tailwind.config.ts:14) have no class use in `frontend/src`. They are safe cleanup candidates if animation is not an external/demo contract. The Tailwind content paths and CSS theme tokens are configuration, not runtime dead components; do not delete them based on no direct TypeScript import.

### A-16 — static F401 output identifies cleanup, not dead behavior

Ruff reported 19 unused imports for the inspected scope. Six are in current backend production files (`config.py`, `models/case_run.py`, `followup/policy.py`, `gap_clarification/model.py`, `case_report_projection.py`, and `case_run_execution.py`); the remaining 13 are in RAG evaluation/support files. These are safe, bounded import cleanups only after checking type-only ORM relationships and package re-exports. They do not justify deleting their surrounding modules. In particular, `ChatMessage` under `TYPE_CHECKING` may be needed by string-based relationship annotations, and evaluation imports can be intentionally public package conveniences.

### A-17 — a few compatibility/no-op surfaces add cost without a current caller (Low)

`execute_claimed_work` in [case_run_execution.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_execution.py:111) accepts `**_kwargs`, although the production caller passes none. `existing_request_matches` in [case_run_service.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_service.py:177) is an async wrapper around one equality expression, and `ClaimedCaseRun.source_revision` is not read by the current application. Inline or remove these only with the stale tests/exports that depend on them.

`complete_case_run` repeats the same evidence-revision check at [case_run_completion.py](/F:/Cybercase%20Framework/backend/app/services/workflow/case_run_completion.py:54) and line 58; `validated_output` is pure and does not change the Case, so the second check has no demonstrated protection. Keep one check and test the stale-revision race if this is cleaned up.

The current RAG `HybridRetriever.close` catches every exception and does nothing at [hybrid_retriever.py](/F:/Cybercase%20Framework/rag_service/app/RAG/GraphRAG/retrieval/hybrid_retriever.py:90). That is an operationally silent fallback rather than a required compatibility boundary. Let the supported client close operation fail visibly or catch only a documented optional-client error. Intentional `pass` bodies for SQLAlchemy's declarative `Base` and exception subclasses are structural and should remain.

## File/function disposition register

This register answers the necessity question at the module boundary for every current production area; individual definitions were included in the AST/reference inventory and the named candidates above are the only deletion proposals.

| Area | Files/functions covered | Disposition and necessity question |
|---|---|---|
| Backend routers and `main.py` | auth, cases, materials, analysis, followups, reports, health; route error adapters and lifespan | **Keep.** Are they registered API/lifecycle entrypoints? Yes; OpenAPI route surface and startup tests exercise them. |
| Backend models and schemas | Case, CaseRun, CaseAnalysisResult, ChatMessage, sources, reports, auth, all Pydantic validators | **Keep.** Are fields consumed by ORM relationships, migrations, serialization, or request validation? Yes. Framework invocation explains definitions with no textual caller. |
| Main analysis | `case_analysis.py`, contracts, prompts, validation, quote resolver, provider stage, structured output, pipeline config | **Keep.** Does it produce validated evidence-bound analysis or Q&A? Yes; workflow and chat call it. The injected HTTP client branch is retained for deterministic fixtures per the current contract. |
| Adaptive clarification | every function in `gap_clarification/` | **Keep.** Is each graph node, checkpoint helper, persistence function, contract validator, or service method wired by `graph.py`/`service.py`? Yes. Do not confuse LangGraph state with duplicate Case truth. |
| Workflow | claim, execution, completion, technical augmentation, service/context helpers | **Keep active path; remove candidates in A-08.** Are functions called from `process_case_run` or completion? Yes, except the specifically listed compatibility helpers. Concurrent lock/order and pointer semantics need tests. |
| Case materials and ingestion | source bundle, material service, document parsers, OCR recognition, rendering | **Keep active path; remove `split_native_blocks` and `image_dimensions` after test migration.** Are upload/document functions reachable from material routes? Yes. |
| Follow-up | `case_followup.py` history; `contracts.py` unavailable predicate; `decision.py` and `policy.py` | **Split.** History and unavailable classification are live. Deterministic selection, old policy adapter, and related metadata are Remove after migration (A-07). |
| Reports | persistence, contracts, template/content, projection, display rendering, HTML/PDF | **Keep.** Are generate/list/HTML/PDF outputs current routes? Yes. Remove only the uncalled validation helper in A-08. |
| Frontend app/routes/layout | all `page.tsx`, `layout.tsx`, providers, workspace shell, chat panel/transcript, intake/material/overview/report/technical components | **Keep.** Are they route entrypoints or imported by the active Case workspace? Yes. Null route shells are intentional Next route boundaries. |
| Frontend hooks/API | `useCaseQueries`, `useCaseIntakeActions`, `useCaseDeletion`, `use-auth`, `useChatDraft`, `useCaseChatSubmission`, `apiClient`, generated contracts | **Keep active path; `useCaseRun` and the duplicated chat session facade are candidates.** Are functions used by a page or mutation? Yes except the two candidates. |
| Frontend evidence/overview utilities | `caseOverview`, `caseOverviewSource`, `technicalContext`, route/error/storage utilities | **Keep.** Do they parse authoritative source/trace data or support current UI navigation? Yes; they are used by overview, technical, transcript, and storage flows. |
| RAG served service | RAG app main/router, agent graph, retrieval, ingestion, models, provider, context store, legal reference | **Keep.** Are they initialized by the served service or reached by `/query`? Yes. The in-memory context store is an active HTTP snapshot boundary even though it is not durable Case truth. |
| RAG legacy/evaluation | `pipeline/chain.py`, benchmarks, evaluator, dataset/ingestion tools, archived results | **Do not classify as production dead.** Are they current serving code? Mostly no; are they deliberately invoked by tests/evaluation scripts or historical deliverables? Yes. Retire only with an explicit evaluation-baseline decision. |

## Verification receipts

- Frontend: `npm test -- --reporter=dot` passed — 29 files, 108 tests.
- Frontend API contract: `npm run check:api-types` completed successfully.
- Backend attempted with the current system Python; collection was blocked by missing `asyncpg` (`ModuleNotFoundError`). The earlier ledger receipt of 192 backend tests is from the prior completed implementation state and does not validate this concurrent-run working-tree change.
- Ruff scope `backend/app rag_service/app --select F401,F811,F841` returned 19 findings, recorded in A-16.
- No browser run or live PostgreSQL concurrency test was run in this audit. The required next test is a disposable PostgreSQL scenario with two same-revision runs, out-of-order completion, duplicate idempotent enqueue, failed-run retry beside a newer run, and fresh Alembic upgrade.
- `git status --short` remains intentionally dirty with the pre-existing implementation changes plus the bounded CaseRun migration/test updates.

## Recommended bounded cleanup order

1. Run the fresh PostgreSQL upgrade/contract test for the new concurrent-run migration; the stale `case_run_active` and old-index assertions are now updated.
2. Define active-pointer and completion-order semantics with PostgreSQL tests before touching UI abstractions.
3. Remove the legacy deterministic follow-up decision/policy path and the exact helpers in A-08 together with their stale tests/exports.
4. Simplify the frontend chat facade and remove `useCaseRun` only after the direct API tests replace session-only test support.
5. Clean the 19 imports and unused animation tokens as separate low-risk patches.
