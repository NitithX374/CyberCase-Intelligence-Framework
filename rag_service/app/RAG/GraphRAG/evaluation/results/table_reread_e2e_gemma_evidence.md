# MITRE table re-read — the served pipeline on the real-CTI incidents

Model `google/gemma-4-26b-a4b-it`. Each incident ran once through `routers.rag._run_pipeline` (agent graph, re-read, table). The answer-grounded table is built from the same retrieval and the same answer. Parent-level technique F1; intervals are 95% bootstrap over incidents, differences are paired.

## test — 45 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.656 | 0.725 | 0.680 [0.616, 0.744] | +0.051 [+0.014, +0.087] | 24/15/6 | 4.07 |
| answer-grounded table | 0.565 | 0.744 | 0.629 [0.570, 0.688] | — | — | 4.98 |
| table as served (re-read) | 0.688 | 0.831 | 0.741 [0.683, 0.797] | +0.112 [+0.058, +0.165] | 27/12/6 | 4.58 |

## dev — 55 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.632 | 0.737 | 0.674 [0.613, 0.733] | +0.038 [+0.008, +0.071] | 24/20/11 | 4.36 |
| answer-grounded table | 0.565 | 0.752 | 0.635 [0.578, 0.693] | — | — | 4.98 |
| table as served (re-read) | 0.697 | 0.831 | 0.748 [0.695, 0.800] | +0.113 [+0.052, +0.176] | 37/8/10 | 4.51 |

## all — 100 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.643 | 0.732 | 0.676 [0.633, 0.722] | +0.044 [+0.021, +0.068] | 48/35/17 | 4.23 |
| answer-grounded table | 0.565 | 0.749 | 0.632 [0.592, 0.674] | — | — | 4.98 |
| table as served (re-read) | 0.693 | 0.831 | 0.745 [0.707, 0.784] | +0.113 [+0.073, +0.153] | 64/20/16 | 4.54 |

## What the re-read did

- Decided the technique rows on 100 of 100 incidents; the other 0 kept the answer-grounded table.
- Rows for a technique retrieval had not returned: 98 (0.98 an incident, on 60 incidents).
- Time in the re-read: median 16.5 s, 90th percentile 47.0 s. Whole request: median 101.2 s. Incidents ran several at a time on one machine, so these are not what one request alone takes.
