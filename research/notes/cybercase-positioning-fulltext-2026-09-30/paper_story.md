# Paper story: current evidence boundary

2026-09-30. Recommendation, not an approved change to experiments or product scope.

**Thesis:** CyberCase is an empirical study of information preservation in narrative incident analysis and report rendering. It is not a new multi-stage extraction or quote-verification algorithm.

## Problem and questions

Generated incident analysis can omit annotated information, attach a source string that does not support a claim, or alter a saved finding during report rewriting. These are distinct failure modes and require distinct denominators.

- RQ1: Does the specified two-call reading/judgement workflow mention more existing CASIE annotated arguments than specified direct/prose/order variants?
- RQ2: Given the identical frozen trace, how much claim text, status, quote, source and gap information do deterministic projection and LLM rewriting preserve?
- Scope boundary: quote occurrence is not entailment; neither recall nor faithful rendering establishes source truth.

## Prior art that constrains the story

Shiri2024 and AEC2026 already provide narrative extraction plus matched workflow comparisons and independent human labels. AEC includes CASIE. They must be extraction baselines for a claim of improvement over prior methods.

Kramer2025 and Wen2026(preprint) preclude narrative-domain novelty. Dehing2026 establishes a staged forensic chat report with trace-ID checking and timeline omission measurements. ClinicalQuotes2026(preprint) directly overlaps exact/normalized/elided quote checking. Quote-Tuning2025 establishes corpus-occurrence quoting. DeepFaith2026(preprint) includes post-hoc faithfulness checks and a template baseline; Jang2026 includes same-student verification/orchestration ablations.

What has not been established in the read set is a controlled deterministic-versus-LLM projection test on identical frozen narrative-analysis traces with per-dimension retention counts. This bounded search outcome is not proof of firstness.

## Claims and receipts

| Candidate claim | Current receipt | Permitted wording |
|---|---|---|
| Two-call better than specified one-call coverage | dev50 .779 vs .667 | Development sample, one model/seed, annotated-argument mention recall |
| Order is irrelevant | Not established: two-late Holm=.0936; late-single nonsignificant | Order ablation is inconclusive for ruling out effects |
| Reading facts unchanged by LLM2 | Facts copied by joined_trace | Storage invariant; not second-LLM semantic fidelity |
| Reports can lose saved information | v1 same-trace tests, dropped/unmapped records and one date error | Measured historical writer/renderer behavior |
| Deterministic reports preserve all provenance | Contradicted in v1: sourceIDs63.19% | Claim text preserved; source display loss reported explicitly |
| Current end-to-end superiority | Held-out100 and report-v2 main incomplete | No current replication conclusion |
| Binder checks factual support | Occurrence only | Verifies recoverable source location, not entailment |

Recall alone can be maximized by copying the article. Saved A3 shows two-call own text at least as long as its article in37/48completedcases and an article-lead descriptive coverage .990 at matched word budgets; this is not a paired comparison against the .779 failure-inclusive mean. It nonetheless precludes interpreting coverage as summary quality/compression. Report extractive sanity controls and task-compatible role/event precision where available.

## Strongest current statement

We evaluate a source-linked narrative-analysis system that separates reading, judgement, and report projection, using existing human CASIE annotations and deterministic coverage/preservation metrics. A one-model development comparison finds higher annotated-argument mention recall for the two-call workflow; a separate historical frozen-trace study measures report losses by dimension. These are scoped empirical observations pending external-method baselines and current held-out replication, not algorithmic novelty or a guarantee of semantic accuracy.

## What would change the verdict

- Complete the predeclared held-out and current-renderer study and report failures, intervals, providers, tokens/cost and deviations.
- Reproduce/adapt Shiri and AEC on identical article-level inputs, backbone and common reported metrics; native trigger/role F1 and whole-report mention recall are not interchangeable.
- To attribute a gain specifically to decomposition rather than an extra call, add a comparable two-call draft/revise treatment; otherwise retain the workflow-level claim.
- Without new human labels or an LLM judge, use existing role/event annotations where outputs support a deterministic mapping; leave unrestricted claim truth/gaps/ATT&CK quality outside the claim.
- If baseline/replication gains disappear, report mixed results and focus the study on preservation contracts and failure analysis. Do not convert a proxy into correctness by renaming it.

