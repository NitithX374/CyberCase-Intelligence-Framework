# MITRE table threshold calibration

45 incidents from `data/incident_draft.json` (LLM-drafted), answers from gen_bench variant C. Scores recomputed with today's reranker; `double` replays the pre-2026-08-15 double sigmoid on the same logits. Macro-averaged soft technique P/R/F1 (exact 1.0, same base 0.5). An ablation for choosing a rule, not a headline benchmark.

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
| cited_only | — | 0.641 | 0.637 | 0.621 | 0 | 0 | 0 |
| keep_all | — | 0.469 | 0.651 | 0.529 | 11 | 75 | 41 |
| absolute | 0 | 0.469 | 0.651 | 0.529 | 11 | 75 | 41 |
| absolute | 0.01 | 0.504 | 0.651 | 0.549 | 11 | 56 | 32 |
| absolute | 0.02 | 0.517 | 0.651 | 0.556 | 11 | 47 | 29 |
| absolute | 0.03 | 0.524 | 0.651 | 0.561 | 10 | 44 | 25 |
| absolute ★ | 0.05 | 0.527 | 0.651 | 0.563 | 10 | 42 | 19 |
| absolute | 0.08 | 0.535 | 0.651 | 0.568 | 10 | 39 | 19 |
| absolute | 0.1 | 0.539 | 0.651 | 0.570 | 10 | 37 | 16 |
| absolute | 0.15 | 0.546 | 0.645 | 0.571 | 8 | 33 | 13 |
| absolute | 0.2 | 0.558 | 0.645 | 0.579 | 8 | 26 | 12 |
| absolute | 0.3 | 0.571 | 0.645 | 0.588 | 7 | 19 | 10 |
| absolute | 0.5 | 0.610 | 0.645 | 0.606 | 7 | 7 | 7 |
| relative | 0.05 | 0.474 | 0.651 | 0.532 | 11 | 73 | 38 |
| relative | 0.1 | 0.478 | 0.651 | 0.534 | 11 | 70 | 38 |
| relative | 0.2 | 0.492 | 0.651 | 0.546 | 11 | 60 | 36 |
| relative | 0.3 | 0.495 | 0.651 | 0.547 | 11 | 58 | 32 |
| relative | 0.5 | 0.527 | 0.651 | 0.569 | 10 | 41 | 29 |
| relative | 0.7 | 0.546 | 0.646 | 0.579 | 8 | 33 | 25 |
| relative | 0.9 | 0.576 | 0.646 | 0.595 | 4 | 24 | 18 |
| rank | rank ≤ 1 | 0.576 | 0.646 | 0.595 | 4 | 23 | 17 |
| rank | rank ≤ 2 | 0.491 | 0.651 | 0.546 | 8 | 63 | 34 |

### double

| rule | cut | P | R | F1 | good | noise | other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cited_only | — | 0.606 | 0.674 | 0.626 | 0 | 0 | 0 |
| keep_all | — | 0.260 | 0.718 | 0.376 | 36 | 276 | 9 |
| absolute | 0.5 | 0.260 | 0.718 | 0.376 | 36 | 276 | 9 |
| absolute | 0.55 | 0.260 | 0.718 | 0.376 | 36 | 276 | 5 |
| absolute | 0.58 | 0.260 | 0.718 | 0.376 | 36 | 276 | 5 |
| absolute | 0.6 | 0.260 | 0.718 | 0.376 | 36 | 276 | 5 |
| absolute ★ | 0.62 | 0.447 | 0.695 | 0.528 | 20 | 77 | 5 |
| absolute | 0.65 | 0.481 | 0.687 | 0.551 | 17 | 51 | 3 |
| absolute | 0.7 | 0.529 | 0.681 | 0.582 | 9 | 28 | 1 |
| absolute | 0.75 | 0.563 | 0.681 | 0.605 | 7 | 12 | 1 |
| absolute | 0.8 | 0.584 | 0.677 | 0.615 | 4 | 5 | 0 |
| relative | 0.7 | 0.260 | 0.718 | 0.376 | 36 | 276 | 9 |
| relative | 0.75 | 0.261 | 0.718 | 0.376 | 36 | 275 | 9 |
| relative | 0.8 | 0.267 | 0.718 | 0.383 | 34 | 266 | 9 |
| relative | 0.85 | 0.270 | 0.718 | 0.386 | 33 | 261 | 6 |
| relative | 0.9 | 0.289 | 0.712 | 0.404 | 26 | 238 | 6 |
| relative | 0.95 | 0.320 | 0.712 | 0.432 | 23 | 202 | 4 |
| rank | rank ≤ 1 | 0.470 | 0.697 | 0.551 | 8 | 73 | 1 |
| rank | rank ≤ 2 | 0.307 | 0.705 | 0.421 | 25 | 209 | 7 |
