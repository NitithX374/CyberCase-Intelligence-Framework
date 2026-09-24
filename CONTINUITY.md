# Continuity Ledger

## Snapshot

- 2026-09-24 [USER] Default model is now `deepseek/deepseek-v4.1-flash` (checked on OpenRouter: structured outputs supported), for backend `CASE_ANALYSIS_MODEL` and RAG `CORE_LLM_OPENROUTER_MODEL` alike; supersedes the same-day `qwen/qwen3.8-27b` default, which stays selectable as `qwen`. Neither variable is set in Doppler or `.env`, so the code and Compose fallbacks decide; containers created before a change keep the old value until recreated.
- 2026-09-24 [CODE] Local DB is at Alembic 0016 (0015 dropped unread user columns and duplicate indexes and cascades report deletes; 0016 folded `document_extractions` into document sources and dropped `case_documents.archived_at`, `case_sources.origin_message_id`, `users.avatar_url`, `case_analysis_results.answer`, dead JSON keys and 2 empty ownerless cases). Dry-run on a restored copy first; every read route returned 200 for all 13 owned cases. Pre-migration dumps are in the session scratchpad; the 11 older `answer` texts that differed from `summary` exist only there. Production needs a manual `alembic upgrade head` deployed together with this code.
- 2026-09-24 [USER] Default model is `qwen/qwen3.8-27b` without `:free`, for backend `CASE_ANALYSIS_MODEL` and RAG `CORE_LLM_OPENROUTER_MODEL` alike; supersedes D065's `qwen/qwen3.8-27b:free` default. The `:free` ID still works as an explicit override, since both resolvers pass full IDs through.
- 2026-09-23 [CODE] D066 follow-up pseudo-source archival is complete in the local backend and database: Alembic 0014 archived 13 duplicate rows across four Cases, each Case revision rose once, historical analysis/report row counts stayed 45/6, and 30 focused tests passed. The four latest analyses are now stale by design.
- 2026-09-23 [TOOL] Retrieval-contract/D066 implementation is committed locally as `1ea50c5`, preceded by root guidance commit `dedd1d8`; `main` is ahead 2/behind 6 `origin/main`, nothing was pushed, and other dirty work remains untouched.

- 2026-09-23 [TOOL] Supersedes the earlier push status: the six research commits through `4678cd1` were reverted by six new commits ending at `5198c65`; GitHub `origin/main` is verified at that SHA, and the net diff from base `e687987` is empty. Revert work was isolated from the dirty primary checkout.
- 2026-09-23 [TOOL] Read-only backend audit completed on live `main` at `4678cd1`; 25 OpenAPI operations, backend/RAG health OK, Alembic 0013, focused schema/route tests 11 passed. Dirty worktree preserved; no app/data changes.
- 2026-09-23 [USER] Current research task: create only a classifier-only LADDER B0 training script and requirements; user trains on Vast AI, with local training and B1 out of scope until B0 review.
- 2026-09-23 [TOOL] LADDER audit is `PARTIALLY_SAFE`: positive alignment train `763/1107`, dev `194/284`, test `259/331`; the completed dataset builder is at `F:/LADDER_2/ladder_joint_detection` and was moved out of this worktree.
- 2026-09-23 [CODE] B0 script and requirements are committed at `4678cd1`; Ruff, format, compile, loader, tokenization, and metric smoke checks passed; no model was trained locally.
- 2026-09-23 [USER] Retrieval contract approved and implemented: remove chat retrieval identity, retain `case_sources.archived_at` and analysis identity, remove only top-level external MITRE, and persist retrieved legal relevance; see spec and Receipts.
- 2026-09-23 [TOOL] Local DB is at migration 0013; backend and RAG health/OpenAPI verified; focused backend/RAG/frontend tests, ESLint, TypeScript, build, Ruff, and diff check passed. API-types check still reports unrelated stale `analysisTypes.ts`.
- 2026-09-23 [TOOL] Backend chat now routes through configured `qwen/qwen3.8-27b:free` despite persisted analysis model metadata; focused regression tests passed and backend/RAG report Qwen at runtime.
- 2026-09-23 [USER] Root `AGENTS.md` now treats modularity as a responsibility/readability goal, not a hard 300-line file limit.
- 2026-09-23 [USER] First refactor phase is backend-only pipeline/model configuration; leave RAG configuration untouched and defer the broader backend refactor. The user approved one `CASE_ANALYSIS_MODEL` selector and preserving the versioned pipeline snapshot contract.
- 2026-09-23 [TOOL] AnnoCTR external evaluation is complete under `experiments/annoctr_external_validation/`; metrics are accuracy `74.02%`, precision `68.19%`, relevant recall `35.50%`, F1 `46.69%`, false skip `64.50%`, false invocation `7.81%`.
- 2026-09-22 [TOOL] Gold Attack Span oracle matched `331/331` positives on 662 LADDER rows, recovered 28 false negatives, and raised binary accuracy `85.8006%` to `89.2749%`; detailed metrics are in Receipts.
- 2026-09-22 [TOOL] XLM-R ranked all `1,107` negative train rows without truncation; 41 exceed `p_relevant >= 0.1` and 33 exceed `0.5`, for candidate hard-negative review.
- 2026-09-23 [CODE] Current Overleaf package and English Chapters 3/4 are delivered under `deliverables/`; bundled Tectonic compiled the 31-page package successfully.
- 2026-09-22 [TOOL] Research-readiness review favors assessment-first, source-bounded general case summarization; software tests establish workflow contracts, not summary quality or user benefit.
- 2026-09-19 [USER] Product scope: general case summarization is core; MITRE is conditional technical augmentation; preserve source vocabulary, request-scoped analysis, existing follow-up/report ownership, and collaborator-owned RAG.
- 2026-09-21 [CODE] Assessment persists separately and does not move `latest_analysis_result_id`; no job/run table or polling is part of the current route contract.

## Done (recent)

- 2026-09-23 [CODE] Added the B0-only XLM-R training script and requirements in `4678cd1`; Ruff, format, compile, loader, tokenization, and metric smoke checks passed; training is deferred to Vast AI and B1 remains out of scope.
- 2026-09-23 [CODE] Consolidated backend model selection on `CASE_ANALYSIS_MODEL` with `qwen/qwen3.8-27b:free`, canonical alias snapshots, and a shared MITRE gate/chat/main-analysis model; no schema migration or RAG code changes.
- 2026-09-23 [CODE] Implemented the approved retrieval-context contract in Alembic 0013 and backend/RAG/frontend: removed chat retrieval identity, retained source archival and analysis identity, removed only duplicated external MITRE, and persisted legal relevance for retrieved contexts.
- 2026-09-23 [CODE] Added the modular AnnoCTR external-validation package, generated the requested reports, and cleaned its focused test fixtures; design and implementation commits are `86697f9`, `dac0c5c`, and `706ff17`.
- 2026-09-22 [CODE] Created and validated the 31-page Overleaf package plus English Chapters 3 and 4; bundled Tectonic compiled successfully and representative pages showed no clipping.
- 2026-09-22/23 [TOOL] Updated research docs to match the assessment-first/source-bounded workflow and completed a read-only backend route, data, and runtime audit; detailed results remain in Receipts.
- 2026-09-21 [CODE] Delivered bordered Case Findings and stable QA source merging, `case_assessment_v1` persistence with deterministic chat routing; real-DB assessment tests passed 34/34, chat routing 19/19 plus concurrency, and full backend suite 238 tests plus 2 subtests (two known Windows GTK PDF failures). English Chapters 3 and 4 remain available under `deliverables/`.

## Decisions

- 2026-09-24 [USER] D067 ACTIVE: drop what nothing reads (0015, 0016 above). A document's text, pages and read warnings live on its `CaseSource`; `CaseSourceRead.filename` comes from the document, because citations name documents by filename and the frontend matches the two. Supersedes D066's retention of `origin_message_id`.
- 2026-09-23 [USER] D066 ACTIVE: archive persisted legacy `followup_answer` CaseSources; increment `source_revision` once per affected Case; preserve historical analysis/report snapshots and legacy fields; hide archived rows from normal `GET /sources`; retain synthetic QA references; keep this phase backend-only. This supersedes the earlier pending-choice entry below.

- 2026-09-23 [USER] D062 ACTIVE: remove `chat_messages.retrieval_context_id`; keep `case_analysis_results` and trace retrieval IDs; keep `case_sources.archived_at`; remove only top-level `external_context_json.mitre_table`; persist RAG legal relevance under `legal_relevance` in both external and reusable retrieval context JSON.
- 2026-09-23 [USER] D063 ACTIVE: no hard 300-line code-file cap; split modules when it improves cohesion, readability, testing, or ownership.
- 2026-09-23 [USER] D064 ACTIVE: consolidate backend pipeline/model configuration first; exclude `rag_service/**`; do the broader backend refactor later.
- 2026-09-23 [USER] D065 ACTIVE: use `CASE_ANALYSIS_MODEL` as the only backend Case Analysis model selector for main analysis, chat answers, and the LLM MITRE gate; default to `qwen/qwen3.8-27b:free`; remove `CHAT_ASK_MODEL`; preserve versioned pipeline snapshots and leave RAG configuration untouched.
- 2026-09-19 [USER] Advisor clarification supersedes cybersecurity-only framing of the preceding proposal. Event representation is still a candidate method, not an approved requirement; cyber-only datasets cannot by themselves establish general-case summarization performance.
- 2026-09-19 [ASSUMPTION] Revised recommendation: general event-supported summarization as the candidate treatment, OCR robustness as a bounded evaluation axis, and defer temporal attack-graph B2. This recommendation is not yet user-approved or implemented.
- 2026-09-19 [USER] D058-D060 retained: no run/job table or polling; use source vocabulary. Historical rationale and earlier decisions remain in the archived ledger.
- 2026-09-19 [USER] Current task supersedes earlier OCR/follow-up research framing for this proposal only; it does not authorize changing the product direction document or implementing the proposal.
- 2026-09-19 [ASSUMPTION] PROPOSED: JSON storage plus deterministic labeled-text serialization and raw sources; no graph database, multi-agent loops, or event-state persistence subsystem.
- 2026-09-19 [ASSUMPTION] PROPOSED: CASIE event-hopper/argument preservation is primary; ChronoCTI report/technique relation sets are separate. Preserve native multilabel relations and do not force a total timeline.
- 2026-09-21 [CODE] D061 ACTIVE: assessment uses a separate strict gaps-only schema rather than weakening `CaseAnalysisTrace`; `decide_followup` and `CaseAnalysisGap` remain unchanged.

## Now / Next

- 2026-09-23 [CODE] Root AGENTS.md now describes clarification replies as chat history with synthetic QA references, while preserving the existing modularization guidance.

- 2026-09-23 [CODE] New narrative sources no longer accept origin_message_id through SourceService; the stored link remains on archived legacy rows for historical traceability.

- 2026-09-23 [CODE] D066 is implemented and verified; this supersedes the pending-design and no-database-write notes below. Broader backend refactoring remains deferred.

- 2026-09-23 [TOOL] Audit covers live `main` at `4678cd1` plus the mounted dirty working tree; runtime has 25 routes, healthy backend/RAG, and schema head 0013. No application or database writes were made.
- 2026-09-23 [TOOL] Backend config consolidation is implemented and verified. Focused tests passed 54/54; backend suite passed 243 with 15 skipped and 2 PDF tests deselected because Windows lacks WeasyPrint's `libgobject-2.0-0`; Compose validation, Ruff, formatting, and diff checks passed.
- 2026-09-23 [TOOL] Read-only backend architecture survey report: `C:\Users\kkham\AppData\Local\Temp\architecture-review-20260923-052231.html`. Runtime OpenAPI has 25 operations; live DB has 13 active legacy follow-up sources, 12 also represented in gap history. Candidate selection is pending; no code or data changed.
- 2026-09-23 [USER] Selected `Retire follow-up pseudo-sources` for grilling; archive/delete, source-revision, visibility, legacy field/API, and synthetic QA UI choices remain open. No schema or data changes have started.
- 2026-09-23 [NEXT] Broader backend route/data-model refactor remains deferred by user; no further changes in that scope until requested.

## Open questions

- 2026-09-23 [TOOL] D066 has no unresolved design question; this supersedes the earlier archive/revision/listing questions below. Four affected Cases now have stale latest analyses and require a fresh analysis only when the user needs a current result. Migration 0014 depends on untracked local 0013, so both files must be delivered together.

- 2026-09-23 [TOOL] Audit: 13 active legacy `followup_answer` source rows duplicate chat answers in analysis inputs and Sources UI. Decide archival migration/revision behavior before cleanup; no rows were changed.
- 2026-09-23 [TOOL] Audit: `case_sources.archived_at` is read but no archive/restore write route was found; decide whether to add lifecycle actions and whether `case_documents.archived_at` remains necessary.
- 2026-09-23 [TOOL] Frontend `caseOverview/followupSources.ts` synthesizes `QA-xx` display/reference rows from follow-up ChatMessages using the `CaseSourceRead` shape; this is not database persistence and may need a distinct presentation type if the backend DTO changes.
- 2026-09-23 [TOOL] Config design question about replacing the MITRE gate's separate model selector is resolved by user approval D065; implementation and verification are complete.
- 2026-09-22 [USER] Which primary research question should be frozen: the implemented assessment-first/source-bounded workflow, OCR downstream impact, or a bounded usability study?
- 2026-09-22 [TOOL] Superseded for this interaction: the earlier file-upload/follow-up-answer contract question remains historical and is not needed to choose the current research contribution.
- 2026-09-19 [TOOL] CASIE repository licensing is UNCONFIRMED; public availability is verified but a top-level license was not visible.
- 2026-09-19 [TOOL] The older canonical direction document conflicts with supplied current instructions and inspected runtime; an authority reset is outside this task.
- 2026-09-19 [ASSUMPTION] Frozen model version, API budget, and availability of a second human auditor are UNCONFIRMED.
- 2026-09-20 [TOOL] Branch spelling `refactor/remove-case-trun` is UNCONFIRMED; the only matching local branch is `refactor/remove-case-run`, and no remote tracking branch exists.
- 2026-09-21 [TOOL] Superseded: the earlier `backend/app/routers/cases.py` import blockage no longer reproduces; the full backend Ruff run now passes.

## Working set

- 2026-09-23 [TOOL] backend/alembic/baseline_versions/0014_archive_legacy_followup_sources.py
- 2026-09-23 [TOOL] backend/tests/test_archive_legacy_followup_sources_postgres.py

- 2026-09-23 [TOOL] backend/app/models/sources.py
- 2026-09-23 [TOOL] backend/app/schemas/sources.py
- 2026-09-23 [TOOL] backend/app/routers/sources.py
- 2026-09-23 [TOOL] backend/app/services/sources/source_service.py
- 2026-09-23 [TOOL] backend/app/services/sources/case_source_bundle.py
- 2026-09-23 [TOOL] backend/alembic/baseline_versions/0013_retrieval_context_contract.py
- 2026-09-23 [TOOL] backend/tests/test_case_sources_provenance_postgres.py
- 2026-09-23 [TOOL] backend/tests/test_database_schema.py
- 2026-09-23 [TOOL] backend/tests/test_case_validation.py
- 2026-09-23 [TOOL] frontend/src/lib/caseOverview/followupSources.ts (read-only)

## Receipts

- 2026-09-23 [TOOL] Follow-up archive preflight: 13 active duplicates across four Cases, zero unmatched, 45 analyses and six reports. The first migration attempt failed because its 36-character revision ID exceeded alembic_version.version_num varchar(32); PostgreSQL rolled back completely. A failing length-guard test reproduced this, the ID was shortened, and local Alembic reached 0014. Postflight: zero active/13 archived duplicates, affected Case revisions moved 2/5/5/8 to 3/6/6/9, analyses/reports unchanged, four latest analyses stale. Focused PostgreSQL and backend tests 30 passed; Ruff, formatting, route-surface, health, reload, and live SourceService listing checks passed.

- 2026-09-23 [TOOL] Reverted the six unintended research commits on `NitithX374/CyberCase-Intelligence-Framework` using six new revert commits (`85c23a4` through `5198c65`), then pushed normally to `main`; remote SHA verified as `5198c659fa57470760f04de5eac37ff34b5e7f3a`, and the net diff against pre-research base `e687987` is empty. Used an isolated worktree; no force-push.
- 2026-09-23 [TOOL] Backend model-config work: 54 focused tests passed; backend suite passed 243 with 15 skipped and 2 PDF tests deselected for unavailable Windows WeasyPrint `libgobject-2.0-0`; `docker compose config --quiet`, Ruff, format, and `git diff --check` passed. The initial unrestricted suite reproduced only those two native-library PDF failures.
- 2026-09-23 [TOOL] Backend-only config inspection: `case_analysis_model` default is 27b, `AnalysisPipelineConfig.model` default is 30b, Compose provides 27b:free; persisted pipeline snapshots and user-owned dirty config edits must be preserved. RAG excluded by user scope.
- 2026-09-23 [TOOL] User approved the backend model-config design and implementation: one selector and model across analysis/chat/MITRE gate, exact Qwen free model ID, unchanged persisted snapshot shape, no RAG changes. `docs/superpowers/specs/2026-09-23-backend-model-config-consolidation-design.md` and its implementation plan record the contract.
- 2026-09-23 [TOOL] Backend audit: live OpenAPI has 25 operations; backend and RAG health are OK; Alembic is at 0013; route-surface/schema tests passed 11/11. Live DB showed 13 active follow-up source duplicates; no application or DB writes were performed.
- 2026-09-23 [TOOL] `improve-codebase-architecture` survey: route count 25 matches `test_route_surface.py`, so no route consolidation candidate passed the deletion test. A read-only local DB aggregate confirmed 13 unarchived `followup_answer` CaseSource rows, all linked to same-case user messages with identical text; 12 also have gap-question lineage. `case_sources.archived_at` filters new bundles and reconstructs historical membership, but no backend writer or route was found. Report is in the OS temp directory; no tests or writes were performed.
- 2026-09-23 [TOOL] Retrieval contract: backend focused tests `50 passed, 2 subtests`; RAG `7 passed`; frontend `24 passed`; ESLint, TypeScript, Next build, Ruff, and diff check passed. Dev DB verified at 0013 (`chat_messages.retrieval_context_id` absent; `case_sources.archived_at` retained; external top-level MITRE absent; nested MITRE retained); backend/RAG health and OpenAPI fields verified. Restarting RAG to load mounted code reset only its in-memory one-hour context cache; DB snapshots remained untouched.
- 2026-09-23 [TOOL] Pushed six research commits to fork `origin/main`, ending at `4678cd1d492eba4183c2451b15ea0354fb55654f`; remote `main` verified at the same SHA. Existing working-tree changes remain unpushed.
- 2026-09-23 [TOOL] LADDER outputs validated: `joint_*` JSONL preserves train `2214`, dev `568`, test `662`; negative all-O supervision is enabled for all `1722` negatives; positive span supervision is `68.4734%/68.3099%/78.2477%`; Ruff, compileall, and focused pytest `8/8` passed.
- 2026-09-23 [TOOL] CUDA evaluation at the fixed 0.50 LADDER decision rule produced LADDER confusion `TN=282 FP=49 FN=45 TP=286` and AnnoCTR `TN=1476 FP=125 FN=487 TP=268`; independent artifact recomputation matched metrics, and Ruff, compileall, and focused pytest `3/3` passed.
- 2026-09-23 [TOOL] AnnoCTR metrics were accuracy `74.02%`, precision `68.19%`, relevant recall `35.50%`, F1 `46.69%`, false skip `64.50%`, and false invocation `7.81%`; LADDER relevant recall was `86.40%` and false skip `13.60%`.
- 2026-09-21 [TOOL] Architecture artifacts parsed as valid XML: system flow has 4 pages/211 cells, component architecture has 2 pages/97 cells, and sequence diagram has 3 pages/24 lifelines/53 messages with no malformed edges; scoped `git diff --check` passed.
- 2026-09-22 [TOOL] Gold oracle completed on 662 LADDER rows: 331/331 positives matched, raw recall 86.4048%, gold recall 93.3535%, 28 recovered false negatives, 5 broken positives, McNemar exact p=0.0000661877; binary oracle accuracy rose 85.8006% to 89.2749% with unchanged FPR 14.8036%.
- 2026-09-22 [TOOL] Post-run recomputation matched the saved confusion matrices and deltas; all new Python files are <=221 lines, `python -m pytest -q backend/tests/test_ladder_segmentation.py` passed 4/4, and direct `pytest` was not used as evidence because its standalone launcher lacked torch.
- 2026-09-20 [TOOL] CaseAnalysisResult is isolated by case_id but permits many rows per case; no unique case_id/source_revision or active-analysis constraint remains after CaseRun removal, so the worker concern is duplicate same-case execution, not cross-case result mixing.
- 2026-09-20 [USER] UI/concurrency decisions: one primary analysis action, defer multi-worker support, and remove redundant Overview status pills while preserving meaning and navigation.
- 2026-09-20 [CODE] Delivered Findings presentation, stable QA source merging, and follow-up state/cache updates; local refactor landed at `afc9b5f`.
- 2026-09-20 [TOOL] Frontend Vitest 21 files/96 tests, TypeScript, ESLint, production build, and browser sign-in-gate check passed; local backend auth was unavailable.
