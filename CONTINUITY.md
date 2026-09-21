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
- 2026-09-21 [TOOL] Chat simplification failure is referent loss, not token-window overflow: the provider completed normally, the prior T1190 answer was present in history, and explicitly restating that answer produced the correct simplification under the same analysis context.
- 2026-09-21 [USER] Active backend task: assess gaps before full analysis so askable cases skip the MITRE gate, RAG retrieval, main analysis call, and binding.
- 2026-09-21 [CODE] Production now uses DB-free `advance_case`; assessment rows persist with status `assessment` but never move `latest_analysis_result_id`.
- 2026-09-21 [TOOL] LADDER benchmark paused after confirming the pasted prompt's label headings are inverted; runner and LADDER ground truth use `0 = no concrete adversarial action` and `1 = concrete ATT&CK pattern`.
- 2026-09-21 [TOOL] Matched LADDER benchmark completed on 662 rows for XLM-R, Luna, and DeepSeek across English, Google-Thai, and NLLB-Thai; accuracy by dataset was XLM-R `85.35/86.10/81.57`, Luna `82.18/79.00/74.02`, and DeepSeek `77.79/75.98/67.82`.
- 2026-09-21 [TOOL] Independent recomputation from raw JSONL matched every stored confusion matrix and metric; all 662 unique IDs eventually succeeded, but raw checkpoints retain transient failed attempts (Luna EN 4, Google-Thai 1, NLLB-Thai 8), so the earlier claim of zero failures was inaccurate.
- 2026-09-21 [TOOL] `CTI_dataset.json` was inspected only by path; it was not run because the user asked to finish the preceding LADDER benchmark first.
- 2026-09-21 [TOOL] CTI pilot ran on the first 10 Thai `query` samples with user-assigned label `1` for every sample; XLM-R, Luna, and DeepSeek each predicted `1/10`, with no pilot call failures. This is a positive-only sanity check, not a two-class accuracy estimate.
- 2026-09-21 [CODE] LLM benchmark prompt now injects three deterministic examples from LADDER `train.csv` only (train rows 1108 label 0, 1 label 1, and 9 label 1) and raises if any selected text overlaps `test.csv`.
- 2026-09-21 [TOOL] Few-shot3 full pipeline completed on all 662 EN, Google-TH, and NLLB-TH rows for all three models; final LLM metrics had 662 unique successes per cell after retries, while raw Luna Thai logs retain transient failed-attempt lines.
- 2026-09-21 [TOOL] CTI few-shot3 pilot repeated the first 10 Thai queries with the same train-only prompt; all three models predicted 10/10 relevant, recorded as a positive-only sanity check.
- 2026-09-21 [TOOL] CTI hard-positive 100 run completed from `CTI_dataset.json` using Thai `query`, user-assigned label 1 for every sample, and the same train-only three-shot prompt; Luna and DeepSeek predicted 100/100, XLM-R predicted 89/100.
- 2026-09-21 [CODE] CTI pilot runner now supports `query_en` and XLM-R-only execution without changing the existing Thai/all-model default.
- 2026-09-21 [TOOL] XLM-R English CTI pilot completed on the first 100 `query_en` samples; 80/100 predicted relevant at threshold 0.50, with 20 false negatives and no execution failures.
- 2026-09-21 [TOOL] XLM-R checkpoint `gate.json` sets `max_tokens` to 96, not 512; all 100 English CTI texts were 109-223 tokenizer tokens and all were truncated during inference.
- 2026-09-21 [TOOL] After setting XLM-R `max_tokens` to 316, the matched 100-sample CTI pilots completed without truncation: English 86/100 and Thai 98/100 relevant, with 0 failures in each run.
- 2026-09-21 [USER] Freeze XLM-R at `max_tokens=316`; prioritize a hard-negative or mixed-label external evaluation next.
- 2026-09-21 [TOOL] Matched EN/TH grouping at 316 is EN✓/TH✓ 85, EN✓/TH✗ 1 (`rcti_032`), EN✗/TH✓ 13, and EN✗/TH✗ 1 (`rcti_023`).

## Done (recent)

- 2026-09-21 [CODE] Added editable draw.io flow and component-architecture maps of the current Analysis and Chat/Follow-up systems, covering contracts, APIs, orchestration, ownership, persistence, outputs, frontend consumers, and trust boundaries.
- 2026-09-19 [CODE] Prior implementation milestone: CaseRun and rag_contexts removed; request-scoped analysis and Case Ask replace jobs/polling (historical ledger D058/D059).
- 2026-09-19 [CODE] Prior implementation milestone: source vocabulary and sources-page intake integration; four Case workspace tabs (historical ledger).
- 2026-09-20 [TOOL] Current route/schema checks passed (12 tests) and frontend Vitest passed (21 files, 96 tests); `tsc --noEmit` passed, while `npm run check:api-types` fails because generated analysisTypes.ts lacks two backend grounding fields.
- 2026-09-20 [CODE] Removed only source-drawer exact-quote highlighting and mark auto-scroll; retained citations, page binding, drawer behavior, and Materials navigation.
- 2026-09-21 [CODE] Added `case_assessment_v1`, shared gap-key prompt rules, assessment persistence, Alembic 0012, and assessment-aware follow-up round reading.
- 2026-09-21 [TOOL] Applied migration 0012 to local PostgreSQL; task-focused tests passed 34/34 with the real DB and task-file Ruff checks passed.
- 2026-09-21 [CODE] Refactored `post_case_message` into explicit retry, ordinary-chat, next-gap, and round-analysis paths; the locked write re-check prevents duplicate follow-up answers.
- 2026-09-21 [TOOL] Chat routing tests passed 19/19, the new PostgreSQL concurrency test passed, and the full backend suite passed 238 tests plus 2 subtests with only the two known Windows GTK PDF failures.

## Decisions

- 2026-09-19 [USER] Advisor clarification supersedes cybersecurity-only framing of the preceding proposal. Event representation is still a candidate method, not an approved requirement; cyber-only datasets cannot by themselves establish general-case summarization performance.
- 2026-09-19 [ASSUMPTION] Revised recommendation: general event-supported summarization as the candidate treatment, OCR robustness as a bounded evaluation axis, and defer temporal attack-graph B2. This recommendation is not yet user-approved or implemented.
- 2026-09-19 [USER] D058-D060 retained: no run/job table or polling; use source vocabulary. Historical rationale and earlier decisions remain in the archived ledger.
- 2026-09-19 [USER] Current task supersedes earlier OCR/follow-up research framing for this proposal only; it does not authorize changing the product direction document or implementing the proposal.
- 2026-09-19 [ASSUMPTION] PROPOSED: JSON storage plus deterministic labeled-text serialization and raw sources; no graph database, multi-agent loops, or event-state persistence subsystem.
- 2026-09-19 [ASSUMPTION] PROPOSED: CASIE event-hopper/argument preservation is primary; ChronoCTI report/technique relation sets are separate. Preserve native multilabel relations and do not force a total timeline.
- 2026-09-21 [CODE] D061 ACTIVE: assessment uses a separate strict gaps-only schema rather than weakening `CaseAnalysisTrace`; `decide_followup` and `CaseAnalysisGap` remain unchanged.

## Now / Next

- 2026-09-21 [TOOL] Now: assess-stage, chat-routing, baseline LADDER, matched CTI XLM-R pilots at max_tokens 316, segmented top-3 evaluator implementation, BGE-M3 EN/TH pair analysis, rcti_003 class/logit/token diagnostic, base-vs-fine-tuned representation diagnostic, rcti_003 sentence ablation, one-ID production encoder-gate run, and the 81-row attack-pattern GT gate run are complete; segmentation tests passed 4/4 and runner Ruff checks are clean.
- 2026-09-21 [TOOL] Next: run the segmented evaluator on a genuinely multi-segment external set, then define or locate a verified negative source for mixed-label evaluation; BGE pair similarity needs a broader matched baseline before causal interpretation.

## Open questions

- 2026-09-19 [TOOL] CASIE repository licensing is UNCONFIRMED; public availability is verified but a top-level license was not visible.
- 2026-09-19 [TOOL] The older canonical direction document conflicts with supplied current instructions and inspected runtime; an authority reset is outside this task.
- 2026-09-19 [ASSUMPTION] Frozen model version, API budget, and availability of a second human auditor are UNCONFIRMED.
- 2026-09-20 [TOOL] Branch spelling `refactor/remove-case-trun` is UNCONFIRMED; the only matching local branch is `refactor/remove-case-run`, and no remote tracking branch exists.
- 2026-09-21 [TOOL] Superseded: the earlier `backend/app/routers/cases.py` import blockage no longer reproduces; the full backend Ruff run now passes.

## Working set

- 2026-09-21 [CODE] docs/architecture/case-analysis-chat-system-flow.drawio
- 2026-09-21 [CODE] docs/architecture/case-analysis-chat-architecture.drawio
- 2026-09-21 [CODE] backend/app/services/analysis/pipeline.py
- 2026-09-21 [CODE] backend/app/services/analysis/steps/assess.py
- 2026-09-21 [CODE] backend/app/services/analysis/contracts/assessment.py
- 2026-09-21 [CODE] backend/app/services/analysis/prompts.py
- 2026-09-21 [CODE] backend/app/services/workflow/run_analysis.py
- 2026-09-21 [CODE] backend/app/services/workflow/analysis_storage.py
- 2026-09-21 [CODE] backend/app/services/chat/case_chat.py
- 2026-09-21 [CODE] backend/alembic/baseline_versions/0012_analysis_assessment_status.py
- 2026-09-21 [CODE] backend/tests/test_analysis_pipeline.py
- 2026-09-21 [CODE] backend/tests/test_case_followup_postgres.py

## Receipts

- 2026-09-21 [TOOL] Architecture artifacts parsed as valid XML: system flow has 4 pages/211 cells and component architecture has 2 pages/97 cells; scoped `git diff --check` passed.
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
- 2026-09-21 [TOOL] Live case audit found analysis trace size 17,264 characters with 17 claims and 5 gaps; Chat serializes analysis plus conversation history into one JSON user message and provides no structural reply target for short requests such as “ไม่เข้าใจ ของ่ายกว่านี้”.
- 2026-09-21 [TOOL] Full backend run with PostgreSQL enabled reached 234 passing and five failures; after adapting to the pre-existing `mitre_table` removal, all non-PDF tests passed (230 plus 2 subtests) and report tests passed 7 with only the two documented GTK tests deselected.
- 2026-09-21 [TOOL] Alembic upgraded local PostgreSQL from 0011 to 0012 and reported 0012 as head.
- 2026-09-21 [TOOL] A later whole-tree Ruff run and route-surface collection were blocked by the concurrently replaced `backend/app/routers/cases.py` (`ModuleNotFoundError: app.auth`); all 18 assess-task files passed Ruff format/check.
- 2026-09-21 [TOOL] Implemented fixed-size 316-token segmentation with top-3 positive-vs-negative logit-margin aggregation; current CTI English/Thai samples each formed one segment and matched whole-document predictions within 6e-8, while a multi-segment smoke test produced `[316, 316, 102]` and selected all three segments.
- 2026-09-21 [TOOL] BGE-M3 dense cosine on the 13 EN✗/TH✓ pairs gave mean `0.8347`, median `0.8258`, range `0.7432-0.8993`; vectors were 1024-dimensional and results are under `results/bge_m3_en_fn_th_tp_max316`.
- 2026-09-21 [TOOL] rcti_003 diagnostic confirmed both languages use positive class 1 with identical runner indexing; EN logits `[0.7508,-0.5890]` gave p1 `0.2075`, TH logits `[-2.6918,2.8237]` gave p1 `0.9960`, and token counts were 151/153 with no truncation.
- 2026-09-21 [TOOL] rcti_003 base-vs-LADDER encoder cosine: CLS layer 12 fell from `0.9992` to `0.5637`, while mean pooling fell from `0.9967` to `0.9069`; CLS layer-wise divergence appeared mainly at the final layer.
- 2026-09-21 [TOOL] rcti_003 English sentence ablation: whole paragraph P(class 1)=0.207543; natural sentences S1-S4 scored 0.000960, 0.001714, 0.156627, and 0.986294; final-event clauses scored 0.009628 and 0.851859. Output is under `backend/experiments/ladder_relevance/results/xlmr_sentence_ablation_rcti003`.
- 2026-09-21 [TOOL] Production XLM-R encoder gate on `rcti_003` / `T1133`: Thai cue max segment score `0.304047` -> `RETRIEVE` at threshold `0.1`; aligned English sentence score `0.001714` -> `SKIP`. Output is under `backend/experiments/ladder_relevance/results/mitre_id_gate_rcti003_t1133`.
- 2026-09-21 [TOOL] Production XLM-R encoder gate on `attack-pattern-matching-gt.csv`: 81 English positive rows, one segment each, 79 TP / 2 FN, recall `97.53%` at gate threshold `0.1` (same 79/2 at `0.5`); FNs are row 39 `T1458` score `0.015835` and row 66 `T1628` score `0.052608`. Output is under `backend/experiments/ladder_relevance/results/attack_pattern_matching_gt_gate`.
