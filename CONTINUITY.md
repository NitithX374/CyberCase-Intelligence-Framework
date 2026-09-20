# Continuity Ledger

## Snapshot

- 2026-09-19 [USER] Latest advisor scope: General Case Summarization is core; MITRE augmentation is conditional; validate single input first while retaining Case -> N Documents -> source contents -> consolidated representation; printed OCR is in scope, HTR is a limitation/future work. Study downstream OCR error impact and preserve available uncertainty signals without assuming confidence exists.
- 2026-09-19 [USER] Active task: literature-grounded redesign of ONLY core case analysis; deliver a concrete one-month undergraduate experiment comparing direct, event-supported, and temporal event-supported analysis.
- 2026-09-19 [USER] RAG, UI, training a large LLM, and validation-heavy anti-hallucination architecture are excluded as primary contributions. No application implementation requested.
- 2026-09-19 [TOOL] Research design and artifact inspection are complete; see docs/research/event-analysis-2026-09-19/paper_story.md and project_inventory.md.
- 2026-09-19 [ASSUMPTION] Recommended primary experiment: B0 versus B1 plus a matched two-call prose-notes control. B2 is a secondary technique-level ChronoCTI experiment, not validated instance-level forensic timeline reconstruction.
- 2026-09-19 [CODE] Inspected pipeline.py runs TechnicalContextStage then AnalysisStage and already provides a database-free Stage protocol.
- 2026-09-19 [USER] Preserve source vocabulary, request-scoped analysis/Case Ask, existing follow-up and report ownership, and collaborator-owned RAG.
- 2026-09-19 [TOOL] Existing modified provider_stage.py and provider-stub.mjs plus untracked helper/OCR files were left unchanged.
- 2026-09-19 [TOOL] Older ledger copied intact to docs/research/event-analysis-2026-09-19/continuity-before-research.md; older architecture facts there may be superseded.
- 2026-09-20 [TOOL] Audited local refactor/remove-case-run: it is 46 commits ahead of main, has no upstream, and is a full request-scoped CaseRun/follow-up/report/frontend refactor rather than a single file removal.
- 2026-09-20 [USER] Source drawers keep source/page attribution and Materials navigation but render source text without exact-quote highlighting or automatic scrolling to a highlighted passage.

## Done (recent)

- 2026-09-19 [TOOL] Inspected original CASIE annotation structure and downloaded/inspected the ChronoCTI archive, including native labels, report masks, duplicate pairs and negative generation.
- 2026-09-19 [TOOL] Wrote research story, experiment design, integration inventory, and dataset caveats; no model evaluation performed.
- 2026-09-19 [CODE] Prior implementation milestone: CaseRun and rag_contexts removed; request-scoped analysis and Case Ask replace jobs/polling (historical ledger D058/D059).
- 2026-09-19 [CODE] Prior implementation milestone: source vocabulary and sources-page intake integration; four Case workspace tabs (historical ledger).
- 2026-09-20 [TOOL] Current route/schema checks passed (12 tests) and frontend Vitest passed (21 files, 96 tests); `tsc --noEmit` passed, while `npm run check:api-types` fails because generated analysisTypes.ts lacks two backend grounding fields.
- 2026-09-20 [CODE] Removed only source-drawer exact-quote highlighting and mark auto-scroll; retained citations, page binding, drawer behavior, and Materials navigation.

## Decisions

- 2026-09-19 [USER] Advisor clarification supersedes cybersecurity-only framing of the preceding proposal. Event representation is still a candidate method, not an approved requirement; cyber-only datasets cannot by themselves establish general-case summarization performance.
- 2026-09-19 [ASSUMPTION] Revised recommendation: general event-supported summarization as the candidate treatment, OCR robustness as a bounded evaluation axis, and defer temporal attack-graph B2. This recommendation is not yet user-approved or implemented.
- 2026-09-19 [USER] D058-D060 retained: no run/job table or polling; use source vocabulary. Historical rationale and earlier decisions remain in the archived ledger.
- 2026-09-19 [USER] Current task supersedes earlier OCR/follow-up research framing for this proposal only; it does not authorize changing the product direction document or implementing the proposal.
- 2026-09-19 [ASSUMPTION] PROPOSED: JSON storage plus deterministic labeled-text serialization and raw sources; no graph database, multi-agent loops, or event-state persistence subsystem.
- 2026-09-19 [ASSUMPTION] PROPOSED: CASIE event-hopper/argument preservation is primary; ChronoCTI report/technique relation sets are separate. Preserve native multilabel relations and do not force a total timeline.

## Now / Next

- 2026-09-19 [TOOL] Now: deliver the literature review and executable experimental specification. No empirical superiority claims are supported yet.
- 2026-09-19 [ASSUMPTION] Next if implementation is requested: freeze dataset manifests and scoring contracts before implementing B0/P1/B1; add B2 only within the bounded temporal benchmark scope.

## Open questions

- 2026-09-19 [TOOL] CASIE repository licensing is UNCONFIRMED; public availability is verified but a top-level license was not visible.
- 2026-09-19 [TOOL] The older canonical direction document conflicts with supplied current instructions and inspected runtime; an authority reset is outside this task.
- 2026-09-19 [ASSUMPTION] Frozen model version, API budget, and availability of a second human auditor are UNCONFIRMED.
- 2026-09-20 [TOOL] Branch spelling `refactor/remove-case-trun` is UNCONFIRMED; the only matching local branch is `refactor/remove-case-run`, and no remote tracking branch exists.

## Working set

- 2026-09-19 [TOOL] docs/research/event-analysis-2026-09-19/paper_story.md
- 2026-09-19 [TOOL] docs/research/event-analysis-2026-09-19/project_inventory.md
- 2026-09-19 [TOOL] docs/research/event-analysis-2026-09-19/continuity-before-research.md
- 2026-09-19 [CODE] backend/app/services/case_analysis/pipeline.py
- 2026-09-19 [CODE] backend/app/services/case_analysis/pipeline_config.py
- 2026-09-19 [CODE] backend/app/services/case_analysis/provider_stage.py
- 2026-09-19 [CODE] backend/app/services/case_workflow/analysis.py
- 2026-09-19 [CODE] backend/app/services/chat/followup.py
- 2026-09-19 [CODE] backend/app/services/reports/
- 2026-09-20 [CODE] frontend/src/components/sources/SourceDrawer.tsx

## Receipts

- 2026-09-19 [TOOL] Research-data milestone: CASIE and ChronoCTI artifacts, labels, splits, duplicate pairs, negative generation, licenses, SIABench, AEC, and ExCyTIn were inspected; detailed receipts live in docs/research/event-analysis-2026-09-19/.
- 2026-09-19 [TOOL] No application tests, model calls, Docker changes, commits, or benchmark performance measurements executed in this research task.
- 2026-09-20 [TOOL] Current request-scoped workflow reads sources, releases the DB connection during the model call, then writes under a source-revision check; concurrent same-revision analyses can both commit, so the branch intentionally rejects multiple application workers.
- 2026-09-20 [TOOL] CaseAnalysisResult is isolated by case_id but permits many rows per case; no unique case_id/source_revision or active-analysis constraint remains after CaseRun removal, so the worker concern is duplicate same-case execution, not cross-case result mixing.
- 2026-09-20 [USER] Current primary UI flow exposes one analysis action and disables the button while that request is in flight; duplicate same-case analysis is outside the intended happy path.
- 2026-09-20 [USER] Defer multi-worker support; keep the branch's one-worker runtime for now and do not expand concurrency architecture in this round.
- 2026-09-20 [USER] Reduce AI-slop visual treatment in the Overview: remove redundant status pills and nested boxes while preserving status meaning, source navigation, and table structure.
- 2026-09-20 [CODE] Findings now render one text-only status/type line (`Not established · Analytical inference`), with no badge background or border; Open Questions remain unchanged.
- 2026-09-20 [TOOL] Frontend Vitest full suite passed 21 files/96 tests, targeted Findings tests passed 3/3, TypeScript and ESLint passed, and browser QA reached the sign-in gate without a case session.
- 2026-09-20 [TOOL] Frontend production build passed after the Findings polish; route output remains unchanged.
- 2026-09-20 [CODE] Follow-up sends now expose one activity state across the workspace, update the returned analysis cache immediately, and avoid refetching Chat through a broad Case invalidation; focused/full frontend tests, TypeScript, lint, build, and diff check passed.
- 2026-09-20 [TOOL] Rechecked the mounted frontend source at 158 lines, rebuilt the follow-up route successfully, and confirmed the reported line-184 syntax overlay no longer reproduces; local backend auth remains unavailable.
- 2026-09-20 [TOOL] Squashed the refactor branch and follow-up UI fix into afc9b5f, fast-forward merged it into local main, and left origin/main unpushed.
- 2026-09-20 [TOOL] Backend boot failure traced to dirty prompts.py removing validate_analysis_request and CASE_TRACE_REVISION_PROMPT while committed callers still imported them; restored the symbols without discarding prompt edits, verified container import, health 200, and 21 focused backend tests.
- 2026-09-20 [TOOL] System OCR warning count is one expected native-text fallback notice per PDF page; latest five-page extraction had 5 OCR machine_read pages with nonempty text.
- 2026-09-20 [USER] Root cause identified: clarification plus file upload can leave a PostgreSQL transaction open while the client request is interrupted; the EOF is the server rolling back that abandoned transaction.
- 2026-09-20 [CODE] Frontend mutation spinners no longer wait for post-success cache invalidations; chat, upload, analysis, and narrative refreshes run after the mutation settles, and the shared Axios default timeout prevents ordinary reads from hanging forever.
- 2026-09-20 [TOOL] Spinner fix regression test, full frontend Vitest (21 files/101 tests), TypeScript, ESLint, production build, and `git diff --check` passed; browser reload reached the login gate with no console warnings/errors.
- 2026-09-20 [TOOL] Source-drawer no-highlight change passed 3 focused files/11 tests, full frontend Vitest 21 files/101 tests, TypeScript, ESLint, production build, and `git diff --check`.
