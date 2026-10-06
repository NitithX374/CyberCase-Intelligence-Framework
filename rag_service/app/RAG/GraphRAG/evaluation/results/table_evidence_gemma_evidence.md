# Case evidence on the MITRE table — the served pipeline on the real-CTI incidents

100 incidents, model `google/gemma-4-26b-a4b-it`. A technique row's evidence is judged against the dataset's own cue for that technique: the exact part of the case file the source's label was written for. Only rows whose technique is in the gold labels can be judged; a row is right when one of its spans shares at least half of the shorter of span and cue.

| evidence | technique rows that have it | of the gold rows, have it | of those, on the cue |
| --- | --- | --- | --- |
| from the re-read | 449 of 454 (99%) | 305 of 305 (100%) | 302 of 305 (99%) |
| from retrieval | 197 of 454 (43%) | 152 of 305 (50%) | 131 of 152 (86%) |
| either | 451 of 454 (99%) | 305 of 305 (100%) | 302 of 305 (99%) |

- Every span of the row is on a cue: re-read 299 of 305 (98%), retrieval 116 of 152 (76%).
- Retrieval is judged on all the sub-queries that returned the technique for 100 of 100 incidents; for the others only the spans the re-read had not already given were kept.
- As a row lists it (the re-read's spans, retrieval's only without them): 305 of 305 (100%) gold rows have evidence, 302 of 305 (99%) include the cue's sentence, 299 of 305 (98%) list nothing else.
- Sub-queries found in the case file by their own words: 240 of 553 (43%).
- Re-read: 1316 sentences copied for 449 kept techniques; 449 of 449 (100%) kept techniques ended with at least one place in the case file.
