# MITRE table re-read — the served pipeline on the real-CTI incidents

Model `google/gemma-4-26b-a4b-it`. Each incident ran once through `routers.rag._run_pipeline` (agent graph, re-read, table). The answer-grounded table is built from the same retrieval and the same answer. Parent-level technique F1; intervals are 95% bootstrap over incidents, differences are paired.

## test — 44 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.628 | 0.698 | 0.652 [0.585, 0.720] | +0.055 [+0.027, +0.086] | 20/22/2 | 4.09 |
| answer-grounded table | 0.549 | 0.681 | 0.597 [0.531, 0.666] | — | — | 4.68 |
| table as served (re-read) | 0.682 | 0.807 | 0.729 [0.660, 0.793] | +0.132 [+0.072, +0.189] | 29/12/3 | 4.45 |

## dev — 55 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.648 | 0.704 | 0.664 [0.599, 0.726] | +0.043 [+0.012, +0.074] | 22/26/7 | 4.18 |
| answer-grounded table | 0.568 | 0.711 | 0.622 [0.560, 0.679] | — | — | 4.76 |
| table as served (re-read) | 0.673 | 0.818 | 0.730 [0.678, 0.780] | +0.108 [+0.047, +0.168] | 32/12/11 | 4.60 |

## all — 99 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.639 | 0.701 | 0.659 [0.612, 0.706] | +0.048 [+0.027, +0.070] | 42/48/9 | 4.14 |
| answer-grounded table | 0.559 | 0.697 | 0.611 [0.566, 0.656] | — | — | 4.73 |
| table as served (re-read) | 0.677 | 0.813 | 0.729 [0.687, 0.770] | +0.119 [+0.075, +0.162] | 61/24/14 | 4.54 |

## What the re-read did

- Decided the technique rows on 99 of 99 incidents; the other 0 kept the answer-grounded table.
- Rows for a technique retrieval had not returned: 110 (1.11 an incident, on 69 incidents).
- Time in the re-read: median 16.8 s, 90th percentile 32.0 s. Whole request: median 91.8 s. Incidents ran several at a time on one machine, so these are not what one request alone takes.
