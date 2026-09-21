# MITRE table threshold calibration

45 incidents from `data/incident_draft.json` (LLM-drafted), answers from gen_bench variant A. Scores recomputed with today's reranker; `double` replays the pre-2026-08-15 double sigmoid on the same logits. Macro-averaged soft technique P/R/F1 (exact 1.0, same base 0.5). An ablation for choosing a rule, not a headline benchmark.

Caveats: the incidents are LLM-drafted, not real CTI. The answers were generated in July from contexts retrieved under the double sigmoid, so any comparison of the two modes' tables favours `double`; compare rules within a mode. Graph centres are rebuilt from the seeds, but neighbours are not fetched, so a cited neighbour row is missing in both modes.

## Retrieval: which hits win the per-sub-query quota

Recall counts technique nodes among the merged vector hits; the second column adds the techniques at either end of a merged relationship hit, which reach the context through graph expansion but can never be an uncited table row.

| mode | technique recall (nodes) | + relationship endpoints | technique precision (nodes) | quota slots by type |
| --- | --- | --- | --- | --- |
| single | 0.487 | 0.737 | 0.419 | Relationship 392, Technique 134, Subtechnique 85, Software 24, Tactic 11, Mitigation 8, DataComponent 6, Group 1, Campaign 1 |
| double | 0.668 | 0.754 | 0.250 | Technique 279, Subtechnique 238, Relationship 126, Tactic 7, DataComponent 5, Mitigation 3 |

## Filter: which uncited rows the table keeps

`good` / `noise` count uncited technique rows whose base technique is / is not in gold, summed over all incidents; `other` counts uncited non-technique rows (Software, Group, Mitigation…), which gold cannot judge. ★ marks the value each mode shipped with.

### single

| rule | cut | P | R | F1 | good | noise | other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cited_only | — | 0.634 | 0.642 | 0.622 | 0 | 0 | 0 |
| keep_all | — | 0.473 | 0.649 | 0.530 | 7 | 71 | 44 |
| absolute | 0 | 0.473 | 0.649 | 0.530 | 7 | 71 | 44 |
| absolute | 0.01 | 0.506 | 0.649 | 0.549 | 7 | 53 | 35 |
| absolute | 0.02 | 0.519 | 0.649 | 0.556 | 7 | 45 | 31 |
| absolute | 0.03 | 0.525 | 0.649 | 0.561 | 6 | 42 | 27 |
| absolute ★ | 0.05 | 0.529 | 0.649 | 0.564 | 6 | 39 | 21 |
| absolute | 0.08 | 0.539 | 0.649 | 0.570 | 6 | 36 | 21 |
| absolute | 0.1 | 0.543 | 0.649 | 0.572 | 6 | 34 | 18 |
| absolute | 0.15 | 0.549 | 0.644 | 0.574 | 5 | 30 | 15 |
| absolute | 0.2 | 0.562 | 0.644 | 0.582 | 5 | 23 | 14 |
| absolute | 0.3 | 0.572 | 0.642 | 0.588 | 4 | 17 | 12 |
| absolute | 0.5 | 0.603 | 0.642 | 0.604 | 4 | 7 | 8 |
| relative | 0.05 | 0.477 | 0.649 | 0.533 | 7 | 69 | 41 |
| relative | 0.1 | 0.480 | 0.649 | 0.535 | 7 | 67 | 41 |
| relative | 0.2 | 0.491 | 0.649 | 0.544 | 7 | 58 | 39 |
| relative | 0.3 | 0.495 | 0.649 | 0.546 | 7 | 56 | 35 |
| relative | 0.5 | 0.525 | 0.646 | 0.565 | 6 | 39 | 31 |
| relative | 0.7 | 0.541 | 0.642 | 0.573 | 5 | 31 | 27 |
| relative | 0.9 | 0.569 | 0.642 | 0.588 | 1 | 23 | 20 |
| rank | rank ≤ 1 | 0.570 | 0.642 | 0.588 | 1 | 22 | 19 |
| rank | rank ≤ 2 | 0.493 | 0.646 | 0.545 | 4 | 59 | 37 |

### double

| rule | cut | P | R | F1 | good | noise | other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cited_only | — | 0.591 | 0.677 | 0.619 | 0 | 0 | 0 |
| keep_all | — | 0.262 | 0.718 | 0.377 | 33 | 266 | 11 |
| absolute | 0.5 | 0.262 | 0.718 | 0.377 | 33 | 266 | 11 |
| absolute | 0.55 | 0.262 | 0.718 | 0.377 | 33 | 266 | 7 |
| absolute | 0.58 | 0.262 | 0.718 | 0.377 | 33 | 266 | 7 |
| absolute | 0.6 | 0.262 | 0.718 | 0.377 | 33 | 266 | 7 |
| absolute ★ | 0.62 | 0.441 | 0.695 | 0.524 | 17 | 74 | 7 |
| absolute | 0.65 | 0.479 | 0.686 | 0.549 | 14 | 46 | 4 |
| absolute | 0.7 | 0.519 | 0.677 | 0.575 | 6 | 25 | 2 |
| absolute | 0.75 | 0.553 | 0.677 | 0.597 | 4 | 10 | 2 |
| absolute | 0.8 | 0.570 | 0.677 | 0.607 | 3 | 4 | 0 |
| relative | 0.7 | 0.262 | 0.718 | 0.377 | 33 | 266 | 11 |
| relative | 0.75 | 0.262 | 0.718 | 0.378 | 33 | 265 | 11 |
| relative | 0.8 | 0.268 | 0.718 | 0.384 | 31 | 256 | 11 |
| relative | 0.85 | 0.271 | 0.718 | 0.388 | 30 | 251 | 8 |
| relative | 0.9 | 0.291 | 0.712 | 0.406 | 24 | 227 | 8 |
| relative | 0.95 | 0.328 | 0.712 | 0.436 | 21 | 189 | 6 |
| rank | rank ≤ 1 | 0.470 | 0.691 | 0.547 | 5 | 66 | 2 |
| rank | rank ≤ 2 | 0.310 | 0.702 | 0.423 | 21 | 198 | 9 |
