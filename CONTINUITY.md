# Continuity Ledger

## Snapshot

- 2026-09-09 [USER] Authorized follow-up fixes and verification of Gemini legacy cleanup; rag_service/** remains excluded.
- 2026-09-09 [CODE] Supersedes cleanup completion caveats: latest overview blocks stale fallback; frontend distinguishes retired vs invalid analysis; ASK cannot bypass via legacy context. Raw persisted data unchanged. Details: docs/research/LEGACY_CLEANUP_VERIFICATION_2026-09-09.md.
- 2026-09-09 [TOOL] Backend 405 passed plus 2 subtests, no skips, disposable PostgreSQL stopped. Frontend 158 passed; lint, API types, tsc and diff checks passed. Production build passed.

- 2026-09-09 [USER] Supplied professor-approved OCR/summarization study scope: prioritize factual correctness and OCR-error propagation; use overall summary metrics secondarily. ThaiSum controlled corruption is accepted with explicit error types, real-OCR-informed severity and reproducible edit logs. Domain mismatch must be acknowledged; small real-case factual validation is optional if time permits. Uncertainty handling/PaddleOCR are supplementary, not core. Sample size and annotation protocol remain UNCONFIRMED; no implementation requested.
- 2026-09-08 [USER] Requested audit/list of old code and consolidation candidates before OAuth; no cleanup implementation authorized.
- 2026-09-08 [TOOL] Static audit complete at main b21b74c plus dirty attribute-first work. Findings and scope: docs/research/CODEBASE_CLEANUP_AUDIT_2026-09-08.md. No source changes or tests run; Ruff found 3 unused imports.

- 2026-09-08 [USER] Authorized attribute-first Phase 1 implementation; later requested continued implementation. Preserve legacy baseline and v3 readers. NLI/XNLI remains subsequent work.
- 2026-09-08 [CODE] COMPLETE: opt-in claim_anchored overview performs extract -> unique exact bind -> stable budget selection -> generate -> v3 assembly. Raw_direct default and legacy ASK remain. No automatic method fallback.
- 2026-09-08 [CODE] V11 run configuration is pinned at creation, inherited by clarification and retained across retry. Stage receipts persist with lease ownership and survive failed/interrupted attempts; generated units map to immutable source spans.
- 2026-09-08 [CODE] Phase 1 suppresses technical augmentation explicitly; gap/follow-up retains full admitted case evidence. SemanticVerifier is injectable but no NLI implementation is installed; receipt says not_performed.
- 2026-09-08 [TOOL] Final backend 386 passed + 2 subtests, no skips (one upstream deprecation warning); frontend 151 passed; API types, Ruff F/I, syntax, Compose config and diff checks passed. Touched Python files remain under 300 physical lines.
- 2026-09-08 [TOOL] Live synthetic Thai smoke: OpenRouter Luna, two completed calls, three source-bound claims, 11.703s provider time, reported cost USD 0.0010808. Not a semantic-accuracy evaluation.
- 2026-09-08 [CODE] Instructions/results: docs/research/ATTRIBUTE_FIRST_IMPLEMENTATION.md; live receipt: ATTRIBUTE_FIRST_SMOKE.json. Work uncommitted; no deployment or persistent environment change.
- 2026-09-08 [TOOL] Baseline dirty files were CONTINUITY.md and untracked PHASE1_CLAIM_ANCHORED_PLAN.md from earlier planning. Preserved and updated. No rag_service or frontend edits.
- 2026-09-08 [USER] Authorized codebase legacy cleanup (excluding rag_service/**, OAuth, and file redesigns) based on CODEBASE_CLEANUP_AUDIT_2026-09-08.md. Preserve dirty attribute-first work and baseline raw_direct.
- 2026-09-08 [CODE] COMPLETE: Legacy cleanup executed. Purged unused helpers (_bounded_json, _invoke_policy_method, _required_material_gap, _required_gap_question, _selected_askable_gap). Removed follow-up legacy action compatibility shims (accept_legacy_action_shape, .action alias, selected_gap="legacy_gap", compatibility_skipped). Fully retired v2 analysis drafting/rendering (frontend/src/lib/case-overview-legacy.ts deleted; case-overview.ts presents explicit re-analysis required banner for historical v2 records; backend validate_analysis_trace removed, keeping read_analysis_trace strictly read-only without fabricating v3 fields).
- 2026-09-08 [TOOL] Verification complete: Backend pytest 388 passed (0 failed, 7 skipped), Frontend vitest 151 passed (36 files), ESLint 0 errors, check:api-types passed, Next.js production build passed, git diff --check passed with 0 errors. All touched files <= 300 lines. rag_service/** untouched. No commit/push.
- 2026-09-07 [TOOL] Prior migration audit and CAMS/OCR assessment remain in docs/research; full Gemini English thesis revision remains in deliverables/thesis_kmutnb_english. Empirical benefit, novelty and Thai annotation capacity remain UNCONFIRMED.

## Done (recent)

- 2026-09-08 [CODE] Implemented and validated attribute-first Phase 1, runtime/version receipts, source isolation and future verifier seam. See docs/research/ATTRIBUTE_FIRST_IMPLEMENTATION.md.
- 2026-09-07 [TOOL] Assessed Attribute-First/OCR study; reproduced semantic contradiction passing literal citation validation and absent quote removal without trace rejection. Legacy attribute pilot differs from ACL method.
- 2026-09-07 [TOOL] Completed full Gemini thesis revision, native math/figure repairs, bibliography and updated contents. Details: deliverables/thesis_kmutnb_english/review/FULL_REVISION_REVIEW.md.
- 2026-09-06 [TOOL] Completed explainability/product-fit audit, three sample DOCX text inspections, v3 explanation parser reproduction and 39 focused tests; proposals and limitations: docs/product/BACKEND_EXPLAINABILITY_REVIEW.md.
- 2026-09-05 [CODE] Completed remaining parser, metadata, follow-up, report and run-recovery work; final 351 backend/150 frontend tests and static/build checks pass. Recovery verified against disposable PostgreSQL and HTTP. Details: backend/REFACTOR.md.
- 2026-09-05 [CODE] Completed frontend Query-backed chat session, single polling loop, draft/retry state isolation, cancellation listener cleanup and 16 lifecycle regression tests. Final 145-test suite, lint, typecheck, build and synthetic browser QA pass.
- 2026-09-04 [CODE] Added Google Vision OCR confidence baseline, provider-neutral words, explicit region confidence semantics, ADC configuration documentation and synthetic response receipt. Core analysis and HTR behavior remain unchanged.

## Decisions

- D001 ACTIVE 2026-08-23 [USER] Do not modify `rag_service/**` for this cutover.
- D002 ACTIVE 2026-08-23 [USER] Raw included user messages are the only authoritative incident evidence.
- D003 ACTIVE 2026-08-23 [CODE] RAG/MITRE/model output is analytical context, never reported evidence.
- D004 ACTIVE 2026-08-23 [CODE] Ask reuses the latest durable run-bound RagContext; initial, clarification, and add-info runs perform fresh RAG.
- D005 ACTIVE 2026-08-23 [USER] Do not retain compatibility shims for the deleted Case State architecture.
- D006 ACTIVE 2026-08-23 [CODE] Reports remain deterministic, template-first, provisional, and source-message traceable.
- D007 ACTIVE 2026-08-23 [CODE] Overview workspace is client-side projection over persisted analysis messages, enforcing trust boundaries (Blue/Violet/Amber/Red/Green) and source traceability without backend mutation.
- D008 ACTIVE 2026-08-24 [CODE] Standalone PDF/HTML reports use clean 1..7 standalone numbering + technical appendix, document-oriented evidence cards, and stacked MITRE cards.
- D009 ACTIVE 2026-08-24 [CODE] Case Materials and Technical Context are pure client-side read projections over existing persisted messages and trace metadata; no new tables or backend models.
- D010 ACTIVE 2026-08-24 [USER] Standalone Investigation Issues page is deleted; gaps and unconfirmed points remain integrated inside Overview.
- D011 ACTIVE 2026-08-24 [CODE] Single canonical classifier `frontend/src/lib/case-evidence.ts` defines evidence semantics across all frontend views.
- D012 ACTIVE 2026-08-24 [CODE] Operation-level errors are presented via Meaningful Error Modal; raw technical error strings are strictly contained in collapsed disclosures.
- D013 ACTIVE 2026-08-24 [CODE] ONE logical Generate Report operation preserves ONE idempotency key across retries; new key generated only on confirmed success or explicit new version request.
- D014 ACTIVE 2026-08-25 [USER] Document ingestion extracts untrusted document content only; it does not persist cases or call analysis, gaps, reports, MITRE, or RAG.
- D015 ACTIVE 2026-08-25 [CODE] PDF native-vs-recognition routing is page-local and conservative; Typhoon output remains unknown-source untrusted text unless the provider supplies reliable metadata.
- D016 SUPERSEDED 2026-08-25 [CODE] Routed mode initially selected Google Enterprise Document OCR `pretrained-ocr-v2.1-2024-08-07` for optional Thai HTR; superseded by D017 after verification of the official language matrix.
- D017 ACTIVE 2026-08-25 [TOOL] Google Document AI and Cloud Vision must not be presented or configured as Thai HTR; use the explicit review-required HTR path until a provider with documented Thai-handwriting support is verified.
- D018 SUPERSEDED 2026-08-25 [CODE] Website document uploads initially routed handwriting to `review_required`; superseded by D019.
- D019 ACTIVE 2026-08-26 [USER] Disable HTR for now; handwriting regions must not invoke an HTR recognizer or produce transcription.
- D020 ACTIVE 2026-08-26 [USER] HTR shutdown must not require an environment variable; the production router keeps it off directly.
- D021 ACTIVE 2026-08-26 [USER] The core Analysis Module targets general criminal-case review, not legal reasoning, Legal RAG, a universal Case State, MITRE redesign, or OCR/HTR work.
- D022 ACTIVE 2026-08-26 [USER] Grounded claims, claim/evidence traceability, sufficiency gaps, stateful unknown handling, and revised analysis are P0; chat remains secondary to the case-review representation.
- D023 ACTIVE 2026-08-26 [USER] Implement only Phase 1-2 contract foundation; do not switch prompts, follow-up, workflow, RAG, frontend, reports, or persistence to v3 and retain legacy `chat_followup.gap_analysis`.
- D024 ACTIVE 2026-08-26 [CODE] `analysis_trace_v3` is a sibling to v2; compatibility reads each persisted version into its native model without fabricating v3 gaps, contradiction, reasoning, or other semantics.
- D025 ACTIVE 2026-08-26 [USER] Phase 3 changes only Main Case Analysis and necessary v3 persistence compatibility; Gap/Follow-up, frontend, reports, database, OCR/HTR, Legal RAG, and `rag_service/**` remain out of scope.
- D026 ACTIVE 2026-08-26 [CODE] The provider emits answer, summary, grounded claims, and optional MITRE candidates; the backend binds evidence hash, optional retrieval ID, empty Phase-3 gaps, and validation status before persistence.
- D027 ACTIVE 2026-08-28 [USER] New v3 analyses use `analysis_trace_v3.gaps` as the canonical analytical gap state while legacy follow-up metadata remains operational; Main Analysis does not generate gaps and Stateful Follow-up remains deferred.
- D028 ACTIVE 2026-08-28 [USER] Only validated `case_overview` v3 traces are canonical case state; `question_answer` traces remain response-scoped with strict local referential integrity, and unavailable/inapplicable RAG degrades to null retrieval plus empty MITRE context.
- D029 ACTIVE 2026-08-28 [USER] `mitre_applicability_v1` is the sole pre-retrieval applicability gate: fixed Thai/English ICL, precision over recall, uncertain/invalid/provider-failed output becomes SKIP, RETRIEVE requires current authoritative source IDs plus exact attributed spans, and only admitted RAG may support MITRE associations.
- D030 ACTIVE 2026-08-29 [CODE] Provider-facing Main v3 claim IDs and MITRE claim references use the supported finite enum `A-01` through `A-64`; local validation remains fail-closed, and only validated `case_overview` traces may supply canonical gaps.
- D031 ACTIVE 2026-08-30 [USER] Phase 5 uses existing message/run JSON metadata and local normalized gap-topic keys; no Case State, follow-up tables, migrations, embeddings, or additional provider stage.
- D032 ACTIVE 2026-08-30 [CODE] Direct clarification is one attempt per normalized topic per chain; a fresh canonical trace may remove the old gap, preserve it exhausted, or expose a genuinely distinct next gap.
- D033 ACTIVE 2026-08-31 [USER] Current intake supports one reviewed document-derived narrative, but the handoff contract is list-shaped for future `1 Case -> N Documents`; extraction never auto-persists evidence, OCR quality is non-evidence context, MITRE remains conditional, and HTR stays disabled.
- D034 ACTIVE 2026-09-01 [CODE] Overview v3 uses structured trace fields only; v2 markdown parsing is isolated, reported material is never labelled confirmed, claim order is not chronology, and MITRE renders only for applicable/unavailable technical-context states.
- D035 ACTIVE 2026-09-01 [CODE] Frontend review flow prioritizes Intake, Overview, Materials, and Report; Chat and Technical Context remain secondary tools, and unavailable people, timeline, or procedural-status data is never synthesized.
- D036 ACTIVE 2026-09-01 [USER] Report creation must not be blocked by the custom source/MITRE binding validator; typed report and snapshot contracts remain active.
- D037 ACTIVE 2026-09-01 [USER] General Case Summarization is the report prerequisite; MITRE ATT&CK retrieval is conditional knowledge augmentation, not a report-generation prerequisite, and its report binding is nullable.
- D038 ACTIVE 2026-09-01 [USER] Traceability supports plain and document-derived narratives; page labels require validated exact quote/page binding, while edited or legacy document text uses reviewed-narrative attribution without inventing a page.
- D039 ACTIVE 2026-09-02 [CODE] Report chronology comes only from the explicit analysis timeline section; claim order is not chronology, raw narrative text is not a presentation section, and MITRE remains conditional external context.
- D040 ACTIVE 2026-09-02 [CODE] Page locator admission requires a literal exact quote, matching document identity, valid text_sha256 spans, complete quote bounds, and one unambiguous page tuple; invalid or edited provenance keeps only the safe continuous prefix, while Overview/Chat expose page-first chips and narrative-only fallback; original PDF viewing is deferred to V2.

- D041 ACTIVE 2026-09-03 [USER] Remove decorative UI bubbles, boilerplate and duplicate elements. Keep functional citations and concise uncertainty/conflict labels; preserve existing frontend/backend citation work.
- D042 SUPERSEDED 2026-09-03 [CODE] Inline narrative attachments and the Files sidebar were replaced by the preparation workspace in D043; one-document extraction, explicit review/import, and backend APIs remain.
- D043 ACTIVE 2026-09-03 [USER] Supersedes D042 layout: Case Preparation Workspace places document management near the top/right, bounds default text, exposes readable/raw modes, and keeps one primary CTA. Only real existing structured fields may be summarized; no sidebar redesign or backend/API change.
- D044 ACTIVE 2026-09-03 [CODE] Current schema offers document pages/quality, evidence messages, and canonical analysis findings/gaps, not a separate pre-analysis entities/events stage. Normalize markup only in reading copies; preserve raw submitted content and exact citation provenance.
- D045 ACTIVE 2026-09-03 [CODE] Overview grouping preserves claim_type and epistemic_status separately. No supported/confirmed category exists; uncertainty groups stay visible and source links never upgrade a claim. Per-finding Analysis details contain reasoning and optional external MITRE references. No original-document viewer or reliable report availability field is supplied to Overview.

- D046 ACTIVE 2026-09-04 [USER] Google Vision is an explicitly selected OCR baseline alongside Typhoon. Confidence calibration, uncertainty UI, downstream experiments and Azure remain deferred.
- D047 ACTIVE 2026-09-04 [CODE] Recognition confidence is minimum reported Google word confidence; missing measurements remain null. DocumentRegion separates recognition_confidence from segmentation_confidence. Raw words stay in preview, and native/Typhoon missing-confidence semantics remain.

- D048 ACTIVE 2026-09-04 [USER] Keep selectable providers and confidence plumbing; Typhoon is the active OCR provider for now.

- D049 ACTIVE 2026-09-05 [CODE] Frontend thread detail has one Query cache owner; run polling stays in one shared function, and pending submission identity/input remain in a separate draft hook. Session lifecycle actions own cancellation, acceptance, recovery and deletion coordination.

- D050 ACTIVE 2026-09-08 [USER] Implement attribute-first before NLI. Preserve raw_direct/v3 compatibility and provide the verifier boundary without claiming semantic verification.
- D051 ACTIVE 2026-09-08 [CODE] Claim-anchored overview is opt-in through CASE_ANALYSIS_PIPELINE; strict unique literal spans, typed unit references, per-run configuration and attempt receipts; technical augmentation explicitly disabled in Phase 1.
- D052 ACTIVE 2026-09-08 [CODE] Retired legacy follow-up compatibility and analysis trace v2 drafting/parsers; active contracts strictly enforce v3, while historical persisted v2 records remain read-only and explicitly require re-analysis in Overview without fallback or synthesized provenance.

## State (Done/Now/Next)

- 2026-09-08 [TOOL] Done: implementation, full regression suites, isolated PostgreSQL worker/retry tests, live Thai provider smoke and final diff review.
- 2026-09-08 [CODE] Now: deliver uncommitted opt-in implementation; raw_direct remains the configured default.
- 2026-09-08 [ASSUMPTION] Next: select/qualify Thai NLI model and calibrate on independent labelled cases. No NLI, multi-document clustering or technical augmentation implementation is included.

## Working set

- 2026-09-08 [CODE] docs/research/ATTRIBUTE_FIRST_IMPLEMENTATION.md
- 2026-09-08 [CODE] docs/research/ATTRIBUTE_FIRST_SMOKE.json
- 2026-09-08 [CODE] docs/research/PHASE1_CLAIM_ANCHORED_PLAN.md
- 2026-09-08 [CODE] backend/app/services/case_analysis/claim_anchored/
- 2026-09-08 [CODE] backend/app/services/case_analysis/pipeline_config.py
- 2026-09-08 [CODE] backend/app/services/workflow/pipeline_execution.py
- 2026-09-08 [CODE] backend/app/services/workflow/analysis_execution_receipt.py
- 2026-09-08 [CODE] backend/app/services/chat/analysis_run_config.py
- 2026-09-08 [CODE] backend/tests/test_claim_anchored_postgres.py
- 2026-09-08 [CODE] backend/scripts/smoke_claim_anchored.py
- 2026-09-08 [CODE] backend/requirements.txt
- 2026-09-08 [CODE] docker-compose.yml

## Receipts

- 2026-09-08 [TOOL] Final pytest tests -q --tb=short with temporary PostgreSQL on 127.0.0.1:55440: 386 passed, 2 subtests, one upstream FastAPI/httpx warning in 12.35s. Temporary server stopped afterward. Earlier full run had connection-refused failures after the previous temporary server disappeared; fresh isolated instance resolved the infrastructure issue.
- 2026-09-08 [TOOL] Frontend npm test: 151 passed across 36 files; npm run check:api-types passed. Ruff --target-version py311 --select F,I, Python syntax, Compose config --quiet and git diff --check passed; max touched Python file 288 lines at check.
- 2026-09-08 [TOOL] Real synthetic Thai smoke via Doppler env_cybercase_framework/dev: 3 claims; extraction 6.890s / generation 4.813s; input 1492, output 652; reported cost 0.0010808 USD. No semantic evaluation. Receipt docs/research/ATTRIBUTE_FIRST_SMOKE.json.
- 2026-09-08 [TOOL] CAMS v4 method/limitations/Table 5 assessed; page 14 visually inspected. Starting git status clean; current model defaults inspected; public Luna pricing/endpoint-schema docs verified; anonymous CAMS artifact URL could not be opened. Planning document and ledger only.
- 2026-09-07 [TOOL] V11 migration audit: 53 passed in 10.50s across citations, trace, canonical state, main analysis, optional RAG, applicability and stateful clarification. CAMS v4 checked. No provider, frontend or report tests in this turn; no production edits.
- 2026-09-07 [TOOL] Attribute-First audit: source_citations, analysis_trace_v3 and document_ingestion_eval tests: 32 passed in 6.03s. Synthetic parser accepted contradicted claim with exact quote and accepted trace after removing absent quote; Thai whitespace WER one-character example = 1.0. No provider calls or production edits.
- 2026-09-07 [TOOL] Final thesis: 89 pages, no blank pages, six chapters, five figures, 80 native math objects, eleven references; visual review completed and original SHA256 unchanged. Receipt: deliverables/thesis_kmutnb_english/review/full_revision_receipt.json. Prior software tests are dated receipts, not rerun for document editing.
- 2026-09-06 [TOOL] Read-only audit at main d889226: 39 tests passed (stateful clarification decisions, gap assembly, v3 trace); actual transpiled frontend parser returned null for canonical v3 gap, accepted legacy affects control. Three DOCX samples read locally. No live provider/browser/prosecutor evaluation; only audit document and ledger changed.
- 2026-09-05 [TOOL] FINAL REFACTOR: backend 351 passed + 2 subtests (includes four PostgreSQL/API tests); frontend 36 files/150 passed; generated API drift, TypeScript, full ESLint, production build, scoped Ruff/format and whitespace checks pass. Prompt text hashes match baseline. Original 13 frontend file hashes preserved except two hooks intentionally extended for retry. Disposable PostgreSQL server stopped; existing application database untouched. Details: backend/REFACTOR.md.
- 2026-09-05 [TOOL] Frontend state/polling refactor: Vitest 35 files/145 tests (16 new regression cases); tsc --noEmit, full/scoped ESLint, final Next production build and diff checks pass. Changed code files max 235 lines. Browser on temporary localhost:3011 frontend and localhost:8011 synthetic API verified selection, Back, message processing/completion, draft clearing, Report navigation and zero final console errors. Temporary servers stopped. Backend/rag_service unchanged; Docker unavailable, live backend/provider not tested.
- 2026-09-05 [TOOL] Refactor review at clean main d889226: measured 8 production files above 300 physical lines; traced current backend/frontend contracts. pytest analysis_trace_v3, canonical_analysis_state, source_citations, stateful_clarification_pipeline, report_view_model_and_pdf: 41 passed. Vitest case-overview, chat-followup, ChatReportView, ChatWorkspaceIntake with --maxWorkers=2: 19 passed. No application edits or live E2E verification.
- 2026-09-04 [CODE] Read-only warning trace: service.py:130 appends one warning for each PDF page routed to OCR, before provider invocation. DocumentIngestionResult.tsx:19 labels any warnings as Review required; case-narrative-document.ts:53 also sets needs_review for any warning. These five notices do not establish OCR failure or low confidence. No product code changed; severity separation remains unimplemented.
- 2026-09-04 [TOOL] Typhoon activation follow-up: local settings, Compose default and running backend select typhoon/TyphoonDocumentRecognizer. Container initially failed router import because google-auth was absent; lazy Google factory import restored startup. Live /api/v1/health returns ok/database connected. 17 focused provider/API tests and scoped Ruff/format/diff checks pass; no OCR request, provider removal, commit or push.
- 2026-09-04 [TOOL] Google Vision baseline: 28 existing ingestion + 51 new Google tests; full backend 336 passed and 2 subtests; frontend focused 17 passed, full 129 passed with --maxWorkers=2 after 3 default-worker timeouts; TypeScript/scoped ESLint/Ruff, 33-file format check, compileall and diff check pass. 17 changed code files are below 300 lines. Full backend Ruff has 14 unchanged violations; broader format check also has unchanged violations. ADC unavailable, so no live Google call or real case data transfer. Architecture/config/semantics/fixture/file inventory: backend/app/services/document_ingestion/GOOGLE_VISION.md. Uncommitted on main at baseline 744a7ba.
- 2026-09-03 [TOOL] Published 5755d684c22147bca2642b1982b8f8112a8d2d0f to origin/main: 44 reviewed files, staged whitespace check passed, all code files below 300 lines, 11 focused backend citation tests passed, existing frontend validation preserved. git ls-remote confirmed exact remote parity. Push succeeded despite the existing nonfatal credential-manager-core warning.
- 2026-09-03 [TOOL] Overview final verification: full frontend suite 31 files/126 tests; final focused Overview/evidence suite 4 files/17 tests; tsc, full and scoped ESLint, final production build and scoped diff checks pass. Browser: all 13 findings accessible, default uncertainty visible, exact page-4 quote centered in desktop/mobile drawer, native close restores citation focus, 390x844 mobile has zero horizontal overflow, Ask/Report navigation works, legacy multi-source cases render. Populated gaps/conflicts verified in fixtures; inspected saved cases have no recorded gaps. All 19 touched frontend code files are below 300 lines. All 24 pre-existing dirty/untracked baseline files match SHA-256 hashes. No case data changed; no commit or push. Initial JSX typo and test-environment dialog/timeout issues were corrected before final checks.
- 2026-09-03 [TOOL] Preparation workspace: 29 test files/120 tests, TypeScript, scoped ESLint, production build, scoped whitespace checks pass. Browser: 320px bounded preview, full-text dialog, raw table markup only in Raw Text, canonical counts, analysis navigation, native chooser, manual readiness and pending-document gate, 390x844 mobile controls/primary CTA visible with zero horizontal overflow; zero browser errors. Disposable empty draft removed. Extraction/retry API contract tested with mocks, no live provider call. All touched code files remain below 300 lines; unrelated baseline hashes unchanged.
