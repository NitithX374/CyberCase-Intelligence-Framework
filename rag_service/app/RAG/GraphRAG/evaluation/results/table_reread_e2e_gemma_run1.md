# MITRE table re-read — the served pipeline on the real-CTI incidents

Model `google/gemma-4-26b-a4b-it`. Each incident ran once through `routers.rag._run_pipeline` (agent graph, re-read, table). The answer-grounded table is built from the same retrieval and the same answer. Parent-level technique F1; intervals are 95% bootstrap over incidents, differences are paired.

## test — 45 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.683 | 0.759 | 0.708 [0.650, 0.767] | +0.077 [+0.049, +0.107] | 26/18/1 | 4.07 |
| answer-grounded table | 0.565 | 0.744 | 0.631 [0.572, 0.690] | — | — | 4.87 |
| table as served (re-read) | 0.662 | 0.826 | 0.723 [0.668, 0.778] | +0.092 [+0.036, +0.143] | 29/12/4 | 4.71 |

## dev — 55 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.663 | 0.761 | 0.700 [0.634, 0.762] | +0.041 [+0.011, +0.073] | 23/25/7 | 4.36 |
| answer-grounded table | 0.583 | 0.779 | 0.659 [0.596, 0.717] | — | — | 5.05 |
| table as served (re-read) | 0.682 | 0.857 | 0.750 [0.702, 0.798] | +0.091 [+0.038, +0.148] | 31/9/15 | 4.82 |

## all — 100 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.672 | 0.760 | 0.704 [0.659, 0.747] | +0.057 [+0.035, +0.079] | 49/43/8 | 4.23 |
| answer-grounded table | 0.575 | 0.763 | 0.647 [0.603, 0.689] | — | — | 4.97 |
| table as served (re-read) | 0.673 | 0.843 | 0.738 [0.703, 0.774] | +0.092 [+0.053, +0.130] | 60/21/19 | 4.77 |

## What the re-read did

- Decided the technique rows on 100 of 100 incidents; the other 0 kept the answer-grounded table.
- Rows for a technique retrieval had not returned: 111 (1.11 an incident, on 64 incidents).
- Time in the re-read: median 11.4 s, 90th percentile 25.4 s. Whole request: median 89.3 s. Incidents ran several at a time on one machine, so these are not what one request alone takes.
