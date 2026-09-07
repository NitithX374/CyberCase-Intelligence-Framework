# CyberCase: adversarial architecture and research assessment

Assessment date: 2026-09-07. Audited local commit: `7a347b4f0fd1c93e43fffc5c3844e0eb50c1410d`. The working tree was clean at the start. Origin is the repository supplied by the user; remote HEAD parity was not checked. This assessment concerns the local checkout. No production code, thesis document, or partner-owned RAG code was changed. No paid inference or real-case OCR experiment was run.

## Verdict

**Only if reframed. GO WITH NARROWED SCOPE.** There is a defensible applied comparison of generation strategies under OCR corruption. There is not yet evidence of a novel CyberCase summarization algorithm or a demonstrated reduction in semantic hallucination.

The strongest question is: **Under a fixed model and summary budget, how do context-only, evidence-first, and CyberCase structured generation differ in propagation of critical OCR errors into Thai case summaries, while preserving salient information and source attribution?**

Treat attribution as support relative to an input, and document fidelity as agreement with a verified transcription. They are different outcomes. A faithfully quoted OCR error can be a document-fidelity failure. This distinction is central to the proposed study, but not claimed as an unprecedented concept.

## A. Current architecture

Paths below are relative to the repository root; function names identify the inspected implementation.

| Stage | Exact implementation | Mechanism and limits |
|---|---|---|
| Extraction preview | `backend/app/services/document_ingestion/service.py`: `DocumentIngestionService.ingest`, `_ingest_pdf`; `parsers/pdf_text_parser.py`, `parsers/docx_parser.py` | Deterministic format/native-text routing; OCR on applicable pages. Produces text/pages/regions, not an independently verified case representation. |
| Recognition | `recognition/typhoon.py`; `recognition/google_vision.py`, `google_vision_response.py` | Learned OCR; Typhoon uses generative model inference. Confidence availability depends on provider. Google minimum word confidence is a reported score, not calibrated correctness. |
| HTR boundary | `backend/app/routers/document_ingestion.py`: region pipeline construction; `routing/region_router.py`: `RegionRouter.route` | The router is configured with `htr_enabled=False`. This does not prove a unified OCR model will never attempt handwriting on an unclassified page. Restrict the study to printed documents. |
| Review/import metadata | `frontend/src/lib/case-narrative-document.ts`; `backend/app/services/chat/document_provenance.py` | Text is reviewed/imported; document identity, page spans and quality metadata can accompany it. Human editing is an intervention and must not be mixed silently with raw OCR. |
| Authoritative snapshot | `backend/app/services/chat/raw_evidence.py`: `build_raw_evidence_snapshot`, `load_raw_evidence_snapshot` | Deterministic ordering, inclusion and hashing of initial user narrative, clarification answers and added information. Assistant/RAG output is excluded. “Authoritative” denotes the admitted input, not proven truth. |
| Workflow | `backend/app/services/workflow/pipeline_execution.py`: `process_chat_run`, `_run_fresh_analysis`, `_run_question` | Stateful run execution, snapshots and persistence; fresh analysis and Ask follow different paths. |
| MITRE admission | `backend/app/services/case_analysis/mitre_applicability_gate.py` and associated validation; workflow `attempt_mitre_applicability` | LLM applicability judgment plus deterministic provenance admission. Selects whether to retrieve technical context, not summary content. |
| Conditional retrieval | workflow `attempt_optional_rag`; partner `rag_service/app/RAG/GraphRAG/pipeline/` | Retrieval and downstream model stages, conditionally invoked. This is a separate subsystem and research scope. |
| Prompt preparation | `case_analysis/case_analysis_prompt_builder.py`: `build_case_analysis_prompt`, `build_overflow_case_context` | Deterministic JSON/context packing. External context is reduced before evidence; if necessary, evidence is truncated to a prefix. This is position-based budget management, not salience selection. |
| Main analysis | `case_analysis/case_analysis_executor.py`: `MainCaseAnalysisService.analyze` | One structured generation request per invocation, producing `answer`, `summary`, claims and optional MITRE associations together. No separate source-selection or sentence-planning call in this service. |
| Parsing and binding | `case_analysis/case_analysis_response_parser.py`: `parse_case_analysis_response`; `source_citations.py`: `bind_analysis_claim_citations`, `_bind_citations`; `validation.py`: `validate_analysis_trace_v3` | Deterministic schema, reference and provenance checks. Invalid literal quotes are discarded. Semantic entailment is not checked. Some structure failures return prose with an unavailable trace; forbidden provenance can fail the request. |
| Gap analysis | `followup/gap_stage.py`: `run_gap_analysis_stage`; `gap_analysis.py`; `case_analysis/gap_assembly.py` | Separate LLM gap judgment followed by normalization, claim linkage and validation. Occurs after main generation. |
| Follow-up decision | `followup/decision.py`: `evaluate_followup_outcome`; `stateful.py`: `select_next_gap`, `normalize_gap_key`; `policy.py` | Deterministic eligibility, repeat-topic and round limits; conditional LLM question policy. Topic exhaustion is not evidence that a question was resolved. |
| Materials display | `frontend/src/components/materials/CaseMaterialsView.tsx`; `frontend/src/lib/case-materials.ts`, `case-evidence.ts` | Read projection and evidence-role filtering. No entity extraction, evidence-first planning, or semantic adjudication here. |

**One-shot verdict:** main analysis is a single jointly structured generation stage; the complete application is a multi-stage, conditional and stateful workflow. It is inaccurate to describe either all of CyberCase as one call or the main summary as a fully decomposed attribution-first algorithm. Count actual calls: fresh runs can include applicability, main analysis, gap analysis, question policy and optional RAG calls; Ask and subsequent clarification runs differ.

**What is standard engineering:** typed output, prompt instructions, JSON schemas, source IDs, hashes, exact substring/page checks, persistence, retries/leases, context budgets and bounded follow-up orchestration. These may be useful engineering contributions, but do not establish a new grounding method. Generated epistemic labels and reasoning summaries remain model outputs, not access to internal token-level causal reasoning.

### Reproduced limitations

Local synthetic parser checks, with no provider call:

1. Source: `The witness did not see the transfer.` Claim: `The witness saw the transfer.` Exact quote: the complete source. Result: validated trace, one retained citation. Literal correctness does not imply entailment.
2. Replaced the quote with nonexistent text. Result: validated trace, zero retained citations, supporting source ID retained. A validated reported claim need not have a surviving exact quote.
3. In both checks, the unrelated strengthened summary `The transfer was proven.` survived. Neither `answer` nor `summary` has an enforced semantic mapping to the claim list.
4. Current OCR WER returns 1.0 for `เขาโอนเงิน` versus `เขาโอนเงน`: whitespace splitting treats each entire string as one word. It is not a defensible Thai lexical WER tokenizer.

Additional structural limits: support and contradiction cannot both use the same message ID in `validate_analysis_trace_v3`. One long police narrative can contain opposing statements inside the same message. Document/speaker/span-level contradiction is therefore more expressive than the current source-role contract. The provider claim-ID space and list are capped at 64; longer-case evaluation needs to acknowledge that bound.

The private source-text map supports post-generation binding, but is excluded from the model prompt. The raw snapshot uses narrative/clarification labels and separately supplies source IDs. This is not an explicit document-span planning representation. Page/quality context travels through optional context and can be reduced under overflow; no calibrated confidence-to-claim uncertainty rule was found.

### Existing experiments: useful assets, not ready-made evidence

| Existing asset | What it actually does | Reuse decision |
|---|---|---|
| `research/attribute_first_pilot/{contracts,prompts,runner,evaluator,provider}.py` | Predicts answerability, question type, relevant sentence IDs and epistemic state for cybersecurity QA; generation receives full original context plus predicted attributes. No sentence plan. Its “direct” prompt already says to use only supplied context. | Conceptually closer to attribute-conditioned QA than the cited ACL method. Do not relabel historical B0 as an unconstrained direct summary baseline. Reuse scaffolding only after protocol/accounting repair. |
| Same pilot: oracle arm | Supplies gold answerability/evidence/epistemic attributes. | Upper-bound diagnostic, not an equally informed deployable baseline. |
| Same pilot: metrics/CSV | Abstention/contradiction measures inspect predicted attribute labels; these do not directly score answer faithfulness. CSV exposes method names. Efficiency assumes four calls per item; skipped generation copies direct-result usage. Provider errors can return zero latency/usage. | Repair accounting, anonymize scoring, retain failures. Do not use these metrics as semantic-summary results. |
| `evaluation/analysis_pilot/` | Saved RAW_DIRECT/EXTRACTED_STATE report for ten cases with probe judgments. | Historical pilot only. `generator.py` imports absent `app.services.extraction.llm_extraction` and `structured_output_router` modules in this checkout. Not the current production main-analysis path; do not present saved scores as current evidence. |
| `experiments/context_refinement/` | Isolated English SEvenLLM context compression with LLMLingua-2, including summary tasks; protected-span preservation is measured afterward, not enforced. | Related pre-generation selection/compression work already exists outside production. It is not claim attribution or Thai OCR validation. Reuse manifest/reproducibility concepts, not its task conclusions. |
| `experiments/semantic_verification/`, `experiments/ctinexus_extraction_benchmark/` | Separate synthetic verification/extraction experiments. | Candidate annotation/probe utilities. Their existence is not summarization or prosecutor evaluation. |
| `backend/app/services/document_ingestion/evaluation/metrics.py`; `backend/tools/document_ingestion_eval.py` | Edit-distance CER/WER, supplied critical-field exact matches, aggregation of supplied unsupported counts. | CER can be reused with declared normalization. Unsupported counts are inputs, not independently discovered hallucinations. WER needs Thai segmentation; critical fields need gold/predicted annotations. |
| Partner `rag_service/.../evaluation/generation_metrics.py` | Optional RAGAS faithfulness; separate ROUGE-L, BERTScore and token-overlap paths. RAGAS can be unavailable. | Do not equate fallback overlap scores with faithfulness or transfer RAG QA scores to case summaries. Leave partner implementation untouched. |

## B. Baselines and fairness

The ACL method selects verbatim spans, groups them into sentence plans, then generates sequential sentences linked to those groups. A two-call selection–generation adaptation removes planning and sequential fusion and must be named accordingly. Selected-span grounding is an instruction/conditioning mechanism, not a semantic guarantee. See the [paper](https://aclanthology.org/2024.acl-long.182/) and [authors' implementation](https://github.com/lovodkin93/attribute-first-then-generate).

| Arm | Definition | Primary-study role |
|---|---|---|
| B0 | Same source and audience/length instruction; simple summarize prompt | Optional prompt-sensitivity control; do not deliberately make it hallucinate or deny it the source. |
| B1 | Same source, explicit source-only, attribution/uncertainty-preservation instructions; one summary call | Essential strong context-only control. |
| B2-lite | LLM selects exact source spans; deterministic resolution; a second LLM generates from those spans with output-to-span links | Essential evidence-first adaptation. Not an exact ACL reproduction. |
| B3-core | Current `MainCaseAnalysisService` and parser, isolated from applicability/RAG/follow-up | Essential CyberCase component comparison. Score `trace.summary` as the primary summary; `answer` and claims are secondary products. Record trace-unavailable outputs as failures. |
| B4 | Same selected spans as B2-lite, then CyberCase-style structured output plus binding | Optional ablation to distinguish selection from output structuring. Modified input representation means an experimental adapter, not unchanged production. |

B1 versus B3 measures a package of prompt, output format and validation differences. It does **not** isolate the causal effect of “claim grounding.” To isolate that effect, add a format-matched one-call structured arm without claim citations, or use a 2×2 selection-on/off × structured-grounding-on/off design. Do this only if the thesis keeps RQ2 as a causal mechanism claim.

1. Use the same pinned model/version/provider route for all generation stages. A smaller selector changes the question to a heterogeneous system comparison. A second model is a later replication, not required for the minimal study.
2. Give every method the same document snapshot, order, IDs, source language and OCR condition. B2's downstream restricted context is its treatment, not an unfair input difference. Gold clean text is evaluator-only in OCR runs.
3. Match task instructions, context capacity, tuning effort and visible summary targets. Do not pad prompts to identical token counts or force equal total tokens across methods with different call counts. Report actual cost and, optionally, a separate matched-cost experiment.
4. Fix visible summary length targets, for example 5–7 sentences and a preregistered Thai-token/character range chosen on development cases. Report actual lengths and salient coverage. Do not truncate generated summaries after generation. Total B3 output must have adequate room for its schema, claims and answer as well as summary.
5. Fix temperature, top-p and supported seed settings. Temperature zero is not a reproducibility guarantee. Current main analysis does not pass an explicit temperature to `structured_output_request_options`; an experimental transport override is needed. Record output token floors and provider transformations too.
6. Count system prompts, schemas, repeated context, intermediate spans/plans, reasoning tokens where reported, output JSON, retries and failed requests. Missing usage is unknown, not zero. Judge and OCR cost are reported separately from generation cost.
7. A closer prompt-based ACL implementation uses one selection call, one planning call and one generation call per output sentence: approximately 2+m calls, excluding retries. Separate calls are not required for B2-lite, which deliberately uses two.
8. The two-call adaptation is defensible if spans are source-verbatim, resolved to stable offsets, truly constrain the second input, and remain linked to output units. Preserve negation, attribution and contextual antecedents; isolated entity names are insufficient evidence.
9. Invalid comparisons include gold spans only for a normal baseline, different OCR corrections, different external knowledge, counting JSON fields as summary text, scoring only B3's self-selected claims, hiding failures, unmeasured truncation, giving one arm interactive clarification, or calling a materially simplified pipeline an exact published-method reproduction.

Do not run the complete production workflow against one-call summarizers in the primary study. That mixes retrieval, follow-up, additional evidence and latency with summarization. A separate end-to-end product evaluation can be useful later.

## C. Research questions under adversarial review

Generic summarization hallucination is established prior work, including [Maynez et al.](https://aclanthology.org/2020.acl-main.173/). Attributed generation and citation evaluation are also established, including [ALCE](https://aclanthology.org/2023.emnlp-main.398/). OCR effects on summarization predate LLMs: [Jing et al.](https://aclanthology.org/W03-0504/). Modern downstream OCR benchmarking includes [OHRBench](https://openaccess.thecvf.com/content/ICCV2025/papers/Zhang_OCR_Hinders_RAG_Evaluating_the_Cascading_Impact_of_OCR_on_ICCV_2025_paper.pdf). A Thai case-document setting is a contextual distinction, not automatic methodological novelty.

| RQ | Assessment | Bachelor / applied publication | Unsafe claim → defensible wording |
|---|---|---|---|
| RQ1: unsupported information from instruction-tuned LLMs | Well covered generically; too broad without model, corpus, language, output length and claim definition. Descriptive evaluation. | Suitable thesis diagnostic; weak standalone publication unless dataset/error analysis is distinctive and reliable. | “We discover that LLMs hallucinate” → “We characterize unsupported propositions in a defined Thai case-summary benchmark.” |
| RQ2: claim grounding reduces unsupported claims | Existing broad literature; current B3 validation does not enforce entailment, and B1/B3 confounds several treatments. | Suitable narrowed ablation; publication requires a clean intervention and credible labels. | “Exact citations guarantee factuality” → “We estimate the observed effect of a specified structured-attribution prompt and validator on independent semantic labels.” |
| RQ3: grounded versus evidence-first generation | Useful comparative evaluation, not inherently a novel algorithm; quality/faithfulness/cost scope is manageable with one model and corpus. | Strong bachelor question; possible applied paper with meaningful case data and error analysis. | “CyberCase introduces attribution-first generation” → “We compare joint structured generation with an explicitly identified evidence-first adaptation.” |
| RQ4: OCR semantic errors and propagation | Strongest fit to advisor requirement; narrow “grounding or uncertainty-aware mechanisms” to tested methods. OCR effects themselves are known. | Strong thesis with verified transcription and paired analysis; best publication opportunity if the error-level annotations and findings add reliable evidence beyond generic OCR degradation. | “First OCR-robust legal LLM” / “prevents OCR hallucination” → “We measure critical OCR error propagation and attribution/document-fidelity trade-offs in Thai case summarization.” |

Recommended primary RQ is the narrow RQ4 in the verdict. RQ3 becomes its method comparison; RQ1 is a diagnostic and RQ2 is omitted as a causal claim unless the additional ablation is run. A careful evaluation study is a legitimate contribution; inventing another module is unnecessary.

## D. Metrics and annotation protocol

### Units and aggregation

Freeze one visible summary per arm. Independently split it into atomic propositions; do not use B3's claim list as the gold segmentation. Preserve who alleged what, negation, modality and time. Judge against the full permitted input and separately against a verified transcription, not just selected spans.

For each evaluable proposition assign supported S, contradicted C, or unsupported U (neither entailed nor explicitly contradicted). N=S+C+U. Record indeterminate labels separately with reasons; do not silently count them as supported. A statement that correctly reports an allegation is supported as an allegation, not as proof of the alleged event. Explicit conflicting sources must not be collapsed into a proven conclusion.

Report case-macro averages as primary and pooled counts as secondary; preserve all denominators. Empty summaries, missing traces and failed calls get a separate failure/abstention record, zero salient coverage, and undefined conditional faithfulness, never a perfect faithfulness score. Use paired case-cluster bootstrap confidence intervals; documents, OCR variants and repeat runs from one case are not independent samples.

| Metric | Exact operational definition | Required evidence / automation |
|---|---|---|
| ROUGE-1, ROUGE-2 | Clipped unigram/bigram overlap O with an independently authored reference: P=O/generated n-grams, R=O/reference n-grams, F1=2PR/(P+R). Freeze multiple-reference aggregation. | Reference summary; deterministic after fixed Thai tokenization. Additional scorer needed. |
| ROUGE-L | LCS length L over fixed generated/reference token sequences; P=L/generated tokens, R=L/reference tokens, report F1. Declare sentence handling and implementation; ROUGE-Lsum is distinct. | Reference; deterministic scorer. Current partner whitespace tokenizer is unsuitable as Thai lexical tokenization. |
| BERTScore | Mean maximum token-embedding cosine match from generated tokens to reference gives precision; reverse gives recall; harmonic F1. Freeze checkpoint, layer, IDF option and rescaling. | Reference plus frozen compatible multilingual encoder. Automatic learned similarity, not an LLM judge or entailment proof. |
| Supported Claim Rate | S/N, using independent summary propositions. | Human labels preferred; judge labels are estimates requiring validation. No reference summary required. |
| Unsupported Claim Rate | U/N under the mutually exclusive definition above. Also report total non-supported rate (U+C)/N so “unsupported” is not used ambiguously. | Same semantic annotations. |
| Contradicted Claim Rate | C/N: source directly conflicts with the proposition, not merely lacks evidence. | Same semantic annotations. |
| Citation Validity Rate | Mechanically valid proposed citation occurrences / all proposed citation occurrences, measured before filtering. Separate source-ID, exact-span and document-page validity. Deduplicate by frozen rule. | Deterministic IDs/text/hash/offset checks largely reusable. Must capture raw proposed citations; post-filter rate alone is selection-biased. |
| Citation Entailment Precision | Output-proposition/citation-set pairs whose cited union entails the proposition / all such cited pairs. Invalid citations count as failures. | Human support judgment or calibrated judge. Judge each cited union; two necessary spans can jointly support a claim without either doing so alone. |
| Individual citation precision | Relevant necessary-or-independently-sufficient links / all emitted links, if needed to detect gratuitous citations. | Semantic labels. Do not equate this with union entailment precision. |
| Citation Coverage | Summary propositions with a mechanically valid linked citation / all summary propositions; also report semantic coverage: propositions fully supported by their cited union / all propositions. | Link mapping plus semantic labels for the latter. No-citation B0/B1 have zero native coverage and undefined precision; they have not failed a requested citation task. |
| Citation burden | Median and distribution of unique cited characters per attributed proposition, alongside entailment. | Automatic once offsets are resolved. Important when discussing fine-grained attribution; short but insufficient quotes are not a win. |
| Salient Fact Coverage | Gold salient propositions correctly preserved / gold salient propositions, with a predefined critical subset reported separately. | Independent source-based gold rubric and human matching; guards against terse, empty or evasive summaries gaming faithfulness. |
| Call count / tokens | Actual generation requests and sum of actual input/output/total tokens over all stages, including failures/retries; retain usage categories separately. | Instrument transport. Existing main result does not provide a complete experiment usage record. Never infer calls from a fixed multiplier. |
| Latency / cost | End-to-end elapsed generation time per case; also stage times, median/p95. Estimated cost=sum of dated provider-billable categories × prices, separately for OCR/judging. | Instrumented timestamps/usage; common concurrency/caching policy. Prices optional, no current estimate made here. |
| CER | Character edit distance (S+D+I) / reference characters after declared Unicode/whitespace normalization. Can exceed 1. Empty references reported separately. | Verified transcription and OCR text. Existing implementation reusable; define Thai combining-mark/code-point convention. |
| WER | Token edit distance (S+D+I) / reference word tokens, using one pinned Thai tokenizer for both. | Verified transcription, versioned tokenizer. Existing `.split()` is not sufficient; report CER as primary. |
| Clean-to-OCR degradation | For quality metrics, score(clean)-score(OCR); for error rates, error(OCR)-error(clean). Report paired percentage-point differences, not unstable percent changes from a zero baseline. | Paired outputs and labels; automatic aggregation after annotation. |
| Critical OCR error propagation | Among annotated critical corruption instances eligible for the task, proportion whose specific wrong value/relation is asserted in the summary. Each error counted once per summary. | Gold alignment/error taxonomy and output annotations. Also label omission, correctly qualified uncertainty, and correct preservation/correction. Report unconditional propagation plus propagation conditional on mentioning the affected fact. |

[ROUGE](https://aclanthology.org/W04-1013/) measures overlap; [BERTScore](https://github.com/Tiiiger/bert_score) measures contextual similarity. Neither alone demonstrates source faithfulness. Automated string equality of an account number also does not establish that the correct person owns it.

**Minimum defensible set:** independent S/U/C rates against clean transcription and model-visible text; salient/critical fact coverage; critical OCR propagation; CER; raw citation validity plus semantic attribution precision/coverage for citation-producing outputs; calls/tokens/latency; failure rate and actual summary length. Add citation burden for the evidence-first argument. ROUGE-L is optional if good references exist; ROUGE-1/2 and BERTScore are supplementary. WER is optional until Thai segmentation is fixed.

Use two Thai-literate annotators with a written rubric, blinded method names and randomized output order. Double-label the main semantic endpoints if feasible; otherwise declare a stratified overlap set before scoring, measure agreement and adjudicate discrepancies. A prosecutor/advisor should validate salience and criticality criteria; if unavailable, claim textual fidelity only, not prosecutor utility. Gold transcription, gold salient facts, OCR error alignment and adjudicated semantic labels are the missing infrastructure. A versioned CSV/JSONL workflow suffices; a new annotation application is unnecessary.

## E. LLM-as-a-judge

**Recommendation: supplementary judge, human-anchored primary semantics.** RAGAS is convenient and can score a summary against supplied case text, but its retrieved-context faithfulness is not automatically fidelity to the original scan. Evaluate it with the same source policy as every other metric and report judge version/prompts and failures. Do not let it view MITRE context as evidence for case facts. Its [faithfulness definition](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) is a supported-statement fraction estimated through model judgments.

| Family | What it does | Why it is different |
|---|---|---|
| ROUGE | Reference lexical overlap | No learned semantic decision. |
| BERTScore | Reference contextual-embedding alignment | Learned representation, but not a generative judge and not contradiction detection. |
| NLI, e.g. [SummaC](https://aclanthology.org/2022.tacl-1.10/) | Learned entailment/contradiction classification and aggregation | Can be automatic without a generative LLM; must validate Thai/domain performance and context limits. |
| QA, e.g. [QAFactEval](https://aclanthology.org/2022.naacl-main.187/) | Generates/answers questions to compare information consistency | Errors can arise in question generation, answerability and answer matching; not equivalent to NLI. |
| RAGAS faithfulness | Decomposes statements and estimates support against context | A particular evaluator pipeline; reference-summary-free does not mean human-calibration-free. |
| General LLM judge | Prompted categorical/rubric decisions | Susceptible to verbosity, position, self-preference and reasoning errors. |
| Human annotation | Independent source-grounded decisions using a rubric | Costly and fallible, but provides task-specific calibration and adjudication. |

Known judge biases are documented in [Zheng et al.](https://arxiv.org/abs/2306.05685). Use an independently chosen judge, blind method labels, counterbalance pair order, and compare judge confusion matrices and per-error-type agreement with humans. A different model family reduces one dependency but does not establish correctness. Treat disagreements and malformed outputs as visible results. Use one calibrated supplemental evaluator, not an ensemble added only for complexity.

## F–G. Implementation alternatives and Thai-NNER

| Option | Complexity / generation calls | Faithfulness and attribution | Baseline status |
|---|---|---|---|
| 1. LLM spans → LLM summary | Low–medium / 2 | Explicit selection bottleneck; may omit important facts or select corrupted spans. Requires output-span mapping. | Recommended B2-lite; a declared evidence-first adaptation. |
| 2. Spans → sentence groups → sequential sentences | Medium–high / about 2+m | Closest to the paper's decomposition; local attribution is easier to inspect, but more calls and selection/planning errors remain. | Optional stronger baseline if resources permit; not the smallest thesis implementation. |
| 3. NER-assisted selection → generation | Medium–high / 1 with deterministic selection, or 2 with an LLM selector; NER inference extra | Identifies mentions, not propositions or support. Can lose negation, speaker attribution and event relations. | Separate salience-feature ablation, not a substitute for Attribute-First. |
| 4. TextRank/embedding salience → generation | Medium / 1 plus ranking computation | Extractive transparency; generic ranking can miss rare critical details and still preserve OCR errors. Need retained span IDs and output links. | Defensible extract-then-generate comparator; not a reproduction of learned planning/sequential fusion. |
| 5. Current joint structured generation | Already implemented / 1 main call | Claims and references jointly generated; validation checks identifiers/quotes, not truth. Summary-link completeness is missing. | B3-core component comparator, not attribution-first. |

[Thai-NNER](https://aclanthology.org/2022.findings-acl.116/) is a nested named-entity corpus, not an attribution method or a uniquely specified deployment model. Its news/review origins raise a domain-transfer question for police narratives. Any chosen checkpoint needs a separate entity evaluation; the corpus name alone does not specify the model.

NER could improve Materials navigation through mention highlighting/filtering and could provide salience features. It cannot determine that a mentioned person committed an event, resolve a disputed relation, or prove which span supports a summary claim. OCR substitutions and boundary errors plausibly harm its performance, especially critical names/numbers; the magnitude needs measurement. Keep mentions as versioned derived metadata with source offsets, model identity and unknown confidence semantics, never authoritative case facts. Do not deduplicate different people solely by similar names or overwrite original text.

**Do not add Thai-NNER now.** It adds another model, error source and ablation without being necessary for the selected RQ. Revisit only if a measured navigation need or a frozen NER-assisted selection hypothesis justifies it. No changes to `CaseMaterialsView.tsx` or `case-evidence.ts` are required for this experiment.

## H. Experiment matrix and smallest implementation

### Proposed matrix

| Dimension | Minimum study | Optional extension |
|---|---|---|
| Methods | B1, B2-lite, B3-core | B0 prompt sensitivity; B4 selection × structuring ablation; full ACL-style B2 |
| Inputs | C0 verified clean transcription; C1 cached actual printed-page OCR | C2 image-degraded OCR, stratified by measured CER; C3 controlled critical semantic corruption |
| Error types | Natural errors labeled as names/roles, amounts/identifiers, dates, negation/modality, source attribution or relations | Matched character-count critical vs noncritical edits to test semantic severity beyond CER |
| Task | Thai general case summary, fixed audience and length | Separate comprehension study, not inferred from summary scores |
| Scope | One fixed generation model; RAG and follow-up absent | One second-model replication |
| Repetition | Paired cases, randomized run order; repeat fixed settings to estimate variability | Provider/decoder sensitivity |

Illustrative planning budget, not a power calculation: 10 development cases and 30 held-out cases, 3 methods × 2 inputs × 3 repeats = 540 summaries. Main-generation calls are 30×2×3×(1+2+1)=720, excluding failed calls, OCR and judge calls. If annotation capacity is lower, reduce repeat count or cases and label the work a pilot; do not imply the number is statistically sufficient. Refine sample size using pilot variance and annotation capacity before locking the test set.

Split by underlying case and document/template family, not individual page, OCR variant or generated paraphrase. Keep real OCR outputs cached and identical across arms. Scanned-image degradation and actual OCR must be distinguished from synthetic text substitutions. Low/mild/severe groups should be measured, not arbitrary filenames. Gold transcriptions and labels never enter OCR generation; oracle experiments must be separately marked.

Critical-error analysis should include failures in which the output has an exact valid OCR citation yet conflicts with clean text. Do not reward omission without checking salient coverage. A model repairing a number by guessing may agree with clean text by chance; label the mechanism/source support separately rather than calling it reliable correction.

Multi-document input can be represented in an offline manifest now: `case_id → documents[] → immutable source text/spans → method input`. The current tuple/list-shaped provenance helps, but chat concatenation is not a completed general document-fusion subsystem. If only one-document cases are evaluated, claim single-document results and future-compatible contracts, not demonstrated multi-document effectiveness.

### Smallest change: an offline extension of the existing pilot

No production pipeline redesign is required. Keep legacy runs and names intact; add a summarization protocol under the existing research package, and reuse production analysis only through an adapter.

| Proposed path | Responsibility |
|---|---|
| `research/attribute_first_pilot/summarization/contracts.py` | Versioned cases/documents/spans, per-stage request receipts, outputs, failures and annotations. |
| `research/attribute_first_pilot/summarization/dataset.py` | Frozen manifests, clean/OCR pairing, case splits, hashes and stable source order. No reading gold annotations in inference inputs. |
| `research/attribute_first_pilot/summarization/spans.py` | Deterministic source segmentation/offset resolution; reject invented/ambiguous spans. Preserve quote text and sufficient context. |
| `research/attribute_first_pilot/summarization/prompts.py` | Frozen B0/B1/selector/generator instructions and matched summary constraints. |
| `research/attribute_first_pilot/summarization/arms.py` | B1/B2-lite sequencing; selected-span-only generation with output linkage; no invented replacement on selection failure. |
| `research/attribute_first_pilot/summarization/production_adapter.py` | Build proper evidence/context and call current `MainCaseAnalysisService.analyze` for B3-core; keep summary/answer/claims separate. |
| `research/attribute_first_pilot/summarization/transport.py` | Same model route and explicit decoding controls for all methods; wrap injected HTTP client to record request/response usage, stage timings, raw proposals and parser results. Mark controlled changes from production defaults. |
| `research/attribute_first_pilot/summarization/runner.py` | Offline CLI, immutable run settings, retries/failures, resume keys and randomization. |
| `research/attribute_first_pilot/summarization/metrics.py` | CER reuse, optional pinned Thai WER, citation mechanics and semantic-label aggregation; no automatic inference of human labels. |
| `research/attribute_first_pilot/summarization/annotation.py`, `reporting.py` | Blind annotation export, joins, paired estimates, intervals and failure tables. |
| `research/attribute_first_pilot/summarization/tests/` | Selection exactness, source isolation, no gold leakage, output choice, cost/failure accounting and paired-metric tests. |
| `research/attribute_first_pilot/README.md` | Clearly distinguish legacy attribute-conditioned QA from new summary protocol and ACL adaptation. |

These are proposed files, not implemented ones. Keep each code file below 300 lines. Do not expand the already large legacy evaluator/provider modules; isolate the new protocol. Initially use existing dependencies and a two-call selector; consult the published implementation for a closer reproduction rather than inventing equivalent research machinery.

The B3 adapter must detect evidence truncation. Either select cases that fit all arms without truncation or preregister a separate long-input experiment with equivalent exposure logging. Do not silently change B3's main prompt and call it unchanged CyberCase. Freeze original and controlled payload hashes. If narrative summaries do not expose claim links, score summary faithfulness independently and report claim-list attribution as a separate secondary endpoint; adding post-hoc summary citations would define a new arm.

### Major validity threats

1. Input-relative support mistaken for accuracy to the original document or truth of an allegation.
2. B3's self-produced claims used as its own evaluation denominator; summary/claim mismatch hidden.
3. Citation filtering removes failures before calculating validity; trace-unavailable generations excluded.
4. Evidence selection improves precision by deleting difficult but important facts.
5. B2 receives gold answers/spans or B3 receives extra RAG/clarification evidence.
6. Different output lengths, actual decoding, schema token floors, truncation, retries or hidden reasoning budgets.
7. Tiny template-derived datasets, correlated variants, development/test leakage or one-case pseudo-replication.
8. Judge circularity, unvalidated Thai entailment, evaluator language limitations and annotator awareness of method names.
9. Synthetic corruption lacks real OCR distributions; confidence is missing or uncalibrated; edit distance hides semantic severity.
10. Review/import changes OCR text, inadvertently measuring human correction rather than robustness.
11. Private police samples contain appended drafting instructions or generated revisions; eligibility and authentic-source boundaries need manual curation. Local prior sample notes are a warning to check, not a basis to assume all files are clean.
12. Results on text quality used to claim prosecutor comprehension, legal correctness, or multi-document effectiveness without corresponding evaluation.

### What not to implement

No Thai-NNER, new graph/entity database, Legal RAG, partner RAG changes, HTR, multi-agent critique loop, automatic OCR correction, new Case State system, new annotation web app, or production UI redesign for this study. Do not bolt on an entailment judge and then claim a causal benefit without a separate ablation. Do not fabricate missing OCR confidence or use gold error markers as if available at runtime. An uncertainty-aware intervention should be a later, explicit arm with realistic non-oracle uncertainty signals and calibration data.

### Contribution statements

**Conservative thesis statement, to use after completing the study:** “This study evaluates context-only, evidence-first, and structured-attribution generation for Thai case summarization using paired verified and OCR-derived inputs. It measures source-relative support, fidelity to verified document text, salient information retention, attribution quality and computational cost, and characterizes propagation of critical OCR errors.”

**Publication-oriented candidate, conditional on evidence and usable artifacts:** “We introduce an annotated evaluation protocol and benchmark for critical OCR error propagation in Thai investigative-document summarization, separating input-relative attribution from verified-document fidelity. Controlled comparisons characterize when attribution mechanisms preserve or propagate corrupted evidence, with case-level uncertainty estimates and independently adjudicated error analysis.”

The stronger claim requires a substantive corpus, a credible access/release arrangement, validated annotations, comparisons with close OCR/attribution work, and nontrivial findings. A private ten-case demonstration or an unvalidated judge score would not justify it. No “first,” superiority, robustness or prosecutor-benefit claim is supported by the current audit.

## Verification receipt

- Read current production and relevant experiment paths; verified the main parser behavior with synthetic contradictory/invalid citations, without inference calls.
- Ran `env_mitre/Scripts/python.exe -m pytest backend/tests/test_source_citations.py backend/tests/test_analysis_trace_v3.py backend/tests/test_document_ingestion_eval.py -q`: **32 passed in 6.03 seconds**.
- Confirmed the two historical analysis-pilot import paths cited above are absent.
- Checked primary literature and authors' repositories/docs linked above. This was targeted prior-work verification, not an exhaustive systematic review; novelty remains unproven.
- No real OCR evaluation, new summary generations, human study, provider benchmark, production edit, commit or push occurred. Test success verifies local contracts, not semantic accuracy.
