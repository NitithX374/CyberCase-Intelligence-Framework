# Continuity Ledger

## Snapshot

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

- 2026-08-20 [CODE] Completed Branch A follow-up, stable delta IDs, Branch B Claim Inspector, and Branch C Case Update projection.
- 2026-08-20 [CODE] Completed Branch D Analysis Trace v1 with native references and independent epistemic status.
- 2026-08-21 [CODE] Added strict Branch E MITRE association contracts and bound-context validation.
- 2026-08-21 [CODE] Added the candidate-only transcript panel and legacy-safe frontend projection.
- 2026-08-21 [TOOL] Added regressions for admission, claim linkage, forbidden semantics, persistence, and UI wording.
- 2026-08-21 [CODE] Added deterministic Thai/English Main Case Analysis personalization without another LLM call.
- 2026-08-21 [CODE] Reverted the uncommitted parallel-RAG prototype without touching earlier or unrelated user work.

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

## Incident: Follow-up false proceed

- 2026-08-20 [USER] Symptom: a name-only submission produced analysis instead of a clarification.
- 2026-08-20 [CODE] Status: corrected with prompt semantics, normalization, and a deterministic material-gap guard.

## Incident: Clarification mutation rejected

- 2026-08-20 [USER] Symptom: the exact Thai clarification displayed `mutateCaseState failed`.
- 2026-08-20 [CODE] Status: corrected with closed categories, legacy normalization, and backend-owned ADD IDs; live V1 to V2 persistence passed.

## State (Done/Now/Next)

- 2026-08-21 [CODE] Done: language-aware Main Case Analysis personalization is implemented without a migration or additional LLM call.
- 2026-08-21 [TOOL] Reproduced the exact validator message for Group/Software IDs, names, missing IDs, and noncanonical whitespace; valid T-shaped IDs pass this layer.
- 2026-08-21 [CODE] Now: parallel-RAG work is stopped; branch restored to `feat/language-aware-analysis-personalization`.
- 2026-08-21 [CODE] Now: retrieval-to-analysis MITRE validation is diagnosed; no production fix has been applied.
- 2026-08-21 [ASSUMPTION] No implementation was made because the user reported the symptom but did not explicitly request a fix.

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
