# Continuity Ledger

## Snapshot

- 2026-09-02 [CODE] Formal report projection now uses the explicit analysis chronology with real date/time labels, source-linked findings instead of raw narrative dumps, domain-neutral verification actions, and an optional MITRE section.
- 2026-09-02 [TOOL] Supersedes the report runtime incident: Alembic `0002_optional_report_context` is applied, no-MITRE reports persist with null retrieval context, identical idempotent retries return the existing report, and long evidence now exports as a page-splittable PDF.
- 2026-09-01 [CODE] Report creation no longer applies the custom source/MITRE binding validation gate; typed report construction and snapshot guards remain.
- 2026-09-01 [CODE] Report creation now requires raw evidence plus completed General Case Summarization, while MITRE/RAG context is optional and persisted as a nullable technical augmentation.
- 2026-09-01 [CODE] Page-aware evidence citations keep the reviewed full narrative authoritative while Overview/Chat show validated exact quotes, document pages when available, and narrative-only labels without fabricated pages.
- 2026-09-01 [CODE] Gap Analysis prompt v4 is domain-neutral: case-specific wording replaces incident/cyber role wording, and MITRE explanation no longer affects general gap priority; MITRE trust-boundary exclusions remain.
- 2026-09-01 [TOOL] Production LLM-prompt audit found the Main Case Analysis prompt domain-neutral with explicit anti-cyber-bias guards; one low-severity Follow-up Gap Analysis rubric still gives `MITRE explanation` material-priority weight.
- 2026-09-01 [USER] Approved implementation of the revised UI plan; current authorization is P0 contract/trust repair only.
- 2026-09-01 [USER] Supersedes the prior scope note: the focused frontend UI/UX redesign is authorized; APIs, backend behavior, and `rag_service/**` remain unchanged.
- 2026-09-01 [CODE] Overview now reads validated canonical v3 summaries, claims, supporting/contradicting sources, reasoning, gaps, and optional MITRE state directly; legacy markdown parsing is isolated to the v2 adapter.
- 2026-09-01 [CODE] Synthetic chronology and “established” claims were removed; the UI now presents case summary, status-labelled findings, open questions, and conditional external cyber reference.
- 2026-09-01 [TOOL] Frontend typecheck, lint, 92/92 tests, production build, and desktop/mobile rendered QA pass.
- 2026-08-31 [USER] Requested reviewed OCR `merged_text` injection into the case narrative while preserving General Case Summarization as core, conditional MITRE augmentation, a single-document baseline, future `1 Case -> N Documents`, and HTR as out of scope.
- 2026-08-31 [CODE] Intake now converts one ingestion result into an editable narrative draft and submits list-shaped document provenance/quality metadata only after the user reviews and submits the case.
- 2026-08-31 [CODE] Raw evidence text/hash remains message-content-only; OCR confidence/warnings travel separately to Main Analysis and the conservative MITRE applicability gate.
- 2026-08-31 [TOOL] Full regression passes: frontend 90/90 and backend 259/259 plus 2 subtests; scoped ESLint and Python compileall pass.
- 2026-08-31 [USER] Requested every file in the four-file developer-handover set as PDF.
- 2026-08-31 [TOOL] Four polished A4 PDFs now cover the handover narrative, exhaustive symbol index, Python generator, and TypeScript extractor; all 124 rendered pages passed structural and visual QA.
- 2026-08-31 [USER] Requested a full senior-developer handover explaining the live architecture, file purposes, and every first-party source function for incoming developers.
- 2026-08-31 [CODE] Developer handover now documents the current dirty `main` checkout at `58f2302`; a reproducible syntax-tree index covers runtime, tests, migrations, research, and tooling.
- 2026-08-30 [USER] General Case Summarization remains the core behavior; clarification improves but never blocks the initial grounded summary.
- 2026-08-30 [CODE] Phases 1-4.3 remain complete: validated canonical `case_overview` v3 traces bind current evidence, claims, one Gap Analysis result, optional RAG, and provider-constrained `A-01`..`A-64` IDs.
- 2026-08-30 [CODE] Phase 5 stateful adaptive clarification is complete for new v3 turns and selects only from the latest validated in-memory canonical trace for the fresh evidence snapshot.
- 2026-08-30 [CODE] Raw user content and evidence-hash semantics are unchanged; assistant questions, ASK messages, prior analysis, RAG, and MITRE remain non-authoritative.

## Done (recent)

- 2026-09-02 [CODE] Reworked the report PDF into a formal three-page case-review document with a seven-row dated timeline, compact claim/source table, conditional technical context, general-case follow-up actions, and a dedicated traceability appendix.
- 2026-09-01 [CODE] Implemented exact-quote evidence citations, validated document page spans, narrative-only source highlighting, Overview/Chat citation chips, and a responsive source inspector without an additional model call.
- 2026-09-02 [CODE] Completed the optional-MITRE report cutover: nullable retrieval migration, stable snapshot idempotency, page-splittable evidence PDF rendering, and generic/no-RAG regression coverage.
- 2026-09-01 [CODE] Removed residual cyber coupling from the general Gap Analysis system/user prompts, bumped the prompt version to v4, and added prompt-boundary regression assertions.
- 2026-09-01 [CODE] Implemented revised-plan P0 plus the focused workflow-first frontend redesign: canonical v3 overview projection, honest evidence labels, grouped navigation, progressive disclosure, traceable sources, and modular sub-300-line production UI files.
- 2026-08-31 [CODE] Completed the reviewed single-document OCR-to-case-narrative handoff, uncertainty provenance, conditional-MITRE quality context, modular workspace actions, and regression coverage without DB migration or `rag_service/**` edits.
- 2026-08-31 [CODE] Added the senior-engineer handover narrative, exhaustive file/function index, and sub-300-line Python/TypeScript index generators under `docs/developer-handover/`.

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

## State (Done/Now/Next)

- 2026-09-02 [TOOL] Done: rebuilt the backend and regenerated the live report as `output/pdf/CyberCase-Report-v1-Formal.pdf`; all three rendered pages passed visual QA and timeline/markdown/HTML content assertions.
- 2026-09-02 [TOOL] Done: rebuilt/recreated the backend, applied `0002_optional_report_context`, verified the live nullable column and healthy API, replayed the original no-MITRE report successfully, and exported its PDF with HTTP 200.
- 2026-09-01 [CODE] Done: Evidence pinpointing is implemented for new v3 analyses; existing analyses remain readable and use message-level source previews until regenerated with exact citations.
- 2026-09-01 [CODE] Done: Report generation accepts generic structured claims without invoking `validate_structured_report`, and a completed general analysis can produce a report without MITRE/RAG context.
- 2026-09-01 [TOOL] Done: Domain-neutral Gap Analysis prompt cleanup passes 57 focused general-case, gap-transport, and stateful-clarification tests plus compileall.
- 2026-09-01 [TOOL] Done: Read-only prompt audit covered all production backend model calls, the served/legacy MITRE GraphRAG prompts, the Typhoon-generated OCR boundary, and isolated research/evaluation prompt families; no code changed.
- 2026-09-01 [CODE] Done: P0 contract/trust repair is implemented and verified; the known v3 Overview recognition defect is closed.
- 2026-09-01 [CODE] Superseded: P1 workflow/navigation redesign is implemented in the frontend; no backend or `rag_service/**` scope was added.
- 2026-08-31 [CODE] Done: Reviewed OCR merged text can populate and submit the initial case narrative with bounded source-quality metadata; no Case=File model or schema migration was introduced.
- 2026-09-01 [TOOL] Done: Final frontend TypeScript, ESLint, Vitest, and Next.js production-build checks pass; live provider-backed OCR was not invoked in this turn.
- 2026-08-31 [USER] Next: Optionally run one real printed-document smoke through configured Typhoon credentials and evaluate OCR semantic-error impact against a human transcript.
- 2026-08-31 [TOOL] Done: The requested four-file handover PDF export is complete and visually verified; no application behavior changed.
- 2026-08-31 [CODE] Done: Complete developer handover suite created for the current checkout; application behavior was documented but not changed.
- 2026-08-30 [CODE] Done: Phase 5 backend semantics and tests are implemented without Phase 6 or forbidden-scope changes.
- 2026-08-30 [TOOL] Open: semantic identity-topic reformulation can still bypass exhaustion; this P0 frontend change does not alter backend clarification normalization.

## Working set

- 2026-09-02 [CODE] `backend/app/services/reports/report_analysis_projection.py`
- 2026-09-02 [CODE] `backend/app/services/reports/report_finding_projection.py`
- 2026-09-02 [CODE] `backend/app/services/reports/report_view_model_builder.py`
- 2026-09-02 [CODE] `backend/app/services/reports/report_pdf_story.py`
- 2026-09-02 [CODE] `backend/app/services/reports/report_pdf_evidence_story.py`
- 2026-09-02 [CODE] `backend/app/services/reports/pdf_design.py`
- 2026-09-02 [CODE] `backend/app/services/reports/pdf_chrome.py`
- 2026-09-02 [CODE] `backend/app/services/reports/report_view_model_text.py`
- 2026-09-02 [CODE] `backend/tests/test_report_view_model_and_pdf.py`
- 2026-09-02 [TOOL] `output/pdf/CyberCase-Report-v1-Formal.pdf`

## Receipts

- 2026-09-02 [TOOL] Formal-report validation passes: 280 backend tests plus 2 subtests, focused report tests 5/5, backend image rebuild/recreate, health and live PDF HTTP 200, seven expected timeline dates, no rendered Markdown headings or raw HTML, all touched production files below 300 lines, and three-page full-resolution visual QA.
- 2026-09-02 [TOOL] Report repair verified after final image recreation: Alembic head `0002_optional_report_context`, health OK, original idempotent no-MITRE report `596d67b7-c5ed-4cd7-aa61-5e144882116a` completed/validated with null retrieval context, PDF HTTP 200 with `%PDF` signature and 75,707 bytes; full backend passes 280 tests plus 2 subtests.
- 2026-09-02 [TOOL] First migration attempt safely rolled back when the 38-character revision exceeded Alembic's `VARCHAR(32)`; revision was shortened to 28 characters and a regression assertion now enforces the limit.
- 2026-09-01 [TOOL] Evidence pinpointing validation passes: backend 278 tests plus 2 subtests, frontend 95 tests, TypeScript, ESLint, production build, scoped diff check, sub-300-line production files, desktop/mobile visual QA, and no browser console errors; `rag_service/**` is unchanged.
- 2026-09-01 [TOOL] Report generation regression: 7 focused report tests pass in `env_mitre`; targeted diff check passes; custom validation no longer runs during generation.
- 2026-09-01 [TOOL] Optional-RAG report validation: 14 focused backend report/schema/migration tests pass, 267 other backend tests pass when excluding the unrelated dirty canonical-analysis fixture, 9 report frontend tests pass, ESLint passes, Alembic head is `0002_optional_report_retrieval_context`, and no `rag_service/**` files changed; full-suite failures remain outside this change in dirty intake/overview fixtures and that canonical fixture.
- 2026-09-01 [TOOL] Prompt cleanup validation: 57/57 focused backend tests pass, follow-up compileall passes, scoped diff whitespace check passes, all touched files remain below 300 lines, and `rag_service/**` is unchanged.
- 2026-09-01 [TOOL] AUDIT BASELINE, superseded for Follow-up by prompt v4: Main Analysis forbids cyber assumptions and MITRE retrieval is gated; the audit found cyber role/priority wording in Gap Analysis, while RAG prompts remain intentionally MITRE-only and direct RAG `/query` has no independent applicability gate.
- 2026-09-01 [TOOL] P0 validation passes: `tsc --noEmit`, ESLint, Vitest 24 files/92 tests, and Next.js production build.
- 2026-09-01 [TOOL] Desktop 1440x900 and mobile 390x844 rendered QA passed on the live mounted frontend; source-evidence popover was also verified on mobile.
- 2026-09-01 [TOOL] Scoped P0 diff whitespace check passes and `rag_service/**` remains untouched; repository-wide diff check still reports the pre-existing blank EOF in `backend/tests/test_general_case_analysis.py`.
- 2026-09-01 [TOOL] All 17 existing source paths named by the revised P0/P1 working set resolve; the one unresolved path is explicitly marked as the proposed new `ClarificationActionCard.tsx`.
- 2026-08-31 [TOOL] OCR narrative regression covers editable merged-text injection, missing-confidence disclosure, one-document request validation, provenance separation from evidence text/hash, prompt transport, MITRE gate transport, and idempotency compatibility.
- 2026-08-31 [TOOL] Frontend full Vitest passes 23 files/90 tests; backend full Pytest passes 259 tests plus 2 subtests with one Starlette deprecation warning; scoped ESLint and compileall pass.
- 2026-08-31 [TOOL] `tsc --noEmit` remains red only on existing stale test fixtures (`ChatPanelFollowUp` and `ChatWorkspaceIntake`); Ruff and Black are not installed in the active backend environment.
- 2026-08-31 [TOOL] PDF outputs contain 17, 99, 5, and 3 A4 pages respectively; Pypdf found no empty pages and pdfplumber found no rendered characters outside page bounds.
- 2026-08-31 [TOOL] Poppler rendered all 124 pages to PNG; contact sheets plus full-resolution cover, body, table, code, middle, and final-page inspection found no clipping, overlap, black boxes, or unreadable layout.
- 2026-08-31 [TOOL] Generated index covers 436 first-party source files and 2,305 named Python/TypeScript/JavaScript symbols; all 436 file links resolve.
- 2026-08-31 [TOOL] Handover generator compiles, TypeScript extractor passes `node --check`, docs contain no trailing whitespace, and live backend OpenAPI confirms all documented `/api/v1` routes including the isolated ingestion preview.
- 2026-09-01 [TOOL] Focused UI redesign rendered QA passes at desktop and mobile; Overview pulse, grouped navigation, source popover, evidence-to-Chat, Intake, Chat, Report, and Technical Context were exercised.
- 2026-09-01 [TOOL] Final frontend validation passes: TypeScript, ESLint, Vitest 24 files/93 tests, Next.js production build, rendered DOM internal-field audit, trailing-whitespace audit, and sub-300-line production UI audit; `rag_service/**` is unchanged.
- 2026-08-30 [TOOL] Phase 5/canonical/gate regression and synthetic scenarios pass; optional RAG remains independent of clarification selection and can fail closed.
- 2026-08-30 [TOOL] Live threads A `42fecb16-f936-4f05-9d31-abd8db5e7e06`, B `3556f16d-ae81-4bda-b666-8e634aadbd4a`, and D `46712cc3-b065-4e71-bad8-773c3507dea7` persist exact short answers plus structural linkage, mark answered topics EXPLICITLY_UNKNOWN/non-askable, and select a different next gap.
- 2026-08-30 [TOOL] Live thread C `17c69176-a8d2-43af-8a03-230ba8e23adc` persists the new identity claim but immediately asks an equivalent reformulation; current bounded aliases do not unify “ตัวตนและลักษณะ” with “รายละเอียดและหลักเกณฑ์การยืนยันตัวบุคคล”.



