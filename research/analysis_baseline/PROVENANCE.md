# Provenance cards for the chapter 5 numbers (2026-10-01)

**How to recount.** Every number below comes from saved files. No model call is needed.
- `python book_scores.py` recounts every number the book prints and writes `results/book_scores.md` (2026-10-01). Its
  rules are in the `scores_*.py` files, and each card names the file and function. The three scripts below are kept as
  the record of the first recount.
- `python traceability.py` writes `results/traceability.md` (M1-M5 and M7).
- `python provenance_recount.py` writes `results/provenance_recount.txt` (RQ1, M6 and the worked cases).
- `python standard_containment.py` writes `results/standard_containment.md` (M5-std and M4b). On Windows, set
  `PYTHONIOENCODING=utf-8` first: the printout holds "−".

**Rules.**
- A number goes into the book only if its recount matches.
- Each card says who made the labels and lists the known errors of the checker.

## RQ1: the classifier

- **Question.** How well do TF-IDF and XLM-R rank and decide attack-pattern sentences, within one annotation scheme and
  across schemes?
- **Labels.** They are the dataset authors' own.
  - LADDER: Alam et al., RAID 2023, `experiments/LADDER/attack_pattern/data/sentence_classification/test.csv`.
  - MalwareTextDB v1.0: Lim et al., ACL 2017. A sentence is positive when it holds an annotated token.
  - The MalwareTextDB split, by report 23/8/8, is ours, because the corpus has no official split. No label was
    changed.
- **Files.**
  - `experiments/gate_generalization/data_xscheme/*.jsonl`. The sha256 values equal `results_xscheme/FROZEN_MANIFEST.json`,
    so nothing has changed since the freeze.
  - `results_xscheme/<run>/predictions/ft/*.jsonl`.
  - The shipped checkpoint: `results_run2/existing_xlmr_ladder/predictions/ft/ladder_test.jsonl`.
- **Recount, 2026-10-01.** `python book_scores.py`. The rules are `scores_classifier.py:auroc`, `:decisions` and
  `:prf`. The rows are in `scores_classifier.py:classifier`.
  - All 10 cells of the paper's ranking and decision tables match: AUROC, precision, recall and F1, each a mean over
    seeds.
  - The LADDER test labels equal the authors' file: 662 sentences, 331 of them positive.
  - The shipped checkpoint on LADDER test has AUROC 0.917. At 0.50 it gives TP 278, FP 44, FN 53 and TN 287:
    precision 278/322 = 0.863 and recall 278/331 = 0.840.
- **Check by eye.**
  - Every cell reduces to TP, FP and FN. For example, E3 seed 42 on MalwareTextDB test gives TP 307, FP 139 and FN 220
    of 527 positives.
  - The seeds differ: E3's recall on MalwareTextDB is 0.583 for seed 42 against a mean of 0.481.

## M1, traceable reported claims

- **Question.** Of the claims the model presents as reported, how many still point to text that exists in the source?
- **Count.**
  - Numerator: claims with status `reported` after binding.
  - Denominator: those claims plus the claims demoted to `not_confirmed`. The binder demotes a `reported` claim that is
    left with no verified quote, and makes `not_confirmed` from nothing else.
  - Pooled over completed cases.
- **Labels.** The binder (code). No human or model judgement is involved.
- **Files.** `results/<run>.jsonl` and `results/raw_<run>/<case>_<arm>_1.json`, the `bound` trace.

| Run | Value |
|---|---|
| single, cases 51-150 | 1,340/1,383 = 0.969 |
| two calls, cases 51-150 | 1,670/1,693 = 0.986 |
| shipped two calls, cases 151-250 | 1,577/1,614 = 0.977 |
| final system (no grammar), cases 151-250 | 1,601/1,625 = 0.985 |

- **Differences.**
  - Design (two calls − single): +0.019 [−0.012, +0.056], not shown.
  - Decoding (final − shipped): +0.008 [−0.013, +0.042], not shown.
- **Check by eye.** Case 1271: 14 claims were demoted, and in every one the model had wrapped each quote in quotation
  marks (see the binder errors below).

## M2, verified quotes

- **Count.** `citations_verified` / `citations_claimed` from the grounding report of each completed case, pooled.

| Run | Value |
|---|---|
| single | 1,399/1,424 = 0.982 |
| two calls | 1,779/1,803 = 0.987 |
| shipped | 1,649/1,668 = 0.989 |
| final | 1,677/1,704 = 0.984 |

- **Differences.**
  - Design: +0.005 [−0.015, +0.018], not shown.
  - Decoding: −0.004 [−0.015, +0.005], not shown.

## M3, fully traceable cases

- **Count.** Completed cases with no claim demoted to `not_confirmed`, over completed cases.
- **Values.** single 77/100; two calls 86/95; shipped 85/96; final 85/99.

## M4, cited coverage (the main coverage figure)

- **Question.** Of the facts CASIE's annotators marked for the main event, how many does a verified quote point at?
- **Count.** For each case: main-event gold facts whose annotated character span overlaps a verified quote, over the
  case's main-event gold facts. A failed run scores 0. The figure is the mean over cases.
- **Labels.**
  - Facts and spans come from CASIE's annotators.
  - The gold is built by `cases.py`:
    - attack events of type Databreach, Phishing and Ransom with realis Actual;
    - the main event is the one mentioned first;
    - fixed roles;
    - at least 3 facts per case.
  - The quotes come from the binder.
  - Matching is by position, so a difference in wording does not matter.

| Run | Value (completed cases only) | Without stitched quotes |
|---|---|---|
| single | 0.805 (0.805) | not identifiable: single saved no written trace |
| two calls | 0.872 (0.917) | 0.855 |
| shipped | 0.888 (0.925) | 0.888 |
| final | 0.928 (0.938) | 0.926 |

- **Differences.**
  - Design, failures scored 0: +0.066 [−0.009, +0.142], not shown.
  - Design, completed in both: +0.120 [+0.059, +0.180], a difference.
  - Decoding: +0.041 [−0.010, +0.099], and +0.011 [−0.021, +0.046] when both completed. Not shown.
- **Recount.** `python book_scores.py` recomputes it from the bound traces, with the rule `scores_analysis.py:m4` (through
  `citing` and `pointed_at`). It equals the stored per-case figure for every case.
- **Limit.** A quote over a fact shows where the model looked. It does not show what the claim says about the fact.
- **Check by eye.** Case 10049, below.

## M5, mention coverage (the only coverage figure prose has)

- **Count.** A main-event gold fact counts when its normalised words appear as a contiguous phrase in the text the arm
  wrote itself. Quotes are excluded, and a failure scores 0. This is the frozen V0 scorer.
- **Values.**
  - Cases 51-150: prose 0.699, single 0.771, two calls 0.793.
  - Cases 151-250: shipped 0.825, final 0.847.
- **Known bias.** Roles are not checked. A paraphrase or a different spelling earns nothing: "the IAAF's servers" and
  "metadata" both miss.
  - With V3 (the words within one sentence, in any order), two calls − prose is +0.064 [+0.010, +0.114] and two calls −
    single is +0.016 [−0.044, +0.079].
  - On the dev cases, the loosest variant left all three arms level.

## M5-std, stated coverage (the standard version of M5)

- **Question.** Of the main-event facts CASIE's annotators marked, how many does the text an arm wrote itself state,
  under a published containment rule?
- **The standard.**
  - Normalisation: `normalize_answer` of the official SQuAD v1.1 evaluation script (Rajpurkar et al., 2016), copied
    line for line: lower case, remove punctuation, remove a/an/the, collapse whitespace. The same function is in:
    - Hugging Face `evaluate`, `metrics/squad/compute_score.py` ("Official evaluation script for v1.1 of the SQuAD
      dataset");
    - DPR, `dpr/data/qa_validation.py`;
    - KILT, `kilt/eval_downstream.py`;
    - Lost in the Middle, `nelson-liu/lost-in-the-middle`, `src/lost_in_the_middle/metrics.py`.
  - Check: `best_subspan_em` from that last file (Liu et al., TACL 2024, following Kandpal et al. and Mallen et al.). A
    fact is stated when a normalised gold form is non-empty and contained in the normalised text. Exact match is not
    used, because the outputs are long texts.
- **Count.**
  - Gold forms: the article text at each annotated span of the fact. The fact is stated when any form is contained.
  - Text: the arm's own text, as for V0: summary, parties, timeline, claim text with reasoning, impacts and gaps, with
    quotes left out. For prose it is the whole text.
  - Per case: stated main-event facts over the case's main-event facts. A failed run scores 0, and the figure is the
    mean over cases.
- **Labels.** The facts and spans come from CASIE's annotators. The containment rule is code.
- **Files.** `data/cases.jsonl`, `results/<run>.jsonl`, `results/raw_<run>/<case>_<arm>_1.json` (the `bound` trace)
  and `results/raw_<run>/<case>_prose_1.txt`.
- **Recount, 2026-10-01.** `python book_scores.py`, with the rule `scores_analysis.py:m5_std` (through `states` and
  `normalize_answer`).
  - The script first reproduces V0 from the saved texts and compares it with each record's `stated_lead`. All 490
    completed records match; on any mismatch it stops without reporting.
  - No gold form is empty after normalisation: 0 of 776 main-event facts on cases 51-150, and 0 of 832 on cases 151-250.

| Run | M5 mention (V0) | M5-std stated | Chance floor (n) |
|---|---|---|---|
| prose, cases 51-150 | 0.699 | 0.767 | 0.141 (100) |
| single, cases 51-150 | 0.771 | 0.808 | 0.151 (100) |
| two calls, cases 51-150 | 0.793 | 0.833 | 0.159 (95) |
| shipped two calls, cases 151-250 | 0.825 | 0.842 | 0.111 (96) |
| final system (no grammar), cases 151-250 | 0.847 | 0.870 | 0.102 (99) |

- **Differences.**
  - Design: two calls − single +0.025 [−0.037, +0.081], not shown. Two calls − prose +0.067 [+0.016, +0.117], a
    difference. Single − prose +0.041 [−0.004, +0.090], not shown.
  - Decoding (final − shipped): +0.028 [−0.012, +0.068], not shown.
- **Chance floor.** Each case's own text is scored against the gold of the next case (case ids sorted as strings; the
  last wraps to the first). It shows how often the rule credits a fact that belongs to another article.
- **Known limits.**
  - A substring can match inside a word: "data" is contained in "metadata". The floor puts the size of such chance
    matches at 0.102-0.159 of another article's facts.
  - Removing punctuation joins letters: "IAAF's" becomes "iaafs".
  - A longer text contains more, by chance as well as by content. The arms write texts of different lengths.
  - English only: CASIE is English, and no Thai text was scored.
  - No check of meaning or role. The words count wherever they appear, in another role or in a negation.
- **Check by eye, 10049 (two calls).** 7/8 stated, the same as V0. "meta data" is missed because the trace wrote
  "Metadata", which normalises to "metadata".

## M4b, pointed at and stated by the same claim

- **Question.** Of the main-event facts, how many does one claim both point at with a verified quote and state in its
  own words?
- **Count.**
  - A fact counts when one claim holds a verified quote whose position overlaps one of the fact's spans, as in M4, and
    the same claim's `text` states the fact by the M5-std rule. Reasoning is not included.
  - Verified quotes are the bound supporting and contradicting citations, located by repeated `text.find` of the exact
    quote. Overlap is `a < fe and b > fs`.
  - A failed run scores 0, and the figure is the mean over cases. Structured arms only.
- **Labels.** The facts and spans come from CASIE's annotators. The quotes come from the binder, and the statement
  check is the M5-std rule.
- **Files.** As for M4.
- **Recount, 2026-10-01.** `python book_scores.py`, with the rule `scores_analysis.py:m4b` (through `stating`). The same
  code counts M4 by position only. It equals
  `traceability.py` for all four arms: 0.805, 0.872, 0.888 and 0.928.

| Run | M4 cited | M4b cited and stated (completed cases only) |
|---|---|---|
| single, cases 51-150 | 0.805 | 0.624 (0.624) |
| two calls, cases 51-150 | 0.872 | 0.729 (0.767) |
| shipped two calls, cases 151-250 | 0.888 | 0.743 (0.774) |
| final system (no grammar), cases 151-250 | 0.928 | 0.775 (0.783) |

- **Differences.**
  - Design (two calls − single): +0.105 [+0.035, +0.172], a difference. Over the 95 cases completed in both, +0.151
    [+0.090, +0.212], a difference.
  - Decoding (final − shipped): +0.032 [−0.019, +0.088], and +0.012 [−0.030, +0.058] over the 95 cases completed in
    both. Not shown.
- **Reading.** M4 (position only) is the upper bound and M4b (position and statement) the lower bound of "the system
  cites the fact".
- **Limits.**
  - Those of M5-std, applied to one claim's text.
  - A claim that states the fact in other words earns nothing.
- **Check by eye, 10049 (two calls).** 6/8.
  - "the attackers": A-06's quote covers "by the attackers", but its text reads "Unauthorized remote access to the
    IAAF network was identified on 21 February", which leaves the attackers out. Not counted, correctly.
  - "meta data": A-07's quote covers it, but the claim wrote "Metadata". Not counted.
  - The other six facts are pointed at and stated by A-02, A-06 or A-07.

## M6, report preservation (RQ2 v2)

- **Labels.** None. The report's fields are compared with the trace's.
- **Files.** `research/report_fidelity/runs_v2/main/<case>/{trace.json, arm_a|arm_b/run_<k>.json, scores.json}` and
  `summary.json`.
- **Recount.** `python book_scores.py` recounts it from the reports themselves, with the evaluator's claim mapping and
  quote rule: `scores_report.py:rows_by_claim`, `:kept_by_report` and `:identical`. It equals the summary.
  - Arm B (code): 2,601/2,601 claims and 2,709/2,709 quotes; reruns identical for 48/48 traces.
  - Arm A (LLM writer): 2,561/2,601 claims, with all 40 losses in 3 malformed reports; 2,630/2,709 quotes; reruns
    identical for 0/48 traces.
- **Independent check, not the evaluator's code.** A trace quote counts when it is found anywhere in the report.
  - Arm B: 2,709/2,709.
  - Arm A: 2,586/2,709 = 0.955 verbatim, and 2,638/2,709 = 0.974 after NFKC and whitespace normalisation. The
    evaluator's 2,630 is the normalised figure, restricted to the claim's own row.
  - So in Arm A, 52 quotes changed only in spacing or Unicode form, and 71 were cut, extended or dropped.
- **Check by eye.**
  - 10078 A-01: Arm A extended a 22-character quote to 79 characters with words the quote did not hold.
  - 10081 A-05: Arm A cut a 340-character quote down to its last 96 characters.

## M7, reliability and cost

- **Files.** The per-call records in `results/<run>.jsonl`: stage, ms, output tokens and usd. `usd_basis` says whether
  the cost is provider-reported or the worst-case price.

| Run | Failed | Calls to the token cap | Median model seconds per case | USD per case |
|---|---|---|---|---|
| single | 0 | 4 | 92 | 0.0032 |
| two calls | 5 | 25 | 170 | 0.0074 |
| shipped | 4 | 19 | 253 | 0.0067 |
| final | 1 | 4 | 136 | 0.0044 |

- **Model seconds.** They are the sum of a case's call durations. Runs before 2026-10-01 started every task at once, so
  their wall-clock seconds include queueing and are not comparable.

## Binder errors (they affect M1-M4)

From the audit of the held-out quotes:
- **Too strict.**
  - Of 22 dropped quotes, 19 kept every word and failed on formatting.
  - 14 of those are in case 1271, where the model wrapped every quote in quotation marks.
  - The rest are a dropped parenthesis and an ambiguous ellipsis.
- **Too lenient.**
  - A quote with a middle ellipsis passes when its pieces occur in order.
  - 10086 A-05: the model wrote 207 characters, and the binder kept a 719-character span.
  - Removing such stitched quotes lowers M4 by 0.017 for two calls on cases 51-150, and by 0.002 or less on cases
    151-250.

## Worked case: 10049 (M4 and M5)

| Gold fact (role) | Span | Prose mentions | Single mentions | Two calls mention | Two calls cite |
|---|---|---|---|---|---|
| the attackers (Attacker) | 741-754 | yes | yes | yes | A-06 |
| meta data (Compromised-Data) | 786-795 | no | no | no | A-07 |
| 21 february (Time) | 768-779 | yes | yes | yes | A-06 |
| a file server (Victim) | 831-844 | yes | yes | yes | A-07 |
| athlete tues (Victim) | 799-811 | no | yes | yes | A-07 |
| athletes therapeutic use exemption tue applications (Victim) | 243-297 | no | yes | yes | A-02 |
| iaaf servers (Victim) | 308-320 | no | yes | yes | A-02 |
| the iaaf network (Victim) | 721-737 | no | yes | yes | A-06 |
| **Total** | | **3/8** | **7/8** | **7/8** | **8/8** |

- **Single:** it cites 0/8. It wrote one claim with one quote, which covers no gold span.
- **"meta data":** in its own text every arm wrote "metadata", so M5 misses it. M4 still finds it, because A-07's quote
  covers the span.

## Datasets and setup

Facts read from files only. "unknown" means no file states it.

| Dataset | File and sha256 | Source | Licence | How the split or order was fixed |
|---|---|---|---|---|
| LADDER test: 662 rows, 331 positive | The authors' file `experiments/LADDER/attack_pattern/data/sentence_classification/test.csv` (`a0ef974e45d067f2…`). The frozen copy `experiments/gate_generalization/data_xscheme/ladder_test.jsonl` (`34f36790dcb999b7…`) holds the same labels | Alam et al., RAID 2023, "Looking Beyond IoCs: Automatically Extracting Attack Patterns from External CTI" (`experiments/LADDER/README.md`) | unknown: no licence file in `experiments/LADDER` | The authors' released split, copied unchanged (`xscheme_data.py`) |
| MalwareTextDB test: 1,831 rows, 527 positive | `experiments/gate_generalization/data_xscheme/mtdb_test.jsonl` (`bd03d94205f6d071…`). It is built from `data_mtdb/malwaretextdb.jsonl` (`3c3c8940582c4a24…`), which comes from `dataset/MalwareTextDB-1.0.zip` of github.com/statnlp-research/statnlp-datasets (zip sha256 `e5b10851ba7d63a4…`, downloaded 2026-09-26) | Lim et al., ACL 2017, doi:10.18653/v1/P17-1143 | none stated: `malwaretextdb_data.py` records "No license is stated" | 23/8/8 of the 39 reports, drawn once with numpy `default_rng(0)` over the sorted report names and never redrawn (`xscheme_data.py`). The report lists are in `data_xscheme/split.json` (`08c868c063f90a0c…`), and the data files equal `results_xscheme/FROZEN_MANIFEST.json` |
| CASIE cases | `research/analysis_baseline/data/cases.jsonl` (`8993fafe176d9883…`), built by `cases.py` from `F:/CASIE` at commit `2c8beef56d48e8de6599891c6a5e0e5f0d82e20c` (`data/manifest.json`) | CASIE, Satyapanich et al. (the book's `satyapanich2020`), 1,000 annotated articles | unknown: no licence file in `F:/CASIE` | See the CASIE selection notes below the table |
| RQ2 v2 traces | `research/report_fidelity/runs_v2/main/` (folder digest `fc51a7b0c1ede6df…`, `summary.json` `0a8b7b9c5ac09605…`) | Our own: the two-call traces of the analysis and the reports written from them | not applicable | Main cases 51-100 of the analysis sample, 1137 first and 10032 last. A case whose analysis failed is a trace failure and is not replaced: 1056 and 10238. 48 of 50 are scored (`research/report_fidelity/PROTOCOL_V2.md`, `340ae77c34df4629…`) |

**CASIE selection** (`cases.py`):
- **Which facts count.**
  - Attack events of subtype Databreach, Phishing or Ransom, with realis Actual.
  - The main event is the one mentioned first.
  - The 12 roles are fixed.
  - A fact is dropped when it is shorter than 4 characters, or when it is a single common word.
  - A case needs at least 3 main-event facts.
- **Which articles.** 155 articles used in earlier studies are excluded, which leaves 370 eligible.
- **Order.** The eligible articles are shuffled once with numpy `default_rng(2026)`. The first 3 are the pilot and the
  next 330 the main sample.
- **The two samples.**
  - Cases 51-150 are `main[50:150]`: 100 cases, 776 main-event facts, a median of 6 per case (3 to 32).
  - Cases 151-250 are `main[150:250]`: 100 cases, 832 facts, a median of 7 (3 to 32).

**Setup.**
- **Model.** `google/gemma-4-26b-a4b-it` through OpenRouter. The providers are `coreweave/bf16` and then
  `nextbit/bf16`, through `CASE_ANALYSIS_PROVIDERS` (README protocols, `PROTOCOL_V2.md`).
- **Budget of one call** (the pinned `app/llm/settings.py`):
  - output 32,608 tokens plus thinking 8,192, so at most 40,800 tokens;
  - context 128,000 and input 80,000;
  - timeout 120 s. The RQ2 Arm A writer has 300 s.
- **Prices.**
  - The worst case is USD 0.10 per million input tokens and USD 0.30 per million output tokens (`run.py`,
    `PROTOCOL_V2.md`).
  - A call uses the provider-reported cost when there is one. Each call record states which (`usd_basis`).
- **Caps and spend.**
  - `main_20260930_020141`: cap USD 1.85, spent 1.4498.
  - `main_20260930_062138`: cap 2.10, spent 1.8317.
  - `main_20260930_193646`: cap 1.20, spent 0.441, or 0.455 with its pilot.
  - RQ2 v2: cap 0.85 for the dry run and the main run together, spent 0.430.
- **Commits.**
  - 1e29bd3, the analysis harness: `pinned/1e29bd3/backend`, which runs every analysis configuration.
  - 8750cbc, production (origin/main after PR #43).
  - 4aa8b18, the report code: `pinned/4aa8b18`, with `report_code` `4aa8b18ba61c3f94738169d5f54d12d8f480a622` in
    `summary.json`.
- **Seeds.**
  - Bootstrap: 2026.
  - Classifier fine-tuning: 42, 7 and 123 (the `results_xscheme` run names). TAPT: 42 (`tapt_mlm.py`).
  - CASIE order: 2026.
  - MalwareTextDB split: 0.
  - The samples drawn for the owner: 2026.

## Quote corruption: grammar with the layout stated (for 5.4.3)

- **Question.** Does grammar-constrained decoding, combined with the JSON layout stated in the instruction, change the
  characters of the quotes the model writes?
- **Rule.** A written quote is corrupted when it holds a character in U+0000-U+001F. No quote in any arm holds a tab, a
  newline or a carriage return, so ordinary layout characters never trigger it.
- **Labels.** None. The rule is code.
- **Files.**
  - The quotes the model wrote: the `reading` in `results/raw_screen_main_20260930_153526/` and
    `results/raw_screen_main_20260930_205044/`, and the `written` trace in `results/raw_main_20260930_193646/`.
  - Recount: `python quote_corruption.py` (`b6085e70247d92e6…`) writes `results/quote_corruption.txt`
    (`727c539552d48720…`).

| Arms | Written quotes holding a control character |
|---|---|
| Grammar and stated layout: template_reorder, Q1 g_template_reorder_noesc, Q2 g_template_shipped_noesc | 94 of 1,404 (52/481, 24/491, 18/432) |
| No grammar: the screen's nogrammar arm and the 100-case confirmation | 0 of 2,221 (0/517, 0/1,704) |
| Grammar without the stated layout: the screen's shipped arm | 0 of 442 |
| gpt-oss-20b | 0 of 342 |

- **Correction.** README "Quick check: result" gives the no-grammar row as 0 of 2,194. That sum takes the 517 written
  quotes of the screen's nogrammar arm, plus the confirmation's 1,677 verified quotes instead of its 1,704 written
  ones. Counted on written quotes, the row is 0 of 2,221. The number of corrupted quotes is 0 either way.
- **Check by eye.** One example from each arm of the first row: its first corrupted quote, in case order. In each, the
  quote's high byte is lost.
  - template_reorder, case 10035, A-03: the model wrote "FSB agents \x14 Igor Suschin", where the source has "FSB
    agents — Igor Suschin" (U+0014 for U+2014).
  - Q1, case 10059, A-01: "Stuart Kettell \x12 owner of audio-visual", where the source has "Stuart Kettell − owner of
    audio-visual" (U+0012 for U+2212).
  - Q2, case 1088, A-02: "millions of users\x19 passwords", where the source has "millions of users’ passwords"
    (U+0019 for U+2019).
- **Limits.**
  - The mechanism is unknown. The raw response text was not saved, so it cannot be told whether the model or the
    serving layer wrote the control character.
  - Each screen arm has 30 cases, and the arms were not run at the same time.

## Corrections made while recounting

- **M3 for two calls on cases 51-150 is 86/95.** In conversation I gave 87/95; that count used claim type `reported`
  rather than status, which is the fixed definition.
- **The M4 design interval here is [−0.009, +0.142].** The held-out section gives [−0.005, +0.145] from `bootstrap.py`.
  The point estimate and the reading are the same; only the resampling code differs.
- **Model seconds replace wall-clock seconds,** as M7 explains.
