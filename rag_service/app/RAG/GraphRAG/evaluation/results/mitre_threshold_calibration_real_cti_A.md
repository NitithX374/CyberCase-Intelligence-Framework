# MITRE table threshold calibration

100 real-CTI incidents (`real_cti/data/CTI_dataset.json`: CISA advisories and CTID emulation plans, drafted in Thai), with the served agent's own sub-queries and broaden rewrites and the answers of `agentic_ablation` arm A (openai/gpt-5.6-luna, 2026-09-18/19). Scores recomputed with today's reranker; `double` replays the pre-2026-08-15 double sigmoid on the same logits. Macro-averaged soft technique P/R/F1 (exact 1.0, same base 0.5). An ablation for choosing a rule, not a headline benchmark.

Caveats: the answers were generated on the single-sigmoid scale, so any comparison of the two modes' tables favours `single`; compare rules within a mode. Retrieval is replayed with today's index, which the agent's own run may not have matched exactly. Graph centres are rebuilt from the seeds, but neighbours are not fetched, so a cited neighbour row is missing in both modes.

## Retrieval: which hits win the per-sub-query quota

Recall counts technique nodes among the merged vector hits; the second column adds the techniques at either end of a merged relationship hit, which reach the context through graph expansion but can never be an uncited table row.

| mode | technique recall (nodes) | + relationship endpoints | technique precision (nodes) | quota slots by type |
| --- | --- | --- | --- | --- |
| single | 0.560 | 0.692 | 0.347 | Relationship 969, Subtechnique 333, Technique 298, Software 124, Tactic 23, DataComponent 15, Mitigation 11, Group 4 |
| double | 0.691 | 0.720 | 0.196 | Subtechnique 752, Technique 606, Relationship 303, Tactic 16, DataComponent 6, Software 1, Mitigation 1 |

## Filter: which uncited rows the table keeps

`good` / `noise` count uncited technique rows whose base technique is / is not in gold, summed over all incidents; `other` counts uncited non-technique rows (Software, Group, Mitigation…), which gold cannot judge. ★ marks the value each mode shipped with.

### single

| rule | cut | P | R | F1 | good | noise | other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cited_only | — | 0.441 | 0.597 | 0.493 | 0 | 0 | 0 |
| keep_all | — | 0.343 | 0.666 | 0.443 | 64 | 207 | 161 |
| absolute | 0 | 0.343 | 0.666 | 0.443 | 64 | 207 | 161 |
| absolute | 0.01 | 0.364 | 0.662 | 0.460 | 58 | 158 | 136 |
| absolute | 0.02 | 0.375 | 0.657 | 0.468 | 53 | 137 | 115 |
| absolute | 0.03 | 0.380 | 0.657 | 0.472 | 52 | 126 | 105 |
| absolute ★ | 0.05 | 0.389 | 0.653 | 0.478 | 46 | 109 | 93 |
| absolute | 0.08 | 0.395 | 0.650 | 0.481 | 42 | 100 | 73 |
| absolute | 0.1 | 0.400 | 0.648 | 0.484 | 40 | 90 | 64 |
| absolute | 0.15 | 0.414 | 0.646 | 0.493 | 35 | 72 | 51 |
| absolute | 0.2 | 0.424 | 0.645 | 0.498 | 33 | 64 | 45 |
| absolute | 0.3 | 0.430 | 0.639 | 0.499 | 27 | 54 | 26 |
| absolute | 0.5 | 0.440 | 0.623 | 0.499 | 19 | 36 | 18 |
| relative | 0.05 | 0.347 | 0.666 | 0.447 | 64 | 198 | 159 |
| relative | 0.1 | 0.352 | 0.665 | 0.451 | 61 | 188 | 155 |
| relative | 0.2 | 0.359 | 0.663 | 0.456 | 57 | 176 | 148 |
| relative | 0.3 | 0.364 | 0.655 | 0.458 | 49 | 162 | 136 |
| relative | 0.5 | 0.382 | 0.652 | 0.470 | 44 | 131 | 106 |
| relative | 0.7 | 0.396 | 0.640 | 0.478 | 30 | 107 | 87 |
| relative | 0.9 | 0.408 | 0.636 | 0.487 | 24 | 85 | 64 |
| rank | rank ≤ 1 | 0.414 | 0.633 | 0.489 | 22 | 77 | 56 |
| rank | rank ≤ 2 | 0.366 | 0.657 | 0.460 | 49 | 158 | 129 |

### double

| rule | cut | P | R | F1 | good | noise | other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cited_only | — | 0.451 | 0.586 | 0.491 | 0 | 0 | 0 |
| keep_all | — | 0.197 | 0.705 | 0.303 | 147 | 766 | 11 |
| absolute | 0.5 | 0.197 | 0.705 | 0.303 | 147 | 766 | 11 |
| absolute | 0.55 | 0.197 | 0.705 | 0.303 | 147 | 766 | 9 |
| absolute | 0.58 | 0.197 | 0.705 | 0.303 | 147 | 766 | 8 |
| absolute | 0.6 | 0.197 | 0.705 | 0.303 | 147 | 766 | 8 |
| absolute ★ | 0.62 | 0.360 | 0.641 | 0.446 | 61 | 157 | 7 |
| absolute | 0.65 | 0.407 | 0.629 | 0.474 | 44 | 91 | 3 |
| absolute | 0.7 | 0.432 | 0.619 | 0.486 | 29 | 59 | 3 |
| absolute | 0.75 | 0.443 | 0.605 | 0.490 | 19 | 28 | 0 |
| absolute | 0.8 | 0.457 | 0.597 | 0.494 | 10 | 11 | 0 |
| relative | 0.7 | 0.198 | 0.705 | 0.303 | 146 | 766 | 11 |
| relative | 0.75 | 0.202 | 0.705 | 0.307 | 141 | 756 | 11 |
| relative | 0.8 | 0.206 | 0.705 | 0.313 | 134 | 739 | 11 |
| relative | 0.85 | 0.211 | 0.700 | 0.318 | 127 | 708 | 9 |
| relative | 0.9 | 0.222 | 0.695 | 0.330 | 113 | 658 | 6 |
| relative | 0.95 | 0.242 | 0.692 | 0.350 | 98 | 584 | 6 |
| rank | rank ≤ 1 | 0.334 | 0.652 | 0.432 | 45 | 239 | 2 |
| rank | rank ≤ 2 | 0.236 | 0.690 | 0.344 | 110 | 570 | 9 |
