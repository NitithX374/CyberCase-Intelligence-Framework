# Continuity Ledger

## Snapshot

- 2026-09-07 [USER] Supersedes the earlier 44-page rewrite: preserve Gemini's full original structure and detail; revise English phrasing and necessary clarity/correctness only.
- 2026-09-07 [TOOL] COMPLETE: revised Gemini full original into deliverables/thesis_kmutnb_english/Cybercase_Thesis_KMUTNB_Full_Revised_English.docx: 89 pages, six chapters, 16 tables, five figures, 80 native math objects, eleven references. Rendered and visually reviewed; original hash unchanged.
- 2026-09-07 [USER] Backend/frontend are the author's scope; partner rag_service is downstream only. Document merge authorized; original Thai/English files and production work preserved. Research contribution, empirical evaluation and official English approval/template requirements remain open.
- 2026-09-06 [TOOL] Gemini added six Thai/English chapters and full documents. Unsupported case scores, invented claim enums/timeline, absolute guarantees and placeholder figures require correction. Preserve originals and production changes; output to deliverables/thesis_kmutnb_english.
- 2026-09-06 [USER] Current goal supersedes research selection: hold alternatives and assess thesis chapter readiness from F:\Chapter_II_Final.docx, F:\Draft_Chapter_I_Complete.pdf and F:\Enhanced Golf Swing Evaluation with MediaPipe.pdf.
- 2026-09-06 [TOOL] Read both drafts and example chapter structure/development sections; I-II-IV can be drafted, III partly, V-VI results/conclusions await research. Drafts contain audience/stack/reference mismatches; findings and outline: docs/research/THESIS_CHAPTER_READINESS.md. Supplied files unchanged.
- 2026-09-06 [TOOL] Five alternatives documented in docs/research/RESEARCH_ALTERNATIVES.md after targeted primary-source research: contextual explanations, attribution/uncertainty preservation, temporal constraints, external-knowledge separation and evidence-presentation evaluation. All remain proposals.
- 2026-09-06 [USER] Latest request expands research exploration to several alternatives beyond clarification admission; no contribution selected.
- 2026-09-06 [ASSUMPTION] Proposed one source-traceable clarification admission mechanism with gate-on/off matched evaluation; not accepted, implemented or evaluated. Story/inventories: docs/research/followup-admission/. Novelty remains UNCONFIRMED after a targeted primary-source literature check.
- 2026-09-06 [USER] Goal: assess backend explainability and fit to helping prosecutors understand police case files; sample directory is F:\งานอัยการ.
- 2026-09-06 [TOOL] Current main HEAD d889226 has pre-existing uncommitted backend/frontend refactors. Preserved; no production edits, staging, commit or push in this audit.
- 2026-09-06 [CODE] Backend is a multi-stage LLM-plus-code workflow; gap identification, priority and semantic interpretation remain model judgments. Existing source/trace validation does not prove semantic support.
- 2026-09-06 [TOOL] Reproduced frontend parser rejecting canonical v3 selected_gap_detail because it expects legacy affects rather than affected_claim_ids; legacy control accepted. 39 focused backend tests passed.
- 2026-09-06 [TOOL] Read three investigation-report DOCX samples; one includes police-to-prosecutor forwarding letter and one includes LINE/transfer-slip evidence in an ordinary fraud case. Some samples contain appended drafting instructions/revised narrative.
- 2026-09-06 [CODE] ATT&CK gate intentionally skips ordinary technology references; dedicated source-backed term explanations and explicit executable review/gap criteria are proposed, not implemented.
- 2026-09-06 [CODE] Done: assessment at docs/product/BACKEND_EXPLAINABILITY_REVIEW.md. Next: validate comprehension rubric and implementation scope with user/professor. Open: complete prosecutor workflow and expert acceptance criteria UNCONFIRMED; no live provider or user study performed.
- 2026-09-05 [TOOL] Previous six-area refactor remains complete and uncommitted; its 351 backend/150 frontend validation receipts are recorded in backend/REFACTOR.md and below, not rerun in this audit.

## Done (recent)

- 2026-09-07 [TOOL] Completed full Gemini thesis revision, native math/figure repairs, bibliography and updated contents. Details: deliverables/thesis_kmutnb_english/review/FULL_REVISION_REVIEW.md.
- 2026-09-06 [TOOL] Completed explainability/product-fit audit, three sample DOCX text inspections, v3 explanation parser reproduction and 39 focused tests; proposals and limitations: docs/product/BACKEND_EXPLAINABILITY_REVIEW.md.
- 2026-09-05 [CODE] Completed remaining parser, metadata, follow-up, report and run-recovery work; final 351 backend/150 frontend tests and static/build checks pass. Recovery verified against disposable PostgreSQL and HTTP. Details: backend/REFACTOR.md.
- 2026-09-05 [CODE] Completed frontend Query-backed chat session, single polling loop, draft/retry state isolation, cancellation listener cleanup and 16 lifecycle regression tests. Final 145-test suite, lint, typecheck, build and synthetic browser QA pass.
- 2026-09-04 [CODE] Added Google Vision OCR confidence baseline, provider-neutral words, explicit region confidence semantics, ADC configuration documentation and synthetic response receipt. Core analysis and HTR behavior remain unchanged.
- 2026-09-03 [CODE] Overview preserves the original summary, groups real claim/status fields with uncertainty first, collapses only long reported/inference groups, and opens filename/page citations in a responsive native drawer at the exact highlighted passage. Real analysis/material metadata and compact questions replace heavy side cards; source ordinals distinguish separate clarification links.
- 2026-09-03 [CODE] Superseded inline intake layout with a preparation workspace: material controls at top/right, explicit lifecycle status, bounded readable/raw text with full modal reader, real findings/evidence/gap counts, English controls and a persistent primary footer. Original source content/provenance and one-document extraction remain intact.

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

## State (Done/Now/Next)

- 2026-09-07 [TOOL] Done: full-original English revision and document QA; production changes and original documents preserved.
- 2026-09-07 [TOOL] Now: deliver the revised 89-page DOCX and record review receipts.
- 2026-09-07 [ASSUMPTION] Next: professor review and future empirical evaluation; contribution selection and expert acceptance remain UNCONFIRMED.

## Working set

- 2026-09-06 [CODE] docs/product/BACKEND_EXPLAINABILITY_REVIEW.md
- 2026-09-06 [CODE] backend/REFACTOR.md
- 2026-09-06 [CODE] backend/app/services/workflow/pipeline_execution.py
- 2026-09-06 [CODE] backend/app/services/case_analysis/
- 2026-09-06 [CODE] backend/app/services/followup/
- 2026-09-06 [CODE] frontend/src/lib/chat-followup.ts
- 2026-09-06 [CODE] frontend/src/components/conversation/
- 2026-09-06 [CODE] rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py
- 2026-09-06 [CODE] rag_service/app/RAG/GraphRAG/pipeline/evaluator.py
- 2026-09-06 [CODE] F:\งานอัยการ\Dataset

## Receipts

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

- 2026-09-03 [TOOL] Intake integration: 27 frontend test files/112 tests, TypeScript, scoped ESLint, production build, and scoped whitespace checks pass. Browser verified shared input controls, native file chooser, persisted filenames, 390x844 mobile layout with zero horizontal overflow, and OCR settings. Empty test draft removed; four original saved cases remain. OCR API behavior verified with mocks; no live provider extraction requested. Initial JSX rewrite syntax error was corrected before final validation; touched code files remain below 300 lines.

- 2026-09-03 [TOOL] Published 93c5ae1 to origin/main after exact staged-frontend validation: 26 test files/107 tests and TypeScript pass; staged whitespace check passes; 30 frontend files only. Push succeeded despite a nonfatal credential-manager-core warning. Remote main equals local HEAD and index is empty. Earlier full-worktree validation passed 108 tests, lint, build and browser QA.

- 2026-09-03 [TOOL] UI cleanup: Vitest 26 files/108 tests pass, scoped ESLint, production build and TypeScript pass, desktop and 390x844 mobile QA pass, zero horizontal overflow, page-4 source inspector opens, chat selection feedback works, browser error log is empty, and all touched code files remain below 300 lines. Initial test failure expected the removed Active case badge; updated assertion passes.

- 2026-09-02 [TOOL] Formal-report validation passes: 280 backend tests plus 2 subtests, focused report tests 5/5, backend image rebuild/recreate, health and live PDF HTTP 200, seven expected timeline dates, no rendered Markdown headings or raw HTML, all touched production files below 300 lines, and three-page full-resolution visual QA.

- 2026-09-02 [TOOL] Report repair verified after final image recreation: Alembic head `0002_optional_report_context`, health OK, original idempotent no-MITRE report `596d67b7-c5ed-4cd7-aa61-5e144882116a` completed/validated with null retrieval context, PDF HTTP 200 with `%PDF` signature and 75,707 bytes; full backend passes 280 tests plus 2 subtests.

- 2026-09-02 [TOOL] First migration attempt safely rolled back when the 38-character revision exceeded Alembic's `VARCHAR(32)`; revision was shortened to 28 characters and a regression assertion now enforces the limit.

- 2026-09-02 [TOOL] V1 final validation passes: backend 285 tests plus 2 subtests, frontend 26 files/108 tests, TypeScript, ESLint, compileall, focused Ruff, production build, and scoped diff checks; all touched code files remain below 300 lines and `rag_service/**` is unchanged. Full repository Ruff/Black checks still report unrelated baseline violations.

- 2026-09-01 [TOOL] Report generation regression: 7 focused report tests pass in `env_mitre`; targeted diff check passes; custom validation no longer runs during generation.

- 2026-09-01 [TOOL] Optional-RAG report validation: 14 focused backend report/schema/migration tests pass, 267 other backend tests pass when excluding the unrelated dirty canonical-analysis fixture, 9 report frontend tests pass, ESLint passes, Alembic head is `0002_optional_report_retrieval_context`, and no `rag_service/**` files changed; full-suite failures remain outside this change in dirty intake/overview fixtures and that canonical fixture.

