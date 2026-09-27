# HyDE Retrieval Ablation — real-CTI tier

Samples: 100 (paired across arms). Steps: 282 described, 61 named.
Decomposed: 100/100. HyDE entries written: 587/587 sub-query slots.
Retrieval only (vector list, graph expansion skipped); every arm uses the same cached sub-queries and entries.

## Per-arm means

| arm | hit@5 | step@5 | step@10 | described@5 | described@10 | named@5 | named@10 | mrr | latency ms |
|---|---|---|---|---|---|---|---|---|---|
| quota | 0.960 | 0.697 | 0.811 | 0.669 | 0.787 | 0.885 | 0.949 | 0.861 | 11148 |
| hyde | 1.000 | 0.772 | 0.906 | 0.771 | 0.899 | 0.810 | 0.949 | 0.814 | 10583 |
| hyde_desc | 0.990 | 0.738 | 0.875 | 0.720 | 0.859 | 0.782 | 0.936 | 0.817 | 10356 |
| hyde_fuse | 1.000 | 0.772 | 0.912 | 0.771 | 0.905 | 0.810 | 0.949 | 0.814 | 23936 |
| hyde_fuse_sub | 0.980 | 0.723 | 0.857 | 0.707 | 0.844 | 0.859 | 0.949 | 0.864 | 17526 |

## StepCoverage by K

**step**

| arm | @1 | @3 | @5 | @10 | @15 |
|---|---|---|---|---|---|
| quota | 0.246 | 0.550 | 0.697 | 0.811 | 0.834 |
| hyde | 0.211 | 0.562 | 0.772 | 0.906 | 0.923 |
| hyde_desc | 0.210 | 0.574 | 0.738 | 0.875 | 0.895 |
| hyde_fuse | 0.211 | 0.562 | 0.772 | 0.912 | 0.926 |
| hyde_fuse_sub | 0.246 | 0.552 | 0.723 | 0.857 | 0.881 |

**described**

| arm | @1 | @3 | @5 | @10 | @15 |
|---|---|---|---|---|---|
| quota | 0.233 | 0.494 | 0.669 | 0.787 | 0.806 |
| hyde | 0.193 | 0.552 | 0.771 | 0.899 | 0.918 |
| hyde_desc | 0.228 | 0.555 | 0.720 | 0.859 | 0.885 |
| hyde_fuse | 0.193 | 0.552 | 0.771 | 0.905 | 0.920 |
| hyde_fuse_sub | 0.237 | 0.504 | 0.707 | 0.844 | 0.863 |

**named**

| arm | @1 | @3 | @5 | @10 | @15 |
|---|---|---|---|---|---|
| quota | 0.412 | 0.788 | 0.885 | 0.949 | 0.966 |
| hyde | 0.261 | 0.585 | 0.810 | 0.949 | 0.949 |
| hyde_desc | 0.179 | 0.609 | 0.782 | 0.936 | 0.962 |
| hyde_fuse | 0.261 | 0.585 | 0.810 | 0.949 | 0.949 |
| hyde_fuse_sub | 0.387 | 0.763 | 0.859 | 0.949 | 0.966 |

## Paired deltas vs `quota`

Δ = arm − quota per sample. 95% CI: paired bootstrap (10,000). p: two-sided Wilcoxon signed-rank on non-zero deltas. Cue-split metrics use only samples that have a step of that cue.

| arm | metric | Δ mean | 95% CI | p | W/T/L | n |
|---|---|---|---|---|---|---|
| hyde | step@5 | +0.075 | [+0.020, +0.131] | 0.0135 | 30/53/17 | 100 |
| hyde | step@10 | +0.095 | [+0.052, +0.141] | 0.0001 | 28/65/7 | 100 |
| hyde | described@5 | +0.102 | [+0.041, +0.165] | 0.0024 | 32/51/15 | 98 |
| hyde | described@10 | +0.112 | [+0.064, +0.162] | 0.0000 | 26/67/5 | 98 |
| hyde | named@5 | -0.075 | [-0.186, +0.032] | 0.2422 | 3/29/7 | 39 |
| hyde | hit@5 | +0.040 | [+0.010, +0.080] | n/a | 4/96/0 | 100 |
| hyde | mrr | -0.047 | [-0.114, +0.022] | 0.2073 | 15/60/25 | 100 |
| hyde_desc | step@5 | +0.042 | [-0.014, +0.100] | 0.0622 | 27/50/23 | 100 |
| hyde_desc | step@10 | +0.064 | [+0.016, +0.114] | 0.0168 | 30/56/14 | 100 |
| hyde_desc | described@5 | +0.051 | [-0.018, +0.120] | 0.0514 | 27/51/20 | 98 |
| hyde_desc | described@10 | +0.072 | [+0.014, +0.130] | 0.0154 | 28/57/13 | 98 |
| hyde_desc | named@5 | -0.103 | [-0.244, +0.038] | 0.1558 | 4/27/8 | 39 |
| hyde_desc | hit@5 | +0.030 | [-0.010, +0.070] | n/a | 4/95/1 | 100 |
| hyde_desc | mrr | -0.044 | [-0.113, +0.026] | 0.2304 | 18/56/26 | 100 |
| hyde_fuse | step@5 | +0.075 | [+0.020, +0.131] | 0.0135 | 30/53/17 | 100 |
| hyde_fuse | step@10 | +0.101 | [+0.057, +0.147] | 0.0000 | 29/65/6 | 100 |
| hyde_fuse | described@5 | +0.102 | [+0.041, +0.165] | 0.0024 | 32/51/15 | 98 |
| hyde_fuse | described@10 | +0.118 | [+0.070, +0.167] | 0.0000 | 27/67/4 | 98 |
| hyde_fuse | named@5 | -0.075 | [-0.186, +0.032] | 0.2422 | 3/29/7 | 39 |
| hyde_fuse | hit@5 | +0.040 | [+0.010, +0.080] | n/a | 4/96/0 | 100 |
| hyde_fuse | mrr | -0.047 | [-0.114, +0.022] | 0.2073 | 15/60/25 | 100 |
| hyde_fuse_sub | step@5 | +0.026 | [+0.007, +0.048] | 0.0347 | 11/87/2 | 100 |
| hyde_fuse_sub | step@10 | +0.047 | [+0.023, +0.074] | 0.0010 | 15/84/1 | 100 |
| hyde_fuse_sub | described@5 | +0.038 | [+0.013, +0.065] | 0.0106 | 12/84/2 | 98 |
| hyde_fuse_sub | described@10 | +0.057 | [+0.028, +0.089] | 0.0009 | 15/82/1 | 98 |
| hyde_fuse_sub | named@5 | -0.026 | [-0.077, +0.000] | n/a | 0/38/1 | 39 |
| hyde_fuse_sub | hit@5 | +0.020 | [+0.000, +0.050] | n/a | 2/98/0 | 100 |
| hyde_fuse_sub | mrr | +0.003 | [-0.018, +0.027] | 0.6250 | 4/94/2 | 100 |

## Diagnostic — does the HyDE entry name the gold technique?

Parent-level, via the alias map (under-counts names shared with mobile). Per-sample recall of gold techniques among the guessed names: **0.547**; precision of the guesses: **0.342**.

## Reading (written by hand after the run, 2026-09-28)

- **Baseline first.** With decomposition actually running, described-cue
  StepCoverage@5 is 0.669, not the ~0.1–0.16 of earlier logs — those runs had no
  core-LLM key, so `decompose()` fell back to the whole incident. The
  described/named gap is ~0.22, not ~0.7.
- **`hyde` gives the largest recall gain** (described@5 +0.102, step@10 +0.095,
  both p<0.02) but pays at the top of the ranking: @1 and MRR fall, named@5
  −0.075 (n.s.). Roughly half the gain needs the guessed technique name
  (`hyde_desc` keeps +0.051 / +0.072), and only 34% of guessed names are gold —
  so part of what `hyde` retrieves is steered by the model's prior.
- **`hyde_fuse` = `hyde`**: reranking against the entry picks the same top
  hits; pooling the sub-query's candidates changes nothing at @5.
- **`hyde_fuse_sub` is the conservative option**: smaller gain (described@5
  +0.038, described@10 +0.057, p≤0.01) with almost no losses (step@10
  15 wins / 84 ties / 1 loss), MRR unchanged. The reranker still judges
  against the case file's own words, so the guess only adds candidates.
- **Latency column is not comparable across arms**: `search_all` is memoised
  across arms, and `quota` ran first with a cold cache.
- Retrieval-only ablation. Before any arm goes into production it has to be
  measured through the served agent (answer F1 + grounding).
