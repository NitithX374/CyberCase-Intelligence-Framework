# Evaluator Prompt Variants — verdicts on arm A's first-pass contexts

- 100 incidents, same contexts for every variant (`agentic_ablation.jsonl`), so only the evaluator changes.
- `v0_served`: the verdicts the served evaluator produced during the ablation (first 4000 context chars, four fixed phases).
- `v1_full_ctx`: served prompt, whole context.
- `v2_subqueries`: whole context, coverage judged against the incident's own decomposed sub-queries.

Ground truth is the context itself: how much of the sample's gold ATT&CK IDs it contains. INSUFFICIENT is treated as a detector of a context that is missing gold. Recall counts IDs only (a technique present by name alone counts as missing), so absolute rates are conservative — but identical across variants.

## Verdicts

| Variant | INSUFFICIENT | mean gold recall when SUFFICIENT | when INSUFFICIENT | flips vs served (S→I / I→S) |
|---|---|---|---|---|
| v0_served | 25/100 (25%) | 0.832 | 0.761 | 0 / 0 |
| v1_full_ctx | 13/100 (13%) | 0.823 | 0.760 | 1 / 13 |
| v2_subqueries | 60/100 (60%) | 0.857 | 0.786 | 44 / 9 |

## INSUFFICIENT as a detector of: context is missing ANY gold technique (recall < 1.0)

| Variant | precision | recall | F1 | accuracy | TP/FP/FN/TN |
|---|---|---|---|---|---|
| v0_served | 0.680 | 0.327 | 0.442 | 0.570 | 17/8/35/40 |
| v1_full_ctx | 0.692 | 0.173 | 0.277 | 0.530 | 9/4/43/44 |
| v2_subqueries | 0.583 | 0.673 | 0.625 | 0.580 | 35/25/17/23 |

## INSUFFICIENT as a detector of: context is missing MOST gold techniques (recall < 0.5)

| Variant | precision | recall | F1 | accuracy | TP/FP/FN/TN |
|---|---|---|---|---|---|
| v0_served | 0.120 | 0.333 | 0.176 | 0.720 | 3/22/6/69 |
| v1_full_ctx | 0.154 | 0.222 | 0.182 | 0.820 | 2/11/7/80 |
| v2_subqueries | 0.100 | 0.667 | 0.174 | 0.430 | 6/54/3/37 |

## Cost

| Variant | calls | input tokens (mean) | output tokens (mean) | latency (s, mean) |
|---|---|---|---|---|
| v0_served | 0 (reused from the ablation run) | — | — | — |
| v1_full_ctx | 100 | 3772 | 622 | 6.0 |
| v2_subqueries | 100 | 3754 | 659 | 6.4 |
