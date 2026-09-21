# MITRE table threshold calibration

100 real-CTI incidents (`real_cti/data/CTI_dataset.json`: CISA advisories and CTID emulation plans, drafted in Thai), with the served agent's own sub-queries and broaden rewrites and the answers of `agentic_ablation` arm M (openai/gpt-5.6-luna, 2026-09-18/19). Scores recomputed with today's reranker; `double` replays the pre-2026-08-15 double sigmoid on the same logits. Macro-averaged soft technique P/R/F1 (exact 1.0, same base 0.5). An ablation for choosing a rule, not a headline benchmark.

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
| cited_only | — | 0.464 | 0.661 | 0.536 | 0 | 0 | 0 |
| keep_all | — | 0.345 | 0.679 | 0.447 | 36 | 194 | 162 |
| absolute | 0 | 0.345 | 0.679 | 0.447 | 36 | 194 | 162 |
| absolute | 0.01 | 0.367 | 0.676 | 0.466 | 31 | 144 | 137 |
| absolute | 0.02 | 0.379 | 0.676 | 0.475 | 29 | 125 | 117 |
| absolute | 0.03 | 0.383 | 0.676 | 0.479 | 29 | 114 | 107 |
| absolute ★ | 0.05 | 0.394 | 0.676 | 0.487 | 25 | 98 | 95 |
| absolute | 0.08 | 0.399 | 0.675 | 0.491 | 23 | 89 | 74 |
| absolute | 0.1 | 0.405 | 0.675 | 0.496 | 22 | 79 | 65 |
| absolute | 0.15 | 0.418 | 0.675 | 0.505 | 18 | 63 | 52 |
| absolute | 0.2 | 0.425 | 0.675 | 0.511 | 17 | 55 | 46 |
| absolute | 0.3 | 0.432 | 0.675 | 0.516 | 15 | 46 | 27 |
| absolute | 0.5 | 0.439 | 0.664 | 0.518 | 9 | 32 | 19 |
| relative | 0.05 | 0.349 | 0.679 | 0.451 | 36 | 186 | 160 |
| relative | 0.1 | 0.354 | 0.679 | 0.455 | 34 | 176 | 156 |
| relative | 0.2 | 0.361 | 0.679 | 0.461 | 31 | 165 | 149 |
| relative | 0.3 | 0.369 | 0.676 | 0.466 | 26 | 150 | 137 |
| relative | 0.5 | 0.383 | 0.676 | 0.478 | 24 | 121 | 109 |
| relative | 0.7 | 0.398 | 0.673 | 0.489 | 15 | 98 | 90 |
| relative | 0.9 | 0.410 | 0.665 | 0.497 | 8 | 78 | 67 |
| rank | rank ≤ 1 | 0.416 | 0.665 | 0.501 | 7 | 70 | 58 |
| rank | rank ≤ 2 | 0.365 | 0.670 | 0.463 | 24 | 147 | 131 |

### double

| rule | cut | P | R | F1 | good | noise | other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cited_only | — | 0.472 | 0.649 | 0.532 | 0 | 0 | 0 |
| keep_all | — | 0.197 | 0.706 | 0.303 | 112 | 750 | 14 |
| absolute | 0.5 | 0.197 | 0.706 | 0.303 | 112 | 750 | 14 |
| absolute | 0.55 | 0.197 | 0.706 | 0.303 | 112 | 750 | 13 |
| absolute | 0.58 | 0.197 | 0.706 | 0.303 | 112 | 750 | 12 |
| absolute | 0.6 | 0.197 | 0.706 | 0.303 | 112 | 750 | 12 |
| absolute ★ | 0.62 | 0.363 | 0.667 | 0.454 | 42 | 147 | 10 |
| absolute | 0.65 | 0.405 | 0.664 | 0.487 | 30 | 83 | 4 |
| absolute | 0.7 | 0.428 | 0.660 | 0.503 | 19 | 52 | 4 |
| absolute | 0.75 | 0.444 | 0.652 | 0.513 | 12 | 27 | 0 |
| absolute | 0.8 | 0.460 | 0.649 | 0.523 | 5 | 10 | 0 |
| relative | 0.7 | 0.198 | 0.706 | 0.304 | 111 | 750 | 14 |
| relative | 0.75 | 0.202 | 0.706 | 0.308 | 106 | 740 | 14 |
| relative | 0.8 | 0.206 | 0.706 | 0.313 | 99 | 724 | 14 |
| relative | 0.85 | 0.211 | 0.701 | 0.318 | 92 | 694 | 12 |
| relative | 0.9 | 0.222 | 0.697 | 0.330 | 78 | 644 | 10 |
| relative | 0.95 | 0.241 | 0.692 | 0.349 | 65 | 569 | 10 |
| rank | rank ≤ 1 | 0.333 | 0.669 | 0.435 | 23 | 228 | 4 |
| rank | rank ≤ 2 | 0.235 | 0.691 | 0.344 | 76 | 558 | 12 |
