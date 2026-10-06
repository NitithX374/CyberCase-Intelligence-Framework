# MITRE table re-read — what the served pipeline scores

Two runs of all 100 real-CTI incidents through `routers.rag._run_pipeline` (agent graph, re-read,
table) on `google/gemma-4-26b-a4b-it`, 2026-10-06. Each run made its own retrieval, answers and
re-read; nothing was replayed. Scores are parent-level technique F1 against the sources' own labels.
The answer-grounded table is built from the same retrieval and answer as the served one, so the
difference between the two is the re-read and nothing else.

| | answer-grounded table | table as served | Δ F1 [95% CI] | W/T/L |
| --- | --- | --- | --- | --- |
| run 1, all 100 | .647 | .738 [.703, .774] | +.092 [+.053, +.130] | 60/21/19 |
| run 2, all 100 | .640 | .744 [.705, .781] | +.104 [+.061, +.145] | 65/20/15 |
| run 1, held-out 45 | .631 | .723 [.668, .778] | +.092 [+.036, +.143] | 29/12/4 |
| run 2, held-out 45 | .640 | .722 [.664, .781] | +.082 [+.021, +.142] | 25/12/8 |
| run 1, design 55 | .659 | .750 [.702, .798] | +.091 [+.038, +.148] | 31/9/15 |
| run 2, design 55 | .640 | .762 [.712, .809] | +.122 [+.066, +.181] | 40/8/7 |

Per-run tables with precision, recall and the answer's own score: `table_reread_e2e_gemma_run1.md`,
`table_reread_e2e_gemma_run2.md`. Rows: `table_reread_e2e_gemma_run{1,2}.jsonl`.

## What the runs say

- The served table is about .74 over the 100 incidents and about .72 on the 45 that were held out
  while the stage was designed, in both runs. The gain over the answer-grounded table is about +.10
  and its interval is clear of zero in every row.
- The lab that designed the stage scored it .760 on the held-out 45, on one frozen served run
  (`sandbox/table-f1`, `LAB_NOTES_gemma.md`). Two fresh served runs give .72. The lab figure was the
  high end of what the stage does there; .72 is the number to quote for held-out incidents.
- Recall is what moves: .75 → .84. The re-read added a row for a technique retrieval had not
  returned on 61–64 of the 100 incidents (106–111 rows). Precision moves from .57 to .67–.69.
- The re-read decided on all 200 requests. No request fell back to the answer-grounded table.
- It took a median of 11 s a request (90th percentile 21–25 s) with three requests running at once
  on one CPU machine. A request alone was not timed.

## Between the two runs

Run 1 was made before the rule for another domain's techniques. Its tables held 15 rows for mobile
techniques, none of them in the gold labels: 11 had entered because a mobile technique shares its
name with an Enterprise one the answer named (Screen Capture is T1113 and T1513), 4 because the
answer cited a mobile ID. With a re-read, such a technique is now a row only when the answer cites
its ID. Applied to run 1's stored rows that gives .747 over the 100 and .733 on the held-out 45;
run 2 was made with the rule in place.

## Limits

- One model. Nothing here says what the re-read does on another.
- A row the re-read adds from the full list has no retrieved passage behind it. Its ID, name,
  tactic and description come from the technique's own node in Neo4j.
- Parent-level scoring against labels that are all parent techniques. The labels are incomplete: a
  technique the case file does state and the source did not label counts against precision.
- The held-out split has been scored several times across the lab and these runs.
