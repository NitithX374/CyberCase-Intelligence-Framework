# Case evidence on the MITRE table — what was measured

Each row of the table `POST /query` returns now says which part of the case file it rests on
(`pipeline/case_evidence.py`). This is how well that works, on the 100 real-CTI incidents through
`routers.rag._run_pipeline` with `google/gemma-4-26b-a4b-it`, 2026-10-06.

**The yardstick.** Every gold step in the dataset carries its `cue`: the exact part of the case file
the source's ATT&CK label was written for. All 347 cues are spans of their case file. A technique
row whose technique is in the gold labels is judged right when its evidence lies on the cue for that
technique (the two share at least half of the shorter). Rows for techniques outside the gold labels
cannot be judged.

## Final design, 100 incidents (`table_evidence_gemma_evidence.md`)

| | gold technique rows that have evidence | include the cue's sentence | list nothing else |
| --- | --- | --- | --- |
| as a row lists it | 305 of 305 | 302 (99%) | 299 (98%) |
| re-read alone | 305 of 305 | 302 (99%) | 299 (98%) |
| retrieval alone | 152 of 305 (50%) | 131 of 152 (86%) | 116 of 152 (76%) |

- Of all 454 technique rows, 451 have evidence. Every one of the 449 techniques the re-read kept had
  at least one of its copied sentences found in the case file (1,316 sentences copied).
- A span is a sentence's worth: median 136 characters, 193 at the 90th percentile, about one span a
  row.
- The 11 rows that are not techniques (software, groups) have none: nothing ties them to a sentence.

## The table itself did not move

Parent-level technique F1 of the served table, the same incidents in each run:

| run | gold among retrieved | answer F1 | table F1 |
| --- | --- | --- | --- |
| run 1 (before evidence) | .814 | .703 | .738 |
| run 2 (before evidence) | .821 | .682 | .746 |
| evidence, decomposer asked for sources | .781 | .659 | .729 |
| evidence, final | .819 | .677 | .747 |

Final against run 2: table F1 +.001 [−.022, +.024], retrieval −.002 [−.030, +.027]. On all 100
incidents the final run's table is .745 [.707, .784] against .632 for the answer-grounded table
built from the same retrieval and answer; .741 on the 45 held-out incidents.

## Two ways of getting the sentence, and why a row lists one

**The re-read copies it.** Each shortlist reply already lists the steps of the case file and a
technique for each; it now also copies the sentence that reports the step. For a kept technique the
copies are looked up in the case file and the places found are the evidence. This is the model
saying "this sentence is this technique", and it is the cue's sentence for 99% of the rows.

**Retrieval is traced back.** `retrieve_multi_quota` records which sub-queries returned each
entity, and a sub-query is found in the case file by its own words. This says why an entity was
looked up. It has nothing for half the gold rows (a technique the re-read added without retrieval,
or one only the whole-incident query returned, or a sub-query reworded past finding: 240 of 553
sub-queries are found), and where it has something a wrong sentence comes with it for a quarter of
the rows, because one sub-query returns several techniques.

So a row lists the re-read's evidence, and retrieval's only when the re-read has none for it. On
this run that fallback was needed for 5 technique rows and had something for 2.

## What was tried and dropped: asking the decomposer for its source

The first version had the decomposer copy, after each sub-query, the part of the incident it was
drawn from (`query || source`). The sources were good: all 544 sub-queries came with one, 542 were
found in the case file, and traced through retrieval they included the right sentence for 97% of
the rows that had any. But the instruction changed the queries. Without it the decomposer ends most
sub-queries with an English gloss ("… (system information discovery)"); with it the gloss mostly
went, and the gloss is what anchors a Thai query to the English corpus. The share of gold techniques
retrieval returned fell from .82 to .78 (−.040 [−.073, −.008] against run 2) and the answer's F1
with it. Rows: `table_reread_e2e_gemma_decomposer_sources.jsonl` (99 incidents; one request failed).

The decomposer is back to what it was, byte for byte. Finding a sub-query by its own words costs no
model call and no recall, and finds fewer of them.

## Cost

No model call is added. The shortlist replies are longer by the sentences they copy, and that is
time: the same 12 incidents through the re-read with and without the copying, turn about, took a
median of 29.3 s against 19.1 s, +10.3 s an incident (means 32.6 s and 21.4 s). That evening the
provider was slow throughout; in the 100-incident runs made in the afternoon, three requests at
once, the re-read's median went from 10.7 s to 16.5 s. Either way a request is some 6 to 11 s
longer. With `MITRE_TABLE_EVIDENCE=false` the re-read's prompt is the one it had before, to the
byte, and none of this is spent.

## Limits

- One model, one dataset whose case files were written from the cues. A real case file may report a
  step across several sentences, or twice.
- The cue is one acceptable sentence, not the only one. A row judged wrong can still point at a
  sentence that states the step.
- 149 of the 454 technique rows are for techniques outside the gold labels and are not judged.
- With the re-read off or failed, evidence is the retrieval kind only: half the rows, and less
  exact.
