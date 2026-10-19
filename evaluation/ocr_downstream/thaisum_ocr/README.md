# OCR errors and the downstream analysis, on Thai crime news (ThaiSum)

This folder is gitignored (`/evaluation/` in the root `.gitignore`). ThaiSum article text belongs to the news outlets.
It may sit here, but it never goes into a tracked file or into a message. Messages and the book carry row indexes, URLs,
lengths, counts and the key facts' categories only.

## Protocol (fixed on 2026-10-02, before any model call; owner approved, cap USD 2.00 including the smoke)

**The question.** This is the advisor's question, priority 1, factual correctness. When a printed-OCR error hits a key
fact in the input, does the analysis:
- carry the error forward;
- restore the right form;
- drop the fact;
- or flag it?

**Scope.**
- The error types come from Typhoon OCR's measured errors on printed pages. Handwriting is out of scope.
- The quote locator is not under test. It checks quotes against the text it receives, by design, so a quote of a
  corrupted form that passes the check is not a finding.

**Seen before this protocol was written.** No model output. Only counts, from `sample_probe.py`:
- 19,869 rows with "อาชญากรรม" in type or tags;
- 10,025 eligible rows, with no duplicate URL;
- in the 100 drawn, every article has at least one candidate. 55 have a number candidate, 24 a place, and 100 an
  other.

### Inputs

- **ThaiSum:** `F:/ThaiSum/thaisum.csv`, with the columns title, body, summary, type, tags and url.
  - **Eligible:** "อาชญากรรม" in type or tags, a non-empty summary, and a body of 1,500-5,000 characters, deduplicated
    by URL.
  - **Draw:** sort the eligible rows by URL, then `numpy.random.default_rng(2026).choice(n, 100, replace=False)`. The
    articles are processed in URL order.
  - **Record:** CSV row index, URL, body length and summary length only.
  - **Normalisation:** body and summary are put in NFC with zero-width characters removed. Whitespace is kept.
- **What the model reads:** the body only. The title is not given, because it often repeats the key facts and would
  undo a deletion.
- **Typhoon error bank:** `../fullpage_bank/verified_bank.json`, the `typhoon` entry. `verify.py` recomputes it without
  the inherited modules.
  - It covers ThaiOCRBench Task=Full-page OCR, 197 printed pages and 285,660 reference characters.
  - Its edits: 3,259 substitutions, 13,297 deletions and 4,886 insertions.
  - It lists all 1,932 substitution pairs with their counts.
  - The older parent-folder modules (`corruption_injector.py`, `factual_spans.py`) are not used.
- **Province list:** the 77 names in `F:/ThaiSum/extract_province.py`.

### Key facts (no new labels; `facts.py`)

- **Tokens:** PyThaiNLP 5.3.7, `newmm`, with whitespace tokens dropped from the word list.
- **Candidate:** 1-4 consecutive words of the body. Its surface is the body text from the first word's start to the
  last word's end, so inner spaces are kept. A candidate qualifies when:
  - it has at least 4 characters and no line break;
  - no word in it is pure punctuation;
  - its first and last words are not PyThaiNLP Thai stopwords;
  - the same surface appears verbatim in the summary.
- **Category,** checked in this order:
  - **number:** the surface contains a Thai or Arabic digit;
  - **place:** after stripping a leading "จังหวัด" or "จ.", it equals a province name;
  - **other:** everything else.
- **Targets:** per article, up to 3, one per category when one exists.
  - Order: number, place, other.
  - Within a category, the candidates are shuffled by the seeded generator, and the first is taken that does not overlap
    an earlier target anywhere in the body and is not a substring of one, nor contains one.
- **Expected size:** about 55 number, 24 place and 100 other targets before the clean filter below. Place cells will
  be small; that is reported, not fixed.

### Arms (fixed before any call)

1. **clean:** the normalised body.
2. **targeted:** every occurrence of each target in the body is corrupted. The same edit is used at every occurrence.
   - **Type,** balanced within each category: half the targets (rounded down) get a substitution and the rest a
     deletion. Substitution targets are drawn by the seeded generator from the targets that can take one. A target
     with no usable pair gets a deletion.
   - **Substitution:** one character of the fact is replaced, using a confusion pair observed in Typhoon's bank.
     - Pairs are drawn by bank count, among the pairs whose source character occurs in the fact.
     - If that character occurs more than once in the fact, one occurrence is chosen uniformly.
     - **Pairs stay in the character's class:** Thai letter or mark to Thai letter or mark (Thai digits excluded), Latin
       letter to Latin letter, and digit to digit within one script.
     - **Why:**
       - 1,991 of the 2,347 substitutions with a Thai source (85%) are Thai to Thai.
       - The cross-class pairs (Thai to Latin, space or punctuation) are almost all single occurrences, the mark of
         Levenshtein misalignment rather than misreading.
       - Spaces and punctuation are not substituted.
   - **Numbers:** substitution touches a digit only, with a digit-to-digit pair the bank contains.
     - The bank does contain them: 92 ASCII digit-to-digit substitutions and 25 Thai digit-to-digit (corrected from 97 by `build.py` before any call; the 97 counted superscripts, which the class rule excludes).
     - Superscripts and other non-ASCII "digits" are excluded.
   - **Deletion:** the fact's text is removed at every occurrence. Deletion is Typhoon's dominant edit (13,297 of
     21,442), though there it removes characters, not whole facts. Removing the whole fact is the severe end of it.
   - **Check:** after corruption, the original form must not occur anywhere in the body. A target whose original still
     occurs is dropped and logged.
   - **Log:** every edit is written to `data/edits.jsonl` with article, offset, original, corrupted, type and category.
3. **realistic (secondary):** the targeted body plus background substitutions over every character outside the target
   occurrences.
   - Each eligible character (one with a class-preserving pair whose source is that character) is substituted with
     probability 0.01141, Typhoon's substitution rate (3,259 / 285,660). The pair is drawn by bank count.
   - The realised rate over all characters is reported. It is lower, because spaces and punctuation are never
     substituted.
   - The background edits are logged too.
   - **It runs only if** the smoke projects all three arms at or below 85% of the cap that remains after the smoke.
     Otherwise only clean and targeted run, and if even those two do not fit, the run stops and is reported. This is a
     mechanical rule, fixed now. The 15% margin is there because `run.py`-style reservations refuse calls near the cap.

All of this is `build.py`, with seed 2026: one generator, used in the order sample, targets, types, edits, background.

### Pipeline

- **Code:** production, `origin/main` at `969d61a1cc01` (it contains bb88875, the claim check before the judgement).
  It is exported with `git archive` to `pinned/969d61a/backend`.
- **Path:** `app.analysis.write.write_trace` (no-grammar reading → claim check → judgement), then
  `app.trace.bind.bound_references`, as `research/analysis_baseline/thai_smoke_pr45.py` does.
  - Language: `case_language` of the bundle, which is Thai for every article.
  - No technical context, so no MITRE gate and no RAG.
- **Model:** `google/gemma-4-26b-a4b-it` with providers `coreweave/bf16`, `nextbit/bf16`, fallbacks off, and
  production's defaults for tokens, thinking and timeout.
- **Asking again:** production's own policy. A reading is asked at most twice on a cap hit or an invalid reply; a
  judgement is asked once more after a whitespace runaway.
- **Records:**
  - every call: stage, provider, stop reason, tokens, USD (provider-reported) and milliseconds;
  - the model's own reading, captured before the claim check, so that the statuses the model wrote are known;
  - the bound trace.
- One run per article per arm.

### Outcomes per target (judge-free; `score.py`)

- **Text:** NFC, zero-width characters removed, whitespace collapsed. Matching is substring matching.
- **Model text:**
  - claim text, summary, party name and role, timeline time and event, and impact descriptions;
  - quotes are not part of it, and are reported separately.
- **Counted targets:** only those whose original form appears in the clean arm's model text for that article. A
  change can then be put down to the corruption.
- **Surfaces:**
  - **R**, the reported surface: summary, parties, timeline, impacts, and the text of claims the model wrote as
    `reported`;
  - **F**, the flagged surface: the text of claims the model wrote with any other status (`suspected`,
    `contradicted`, `not_established`, `unknown`), plus each gap's description and clarification question.
- **Substitution target**, in the corrupted arm, checked in this order:
  1. **mixed:** both the corrupted and the original form are in R;
  2. **propagated:** the corrupted form is in R;
  3. **restored:** the original form is in R;
  4. **flagged:** either form is in F only;
  5. **omitted:** neither form is in R or F.
- **Deletion target:** restored (the original is in R), flagged (in F only), or omitted.
- **Statuses:**
  - "Flagged" uses the statuses the model wrote. The binder's `not_confirmed` demotion is the locator's work, and the
    locator is not under test.
  - **Sensitivity:** the same classification with the bound statuses, where `not_confirmed` counts as non-reported. It
    is reported beside the primary.
- **A failed run** (clean or corrupted) gives no outcome. Its targets are counted as "run failed" and left out of the
  shares.
- **Reported:** counts and shares by type × category and by type, each share with a case bootstrap: 2,000 resamples of
  articles, `default_rng(2026)` fresh for each cell, 95% percentile interval.

### Per-arm measures

- **M2-style verified quotes:** `citations_verified` / `citations_claimed`, pooled.
- **Quotes holding a corrupted form:** in the model's written quotes, and among the verified ones.
- **ROUGE-L F1** of the judgement summary against ThaiSum's reference summary.
  - It uses the LCS over PyThaiNLP `newmm` tokens with whitespace dropped.
  - Each arm gets a mean, and each corrupted arm a paired difference from clean with a case bootstrap.
  - It is a secondary measure.
- **Reliability and cost:** failures by kind, calls to the cap, invalid replies and re-asks (from the call records,
  counted as in `research/analysis_baseline/single_nogrammar.py`), median model seconds per article, and USD.

### Predictions (written before any call; reported whatever comes out)

- **H1:** most character substitutions are restored or propagated, and rarely omitted. Read as: restored + propagated
  + mixed > 50% of the counted substitution targets, and omitted < 20%.
- **H2:** most deleted facts are omitted (omitted > 50% of the counted deletion targets).
- **H3:** flagged is rare in every type (flagged < 10% within each type).

Each is judged on the point estimate, with the interval shown.

### Limits, known now

- **Domain:** news against case files, and ThaiOCRBench pages against news print.
- **No rerun arm:** the clean arm is one sample. "Omitted" therefore includes the facts a second clean run would drop
  anyway, and that base rate is not measured.
- Deleting a whole fact is harsher than Typhoon's character-level deletions.
- One model, one run per arm.

### Order, budget and stops

1. `build.py`: the sample, targets, corrupted bodies and edit log. Its counts are recorded below.
2. **Smoke:** the first 3 articles in URL order × all three arms, cap USD 0.10, concurrency 3. It checks Thai output,
   that quotes bind, and the cost per article and arm. It is rerun as part of the main run.
3. **Main run:** all 100 articles, the arms the projection rule allows, the rest of the USD 2.00 cap, concurrency 8.
4. `score.py`, then a result section here.

**Stop and report** on any of these:
- a harness error;
- more than 10 failures in an arm;
- a projection over the cap;
- a design problem this protocol did not foresee.

Nothing is tuned on outcomes.

## Build and smoke (2026-10-02)

**Build** (`build.py`; `data/build_summary.json`).
- 10,025 eligible rows; 100 drawn.
- Targets: 55 number (27 substitution, 28 deletion), 24 place (12, 12) and 100 other (50, 50). Every target could take
  a substitution.
- 412 target occurrences were edited in the targeted arm.
- No original form survives its edit, and no substituted form already occurred in its clean body.
- Bank, class-preserving substitutions kept: Thai 1,991, Latin 126, ASCII digits 92 and Thai digits 25, over 122
  source characters.
- Realistic arm: 2,369 background substitutions over 223,050 body characters, a realised rate of 0.01062 against the
  bank's 0.01141.
- **Harness fix, before any call:** `run.py` first split `articles.jsonl` with `splitlines()`, which also splits on the
  Unicode line separators inside article text. It now splits on newline only.

**Smoke** (`run_20261001_222406`, USD 0.0371).
- The first 3 articles (r284702, r337255, r5339) × 3 arms, concurrency 3.
- 9 of 9 runs completed, in 18 calls: no re-ask, all HTTP 200, all `end_turn`. The largest output was 11,299 tokens.
- Every summary is in Thai. 113 of 116 quotes bound.
- The model's own reading was captured, so its written statuses are known apart from the binder's demotions.
- **Cost:** USD 0.0041 per article and arm. Projection for 300 runs: USD 1.24. 85% of the remaining USD 1.963 is
  USD 1.668, so **all three arms run**, by the rule fixed above.
- **Main run:** 100 articles × 3 arms, cap USD 1.962, concurrency 8.

## Result (2026-10-02)

**Run.** `run_20261001_223057`, USD 1.3668; USD 1.4039 with the smoke, of the 2.00 cap.
- 298 of 300 runs completed. Two clean-arm judgements failed validation twice. No harness error, no stop.
- Scores: `results/score_20261001_223057.md` (counts only) and `.json` (per target).

**Counted targets:** 134 of 179, 64 substitutions and 70 deletions.
- 41 were left out because the clean arm's model text never stated the fact.
- 4 were left out because their clean run failed.

**Targeted arm, the model's written statuses (primary).** Share [95% case-bootstrap interval]:

| Substitution | n | propagated | restored | mixed | flagged | omitted |
|---|---|---|---|---|---|---|
| all | 64 | 0.28 [0.17, 0.39] | 0.42 [0.31, 0.55] | 0.16 [0.07, 0.25] | 0.00 | 0.14 [0.06, 0.23] |
| number | 19 | **0.74** [0.53, 0.93] | 0.05 [0.00, 0.19] | 0.11 | 0.00 | 0.11 |
| place | 11 | 0.09 | 0.27 [0.00, 0.57] | 0.36 [0.08, 0.67] | 0.00 | 0.27 |
| other | 34 | 0.09 [0.00, 0.19] | **0.68** [0.51, 0.83] | 0.12 | 0.00 | 0.12 |

| Deletion | n | restored | flagged | omitted |
|---|---|---|---|---|
| all | 70 | 0.14 [0.07, 0.22] | 0.03 [0.00, 0.08] | **0.83** [0.75, 0.91] |
| number | 20 | 0.00 | 0.00 | 1.00 |
| place | 11 | 0.18 | 0.00 | 0.82 |
| other | 39 | 0.21 [0.09, 0.33] | 0.05 | 0.74 [0.61, 0.88] |

**The other views.**
- **Realistic arm** (background substitutions added): the same picture.
  - Substitutions: propagated 0.28, restored 0.53, mixed 0.06, omitted 0.12.
  - Numbers propagated 0.68. Deletions omitted 0.86.
- **The bound-status sensitivity** changes one target in one cell, by binder demotion.

**Predictions, judged as fixed.**
- **H1 holds:** restored + propagated + mixed is 0.86 (realistic 0.88), and omitted is 0.14 (0.12).
- **H2 holds:** omitted is 0.83 (0.86).
- **H3 holds:** flagged is 0.00 for substitutions and 0.03 for deletions (0.00 and 0.00).

**What the analysis does with an OCR error in a key fact.**
- **A misread digit is carried forward:** 14 of 19 number substitutions (74%) appear in the analysis with the wrong
  digit, and 1 is restored.
  - Nothing in the text tells the model the number is wrong. It reports the number it received.
- **A misread word is usually corrected:** 23 of 34 "other" substitutions (68%) come back in their right form. The
  model reads through a one-character misspelling of a common word.
  - Province names fall in between: 11 targets, mostly mixed or restored.
- **A deleted fact is gone:** 58 of 70 (83%), and every deleted number (20 of 20). The 14% restored are mostly common
  words the model could write without being told.
- **No error was flagged.** No substituted fact turned up only in a hedged claim or a gap. 2 of 70 deletions did. The
  analysis states the corrupted fact with the same confidence as a clean one.

**Per arm.**

| Arm | Completed | M2 verified quotes | Written quotes holding a corrupted form | ROUGE-L F1 | ROUGE-L − clean |
|---|---|---|---|---|---|
| clean | 98/100 | 1,548/1,580 = 0.980 | - | 0.150 | - |
| targeted | 100/100 | 1,484/1,511 = 0.982 | 119/1,511 | 0.146 | −0.003 [−0.011, +0.005] |
| realistic | 100/100 | 1,445/1,493 = 0.968 | 123/1,493 | 0.139 | −0.012 [−0.019, −0.004] |

- Calls to the cap: 1, 1 and 1. Invalid replies: 2, 5 and 2. Re-asks: 1, 6 and 3.
- Median model seconds per article: 134, 130 and 128. USD: 0.452, 0.463 and 0.452.
- **Quotes keep the corrupted text,** as the locator's definition requires: 119 written quotes in the targeted arm hold
  a corrupted form, and none holds the original. The verified share does not drop. So a quote check cannot catch an
  OCR error: the system is traceable to the text it received, not to the paper.
- **ROUGE-L hardly moves** (−0.003 targeted; −0.012 realistic, which excludes 0). The summary-quality measure misses
  what the fact-level outcome shows, which is the advisor's reason for putting factual correctness first.

**Limits.**
- **No rerun arm:** part of "omitted" may be facts a second clean run would also drop.
- **Small cells:** place is 11 per type, number 19-20.
- **Domain:** news, not case files. The error profile comes from ThaiOCRBench printed pages.
- **Harshness:** whole-fact deletion is harsher than Typhoon's character deletions.
- One model, one run per arm.
