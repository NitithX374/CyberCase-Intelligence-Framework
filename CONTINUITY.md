# Continuity Ledger

## Snapshot

- 2026-08-22 [USER] Superseded by the current audit request: the prior read-only library audit identified React Query and Zod boundaries without changing backend dataclasses.
- 2026-08-22 [USER] Superseded implementation goal: no frontend library implementation is in scope for the current read-only main-branch audit.
- 2026-08-21 [USER] Goal: make Main Case Analysis respond naturally in the language of the user's current message.
- 2026-08-21 [USER] Current diagnostic goal: explain two simultaneous chat runs and RAG queries in the live checkout.
- 2026-08-21 [CODE] Current branch is `feat/language-aware-analysis-personalization`; HEAD remains `3f37eddf5ad9d0c1268752334a736d158f1edad7` and all earlier dirty work is preserved.
- 2026-08-22 [CODE] Superseded: the current checkout for this audit is clean `main` at `c48bfd9`, equal to `origin/main`; no source changes were made by the audit.
- 2026-08-22 [CODE] Superseded: backend/frontend refactor changes are now uncommitted in the same `main` checkout; `rag_service` remains outside the approved scope and unchanged during implementation.
- 2026-08-22 [USER] Current read-only goal: run the full static, runtime, test, route/import, and dead-code audit on `main`.
- 2026-08-22 [USER] Superseded: the user authorized deletion of high-confidence dead code and unused surfaces found by the audit.
- 2026-08-22 [USER] New design goal: define a readable, bounded-context refactor for ambiguous names and oversized modules before implementation.
- 2026-08-22 [USER] Implementation scope is backend and frontend only; do not modify `rag_service` without explicit approval.
- 2026-08-21 [CODE] The latest user message deterministically selects Thai or English before the existing Main Case Analysis provider call.
- 2026-08-21 [CODE] Thai takes precedence when Thai script appears alongside English technical terms; English requires Latin letters; unrecognized language fails before provider invocation.
- 2026-08-21 [CODE] The prompt requests natural, direct, professional analyst phrasing without invented familiarity, identity, emotions, or unsupported personalization.
- 2026-08-21 [CODE] Response language survives bounded-context truncation and applies to answer prose, claim text, and MITRE association reasons while schema literals remain exact.
- 2026-08-21 [CODE] Main Case Analysis returns claims and MITRE associations in the same structured provider call; no second LLM call or migration was added.
- 2026-08-21 [CODE] Associations contain only association ID, exact technique ID, linked claim IDs, reason, `candidate_only`, and `external_technical_context`.
- 2026-08-21 [CODE] Exact Technique/Subtechnique membership is validated against the bound RagContext MITRE table; assistant prose and non-technique rows cannot admit IDs.
- 2026-08-21 [CODE] Associations never carry incident entity, relationship, evidence, or timeline references and never modify claim epistemic status.
- 2026-08-21 [CODE] The transcript renders a quiet expandable MITRE Candidate panel linked to claims and explicitly labels external context as not incident evidence.
- 2026-08-21 [CODE] Legacy, malformed, unbound, or unsafe association metadata renders no candidate panel.
- 2026-08-21 [TOOL] Full production backend, compileall, and diff whitespace checks pass after language-aware personalization.
- 2026-08-21 [CODE] Same-thread concurrent submissions serialize on the ChatThread row lock; the second distinct request receives HTTP 409 while one run is queued/running.
- 2026-08-21 [CODE] Different-thread runs can overlap in backend BackgroundTasks, but the single-worker RAG route invokes synchronous `rag_agent.query()` on its event loop, so RAG computation is effectively first-in-one-at-a-time.
- 2026-08-21 [CODE] Each completed RAG query receives a unique in-memory retrieval-context ID; queued time counts against each backend request's 300-second timeout.
- 2026-08-21 [USER] Symptom: `MITRE association technique ID is invalid` appears after retrieval.
- 2026-08-21 [CODE] The message is raised after the Main Case Analysis provider response by `detect_forbidden_provenance`; RAG can expose Group/Software IDs in the generic `technique_id` field, which is a confirmed trigger candidate.
- 2026-08-21 [USER] Stop and revert the attempted parallel-RAG implementation.
- 2026-08-21 [CODE] The bounded-thread parallel prototype, tests, Compose setting, and temporary branch were removed; current RAG behavior remains serialized.

## Done (recent)

- 2026-08-22 [CODE] Applied TanStack Query to chat thread/report remote state and Zod to persisted extraction parsing; OpenAPI type generation is reproducible without committing a large generated declaration.
- 2026-08-22 [TOOL] Deleted high-confidence dead report provider/prompt plumbing, broken CTINexus tests, unwired timeline/Card surfaces, the orphan schema helper, the unused model-download utility, and targeted production unused imports.
- 2026-08-22 [CODE] Split backend/frontend production boundaries into focused contracts, stages, persistence/rendering, polling, API, graph, inspector, and landing-page modules while preserving compatibility facades.
- 2026-08-22 [TOOL] Full backend regression passed: 267 tests and 24 subtests.
- 2026-08-22 [TOOL] Full frontend regression passed: 77 tests; TypeScript, targeted ESLint, and Next production build passed.
- 2026-08-22 [TOOL] Production LOC inventory passed: all `backend/app` and `frontend/src` source files are at or below 300 LOC.
- 2026-08-22 [USER] `rag_service` remained outside the implementation scope and was not modified.

## Decisions

- D001 ACTIVE 2026-08-20 [USER] Store deterministic metadata snapshots, not chain-of-thought or UI reinterpretations.
- D002 ACTIVE 2026-08-20 [CODE] Treat invalid or legacy metadata as absent for compatibility.
- D003 ACTIVE 2026-08-20 [USER] Keep explanatory UI visually quiet and predominantly monochrome.
- D004 ACTIVE 2026-08-20 [CODE] Backend exclusively assigns stable Case State IDs and rewrites matching delta references.
- D005 ACTIVE 2026-08-20 [USER] `reported` records report provenance and does not establish truth.
- D006 ACTIVE 2026-08-20 [USER] Claim type and epistemic status are independent; entity membership is contextual, not semantic support.
- D007 ACTIVE 2026-08-20 [USER] MITRE has one source of truth through `mitre_associations`; claims contain no MITRE IDs.
- D008 ACTIVE 2026-08-21 [USER] MITRE associations are candidate-only external interpretation linked through claims and are never incident evidence.
- D009 ACTIVE 2026-08-21 [CODE] Personalization adapts language and professional voice only; it never changes fact authority, epistemic status, or user identity assumptions.
- D010 ACTIVE 2026-08-22 [USER] Keep the current RAG answer-generation path unchanged; its simplification is out of scope.
- D011 ACTIVE 2026-08-22 [USER] Keep report generation deterministic and template-first; re-audit report dataclasses and dataflow before changing its boundaries.
- D012 SUPERSEDED 2026-08-22 [CODE] The earlier compatibility-preservation decision was superseded by the user's authorized dead-code cleanup; active report templates, routes, PDF branches, and persisted metadata remain preserved.
- D013 ACTIVE 2026-08-22 [CODE] Main Case Analysis must copy each referenced relationship's exact status; mixed-status relationship references must be split, and validation remains fail-closed.
- D014 ACTIVE 2026-08-22 [CODE] TanStack Query owns remote chat/report cache and mutation state; explicit idempotency and run polling remain in ChatWorkspace.
- D015 ACTIVE 2026-08-22 [CODE] OpenAPI types are generated from the live FastAPI contract on demand; the generated snapshot stays ignored to preserve the repository's modular file-size limit.
- D016 ACTIVE 2026-08-22 [USER] Delete high-confidence unreferenced or non-production dead code found on `main`; retain historical, evaluation, and manual tooling unless separately authorized.
- D017 ACTIVE 2026-08-22 [CODE] Preserve HTTP, database, RAG, and provenance contracts while splitting heavy backend/frontend modules by contracts, stages, validation, orchestration, persistence, and rendering; use compatibility facades during migration.
- D018 ACTIVE 2026-08-22 [USER] Do not modify `rag_service`; all implementation changes in this pass are limited to backend and frontend.

## Incident: Follow-up false proceed

- 2026-08-20 [USER] Symptom: a name-only submission produced analysis instead of a clarification.
- 2026-08-20 [CODE] Status: corrected with prompt semantics, normalization, and a deterministic material-gap guard.

## Incident: Clarification mutation rejected

- 2026-08-20 [USER] Symptom: the exact Thai clarification displayed `mutateCaseState failed`.
- 2026-08-20 [CODE] Status: corrected with closed categories, legacy normalization, and backend-owned ADD IDs; live V1 to V2 persistence passed.

## Incident: Baseline extraction validation failure

- 2026-08-22 [TOOL] Live chat run failed with `extraction_validation_failed`; valid JSON was logged before the failure.
- 2026-08-22 [TOOL] Evidence: a relationship targeted `Application Shimming` without a matching entity, and other relationships targeted free-text values.
- 2026-08-22 [CODE] Boundary: relationship endpoints are required to be entity IDs in `validate_baseline_extraction`; the pipeline stops before RAG when validation returns no Case State.
- 2026-08-22 [USER] Extraction repair/retry behavior remains out of scope; preserve fail-closed validation.

## Incident: Analysis trace relationship status mismatch

- 2026-08-22 [TOOL] Live run `b295c7c1-d7b4-4e9e-9910-c4e9cd69425d` passed extraction and RAG, then failed at Main Case Analysis with `analysis_trace_relationship_status_changed`.
- 2026-08-22 [CODE] `validate_analysis_trace` compares every claim `epistemic_status` to each referenced Case State relationship `status`; the bound Python snapshot is not rewritten between extraction and analysis.
- 2026-08-22 [CODE] Main Case Analysis now distinguishes `not_established` from `not_confirmed`, requires exact ID-based status copying, rejects mixed-status claim references, and preserves a compact status ledger under bounded truncation.
- 2026-08-22 [TOOL] Focused trace/prompt/input-mode tests passed 50 tests plus 8 subtests; compileall and scoped diff checks passed.
- 2026-08-22 [TOOL] Idempotent retry was blocked earlier at `extraction_validation_failed`; exact provider claim/status payload remains UNCONFIRMED because it was not persisted.

## State (Done/Now/Next)

- 2026-08-22 [TOOL] Superseded: the main-branch audit identified a missing RAG Dockerfile module, three non-reproducible CTINexus test surfaces, two unwired frontend components, and an uncalled database schema helper.
- 2026-08-22 [TOOL] Superseded: the pre-cleanup validation was backend production subset 279 passed plus 30 subtests, RAG 35 passed, frontend 80 passed; frontend lint/build, compileall, and Alembic heads passed.
- 2026-08-22 [TOOL] Report prompt trace: `chat_report_prompt_v2` and `AnthropicReportAdapter` are provider/compatibility and test-only surfaces; production reports use `chat_preliminary_analysis_template_v1` through deterministic template generation.
- 2026-08-22 [TOOL] Resolved: the authorized cleanup removed the provider/prompt compatibility branch and high-confidence dead surfaces; evaluation, historical migration, and manual tooling remain intentionally retained.
- 2026-08-22 [TOOL] Library audit completed: `@tanstack/react-query` owns live chat/report remote state, Zod owns frontend extraction metadata validation and inferred types, and no backend dataclass replacement is recommended.
- 2026-08-21 [CODE] Done: language-aware Main Case Analysis personalization is implemented without a migration or additional LLM call.
- 2026-08-21 [TOOL] Reproduced the exact validator message for Group/Software IDs, names, missing IDs, and noncanonical whitespace; valid T-shaped IDs pass this layer.
- 2026-08-21 [CODE] Now: parallel-RAG work is stopped; branch restored to `feat/language-aware-analysis-personalization`.
- 2026-08-21 [CODE] Now: retrieval-to-analysis MITRE validation is diagnosed; no production fix has been applied.
- 2026-08-21 [ASSUMPTION] No implementation was made because the user reported the symptom but did not explicitly request a fix.
- 2026-08-22 [CODE] Done: status-preserving Main Case Analysis prompt guidance and bounded relationship status projection are implemented; extraction validation remains out of scope.
- 2026-08-22 [CODE] Done: frontend chat/report server-state mutations use React Query, and extraction metadata uses Zod schemas with inferred types plus fail-closed reference checks.
- 2026-08-22 [TOOL] Done: `generate:api-types` successfully generated the live FastAPI contract; the generated 830-line declaration is ignored rather than committed.
- 2026-08-22 [TOOL] Now: live backend reloaded the status-preserving change; a live end-to-end success is UNCONFIRMED because the idempotent retry failed earlier during extraction validation.
- 2026-08-22 [TOOL] Done: authorized dead-code cleanup is applied on `main`; source changes and deletions are uncommitted and ready for review.
- 2026-08-22 [CODE] Done: approved backend/frontend architecture refactor is implemented; public import paths and runtime contracts remain stable through facades.
- 2026-08-22 [TOOL] Now: backend 267 tests plus 24 subtests, frontend 77 tests, TypeScript, full `frontend/src` ESLint, build, compileall, and scoped diff checks pass; the root `npm run lint` wrapper remains unconfirmed because it hung without output.

## Open questions

- 2026-08-22 [TOOL] Resolved: high-confidence dead-code candidates and the retired provider report adapter/prompt surface were removed; CTINexus test files were deleted because their referenced research packages are absent from the checkout.
- 2026-08-22 [TOOL] Remaining separate blocker: `rag_service/Dockerfile` does not copy `app/RAG/GraphRAG/model_registry.py`, although runtime config imports it; this is not dead code and was left unchanged.
- 2026-08-22 [TOOL] Design decision gate: repository guidance says reports are client-only while the live backend exposes persisted report routes/models; report scope must be confirmed before refactoring that boundary.
- 2026-08-21 [TOOL] UNCONFIRMED whether the live provider returned a Group/Software ID, a technique name, or whitespace; the persisted provider payload/log line is needed to distinguish the trigger.

## Working set

- 2026-08-22 [CODE] `backend/app/services/workflow/{pipeline,pipeline_execution,pipeline_mutation,pipeline_initial,pipeline_question}.py`
- 2026-08-22 [CODE] `backend/app/services/{case_analysis,case_state,extraction,followup,reports}/`
- 2026-08-22 [CODE] `backend/app/services/chat/{chat_message,chat_run_creation,clarification_chain}.py`
- 2026-08-22 [CODE] `frontend/src/features/chat/` and `frontend/src/lib/api-{client,types}.ts`
- 2026-08-22 [CODE] `frontend/src/components/relationships/` and `frontend/src/components/conversation/`
- 2026-08-22 [CODE] `frontend/src/components/home/`
- 2026-08-22 [USER] `rag_service/**` remains an explicit no-touch boundary for this implementation.

## Receipts

- 2026-08-20 [TOOL] Branch D production backend: 256 passed, 30 subtests passed; frontend: 68 passed across 9 files.
- 2026-08-21 [TOOL] Branch E focused backend structured/workflow suite: 92 passed, 18 subtests passed.
- 2026-08-21 [TOOL] Branch E full production backend excluding three research/CTINexus modules: 265 passed, 30 subtests passed, 2 warnings.
- 2026-08-21 [TOOL] Branch E full frontend: 74 passed across 11 files.
- 2026-08-21 [TOOL] Focused MITRE candidate frontend: 6 passed across 2 files after the final binding guard.
- 2026-08-21 [TOOL] ASK persistence regression with linked candidate association: 1 passed.
- 2026-08-21 [TOOL] Frontend ESLint and Next.js production build passed.
- 2026-08-21 [TOOL] RAG query route: 1 passed, 4 warnings after clearing inherited `SSLKEYLOGFILE`.
- 2026-08-21 [TOOL] Python compileall passed.
- 2026-08-21 [TOOL] `git diff --check` passed with only existing LF-to-CRLF notices.
- 2026-08-21 [TOOL] Language-personalization focused workflow: 65 passed, 11 subtests passed.
- 2026-08-21 [TOOL] Language-personalization full production backend: 269 passed, 30 subtests passed, 2 warnings.
- 2026-08-22 [TOOL] Report cleanup validation: report/PDF/provider-schema/route tests passed 24 tests plus 6 subtests; structured-output compatibility tests passed 21 tests plus 3 subtests.
- 2026-08-22 [TOOL] Relationship-status fix validation: 50 focused tests plus 8 subtests passed in `env_mitre`; compileall passed; live backend reloaded the change.
- 2026-08-22 [TOOL] Exact failed-run retry reached extraction validation failure before Main Case Analysis, so live end-to-end success is UNCONFIRMED.
- 2026-08-22 [TOOL] Workspace synchronization reset the first source/test patch; the intended files were re-applied, revalidated, and unrelated dirty changes were preserved.
- 2026-08-22 [TOOL] Frontend library integration: focused extraction/chat tests 42 passed; full frontend suite 80 passed; lint and Next production build passed.
- 2026-08-22 [TOOL] OpenAPI generation from `http://localhost:8000/openapi.json` passed with `openapi-typescript` 7.13.0; generated output was removed and ignored after validation.
- 2026-08-22 [TOOL] Main full-audit receipt: `main` and `origin/main` both resolve to `c48bfd9`; the source worktree was clean before this ledger update and `git diff --check` passed; only `CONTINUITY.md` changed for bookkeeping; Ruff found 96 targeted findings across backend, RAG, and research/evaluation scopes.
- 2026-08-22 [TOOL] Report prompt follow-up: `/reports` reaches `run_report_generation` → `build_template_report`; it does not call the injected adapter or `REPORT_SYSTEM_PROMPT`; persisted prompt metadata is `chat_preliminary_analysis_template_v1`.
- 2026-08-22 [TOOL] Cleanup validation: backend 267 passed plus 24 subtests, RAG 35 passed, frontend 77 passed across 11 files; frontend lint/build and Python compileall passed.
- 2026-08-22 [TOOL] Cleanup scope: 44 files changed, including 11 deleted files; no commit or staging was performed.
- 2026-08-22 [TOOL] Architecture design inventory: production files over 300 LOC include backend extraction/case-analysis/workflow/case-state/follow-up/report modules, frontend workspace/relationship graph, and RAG agent graph; no source files were changed during this design pass.
- 2026-08-22 [TOOL] Dirty-baseline receipt: `backend/requirements.txt` contains an uncommitted user-owned `jinja2>=3.1.0` addition; it was preserved and not part of the refactor design changes.
- 2026-08-22 [TOOL] Refactor validation: production `backend/app` and `frontend/src` files are all at or below 300 LOC; only test files remain above the threshold.
- 2026-08-22 [TOOL] Boundary validation: current `git diff --name-only -- rag_service` matches the pre-implementation dirty baseline; no `rag_service` file was changed by this pass.
