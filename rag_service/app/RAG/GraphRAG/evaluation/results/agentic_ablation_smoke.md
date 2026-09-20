# Agentic Ablation — ATT&CK Technique P / R / F1

- Dataset: real-CTI tier (`CTI_dataset.json`), 5 samples (3 named / 15 described steps)
- Core LLM: `openrouter:openai/gpt-5.6-luna`; commit `2e4c9f6`
- Run file: `agentic_ablation_smoke.jsonl`
- Arms: **A** full agent (headline) · **B** A without the evaluator/broaden loop (derived from A's first pass) · **C** `query_fast()`

Scoring: technique IDs cited in the answer (`extract_technique_ids`), rolled up to the parent technique because all gold IDs are parent-level, then `technique_set_score` against the sample's `gold_attack_ids`. Macro = mean over samples; micro = pooled matches. Name matching is reported as a secondary row only — see §6.

## 1. Technique precision / recall / F1

| Metric | A  full agent (headline) | B  agent - self-reflection | C  fast path |
|---|---|---|---|
| Macro precision | 0.600 | 0.600 | 0.612 |
| Macro recall | 0.780 | 0.780 | 0.860 |
| Macro f1 | 0.670 | 0.670 | 0.698 |
| Micro precision | 0.560 | 0.560 | 0.593 |
| Micro recall | 0.737 | 0.737 | 0.842 |
| Micro f1 | 0.636 | 0.636 | 0.696 |
| Macro F1, no parent roll-up | 0.493 | 0.493 | 0.515 |
| Macro F1, + name matching (defective alias map, §6) | 0.500 | 0.500 | 0.447 |
| Mean techniques cited | 5.00 | 5.00 | 5.40 |
| Answers citing no technique | 0 | 0 | 0 |

### Step recall by cue type

Precision cannot be split by cue type — a predicted technique belongs to the answer, not to a step — so the split is recall only: the share of steps whose gold technique the answer cites.

| Cue type (steps) | A | B | C |
|---|---|---|---|
| named (3) | 1.000 | 1.000 | 1.000 |
| described (15) | 0.667 | 0.667 | 0.800 |

## 2. Paired comparisons (same samples)

Δ = left − right, per-sample macro metric. 95% CI: paired bootstrap (10k resamples). p: two-sided Wilcoxon signed-rank on non-zero Δ (n/a below 6 non-zero pairs). `*` = CI excludes 0. W/T/L = samples where left is better / equal / worse.

| Comparison | mean Δ | 95% CI | Wilcoxon p | n | W/T/L |
|---|---|---|---|---|---|
| A − B f1 | +0.000 | [+0.000, +0.000] | n/a | 5 | 0/5/0 |
| A − B precision | +0.000 | [+0.000, +0.000] | n/a | 5 | 0/5/0 |
| A − B recall | +0.000 | [+0.000, +0.000] | n/a | 5 | 0/5/0 |
| B − C f1 | -0.028 | [-0.221, +0.165] | n/a | 5 | 3/0/2 |
| B − C precision | -0.012 | [-0.164, +0.140] | n/a | 5 | 2/1/2 |
| B − C recall | -0.080 | [-0.360, +0.220] | n/a | 5 | 1/2/2 |
| A − C f1 | -0.028 | [-0.221, +0.165] | n/a | 5 | 3/0/2 |
| A − C precision | -0.012 | [-0.164, +0.140] | n/a | 5 | 2/1/2 |
| A − C recall | -0.080 | [-0.360, +0.220] | n/a | 5 | 1/2/2 |

## 3. Self-reflection loop diagnostics (arm A)

| Diagnostic | Value |
|---|---|
| First-pass verdict INSUFFICIENT | 0/5 (0.0%) |
| Broaden rounds used: 0 / 1 / 2 | 5 / 0 / 0 |
| Answer replaced by ACKNOWLEDGE_LIMIT | 0/5 (0.0%) |
| Samples where the loop changed the answer path (B ≠ A) | 0/5 |
| LLM-judged evaluations (excl. forced SUFFICIENT at max retries) | 5 |
| … of which INSUFFICIENT | 0 |
| … INSUFFICIENT strategies | — |
| … SUFFICIENT with strategy PARTIAL_ANSWER (gap warning never reaches the answer) | 1 |
| … evaluator parse / exception fallbacks to SUFFICIENT | 0 |

### A − B restricted to samples where the loop acted

On every other sample B ≡ A by construction (Δ = 0), so the all-sample A − B above is this subset's effect diluted by the samples the loop never touched.

| Subset | mean Δ F1 | 95% CI | Wilcoxon p | n | W/T/L |
|---|---|---|---|---|---|
| broadening fired (≥1 round) | — | — | — | 0 | — |
| ACKNOWLEDGE_LIMIT returned | — | — | — | 0 | — |
| loop changed answer path (any) | — | — | — | 0 | — |

## 3b. Evaluator sensitivity and calibration

The evaluator reads only the first 4000 characters of the context. "Visible recall" = share of gold technique IDs inside that window; "full recall" = in the whole context the reasoning LLM gets. Both count IDs only, so a technique present by name alone counts as missing.

| Context judged | n | INSUFFICIENT | visible recall | full recall | mean context chars |
|---|---|---|---|---|---|
| A first pass (served) | 5 | 0 (0.0%) | 0.497 | 0.780 | 9527 |
| C fast-path context (probe S) | 0 | — | — | — | — |

Calibration, pooled over all 5 judgements. A SUFFICIENT verdict in the first row is a likely miss: most of the incident's gold techniques are not in what the evaluator read.

| Visible gold recall | n | SUFFICIENT | INSUFFICIENT |
|---|---|---|---|
| visible recall < 0.5 | 2 | 2 | 0 |
| 0.5 ≤ visible recall < 1 | 3 | 3 | 0 |
| visible recall = 1 | 0 | 0 | 0 |

## 4. Grounding — context vs answer

Context recall: share of gold technique IDs that appear in the context the reasoning LLM saw. Only vector-hit and subgraph headers carry IDs (relationship documents and neighbour lists carry names), so both context recall and "absent from context" are conservative: a technique present only by name counts as absent. Answer recall above context recall means the model cited techniques from its own parametric knowledge.

| | A | B | C |
|---|---|---|---|
| Context recall | 0.780 | 0.780 | 0.207 |
| Answer recall (macro) | 0.780 | 0.780 | 0.860 |
| Cited IDs absent from context (mean share per answer) | 0.000 | 0.000 | 0.755 |
| Correct (gold) citations absent from context | 0/14 (0.0%) | 0/14 (0.0%) | 12/16 (75.0%) |

## 5. Latency and LLM cost per sample

Cost at OpenRouter list price $0.20 / $1.20 per 1M input / output tokens. B's latency is reconstructed (A's shared node timings + its own reasoning), not measured end-to-end. Non-LLM time is local BGE-M3 / reranker / Neo4j / Qdrant on the benchmark machine and does not transfer to production hardware.

| Metric | A | B | C |
|---|---|---|---|
| Latency mean (s) | 40.7 | 33.8 | 32.1 |
| Latency median (s) | 38.4 | 30.8 | 18.6 |
| Latency p90 (s) | 52.1 | 43.8 | 89.8 |
| … of which LLM (s, mean) | 24.3 | 17.4 | 28.7 |
| LLM calls mean | 4.00 | 3.00 | 1.00 |
| LLM calls min–max | 4–4 | 3–3 | 1–1 |
| Input tokens mean | 7276 | 4923 | 1909 |
| Output tokens mean | 2242 | 1632 | 1662 |
| Cost per sample (USD) | 0.0041 | 0.0029 | 0.0024 |

## 6. Limitations

- **B is a counterfactual branch of A**, not an independent run. That is what makes A − B exactly the loop's effect, but B ≡ A on samples where the loop did not act, so the all-sample A − B is necessarily diluted.
- **B − C is not decomposition + quota alone.** `query_fast` also renders a smaller context (5 vector hits / 3 subgraphs vs 15 / 8) and skips the router call; the difference bundles all of these.
- **One run per arm.** The core LLM is sampled at temperature 0 but is not guaranteed deterministic; comparisons involving an independent generation (B − C, A − C, and A − B on the loop subset) include run-to-run variance, which the paired CI reflects but cannot separate out.
- **Extraction.** Predictions are the technique IDs an answer cites. A technique described only in prose without its ID is not counted, and an ID mentioned in a negative sense counts as predicted. Name matching was the intended complement but is not used for the headline: `attack_lookup.json`'s alias map keeps one ID per name and resolves names shared by enterprise and mobile techniques to the mobile ID (e.g. "screen capture" → T1513, "system information discovery" → T1426), plus some revoked IDs ("data encrypted" → T1022). Found on the 5-sample smoke run, before the full run; the name-matched F1 is still reported for transparency.
- **Evaluator probe.** S reuses C's context, so its verdicts share C's retrieval; calibration buckets use ID-visible recall, which undercounts techniques the context names without an ID and so overstates likely misses.
- **Gold coverage.** One gold ID (T0827) is ICS, which is not ingested, so it is unreachable for every arm. The ATT&CK version of the index (v19) differs from the source advisories' version; drifted IDs penalise all arms equally.
