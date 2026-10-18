# AttributionBench downstream Judgement feasibility audit

Audit date: 2026-10-07. Audited repository commit: `34a948c2451e0674e2443d8366beb36b9cad0b8e`.

`git fetch origin main` confirmed local `main` and fetched `origin/main` at that commit. A later `git ls-remote origin refs/heads/main` independently returned the same commit. Application and research code were inspected as committed Git blobs, because the working checkout contains unrelated edits. Existing downloaded raw files were checked against the committed manifest. No experiment, Reader call, Judgement call, neural inference, training, manual claim annotation, application/database write, or test run was performed. This document and temporary audit receipts are the audit deliverables.

The user request ends at “where one response contains BOTH”. This audit interprets that as both `attributable` and `not attributable`, and covers the stated overall feasibility question. Additional questions after that fragment were not received.

**Verdict: technically feasible as an offline replay, scientifically defensible as a narrowly defined claim-ID propagation study. The stronger claim that verification reduces semantically unsupported assertions in final summaries is not established by the existing gold or code.** The complete proposed experiment cannot be treated as an already valid, ready-to-run semantic evaluation.

Existing claim text, claim/evidence labels, original response text, references and verifier scores can all be reused. A small research adapter and evaluator would still be needed later. Those have not been implemented.

## 1. Raw data identity and actual schema

The local data are official `osunlp/AttributionBench`, configuration `subset_balanced`, pinned revision `62569e644f4186606f54f742178a4517431b42e1`.

| Split | Raw rows | SHA-256, verified against committed manifest |
|---|---:|---|
| train | 13,322 | `c7d6232048298b8f06afc556214c3739b5432f10f2641db2f73715fd126b1a63` |
| dev | 1,198 | `a744d1f84e621015f7a7e1941c3fb3f0838be767645dfb2ec784efd3133ab7d6` |
| test | 1,610 | `c2ff75dd4ea5cf12d86166ead66a96b42d5001a36daf02ff71303ef3317715a8` |
| test_ood | 1,686 | `90d8f5363cec90197f80b3e896dad17e091a108a5bf282c3d515d48c9a01a934` |

Actual raw rows contain these ten fields: `id`, `src_dataset`, `question`, `response`, `claim`, `claim_raw_string`, `references`, `citation_links`, `webpage_references`, and `attribution_label`. The grouping fields are strings; references are lists of evidence strings. None of the audited dev/test/OOD rows has an empty question, response, claim or source-dataset name. Row IDs are unique within each split.

The [official schema](https://github.com/OSU-NLP-Group/AttributionBench#dataset-structure) defines `response` as the generated response and `claim` as a part of it, potentially containing multiple sentences. The [paper, section 2](https://aclanthology.org/2024.findings-acl.886.pdf) defines the label for the claim together with its accompanying evidence, and describes label-balanced sampling. These are not proposition-level truth labels or annotations of a later summary.

### Does `cluster_key()` represent response grouping?

Yes, for **exact stored response content**. `research/attribution_benchmark/data.py:44` computes SHA-256 over a JSON serialization of:

`[row["src_dataset"], row["question"], row["response"]]`

This audit extracted and executed that exact function from the committed source, then independently grouped the raw rows by the unhashed tuple. Cluster counts agree on all four splits. The key is already used for clustered uncertainty estimation; it is not an original-generation identifier supplied by the dataset.

Consequently:

- It reliably reunites rows having the same source dataset, question and stored response.
- It does not normalize whitespace or approximate semantically equivalent answers.
- It cannot distinguish two physical generations with identical stored strings for the same question. No separate generation ID is present in this schema.
- It does not prove that every claim from an original response survived balanced sampling.

Exact response-cluster, row-ID, and `(src_dataset, question)` intersections are zero for every pair of train/dev/test/test_ood splits. This is a within-source content check, not a semantic duplicate audit across different source datasets.

## 2. Requested response-cluster statistics

Here “mixed” means at least one row labeled `attributable` and at least one labeled `not attributable`. The first table counts benchmark rows; it must not be read as counting distinct propositions.

| Split | Rows | Response clusters | Clusters with >=2 rows | Mixed clusters | Mixed / all clusters | Mixed / multi-row clusters |
|---|---:|---:|---:|---:|---:|---:|
| dev | 1,198 | 531 | 300 (56.50%) | 132 | 24.86% | 44.00% |
| test | 1,610 | 748 | 406 (54.28%) | 184 | 24.60% | 45.32% |
| test_ood | 1,686 | 1,229 | 246 (20.02%) | 125 | 10.17% | 50.81% |

Full distribution of benchmark rows per stored response:

| Rows in cluster | dev clusters | test clusters | test_ood clusters |
|---:|---:|---:|---:|
| 1 | 231 | 342 | 983 |
| 2 | 142 | 199 | 143 |
| 3 | 69 | 109 | 53 |
| 4 | 51 | 47 | 26 |
| 5 | 18 | 16 | 10 |
| 6 | 9 | 12 | 4 |
| 7 | 1 | 7 | 5 |
| 8 | 1 | 5 | 3 |
| 9 | 1 | 4 | 0 |
| 10 | 2 | 4 | 1 |
| 11 | 2 | 1 | 1 |
| 12 | 2 | 0 | 0 |
| 13 | 0 | 1 | 0 |
| 14 | 0 | 1 | 0 |
| 18 | 1 | 0 | 0 |
| 20 | 1 | 0 | 0 |

Mean/median/max rows per cluster: dev `2.256 / 2 / 20`; test `2.152 / 2 / 14`; OOD `1.372 / 1 / 11`. The 95th-percentile sizes are 5, 5 and 3 respectively, using the nearest observed sorted size.

### Multiple rows are not necessarily multiple extracted claims

This is the most consequential data finding. Some rows hold an identical claim with different references. The attribution label can then differ without a contradiction in the annotation contract.

For example, test rows `AttributedQA_64ce0b41-5eb1-4cf0-a4e2-6b1a932364e7` and `AttributedQA_b5f62a08-acd2-4858-a101-1d6bceef360f` have the same question, response and claim about Finn in Glee. One row has supporting evidence and label `attributable`; the other has different evidence and label `not attributable`. Counting those as two different factual propositions would be wrong.

In dev/test/OOD, 83/127/42 response clusters contain repeated exact claim text. There are 27/43/27 response clusters containing at least one identical claim with both labels. No audited identical `(question, response, claim, references)` tuple has conflicting labels within its source dataset. The differences therefore concern evidence-dependent examples, rather than an observed same-input annotation conflict.

| Split | Clusters with >=2 distinct exact claim texts | Such clusters with no same-text label conflict | Mixed clusters with distinct claims and no same-text label conflict |
|---|---:|---:|---:|
| dev | 257 | 244 | 105 |
| test | 323 | 308 | 141 |
| test_ood | 204 | 204 | 98 |

The distinct-claim count distributions are:

| Distinct claim texts | dev clusters | test clusters | test_ood clusters |
|---:|---:|---:|---:|
| 1 | 274 | 425 | 1,025 |
| 2 | 138 | 166 | 109 |
| 3 | 52 | 77 | 46 |
| 4 | 31 | 32 | 25 |
| 5 | 16 | 14 | 10 |
| 6 | 9 | 11 | 4 |
| 7 | 1 | 7 | 5 |
| 8 | 1 | 5 | 3 |
| 9 | 1 | 4 | 0 |
| 10 | 2 | 4 | 1 |
| 11 | 2 | 1 | 1 |
| 12 | 2 | 0 | 0 |
| 13 | 0 | 1 | 0 |
| 14 | 0 | 1 | 0 |
| 18 | 1 | 0 | 0 |
| 20 | 1 | 0 | 0 |

### Which source datasets actually support multi-claim replay?

| Split/source | Response clusters | Multi-row clusters | Multi-distinct-claim clusters | Raw mixed clusters |
|---|---:|---:|---:|---:|
| dev / AttributedQA | 61 | 12 | 0 | 5 |
| dev / ExpertQA | 139 | 112 | 112 | 52 |
| dev / LFQA | 30 | 27 | 27 | 9 |
| dev / Stanford-GenSearch | 301 | 149 | 118 | 66 |
| test / AttributedQA | 179 | 45 | 0 | 17 |
| test / ExpertQA | 193 | 143 | 143 | 71 |
| test / LFQA | 57 | 42 | 42 | 20 |
| test / Stanford-GenSearch | 319 | 176 | 138 | 76 |
| test_ood / AttrScore-GenSearch | 111 | 42 | 0 | 27 |
| test_ood / HAGRID | 682 | 204 | 204 | 98 |
| test_ood / BEGIN | 436 | 0 | 0 | 0 |

AttributedQA and AttrScore-GenSearch have `claim == response` on every row in the inspected splits. Their multiple rows represent alternative evidence pairings for one claim. BEGIN is entirely singleton here. HAGRID provides all multi-distinct-claim OOD clusters. A multi-claim OOD result therefore cannot be described as covering all three OOD domains equally.

### Conservative reuse slice, without creating or annotating claims

A label-independent structural inclusion rule would retain existing clusters with at least two rows, one row per distinct exact claim text, and nonempty reference bundles on every row. It removes ambiguity about duplicate propositions without synthesizing or merging evidence.

| Split | Eligible clusters | Existing rows | Mixed-label eligible clusters |
|---|---:|---:|---:|
| dev | 217 | 729 | 95 |
| test | 279 | 933 | 128 |
| test_ood | 169 | 491 | 79 |

This is a possible declared evaluation slice of existing IDs, not a new annotated dataset. It remains sampled benchmark material, with limited domain coverage. It is a recommendation only; no slice dataset or experiment runner was created. All eligible OOD clusters are HAGRID.

Without the nonempty-reference condition, the one-row-per-distinct-claim multi-claim counts are 217/279/204, with 95/128/98 mixed clusters. The difference is 35 HAGRID clusters containing an empty-reference row.

## 3. Evidence scope, ordering and inherited gold

Each original row's gold applies to its own `claim` and `references`. Do not merge every cluster's references into a new common evidence bundle and assume the old labels remain valid. Reference bundles differ within 266 dev, 350 test and 222 OOD clusters. Even distinct claims can obtain support from another claim's evidence. Same-text positive/negative pairs provide a directly observed example of that problem.

For the narrow experiment, retain the original row/evidence association in the evaluator. Say “gold-negative claim/evidence row cited by a summary unit,” rather than “false fact.” Seeing all retained claims and their citations is normal for Judgement, but the inherited gold does not label factual support against their combined evidence.

Other constraints found in actual data:

- Every source subset in dev/test/OOD is ordered as one positive-label block followed by one negative-label block. Every mixed cluster encountered in raw file order begins with an attributable row. Assigning `A-01...` in that order exposes a gold-correlated ordering cue. A later replay needs a fixed order chosen without labels, such as sorting by immutable row ID or a fixed seeded permutation, with IDs fixed before filtering.
- Some claim strings are not exact substrings of their response: notably 62 of 612 ExpertQA test rows. No universal original claim-offset field is present. A response-position ordering rule therefore cannot silently invent offsets for every example.
- OOD has 75 empty reference bundles, all in HAGRID: 10 gold-positive and 65 gold-negative. Thus even `attributable` does not guarantee visible nonempty evidence in these files. Retain and stratify them in full benchmark reporting, or declare an evidence-complete propagation slice before running it.
- The published benchmark balances sampled attribution examples. Replaying the surviving rows does not reconstruct a demonstrably complete original response decomposition.
- `not attributable` includes lack of full support; it does not distinguish false statements, contradictions and partially supported propositions. The [paper also documents human/model evidence-access mismatch](https://aclanthology.org/2024.findings-acl.886.pdf). Treat the official gold as benchmark gold rather than newly established truth about sources or final prose.

## 4. Existing loaders and cached verifier artifacts

`research/attribution_benchmark/data.py` reads all raw fields without filtering rows, validates basic types/labels/counts, and verifies the pinned manifest. Its README correctly limits the existing results to checkpoint performance under the recorded visible-evidence policy; it does not establish downstream summary quality.

The separate `nli_grounding_experiment/src/datasets/attributionbench.py` loader creates `AttributionBenchExample` with row ID, stripped claim, sentence-split evidence, binary label and source dataset. Its `meta` contains question and raw label, **not response**. It therefore does not preserve enough information in that object alone to reconstruct response grouping. Grouping remains recoverable by joining the original row ID to the verified raw JSONL.

That loader also treats any non-attributable/unknown label as binary zero, falls back to response for a blank claim, and discards very short sentence fragments. The present raw rows have the expected two labels and nonblank claims, so those claim/label fallbacks were not needed for these files. Its evidence representation is nevertheless different from untouched reference strings.

The NLI runner uses 512-token longest-first pair truncation (`truncation=True`), which can affect either side. The older research baseline instead preserves the claim and truncates only evidence. Those are different recorded protocols; they should not be treated as interchangeable scores from the same effective inputs.

### Cache verification performed in this audit

- All six successful candidate research runs have 1,198 dev, 1,610 test and 1,686 OOD rows each. IDs, claim strings, reference lists, source datasets, gold labels and response-cluster hashes match the raw files. Their local JSON records also match committed main records.
- Frozen EN-dev support thresholds are AttrScore `0.23`, DeBERTa-small `0.01`, mDeBERTa `0.15`, MiniCheck `0.22`, MiniLM `0.27`, and XLM-R `0.05`. Use the existing selections rather than optimizing on downstream test outcomes.
- The committed `nli_grounding_experiment/outputs/attributionbench_predictions.csv` contains 3,296 rows, with exact ID/source/claim/gold correspondence to the two test splits. Local records agree after normalizing Windows newline handling. It stores B0, B1, B3 and B4 decisions.
- Six relevant committed forward/reverse cache files have the expected ordered IDs and gold: 1,610 ID or 1,686 OOD rows each. Full/filtered ID forward caches mark 324/288 rows truncated; OOD 160/124. These caches do not store complete original premise text or content hashes, so ordered identity verification is weaker than complete historical input provenance.
- B1-LR has a saved trained classifier and forward caches. `compute_b1_lr_and_audit.py` computes AttributionBench aggregate metrics, but saves its per-row B1-LR column to **WiCE** predictions, not AttributionBench predictions. `outputs/canonical/final_predictions.csv` is also WiCE. A per-row AttributionBench B1-LR gate would need to apply the already frozen classifier to the corresponding saved forward probabilities later; no new NLI or Reader inference is intrinsically required. Rerunning a training script is unnecessary.

Actual admission counts from the committed AttributionBench prediction CSV:

| Split | Gate | Accepted rows | Accepted gold-positive | Accepted gold-negative |
|---|---|---:|---:|---:|
| test | B0 | 771 | 496 | 275 |
| test | B1 | 867 | 543 | 324 |
| test | B3 | 784 | 505 | 279 |
| test | B4 | 0 | 0 | 0 |
| test_ood | B0 | 972 | 668 | 304 |
| test_ood | B1 | 1,024 | 700 | 324 |
| test_ood | B3 | 987 | 689 | 298 |
| test_ood | B4 | 0 | 0 | 0 |

B4 rejects 76/36 rows and abstains on 1,534/1,650 ID/OOD rows. It accepts nothing. Zero accepted unsupported rows under that gate is an admission result with zero supported retention, not evidence of a useful downstream summary. These counts are over full official test rows, not the proposed conservative cluster slice, and are not observed downstream outcomes.

No downstream AttributionBench Judgement outputs or executable claim-propagation path were found in these research runners. Classifier reports and diagrams describing future admission do not establish a production integration.

## 5. Actual CyberCase Reader-to-Judgement boundary

The committed production path is:

1. `pipeline.py:advance_case` assesses gaps, may pause for follow-up, retrieves optional technical context, and calls `write_analysis`.
2. `write.py:write_trace` always requests `case_reading`, converts its reply and binds evidence.
3. It starts derived-view extraction and requests `case_judgement` independently, in parallel. Both receive the canonical claims; derived views do not feed Judgement.
4. `joined_trace` combines outputs; `bound_references` resolves summary claim-ID references and other downstream links.

There is **no semantic accept/reject gate between binding and Judgement**. `reading_payload()` serializes every claim in the reading. Unresolved claims are not removed.

### Judgement can be invoked without Reader

`write.py:judgement_request`, `reading_payload`, `CASE_JUDGEMENT_SYSTEM_PROMPT`, `CaseProviderJudgement`, and the generic `request_stage(stage="case_judgement", ...)` expose the needed lower-level boundary. They operate on supplied in-memory models rather than requiring a stored Case.

A later isolated research harness could construct a `CaseProviderReading` from existing benchmark claim strings, retain only accepted original row IDs, and call that exact Judgement prompt/schema/provider path. It must bypass `advance_case` and `write_trace`, which would invoke upstream stages. Derived-view generation is also unnecessary for a summary-only replay. This is static architectural feasibility, not a tested benchmark adapter.

The raw AttributionBench dictionaries cannot be passed directly as native reading claims. `CaseAnalysisClaim` additionally requires an `A-xx` ID, claim type, epistemic status and native citation structure. A deterministic adapter must keep a fixed `A-xx -> original row ID` mapping and original evidence strings. Mechanical metadata is not a new human annotation, but its policy must be declared.

Do not map gold-negative labels to `not_confirmed`, `contradicted` or `not_established` in operational arms. That would give Judgement the answer. `not_confirmed` is the current code's evidence-location status, not an attribution gold label.

All inspected response groups fit the native 64-claim limit: maximum dev/test/OOD row counts are 20/14/11. Maximum claim lengths are 401/646/996 characters, below the 4,000-character native claim limit. Maximum reference counts are 4/13/6, below 64. Some references exceed the 2,000-character single-quote limit, so copying each full reference into one `exact_quote` is not generally valid. Existing revision-bearing Evidence Units can preserve source text in smaller exact spans. That conversion has not been implemented or tested here.

### What citation binding actually establishes

- `sources/evidence.py` derives deterministic unit IDs, source revisions and exact source offsets.
- `trace/evidence_binding.py` checks source identity, revision, selected unit existence and duplicates, then reconstructs exact original evidence text.
- `trace/bind.py:confirmed_status` demotes a reported claim with no resolved supporting citation to `not_confirmed`.
- Neither that demotion nor successful binding establishes semantic support for claim content. A gold-negative claim can bind perfectly to evidence that does not fully support it.
- The optional legacy meaning pointer attaches advisory passages to unresolved citations. It does not implement the research classifier gate; its data are hidden from the Judgement payload.

The exact native Judgement input includes language, follow-up history, optional technical context, and the reading claims with resolved citation content. It excludes raw full Case sources and citation-context diagnostics. For a controlled benchmark replay, set follow-up history empty and technical context absent, identically across arms. Keep the original response for grouping only: passing its full text downstream would allow removed claims to re-enter.

## 6. What can be measured without new annotations?

The existing Judgement prompt requires each summary sentence to end in `[A-xx]` references. `trace/summary.py` parses citation-delimited text blocks; `trace/bind.py:summary_units` keeps known IDs, counts unknown ones, and assigns structural support states. `trace/support.py:item_support` bases `bound/mixed/unbound/no_claim` on the presence of supporting citations, not semantic entailment. `CaseProviderJudgement` validates summary text as a string; it does not enforce every sentence's semantic relationship to its IDs.

Therefore the following is measurable using existing human gold and original-ID mapping:

> After each fixed gate, how often does a parsed Judgement summary unit cite an original claim/evidence row whose AttributionBench label is `not attributable`?

For each original cluster and gate, define accepted row IDs `A`, original gold-negative row IDs `U`, original gold-positive row IDs `S`, and original row IDs cited by the resulting summary `C`. Defensible structural measurements include:

- False admission: `|A intersect U| / |U|`.
- Gold-negative ID propagation: `|C intersect U| / |U|`, with the same original denominator across gates.
- Conditional propagation among falsely admitted rows: `|C intersect A intersect U| / |A intersect U|`; report undefined when the denominator is zero.
- Gold-positive ID retention: `|C intersect S| / |S|`.
- Fraction of parsed summary units citing any gold-negative row, plus uncited units, unknown/disallowed IDs, failed outputs, no-input clusters, output length and cost.

These are citation/dependency exposure measures. They do **not** establish that:

- The summary repeats the unsupported part of a partially supported input claim.
- A cited claim is asserted rather than questioned or described as unconfirmed.
- The summary has no newly invented proposition, omitted citation or misassigned ID.
- A sentence supported by several claims is unsupported against their combined evidence.
- A verifier reduces the human-gold semantic hallucination rate of final summaries.

Original claim labels cannot simply be transferred to newly synthesized sentences. A separate semantic evaluator could supply an automatic proxy, but it would not create independent human summary gold. Reusing the gate itself to judge its own outputs adds circularity. Under the stated no-new-annotation constraint, the strongest clean endpoint currently available is the explicitly named ID-propagation endpoint.

## 7. Minimum conditions for a valid later experiment

These are design requirements, not an implementation proposal accepted for execution:

1. Declare the evaluation unit as an original claim/evidence row within an exact stored response cluster. Predeclare duplicate/evidence-empty handling and report every resulting denominator. Use all eligible multi-claim clusters for the primary analysis, with mixed clusters as a declared diagnostic slice.
2. Reuse original claim text and gold unchanged. Preserve row-local references, fixed label-independent order, and fixed IDs across gates. Never merge alternative evidence pairings and silently inherit their labels.
3. Supply only admitted rows to Judgement. Exclude gold labels, probabilities, rejected text, the full original response, follow-up evidence and MITRE/RAG content from the operational summary inputs. An explicitly labeled oracle arm may intentionally use gold as a separate upper-bound comparison.
4. Keep the Judgement model/version, native prompt/schema, decoding policy, evidence supplied for each retained row, budgets and retry rules fixed. If filtering changes the evidence also shown to Judgement, that is a joint evidence-and-admission intervention, not an isolated admission effect.
5. Include an unfiltered baseline and report supported retention and no-input rate with negative propagation. A matched label-independent dropping control can test whether any gain is explained by removing more content. Zero output cannot establish useful summary improvement.
6. Define the zero-admitted-claims outcome before execution. Native claims may be empty, but the summary schema requires nonempty text while the prompt requires supplied claim IDs for sentences. Treat starvation/abstention explicitly; do not manufacture a successful factual summary or score an absent summary as semantically safe.
7. Use paired cluster-level comparisons and source-stratified cluster bootstrap intervals. Existing claim rows from one response are dependent. Freeze gates before downstream test outputs; do not select a winner or thresholds by those same outcomes.
8. Label the study an English benchmark-claim replay through CyberCase Judgement. It does not measure CyberCase Reader errors, native Thai/legal Case accuracy, complete original response coverage, or end-to-end system improvement. B1-LR versus B3 is the appropriate existing learned-boundary comparison for isolating reverse NLI; B0 versus B3 changes multiple components.

**Decision:** proceed to a bounded design for a claim-ID propagation replay if that narrower endpoint is acceptable. Do not approve the stronger semantic final-summary claim from current assets alone. No new input claims, annotations or Reader runs are inherently needed for the narrow study, but new downstream Judgement outputs would still be required, and a deterministic research adapter/evaluator does not yet exist.

## 8. Evidence receipts

Temporary audit receipts are under `tmp/attribution-judgement-audit/`:

- `raw_grouping.json`: original file hashes, tuple/cluster-key equivalence, full row distributions, source breakdowns, exact cross-split overlaps and original-ID samples.
- `distinct_claims.json`: distinct claim-text counts, duplicate/evidence-dependent label cases, and mixed-cluster refinements.
- `strict_slice_counts.json`, `nonempty_slice_counts.json`: counts for the two possible conservative structural slices; no new dataset records.
- `schema_ordering.json`: original label-block ordering, reference cardinalities, substring checks and same-input label consistency.
- `cached_artifacts.json`: current-main cache identity/gold/input/cluster checks and cached admission counts. A raw byte comparison differs for the CSV because of Windows newlines; the normalized logical records match.
- `source_receipt.json` and `main_snapshot/`: SHA-256 hashes, definition locations and immutable copies of 23 inspected main files.
- `baseline.json`: starting HEAD/index identity and dirty-path fingerprints.

Checks used only Python standard-library parsing/counting/hashing and read-only Git inspection. Existing test source was inspected for the Reader/Judgement contract; tests were not executed. There is no claimed live-model or runtime-adapter validation.
