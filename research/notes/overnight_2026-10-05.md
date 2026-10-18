# Overnight work, 2026-10-04 night to 2026-10-05

The owner went to sleep at about 20:40. Their instruction: talk to Codex about future directions as needed, use
Codex freely, finish pieces with numbers, and take clear positions.

Nothing was merged or pushed to main, and no paid API was called. Codex ran only in empty, read-only folders with
numbers and no case data. Every result below is recorded in `research/analysis_baseline/README.md` under the section
named.

## Finished, with numbers

### 1. NLI cannot replace the rule layer (README "NLI threshold curve: result")
- **English:** no threshold from 0.01 to 0.99 brings NLI alone down to the rule-then-NLI alert rate. Its lowest is
  0.107 and 0.120, against 0.064 and 0.060.
- **Thai:** the threshold that matches the alert rate (fitted in-sample, which favours NLI) loses 13.8 points of
  digit-edit detection [10.4, 17.5].
- **Folding number formats** (thousands commas, Thai digits, times; post hoc): Thai V3 falls from 15 to 1, and the
  alert rate from 0.049 to 0.041, with no detection lost.

### 2. Ellipsis gaps (README "b. Ellipsis gaps: result" and "b, confirmation: result")
- **Checking the full source span, skipped text included,** catches a dropped negation in 97-100% of planted pairs.
  The quoted pieces alone cannot.
- **Contradiction-only rule, confirmed on 240 fresh pairs against criteria fixed in advance:**
  - detection 0.967 in English and 0.917 in Thai;
  - control warnings 0/60 in each language.
- **Real data:** 65 ellipsis quotes in about 5,100 located quotes; 8 have a negation somewhere in the skipped text.

### 3. Summary sentences against their cited claims (README "d. Summary additions: result")
- **One-digit edits** are caught 92-98%. The ID check cannot see them.
- **Certainty strengthening** ("It is confirmed that" on a sentence citing an unconfirmed claim) is caught only when
  the premise carries each claim's status: 7/10 against 4/10 in English, 12/14 against 3/14 in Thai. The counts are
  small.
- **13-18% of real summary sentences are not entailed by their cited claims.** There is no gold. My informal read of
  8 found three kinds: real small additions, NLI over-strictness, and fragments.

### 4. The two-level warning (README "Post hoc: contradiction against neutral ...")
Contradiction is rare on real output and common on planted errors, in all three checks:

| Check | Real output with contradiction | Planted errors with contradiction |
|---|---|---|
| Numeric claims | 6 of 1,612 | 68-82% of digit edits |
| Summary sentences | 1-3% | 78-83% of digit edits |

This supports Codex's two levels: `possible_conflict` and `support_uncertain`. It is post hoc for numbers and
summaries, and confirmed only for ellipsis.

### 5. Statistics fix (README "C against Attribute First failures: paired test")
- C and AF ran on the same items, so exact McNemar replaces Fisher: p = 0.008 (Gemma) and 0.039 (Gemini).
- The paper draft and the book are updated; Drafter confirmed 0 Fisher left in the PDF.
- The paper draft now says "quote-checked claims", defined at first use, so it does not imply the meaning was
  verified.

## Codex conversations (in `docs/thesis/`)
- **`codex_nli_design_review_2026-10-04.md`.** It agreed with "rules for form, NLI for meaning, NLI only warns".
  It disagreed with letting NLI clear `?`, `~` or `%`, which led to the stage 1 rule. It also said to keep NLI flags
  separate from `not_confirmed`.
- **`codex_story_future_2026-10-04.md`.**
  - **Headline:** typography-tolerant quote localisation with explicit limits on semantic support.
  - **Framing:** value checking as numeric-consistency screening; claims-only generation as a short ablation.
  - **Wording:** call the alert rate an alert rate, not a false-positive rate.
  - **Before more sweeps:** mark the real alerts.
  - **Future order:** names, then the V0 semantic hole, a real-case pilot, production NLI in shadow mode, and a
    reviewer study.
- **`docs/audits/2026-10-05-stage3-nli-production-draft.md`.** Codex's engineering spec for production NLI after the
  paper. It is not sent to Coder.

## Running or waiting
- **Wide premises** (SummaC/SeNtLI-style top-3 and ±1 sentence): 11,043 NLI pairs at about 2 s each. Then P2all
  (the whole source). The result section is added when they finish.
- **Stage 1 meaning-mark warning** (`? ~ ≈ ± % <>`, including "50%" read as "50", which passes today): with Coder;
  spec `docs/audits/2026-10-04-meaning-mark-warning-spec.md`.
- **PR #63** (locator holes; rules 2 and 4 reverted at your request): ready for you to merge.

## Decisions waiting for the owner
1. **Merge PR #63.** Then decide the dash between digits; I recommend keeping it refused.
2. **Paper scope for NLI.** Report the numeric layer, ellipsis and summary checks as measured research components
   beside the prototype, or keep only the locator results in the paper.
3. **Mark the check sheets.** Hallucination 50+50, value binding 120 rows; a summary-unit sheet could be added. This
   is the one thing that turns alert rates into precision.
4. **Stage 3** (production NLI) after the paper, and in which order.
5. **Book chapter 1** and the other open Drafter decisions.

## My position
- **Lead the paper with the quote-check policy (decision 1).** It has the strongest and least model-dependent
  numbers.
- **Report the NLI layer as screening with two warning levels.** Use only the confirmed ellipsis rule as a confirmed
  result; the rest is measured but post hoc.
- **Do not add new studies before 15 Oct.** The remaining gap is human marking, not more sweeps.
