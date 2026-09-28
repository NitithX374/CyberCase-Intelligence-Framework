# HyDE through the served agent — real-CTI tier

Samples: 100 paired. Model: `openrouter:openai/gpt-5.6-luna`. Commit(s): eee50ef.
H replayed 112 of its 120 decompositions from P (P retrieved 123 times); any others ran live. H's latency omits the replayed decomposition calls, so it is understated.

## Per-arm means

| Metric | P  production | H  + HyDE (fuse_sub) |
|---|---|---|
| F1 | 0.727 | 0.719 |
| Precision | 0.676 | 0.655 |
| Recall | 0.815 | 0.828 |
| Step recall, described | 0.800 | 0.818 |
| Step recall, named | 0.944 | 0.955 |
| Context gold recall | 0.862 | 0.881 |
| Cited IDs not in context | 0.002 | 0.005 |
| Correct IDs not in context (total) | 1 | 0 |
| Broaden rounds (total) | 23 | 20 |
| ACKNOWLEDGE_LIMIT answers | 0 | 0 |
| LLM calls / sample | 4.460 | 4.480 |
| Latency s / sample | 45.840 | 66.408 |
| Cost USD (total) | 0.470 | 0.532 |

## Paired: H − P

Per-sample Δ; 95% CI paired bootstrap; p two-sided Wilcoxon; * = CI excludes 0.

| Metric | Δ mean | 95% CI | p | n | W/T/L |
|---|---|---|---|---|---|
| F1 | -0.007 | [-0.033, +0.018] | 0.6793 | 100 | 25/46/29 |
| Precision | -0.021 | [-0.049, +0.006] | 0.1300 | 100 | 23/48/29 |
| Recall | +0.013 | [-0.017, +0.042] | 0.2656 | 100 | 15/75/10 |
| Step recall, described | +0.018 | [-0.018, +0.054] | 0.2577 | 98 | 14/74/10 |
| Step recall, named | +0.011 | [+0.000, +0.034] | n/a | 39 | 1/38/0 |
| Context gold recall | +0.019 | [-0.007, +0.043] | 0.1223 | 100 | 11/85/4 |
| Cited IDs not in context | +0.003 | [-0.004, +0.011] | n/a | 100 | 3/96/1 |

First evaluator verdict identical in 81/100 samples.
