# Agentic Ablation — ATT&CK Technique P / R / F1

- Dataset: real-CTI tier (`CTI_dataset.json`), 100 samples (61 named / 286 described steps)
- Core LLM: `openrouter:openai/gpt-5.6-luna`; commit(s) `7ffe0d8`, `9537e7c`
- Run file: `agentic_ablation.jsonl`
- Arms: **A** full agent (headline) · **B** A without the evaluator/broaden loop (derived from A's first pass) · **C** `query_fast()`

Scoring: technique IDs cited in the answer (`extract_technique_ids`), rolled up to the parent technique because all gold IDs are parent-level, then `technique_set_score` against the sample's `gold_attack_ids`. Macro = mean over samples; micro = pooled matches. Name matching is reported as a secondary row only — see §6.

## 1. Technique precision / recall / F1

| Metric | A  full agent (headline) | B  agent - self-reflection | C  fast path |
|---|---|---|---|
| Macro precision | 0.583 | 0.648 | 0.707 |
| Macro recall | 0.700 | 0.765 | 0.655 |
| Macro f1 | 0.629 | 0.693 | 0.623 |
| Micro precision | 0.622 | 0.624 | 0.655 |
| Micro recall | 0.697 | 0.765 | 0.658 |
| Micro f1 | 0.657 | 0.687 | 0.657 |
| Macro F1, no parent roll-up | 0.473 | 0.519 | 0.468 |
| Macro F1, + name matching (defective alias map, §6) | 0.518 | 0.552 | 0.502 |
| Mean techniques cited | 4.10 | 4.49 | 3.68 |
| Answers citing no technique | 10 | 0 | 0 |

### Step recall by cue type

Precision cannot be split by cue type — a predicted technique belongs to the answer, not to a step — so the split is recall only: the share of steps whose gold technique the answer cites.

| Cue type (steps) | A | B | C |
|---|---|---|---|
| named (61) | 0.836 | 0.921 | 0.899 |
| described (286) | 0.679 | 0.749 | 0.603 |

## 2. Paired comparisons (same samples)

Δ = left − right, per-sample macro metric. 95% CI: paired bootstrap (10k resamples). p: two-sided Wilcoxon signed-rank on non-zero Δ (n/a below 6 non-zero pairs). `*` = CI excludes 0. W/T/L = samples where left is better / equal / worse.

| Comparison | mean Δ | 95% CI | Wilcoxon p | n | W/T/L |
|---|---|---|---|---|---|
| A − B f1 | -0.064 * | [-0.113, -0.021] | 0.0124 | 100 | 6/80/14 |
| A − B precision | -0.064 * | [-0.112, -0.024] | 0.0062 | 100 | 5/81/14 |
| A − B recall | -0.066 * | [-0.119, -0.017] | 0.0238 | 100 | 6/81/13 |
| B − C f1 | +0.070 * | [+0.015, +0.127] | 0.0448 | 100 | 50/14/36 |
| B − C precision | -0.059 * | [-0.114, -0.001] | 0.0051 | 100 | 28/23/49 |
| B − C recall | +0.111 * | [+0.040, +0.185] | 0.0071 | 100 | 40/34/26 |
| A − C f1 | +0.006 | [-0.066, +0.076] | 0.5879 | 100 | 46/16/38 |
| A − C precision | -0.123 * | [-0.193, -0.056] | 0.0002 | 100 | 25/25/50 |
| A − C recall | +0.045 | [-0.039, +0.130] | 0.2880 | 100 | 36/34/30 |

## 3. Self-reflection loop diagnostics (arm A)

| Diagnostic | Value |
|---|---|
| First-pass verdict INSUFFICIENT | 25/100 (25.0%) |
| Broaden rounds used: 0 / 1 / 2 | 75 / 25 / 0 |
| Answer replaced by ACKNOWLEDGE_LIMIT | 10/100 (10.0%) |
| Samples where the loop changed the answer path (B ≠ A) | 25/100 |
| LLM-judged evaluations (excl. forced SUFFICIENT at max retries) | 125 |
| … of which INSUFFICIENT | 35 |
| … INSUFFICIENT strategies | ACKNOWLEDGE_LIMIT 10, BROADEN_SEARCH 25 |
| … SUFFICIENT with strategy PARTIAL_ANSWER (gap warning never reaches the answer) | 3 |
| … evaluator parse / exception fallbacks to SUFFICIENT | 0 |

### A − B restricted to samples where the loop acted

On every other sample B ≡ A by construction (Δ = 0), so the all-sample A − B above is this subset's effect diluted by the samples the loop never touched.

| Subset | mean Δ F1 | 95% CI | Wilcoxon p | n | W/T/L |
|---|---|---|---|---|---|
| broadening fired (≥1 round) | -0.257 * | [-0.422, -0.095] | 0.0124 | 25 | 6/5/14 |
| ACKNOWLEDGE_LIMIT returned | -0.704 * | [-0.828, -0.576] | 0.0020 | 10 | 0/0/10 |
| loop changed answer path (any) | -0.257 * | [-0.422, -0.095] | 0.0124 | 25 | 6/5/14 |

Did broadening put more gold techniques into the context? (share of gold technique IDs appearing in the rendered context)

| Subset | first-pass ctx recall | final ctx recall | mean Δ | 95% CI | n |
|---|---|---|---|---|---|
| broadening fired | 0.761 | 0.759 | -0.002 | [-0.077, +0.073] | 25 |

## 3b. Evaluator sensitivity and calibration

The evaluator reads only the first 4000 characters of the context. "Visible recall" = share of gold technique IDs inside that window; "full recall" = in the whole context the reasoning LLM gets. Both count IDs only, so a technique present by name alone counts as missing.

| Context judged | n | INSUFFICIENT | visible recall | full recall | mean context chars |
|---|---|---|---|---|---|
| A first pass (served) | 100 | 25 (25.0%) | 0.553 | 0.815 | 9258 |
| C fast-path context (probe S) | 100 | 65 (65.0%) | 0.272 | 0.272 | 3241 |

Same incident, two contexts (rows: verdict on A's first pass; columns: verdict on C's context). A sensitive evaluator puts mass in the SUFFICIENT → INSUFFICIENT cell.

| A \ C | SUFFICIENT | INSUFFICIENT |
|---|---|---|
| SUFFICIENT | 31 | 44 |
| INSUFFICIENT | 4 | 21 |

Exact McNemar p (discordant 44 vs 4): 0.0000

Calibration, pooled over all 200 judgements. A SUFFICIENT verdict in the first row is a likely miss: most of the incident's gold techniques are not in what the evaluator read.

| Visible gold recall | n | SUFFICIENT | INSUFFICIENT |
|---|---|---|---|
| visible recall < 0.5 | 128 | 51 | 77 |
| 0.5 ≤ visible recall < 1 | 51 | 41 | 10 |
| visible recall = 1 | 21 | 18 | 3 |

Evaluator checklist vs the incident's own tactics. The prompt checks four fixed phases (Initial Access, Credential Access, Privilege Escalation, Impact); the column counts how many of them occur among the sample's gold tactics. If verdicts track this count rather than visible recall, the loop is triggered by the rubric, not by what the context is missing.

| Checklist phases in gold | n | A first pass INSUFFICIENT | visible recall (A) | probe S INSUFFICIENT |
|---|---|---|---|---|
| 0 | 31 | 16 (52%) | 0.404 | 28/31 (90%) |
| 1 | 45 | 8 (18%) | 0.588 | 22/45 (49%) |
| 2 | 21 | 0 (0%) | 0.677 | 12/21 (57%) |
| 3 | 3 | 1 (33%) | 0.717 | 3/3 (100%) |

## 4. Grounding — context vs answer

Context recall: share of gold technique IDs that appear in the context the reasoning LLM saw. Only vector-hit and subgraph headers carry IDs (relationship documents and neighbour lists carry names), so both context recall and "absent from context" are conservative: a technique present only by name counts as absent. Answer recall above context recall means the model cited techniques from its own parametric knowledge.

| | A | B | C |
|---|---|---|---|
| Context recall | 0.814 | 0.815 | 0.272 |
| Answer recall (macro) | 0.700 | 0.765 | 0.655 |
| Cited IDs absent from context (mean share per answer) | 0.006 | 0.004 | 0.436 |
| Correct (gold) citations absent from context | 2/255 (0.8%) | 1/280 (0.4%) | 145/241 (60.2%) |

## 5. Latency and LLM cost per sample

Cost at OpenRouter list price $0.20 / $1.20 per 1M input / output tokens. B's latency is reconstructed (A's shared node timings + its own reasoning), not measured end-to-end. Non-LLM time is local BGE-M3 / reranker / Neo4j / Qdrant on the benchmark machine and does not transfer to production hardware.

| Metric | A | B | C |
|---|---|---|---|
| Latency mean (s) | 59.1 | 43.6 | 21.1 |
| Latency median (s) | 48.8 | 38.8 | 19.7 |
| Latency p90 (s) | 92.4 | 69.3 | 29.0 |
| … of which LLM (s, mean) | 26.4 | 17.4 | 12.8 |
| LLM calls mean | 4.50 | 3.00 | 1.00 |
| LLM calls min–max | 4–6 | 3–3 | 1–1 |
| Input tokens mean | 7818 | 4915 | 1944 |
| Output tokens mean | 2419 | 1680 | 1476 |
| Cost per sample (USD) | 0.0045 | 0.0030 | 0.0022 |

## 6. Limitations

- **B is a counterfactual branch of A**, not an independent run. That is what makes A − B exactly the loop's effect, but B ≡ A on samples where the loop did not act, so the all-sample A − B is necessarily diluted.
- **B − C is not decomposition + quota alone.** `query_fast` also renders a smaller context (5 vector hits / 3 subgraphs vs 15 / 8) and skips the router call; the difference bundles all of these.
- **One run per arm.** The core LLM is sampled at temperature 0 but is not guaranteed deterministic; comparisons involving an independent generation (B − C, A − C, and A − B on the loop subset) include run-to-run variance, which the paired CI reflects but cannot separate out.
- **Extraction.** Predictions are the technique IDs an answer cites. A technique described only in prose without its ID is not counted, and an ID mentioned in a negative sense counts as predicted. Name matching was the intended complement but is not used for the headline: `attack_lookup.json`'s alias map keeps one ID per name and resolves names shared by enterprise and mobile techniques to the mobile ID (e.g. "screen capture" → T1513, "system information discovery" → T1426), plus some revoked IDs ("data encrypted" → T1022). Found on the 5-sample smoke run, before the full run; the name-matched F1 is still reported for transparency.
- **Evaluator probe.** S reuses C's context, so its verdicts share C's retrieval; calibration buckets use ID-visible recall, which undercounts techniques the context names without an ID and so overstates likely misses.
- **Gold coverage.** One gold ID (T0827) is ICS, which is not ingested, so it is unreachable for every arm. The ATT&CK version of the index (v19) differs from the source advisories' version; drifted IDs penalise all arms equally.
