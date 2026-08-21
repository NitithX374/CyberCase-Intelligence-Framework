# Continuity Ledger

## Snapshot

- 2026-08-22 [USER] Current read-only audit goal: identify libraries that reduce frontend state and redundant data-shape code without weakening CyberCase persistence, provenance, or validation boundaries.
- 2026-08-22 [USER] Implementation goal: apply the approved frontend library reductions while keeping Axios transport, idempotent run polling, backend route boundaries, and internal dataclass ownership stable.
- 2026-08-21 [USER] Goal: make Main Case Analysis respond naturally in the language of the user's current message.
- 2026-08-21 [USER] Current diagnostic goal: explain two simultaneous chat runs and RAG queries in the live checkout.
- 2026-08-21 [CODE] Current branch is `feat/language-aware-analysis-personalization`; HEAD remains `3f37eddf5ad9d0c1268752334a736d158f1edad7` and all earlier dirty work is preserved.
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

- 2026-08-20 [CODE] Completed Branch A-D follow-up, stable delta IDs, Claim Inspector, Case Update projection, and Analysis Trace v1.
- 2026-08-21 [CODE] Added strict Branch E MITRE association contracts and bound-context validation.
- 2026-08-21 [CODE] Added the candidate-only transcript panel and legacy-safe frontend projection.
- 2026-08-21 [TOOL] Added regressions for admission, claim linkage, forbidden semantics, persistence, and UI wording.
- 2026-08-21 [CODE] Added deterministic Thai/English Main Case Analysis personalization without another LLM call.
- 2026-08-21 [CODE] Reverted the uncommitted parallel-RAG prototype without touching earlier or unrelated user work.
- 2026-08-22 [CODE] Applied TanStack Query to chat thread/report remote state and Zod to persisted extraction parsing; OpenAPI type generation is reproducible without committing a large generated declaration.

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
- D012 ACTIVE 2026-08-22 [CODE] Preserve historical report schemas, provider compatibility modules, and PDF version branches while removing only dead deterministic adapter plumbing.
- D013 ACTIVE 2026-08-22 [CODE] Main Case Analysis must copy each referenced relationship's exact status; mixed-status relationship references must be split, and validation remains fail-closed.
- D014 ACTIVE 2026-08-22 [CODE] TanStack Query owns remote chat/report cache and mutation state; explicit idempotency and run polling remain in ChatWorkspace.
- D015 ACTIVE 2026-08-22 [CODE] OpenAPI types are generated from the live FastAPI contract on demand; the generated snapshot stays ignored to preserve the repository's modular file-size limit.

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

## Open questions

- 2026-08-21 [TOOL] UNCONFIRMED whether the live provider returned a Group/Software ID, a technique name, or whitespace; the persisted provider payload/log line is needed to distinguish the trigger.

## Working set

- 2026-08-21 [CODE] `backend/app/services/case_analysis/service.py`
- 2026-08-21 [CODE] `backend/app/services/case_analysis/personalization.py`
- 2026-08-21 [CODE] `backend/tests/test_analysis_trace.py`
- 2026-08-21 [CODE] `backend/tests/test_main_case_analysis.py`
- 2026-08-21 [CODE] `backend/tests/test_chat_phase2_routing.py`
- 2026-08-21 [CODE] `frontend/src/lib/mitre-candidate.ts`
- 2026-08-21 [CODE] `frontend/src/components/conversation/MitreCandidatePanel.tsx`
- 2026-08-21 [CODE] `frontend/src/components/conversation/ChatTranscript.tsx`
- 2026-08-21 [CODE] `backend/app/services/workflow/pipeline.py`
- 2026-08-21 [CODE] `backend/app/services/chat/chat_message.py`
- 2026-08-21 [CODE] `backend/app/services/workflow/worker.py`
- 2026-08-21 [CODE] `backend/app/services/case_analysis/validation.py`

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
