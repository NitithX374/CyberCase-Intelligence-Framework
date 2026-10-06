# MITRE table re-read — the served pipeline on the real-CTI incidents

Model `google/gemma-4-26b-a4b-it`. Each incident ran once through `routers.rag._run_pipeline` (agent graph, re-read, table). The answer-grounded table is built from the same retrieval and the same answer. Parent-level technique F1; intervals are 95% bootstrap over incidents, differences are paired.

## test — 45 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.645 | 0.735 | 0.680 [0.613, 0.746] | +0.039 [+0.013, +0.064] | 23/17/5 | 4.18 |
| answer-grounded table | 0.571 | 0.757 | 0.640 [0.577, 0.704] | — | — | 4.91 |
| table as served (re-read) | 0.664 | 0.823 | 0.722 [0.664, 0.781] | +0.082 [+0.021, +0.142] | 25/12/8 | 4.69 |

## dev — 55 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.650 | 0.732 | 0.681 [0.619, 0.741] | +0.041 [+0.015, +0.067] | 24/25/6 | 4.29 |
| answer-grounded table | 0.575 | 0.750 | 0.640 [0.582, 0.694] | — | — | 4.95 |
| table as served (re-read) | 0.702 | 0.851 | 0.762 [0.712, 0.809] | +0.122 [+0.066, +0.181] | 40/8/7 | 4.60 |

## all — 100 incidents

| | P | R | F1 [95% CI] | Δ F1 vs answer-grounded table | W/T/L | rows |
| --- | --- | --- | --- | --- | --- | --- |
| answer (the IDs it cites) | 0.648 | 0.733 | 0.680 [0.635, 0.726] | +0.040 [+0.022, +0.058] | 47/42/11 | 4.24 |
| answer-grounded table | 0.573 | 0.753 | 0.640 [0.598, 0.684] | — | — | 4.93 |
| table as served (re-read) | 0.685 | 0.839 | 0.744 [0.705, 0.781] | +0.104 [+0.061, +0.145] | 65/20/15 | 4.64 |

## What the re-read did

- Decided the technique rows on 100 of 100 incidents; the other 0 kept the answer-grounded table.
- Rows for a technique retrieval had not returned: 106 (1.06 an incident, on 61 incidents).
- Time in the re-read: median 10.7 s, 90th percentile 20.8 s. Whole request: median 89.7 s. Incidents ran several at a time on one machine, so these are not what one request alone takes.
