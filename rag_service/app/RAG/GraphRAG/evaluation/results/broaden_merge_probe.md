# Broaden Merge Probe — does the broaden round add context or reshuffle it?

- 25 samples: every incident where the served agent broadened (`agentic_ablation.jsonl`).
- Retrieval only, reusing the sub-queries and rewrite the agent produced at the time. No LLM calls.
- `replace`: second retrieval under the first pass's budget — what the pipeline did. `merge`: union with the first pass, budget raised one BROADEN_* step.
- Recall = share of the sample's gold ATT&CK IDs appearing in the rendered context (IDs only, so conservative but identical across columns).

| Context | mean gold recall | mean chars |
|---|---|---|
| first pass | 0.761 | — |
| after broaden, replace | 0.759 | 9164 |
| after broaden, merge | 0.837 | 14210 |

- merge vs replace: better on 7, equal on 18, worse on 0
- lost ground against the first pass: replace 6, merge 0

Stored columns re-check the probe against the run it replays (stored first pass 0.761, stored final 0.759); retrieval is deterministic, so a gap here would mean the replay is not faithful.

| sample | first | replace | merge |
|---|---|---|---|
| rcti_002 | 0.60 | 0.40 | 0.60 |
| rcti_006 | 0.75 | 0.75 | 0.75 |
| rcti_016 | 0.33 | 0.67 | 0.67 |
| rcti_019 | 1.00 | 0.67 | 1.00 |
| rcti_023 | 0.67 | 0.67 | 0.67 |
| rcti_024 | 1.00 | 1.00 | 1.00 |
| rcti_026 | 1.00 | 1.00 | 1.00 |
| rcti_030 | 0.67 | 0.67 | 0.67 |
| rcti_034 | 0.80 | 1.00 | 1.00 |
| rcti_040 | 1.00 | 1.00 | 1.00 |
| rcti_041 | 0.67 | 0.67 | 0.67 |
| rcti_047 | 1.00 | 1.00 | 1.00 |
| rcti_065 | 1.00 | 0.75 | 1.00 |
| rcti_070 | 0.33 | 0.33 | 0.33 |
| rcti_073 | 0.83 | 1.00 | 1.00 |
| rcti_079 | 0.67 | 0.33 | 0.67 |
| rcti_090 | 0.40 | 0.40 | 0.40 |
| rcti_097 | 0.67 | 0.33 | 0.67 |
| rcti_098 | 1.00 | 1.00 | 1.00 |
| rcti_100 | 0.80 | 1.00 | 1.00 |
| rcti_046 | 0.67 | 1.00 | 1.00 |
| rcti_054 | 0.67 | 0.67 | 1.00 |
| rcti_060 | 0.83 | 0.67 | 0.83 |
| rcti_063 | 1.00 | 1.00 | 1.00 |
| rcti_064 | 0.67 | 1.00 | 1.00 |
