# Phase 1 Claim-Anchored Analysis Plan (HOW)

> [!NOTE]
> **Document Role**: Implementation Architecture Plan (**HOW**).
> * **Canonical Project Direction (WHY / WHAT)**: [`CURRENT_PROJECT_DIRECTION.md`](CURRENT_PROJECT_DIRECTION.md)
> * **Actual Implemented Code (STATUS)**: [`ATTRIBUTE_FIRST_IMPLEMENTATION.md`](ATTRIBUTE_FIRST_IMPLEMENTATION.md)
> * **Historical Ledger**: Retained in the appendix at the bottom of this document.

## 1. Recommendation
Implement the limited opt-in case-overview branch (`CASE_ANALYSIS_PIPELINE=claim_anchored`). Use GPT-5.6 Luna for extraction and generation initially, with the same model in the case-only baseline. Treat CAMS as methodological related work, not a reproduced algorithm or evidence that CyberCase improves accuracy.

## Verified starting point

- 2026-09-08 [TOOL] Starting git status was clean. Read existing migration audit, backend config and analysis executor. No production edits or provider calls in this assessment.
- 2026-09-08 [CODE] backend/app/config.py sets core_llm_openrouter_model and chat_ask_model to openai/gpt-5.6-luna. The executor uses resolve_core_llm_target(settings.chat_ask_model); effective deployed configuration was not inspected.
- 2026-09-08 [CODE] Existing analysis generates answer, summary and claims jointly, then binds/validates citations. Existing exact-quote infrastructure is part of the baseline, not a new v11 contribution.

## Paper suitability

2026-09-08 [TOOL] Read the supplied 16-page PDF, including method, evaluation, limitations and reproducibility table; visually inspected page 14. Verified title/version at https://arxiv.org/abs/2606.23989v4. This is the same paper cited in the earlier migration audit: Shuo Guan, Attributable by Construction: Claim-Anchored Provenance for Multi-Document Summarization, v4, 4 September 2026. Publication acceptance was not established. The anonymous artifact link could not be opened; released code/data reproducibility remains UNCONFIRMED.

2026-09-08 [TOOL] Relevant source sections: 3.2 provenance invariant versus semantic faithfulness; 3.3 quote-to-span binding; 3.5 selection; 3.6 attributable rewriting; 4.2 controls; 4.3 separate citation/localization evaluation; page 9 limitations; Appendix C/Table 5 implementation.

| Paper element | Phase 1 decision | Reason |
|---|---|---|
| Separate claim text and verbatim evidence | Adopt | Makes extraction interpretation inspectable |
| Resolve source location before generation | Adopt with exact unique matching | Reject wrong/ambiguous source links before generation |
| Generated text refers to admitted IDs | Adopt as typed generated units | Resolve citations from a stored map, not newly invented references |
| Fuzzy quote rescue | Exclude | Conflicts with exact-evidence admission; especially risky for changed digits/negation |
| Cross-document clustering and conflict NLI | Defer | Requires real multi-document cases and calibrated relation labels |
| LightGBM salience and support selector | Defer | Requires training labels; news repetition is not evidential importance |
| NLI verification and repair loops | Defer | Requires Thai-domain validation; adds cost and another semantic error source |
| Separate evaluation of traceability and support | Adopt | Resolvable evidence does not prove the generated proposition is supported |

2026-09-08 [ASSUMPTION] These choices are a simplified CAMS-inspired adaptation. Removing clustering, learned selection and verification prevents transferring the full paper's reported gains or describing Phase 1 as CAMS reproduction. The paper's experiments concern English news, not Thai investigation files or OCR reliability.

## Model and provider plan

- 2026-09-08 [ASSUMPTION] Extraction: openai/gpt-5.6-luna. Generation: the same model. Baseline: the same model. Selection/binding/assembly: Python, with no additional model. Retain existing gap/follow-up mechanisms with case-only input.
- 2026-09-08 [ASSUMPTION] Model choice is a starting engineering decision based on the current integration and low advertised cost, not demonstrated superiority on Thai cases. Run a small Thai pilot before freezing the experiment. If it fails, compare one stronger candidate on development data and rerun every experimental arm with the selected model; no automatic production model fallback.
- 2026-09-08 [TOOL] OpenRouter currently lists Luna at USD 0.20/M input and 1.20/M output tokens: https://openrouter.ai/compare/openai/gpt-5.6-luna/qwen/qwen3.7-flash. Recheck at execution. A hypothetical total of 20k input plus 6k billed output tokens across two calls costs USD 0.0112, excluding gap calls, retries and other overhead. This is illustrative, not a measured case cost.
- 2026-09-08 [TOOL] Structured-output support is endpoint-specific: https://openrouter.ai/docs/guides/features/structured-outputs. Verify actual transport/schema compatibility through existing utilities; do not copy a new API request shape blindly.
- 2026-09-08 [ASSUMPTION] Pin model identifier, resolved provider, decoding/reasoning settings supported by that endpoint, prompt/schema/pipeline versions and source hashes per run. Record actual returned model/version and usage. A rolling alias cannot guarantee immutable weights. Do not force unsupported temperature parameters or claim deterministic LLM outputs.

## Execution stages and contracts

| Stage | Input/output | Enforced behavior |
|---|---|---|
| Source registry | Admitted messages -> immutable text/hash/source IDs | Case material only; retain original Thai and validated page metadata |
| Extraction call | Sources -> claims, exact quotes, source IDs, existing epistemic labels | No invented offsets; preserve speaker, negation, quantities and uncertainty |
| Exact binding | Candidate quotes -> unique source-relative spans | Unknown source, absent quote, repeated ambiguous occurrence or stale hash fails explicitly |
| Selection | Bound claims -> selected IDs and omission receipt | Transparent stable policy and real token/claim limits |
| Generation call | Selected claims AND quotes -> text units with selected IDs | No full raw-source or RAG access; no provider replacement of stored citations/statuses |
| Assembly | Valid units -> existing AnalysisTraceV3 plus separate receipt | Reject unknown/empty ID links; render both answer and summary from admitted units |
| Existing downstream flow | Final claims plus full admitted case evidence -> gaps/follow-up | Preserve receipt and pinned version; selection omissions are not automatically missing case facts |

2026-09-08 [ASSUMPTION] Prototype selector policy: retain all admitted candidates when they fit. Deduplicate only identical records, preserving attribution and spans; do not merge paraphrases or conflicting accounts. Under a tight budget, reserve admitted uncertain/conflicting groups first, then fill stably in source order, recording every omission and token cost. Fail if mandatory groups cannot fit. This is a coverage policy, not a validated salience algorithm; ordering and required-group detection remain evaluation concerns. Keep the final existing 64-claim limit explicit. Full input extraction must fit the declared budget; no silent source truncation or fallback to v10.

2026-09-08 [ASSUMPTION] The enforceable invariant is: each admitted generated unit has a nonempty set of selected IDs, each resolving to exact spans in the immutable source registry. A unit can still contain an unsupported clause. Do not describe unit-level structural validation as sentence-level semantic verification. User-facing headings may be deterministic labels without evidence assertions.

## Implementation sequence

1. 2026-09-08 [ASSUMPTION] Freeze the case-only baseline, development examples, model settings, output target and error taxonomy. Preserve default raw_direct.
2. 2026-09-08 [ASSUMPTION] Add internal contracts, source registry and exact resolver/binder under case_analysis/claim_anchored; retain the legacy binding facade.
3. 2026-09-08 [ASSUMPTION] Add extraction, selection, generation and assembly behind the existing service entrypoint. Keep each code file below 300 LOC.
4. 2026-09-08 [ASSUMPTION] Integrate explicit overview dispatch, per-run configuration pinning, retry/clarification inheritance, receipt persistence and case-only gap inputs. ASK stays explicitly legacy; MITRE augmentation is deferred for this opt-in branch.
5. 2026-09-08 [ASSUMPTION] Validate failure behavior and existing consumers, then run the frozen pilot. Keep v11 opt-in until empirical acceptance is established.

2026-09-08 [ASSUMPTION] Reuse file-level implementation and test list in MAIN_ANALYSIS_V11_MIGRATION_AUDIT.md. No new database, frontend redesign, report schema, OCR/HTR, legal reasoning or rag_service changes are proposed.

## Research question and evaluation

2026-09-08 [ASSUMPTION] Research question: Under a fixed model and matched case-only inputs, does pre-binding an intermediate claim representation improve supported-proposition attribution and preserve important case information compared with joint analysis generation?

| Arm | Purpose |
|---|---|
| A: case-only v10, existing joint claims/summary and quote binding | Strong existing-mechanism control |
| B: case-only v11, extract/bind/select/generate | Tests the complete Phase 1 package |
| C: optional v11 with selection bypassed on inputs fitting both budgets | Isolates selection effects while retaining claim-first generation |

2026-09-08 [ASSUMPTION] A versus B does not isolate every component or prove gains independent of extra inference cost. Report total tokens, calls, latency, rejections and coverage. A compute-matched control is needed before claiming the ordering alone is superior. Original combined-context v10 can be a separate product reference, but cannot substitute for the matched case-only baseline.

- 2026-09-08 [ASSUMPTION] Start with 10-15 development cases to qualify Thai quote copying, attribution/negation preservation, schema compliance and input budgets. Then freeze policy and prompts. A proposed 30-50 held-out-case pilot can estimate feasibility; final sample size depends on observed variance and annotation capacity and is not a power guarantee.
- 2026-09-08 [ASSUMPTION] Annotate actual output propositions against raw source context, not only the model's own claim records. Label supported, unsupported, contradicted and attribution/uncertainty errors. Measure important source-fact recall, citation support precision, exact link validity, rejection rate, runtime and billed cost separately. Failures count in denominators; do not report only accepted outputs.
- 2026-09-08 [ASSUMPTION] Have Thai-capable reviewers judge blinded outputs; independently double-label a subset, report disagreement and adjudication. Split by case/document family to prevent near-duplicate leakage. Use paired case-level uncertainty estimates; many claims from one case are not independent cases.
- 2026-09-08 [ASSUMPTION] Keep identical reviewed source/OCR snapshots across arms. This evaluates analysis conditional on input, not whether OCR matches the original document. An OCR robustness study requires paired verified transcription and cached OCR with critical-error labels.
- 2026-09-08 [ASSUMPTION] Verification-time evaluation is optional and requires matched interfaces and counterbalanced order. Existing source links mean a faster review claim cannot be inferred from adopting CAMS.

## Acceptance and remaining decisions

- 2026-09-08 [ASSUMPTION] Engineering gate: all accepted evidence-bearing units resolve; explicit failures for invalid/ambiguous links and budgets; original v10 behavior preserved; source isolation and receipt propagation tested; retry publishes one outcome. Run focused resolver/selection/generation/versioning tests and impacted canonical-state, follow-up, optional-RAG, report and frontend-reader regressions. No new tests were executed during planning.
- 2026-09-08 [ASSUMPTION] Research gate: prespecify acceptable support-error, important-fact coverage and cost/latency changes after development and before held-out evaluation. Higher citation validity alone is insufficient for promotion. Numerical thresholds and expert acceptance are UNCONFIRMED.
- 2026-09-08 [ASSUMPTION] Prior 8-16 engineering-hour estimate covers the bounded implementation and regression scope, not full CAMS reproduction, annotated evaluation, model comparison or unpredictable integration repairs. Treat it as provisional rather than a deadline.
- 2026-09-08 [ASSUMPTION] Defensible framing: a CAMS-inspired, source-bound intermediate representation for Thai case analysis, evaluated against the existing joint-generation pipeline. Novelty and empirical benefit remain unestablished. Do not claim a new trained model, hallucination elimination or proven legal reliability.

---

## Appendix: Historical Planning Ledger

* **2026-09-08 [USER]**: Attribute-first implementation authorized and documented in `ATTRIBUTE_FIRST_IMPLEMENTATION.md`. NLI remains the next separate integration step, with a verifier interface provided by Phase 1.
* **2026-09-08 [USER]**: Subsequent clarification: User prefers dedicated learned components (NLI/learned verification) beyond pure generative LLM prompts. Candidate scope includes evidence-to-claim NLI support checks and evidence-to-generated-proposition checks.
* **2026-09-08 [USER]**: Initial request for proposed Phase 1 plan and CAMS v4 suitability assessment.

