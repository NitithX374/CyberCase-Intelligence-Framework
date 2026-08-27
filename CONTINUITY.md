# Continuity Ledger

## Snapshot

- 2026-08-23 [USER] Demo uses raw user-authored initial, clarification-answer, and add-information messages as authoritative evidence; ordinary asks and all assistant/RAG text are excluded.
- 2026-08-23 [CODE] Fresh evidence invokes RAG, asks reuse the latest completed run-bound RagContext, and `analysis_trace_v2` binds source messages, evidence hash, retrieval context, and candidate-only MITRE associations.
- 2026-08-23 [CODE] Persistence is limited to chat threads/messages/runs, RagContexts, and chat reports; report generation remains deterministic and source-traceable.
- 2026-08-23 [USER] `rag_service/**` remains outside backend architecture changes.
- 2026-08-24 [CODE] Intake, Overview, Technical Context, Report Workspace, provenance, PDF viewing, safe error presentation, report idempotency, and module consolidation were completed and verified.
- 2026-08-24 [CODE] Frontend evidence semantics are centralized in `frontend/src/lib/case-evidence.ts`; standalone Investigation Issues remains removed.
- 2026-08-25 [USER] Goal: add a focused, deletable document-ingestion prototype for PDF, DOCX, PNG, and JPEG without persistence, analysis, MITRE, or RAG changes.
- 2026-08-25 [CODE] Added `/api/v1/document-ingestion/preview`, provider-neutral page/block contracts, deterministic content-hash document IDs, and page-traceable block IDs.
- 2026-08-25 [CODE] DOCX and usable PDF pages use native extraction; weak PDF pages and images use the configured Typhoon recognizer; mixed PDFs are supported per page.
- 2026-08-25 [TOOL] Focused ingestion/API tests, full backend suite, formatting, lint, and dependency checks pass; Docker build is UNCONFIRMED because Docker Desktop is not running.
- 2026-08-25 [USER] Requested `Downloads\งานอัยการ` be copied into project `Documents` and a PDF longer than three pages be ingested with results returned.
- 2026-08-25 [TOOL] Copied 324 files totaling 1,925,335,135 bytes to `Documents\งานอัยการ`; source/destination file counts and byte totals match.
- 2026-08-25 [TOOL] Live-ingested four-page `ลำดับ06 เอกสารผู้กล่าวหา.pdf`; all pages used Typhoon recognition and produced 37 validated blocks / 1,127 characters in the saved JSON result.
- 2026-08-25 [USER] Requested the root `Documents` directory be ignored by Git; `/Documents/` now excludes new dossier material while six pre-existing tracked PDFs remain tracked.
- 2026-08-25 [TOOL] Independent visual verification of all four source pages found all 24 core numeric/transaction fields correct, but sender-name abbreviation errors on 3/4 pages, one page-3 heading error, and unreliable handwritten-annotation capture.
- 2026-08-25 [USER] Supersedes the whole-page recognition target with a region-aware prototype: segment mixed pages, route printed regions to OCR and handwritten regions to HTR, then merge with page/region provenance; analysis, RAG, MITRE, gaps, and `rag_service/**` remain out of scope.
- 2026-08-25 [CODE] Region-aware ingestion is implemented with Google Enterprise Document OCR line/style segmentation, Typhoon printed OCR, Google/review-required HTR, deterministic routing, crop recognition, reading-order merge, region provenance, and unified/routed comparison modes.
- 2026-08-25 [CODE] Typhoon `<figure>` descriptions are excluded from transcription and retained only as non-authoritative generated content; handwriting and mixed regions remain review-required.
- 2026-08-25 [TOOL] Google Document AI's current official processor matrix explicitly marks Thai-script handwriting as `Not Supported`; the implemented Google HTR selection is invalid and must not be represented as Thai HTR.
- 2026-08-25 [TOOL] SUPERSEDES the earlier no-model finding: Hugging Face hosts Thai-handwriting checkpoints including `waritkan/thai-ocr-model` and `sivakorn-su/typhoon-ocr-7b-thai-handwriting-lora-v1`; neither is yet benchmarked on CyberCase legal documents.
- 2026-08-25 [USER] Requested the OCR/HTR document-ingestion prototype be implemented in the current website.
- 2026-08-26 [CODE] Intake exposes preview-only PDF/DOCX/PNG/JPEG upload with routed/unified selection; HTR is disabled directly without an env setting, handwriting is `needs_review` without transcription/provider calls, and printed OCR remains active.
- 2026-08-26 [USER] New goal: redesign the LLM Analysis Module as a general, evidence-grounded case-review system; the first task is a read-only repository assessment and must not implement code.
- 2026-08-26 [TOOL] Current assessment: fresh analysis and reports are hard-bound to RAG context; claims and gaps are split across `analysis_trace_v2` and follow-up metadata; the primary Overview remains cyber/MITRE-specific.
- 2026-08-26 [CODE] Phase 1-3 is complete: Main Case Analysis now uses the domain-neutral validated `analysis_trace_v3` runtime with optional external/MITRE context while explicit v2 reading remains intact.

## Done (recent)

- 2026-08-25 [CODE] Completed isolated document ingestion service, preview API, Typhoon adapter, native PDF/DOCX parsing, rendering, provenance, evaluation utility, documentation, and tests.
- 2026-08-25 [TOOL] Completed first real dossier ingestion and saved the page/block-traceable structured result under `Documents\งานอัยการ\Ingestion Results`.
- 2026-08-25 [CODE] Added root-only `/Documents/` ignore rule; verified the copied dossier/result no longer appears in Git status.
- 2026-08-25 [TOOL] Completed page-by-page rendered-PDF comparison against Typhoon output; temporary page renders were removed after inspection.
- 2026-08-26 [CODE] Disabled HTR routing and removed its env/config requirement while retaining handwriting provenance, manual-review warnings, and the no-analysis/no-persistence boundary.
- 2026-08-26 [CODE] Added v3 claim support/contradiction provenance, gaps, optional retrieval context and MITRE context, explicit v2/v3 reading, and five-domain characterization plus validator tests.
- 2026-08-26 [CODE] Generalized Main Case Analysis, switched provider/runtime output to v3, kept gaps empty, added optional external context and trusted backend bindings, and preserved direct question-answer behavior.

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

## State (Done/Now/Next)

- 2026-08-26 [CODE] Done: Implemented only Phase 3 general Main Case Analysis with optional external context, v3 output/validation, direct QA behavior, and v2/v3 persistence compatibility.
- 2026-08-26 [TOOL] Now: Focused Phase 3 tests and the full backend suite pass; frontend/report readers remain v2-shaped and were intentionally not changed under this phase boundary.
- 2026-08-26 [USER] Next: Stop before Phase 4 canonical Gap Assembly or Stateful Follow-up and await explicit authorization.

## Working set

- 2026-08-26 [CODE] `backend/app/services/case_analysis/**`
- 2026-08-26 [CODE] `backend/app/services/workflow/outcome.py`
- 2026-08-26 [CODE] `backend/app/services/workflow/chat_run_completion.py`
- 2026-08-26 [CODE] `backend/tests/test_main_case_analysis.py`
- 2026-08-26 [CODE] `backend/tests/test_general_case_analysis.py`
- 2026-08-26 [CODE] `backend/tests/test_analysis_trace_v3.py`
- 2026-08-26 [CODE] `backend/tests/test_analysis_trace_cross_domain.py`
- 2026-08-26 [CODE] `backend/tests/test_structured_output.py`
- 2026-08-26 [CODE] `backend/tests/test_chat_raw_pipeline.py`

## Receipts

- 2026-08-25 [TOOL] `git check-ignore -v` confirms `/Documents/` ignores the ingestion result; scoped Git status shows only `.gitignore` modified and six existing Documents files remain tracked.
- 2026-08-25 [TOOL] Visual comparison receipt: dates/times, both masked accounts, transaction IDs, amounts, and fees matched on 4/4 pages; handwritten notes were not reliably preserved.
- 2026-08-25 [TOOL] Region-aware focused suite: 26 passed; full backend suite: 99 passed plus 2 subtests, with one pre-existing Starlette deprecation warning.
- 2026-08-25 [TOOL] Ruff check/format, Python compileall, and scoped git diff check passed; repository-wide diff check remains blocked by an unrelated pre-existing EOF blank line in `backend/tests/test_chat_followup_policy.py`.
- 2026-08-25 [TOOL] `google-cloud-documentai==3.15.0` and `typhoon-ocr==0.4.1` import from `env_mitre`; `pip check` reports no broken requirements.
- 2026-08-25 [TOOL] Docker build remains UNCONFIRMED because the Docker Desktop Linux engine pipe is unavailable.
- 2026-08-25 [TOOL] Official Google Document AI HTML row for Thai contains `compare-no` with `aria-label="Not Supported"` in the handwriting column; Cloud Vision's supported handwriting scripts also omit `Thai`.
- 2026-08-25 [TOOL] Primary-source literature review found ICDAR 2019 block-level Thai archive HTR, MIWAI 2021 BEST2019 HTR, ICEAST 2020 multilingual multi-task HTR, CycleAugment 2022 historical Thai word HTR, and KMUTNB 2024 province-name HTR; public searches found papers/datasets but no author-published inference package with pretrained Thai legal-handwriting weights.
- 2026-08-25 [TOOL] Website implementation validation: focused frontend 7/7, full frontend 87/87, and full backend 99/99 plus 2 subtests passed.
- 2026-08-25 [TOOL] ESLint, Ruff check/format, Python compileall, scoped diff check, and Next.js 16.2.10 production build all passed.
- 2026-08-25 [TOOL] Dependency audit found only undeclared `PIL`; after adding `Pillow>=11.0.0`, all declared backend imports load, focused ingestion tests pass 23/23, and `pip check` reports no broken requirements.
- 2026-08-25 [TOOL] Hugging Face audit: `waritkan/thai-ocr-model` provides a 1.38 GB TrOCR checkpoint plus Thai SentencePiece tokenizer and reports CER 0.488% without a documented legal-domain benchmark; the Typhoon 7B Thai-handwriting LoRA reports CER 13.36% and exact match 45.26% on 559 CPE-OPH samples while warning of train/test text overlap.
- 2026-08-26 [TOOL] HTR-disabled validation: focused ingestion 27/27, focused frontend 7/7, full backend 100/100 plus 2 subtests, full frontend 87/87, ESLint, Ruff, and Next.js production build passed.
- 2026-08-26 [TOOL] HTR env-removal validation: no HTR env/config identifiers remain, focused backend/API/route tests pass 15/15, Ruff and scoped diff check pass, and `rag_service/**` remains untouched.
- 2026-08-26 [TOOL] Assessment baseline: `main...origin/main`; dirty worktree contains existing document-ingestion/HTR work and was preserved without code changes.
- 2026-08-26 [TOOL] Live code trace confirms raw-evidence reconstruction excludes analyst asks/assistant text, `analysis_trace_v2` persists in assistant JSONB metadata, follow-up gaps persist separately, and report generation requires a completed `RagContext`.
- 2026-08-26 [TOOL] Phase 1-2 focused suite passes 25/25; full backend suite passes 123/123 plus 2 subtests; Python compileall and scoped diff checks pass.
- 2026-08-26 [TOOL] Repository-wide diff check remains blocked only by the pre-existing trailing blank line in dirty `backend/tests/test_chat_followup_policy.py`; no new scoped whitespace errors exist.
- 2026-08-26 [TOOL] Phase 3 focused suite passes 57/57; full backend suite passes 147/147 plus 2 subtests; Python compileall and scoped diff/whitespace checks pass.
- 2026-08-26 [TOOL] Scope audit confirms no Phase 3 edits under `rag_service/**`, frontend, reports, follow-up, or Alembic; their existing dirty worktree changes were preserved.



