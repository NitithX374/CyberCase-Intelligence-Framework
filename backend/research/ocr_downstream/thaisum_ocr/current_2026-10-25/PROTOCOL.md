# OCR errors and the downstream analysis, re-run on the current backend (protocol, 2026-10-25)

Supplementary measurement for the thesis book's Appendix A (Table A-1), so that the appendix describes the system as it
is now. Not for the paper. The 2026-10-02 protocol and its results are in `../README.md`; everything not changed here is
as written there.

ThaiSum article text belongs to the news outlets. It never goes into this file, a message or the book: counts, ids,
lengths and categories only. The raw traces and run records (`results/raw_*/`, `results/run_*.jsonl`) hold article
text and are kept out of git by `.gitignore` in this folder; the `score_*.md` and `score_*.json` files hold none.

**Fixed on 2026-10-25 at 06:06 local time (2026-10-24 22:06 UTC), before any model call of this re-run,** with the
owner's decisions of 2026-10-25 (sample, cap, where it runs, thinking, stop rules, predictions). Seen before it was
fixed: no output of the current backend on these articles, other than a dry run against a local stub whose replies are
fake (below). The 2026-10-02 outcomes for the same articles are known (they are in the book).

## Question

Unchanged: when a printed-OCR error hits a key fact in the input, does the analysis carry the error forward, restore
the right form, drop the fact, or flag it? Now asked of the current backend.

## Sample (owner's decision: the full original sample)

- **All 100 articles** of `../data/articles.jsonl`, in file order. That is the order of `../data/sample.json` and the URL
  order the 2026-10-02 run processed (checked: same 100 rows, same order, sorted by URL). The ids are written to each
  run summary (`article_ids`).
- Same bodies, same targets, same edits (`../data/edits.jsonl`), same three arms (`clean`, `targeted`, `realistic`),
  same key-fact definitions (`../facts.py`). Nothing is rebuilt: `build.py` is not run again.
- **Targets** (as in `../data/build_summary.json`; at most one per category per article, so the article count equals
  the target count):

  | Category | Articles with a target | Substitution | Deletion |
  |---|---|---|---|
  | number | 55 | 27 | 28 |
  | place | 24 | 12 | 12 |
  | other | 100 | 50 | 50 |
  | all | 100 | 89 | 90 |

- **Cells after the clean filter** in the 2026-10-02 run: 134 counted targets; substitution number 19, place 11,
  other 34; deletion number 20, place 11, other 39. The number-substitution cell behind the book's "14 of 19 (74%)" is
  19 there and will be about that size here, depending on what the clean arm states.

## Arms

Unchanged (`clean`, `targeted`, `realistic`, the bodies already in `articles.jsonl`). The 2026-10-02 rule that runs the
realistic arm only if the smoke projects all three arms within 85% of the remaining cap is kept (see Budget).

## Pipeline: what runs

- **Where:** inside the running `cybercase-backend` container (owner's decision), so that units are cut by SaT on the
  GPU as in production. The container's code is the checkout's `backend/app`, mounted at `/app/app`: main at
  `f0fcf37b59244539a388c3a6255b658ad5e54abf`, with no uncommitted change under `backend/app` (checked on the host on
  2026-10-25). The container has no `git`, so the commit and the image id
  (`sha256:e7ea0110390bac0a6e328f7773d5816173d33b06e435024c8f6f6e37cfa8f90f`) are passed by hand to `run_current.py`
  (`--code-commit`, `--image-id`) and stored in the run summary. Python 3.11.17, torch 2.11.0+cu128, wtpsplit 2.2.2.
  - The harness, `../data/` and `../facts.py` are copied into a fresh `/tmp/ocr_rerun/thaisum_ocr/` in the container
    with `docker cp`; `CYBERCASE_BACKEND=/app` tells the harness where the code and `models/` are. After the run the
    results are copied back to `results/` here and `/tmp/ocr_rerun/` is removed from the container.
  - The running server is not touched: its settings are not changed and it is not restarted. The run is a separate
    process started with `docker exec`.
- **Path:** `app.analysis.write.write_trace(sources=..., language=..., config=...)` called directly, then
  `app.trace.bind.bound_references(trace, [])`, which is what `analysis/pipeline.py` does after it
  (`write_analysis`, `bind_to_case`). No preflight assessment, no follow-up, no MITRE gate, no technical context, no RAG
  call (`MITRE_GATE_MODE=never`, `RAG_SERVICE_URL` at a closed local port, and nothing on this path calls it).
  - Bundle: one source, `source_id="SRC-1"`, `source_kind="narrative"`, text = the arm's body; revision 1.
  - Language: `case_language(bundle)`, Thai for every article.
- **What `write_trace` now does,** and how it differs from the 2026-10-02 run (pinned `969d61a`):
  1. **Reading selects source units; it writes no quotations.** The backend cuts the source into exact-offset units
     (`sources/evidence.py`), sends them with local IDs `U001`, `U002`, ..., and the reading writes claims only, each
     selecting supporting/contradicting unit IDs. The backend binds the IDs to the original text
     (`analysis/reading_sources.py`, `trace/evidence_binding.py`). An ID that does not resolve is kept as an invalid
     reference with its reason. Old: the reading wrote claims with copied quotations plus parties, timeline and impacts,
     and a quote locator checked the quotations.
  2. **Four structural rules decide which claims go on** (`trace/claim_validation.py`, `assessment_blocker`): a claim
     needs a resolved supporting unit (`no_resolved_source`), no unresolved supporting reference
     (`unresolved_source_reference`), no contradicting source (`conflicting_source`), and a status of `reported` or
     `unknown` (`claim_uncertain`). Claims that fail stay in the trace but reach neither Judgement nor the views. Old:
     Judgement received every claim, hedged ones included.
  3. **Judgement gets the checked claims only**: claim ID, type, text, status and the cited unit text. No case source,
     no technical context. It writes the summary, each sentence ending in claim-ID brackets, and gaps, and is asked for
     at most `summary_sentence_limit` sentences (one per three claims, 2 to 8). Old: Judgement received the case source
     text and the whole reading, and had no sentence limit.
  4. **Parties, timeline and impacts come from a separate views call** (`analysis/views.py`) over exactly the claims
     Judgement receives (ID and text only), run in parallel with Judgement. If it fails, the trace records the failure
     and empty views, and the run still completes. Old: the reading call wrote them directly from the source.
  5. **The claim verifier is disabled** (owner's decision), for these runs only, through the environment of the
     `docker exec` process: `CLAIM_NLI_PATH` and `CLAIM_SELECTOR_PATH` point into a folder that does not exist. In
     production its verdict is a label: it never enters a prompt and filters nothing (`write.py` sends Judgement and the
     views the claims as they were before the check, and the check only sets `semantic_grounding`), so it cannot change
     any text the scorer reads. Confirmed from the code and in the dry run: `load_verifier()` builds the selector first,
     `build_selector()` finds no `model.safetensors` and raises `NliUnavailable` before importing
     `sentence_transformers`, so `load_nli()` (mDeBERTa) is never reached; `analysis/claim_gate.py` catches
     `NliUnavailable`, logs it, and marks every claim `unassessed` with `verifier_unavailable`, or its structural reason.
     The analysis continues. `run_current.py` refuses to start if either folder exists.
- **Model and provider settings** (production values: `docker-compose.yml` backend environment, the root `.env` it
  interpolates, and `backend/app/config.py` / `llm/settings.py`; the running container was checked with
  `docker inspect` on 2026-10-25):

  | Setting | This re-run | Production source | 2026-10-02 run |
  |---|---|---|---|
  | Model | `google/gemma-4-26b-a4b-it` | compose default, `CASE_ANALYSIS_MODEL` | same |
  | Providers, fallbacks | `nextbit/bf16`, `coreweave/bf16`, fallbacks off | compose default `CASE_ANALYSIS_PROVIDERS` | `coreweave/bf16`, `nextbit/bf16` (order reversed) |
  | Server | OpenRouter Messages API | `CASE_ANALYSIS_SERVER` default | same |
  | Reading thinking | **0 (off)** | root `.env` `CASE_READING_THINKING_TOKENS=0`, in the running container (compose default 8,192) | **8,192** |
  | Judgement thinking | **2,048** | root `.env` `CASE_JUDGEMENT_THINKING_TOKENS=2048`, in the running container (compose default 8,192) | **8,192** |
  | Views | thinking off, temperature 0, at most 4,096 output tokens, 60 s deadline | `AnalysisPipelineConfig.for_views`, `views.py` | no views call |
  | max_tokens (reading, judgement) | 32,608 and 34,656 (32,608 + thinking) | `AnalysisPipelineConfig` defaults | 40,800 both |
  | Timeout | 120 s per call (views 60 s) | defaults | 120 s |
  | Asking again | invalid or truncated reply asked once more (2 attempts) in every stage; one transport retry after 2 s on a dropped connection or HTTP 429/5xx | `llm/request.py` | reading twice; judgement once more after a runaway |
  | Temperature | not sent (views: 0) | production | not sent |

  **Thinking differs from the 2026-10-02 run** (owner's decision to use what the running stack uses): reading 0 and
  judgement 2,048 now, 8,192 and 8,192 then. A difference between the two runs may therefore come from the thinking
  budget as well as from the pipeline changes above; the re-run does not separate the two. The values are set
  explicitly in `run_current.py` (`MODEL`, `PROVIDERS`, `READING_THINKING_TOKENS`, `JUDGEMENT_THINKING_TOKENS`); the
  environment's thinking knobs are not read.
- **Sentence segmenter:** SaT `sat-3l-sm` at revision `137da054`, threshold 0.025, on the GPU (`cuda:0`), as production.
  `run_current.py` is started with `--expect-segmenter sat` and refuses to start if `segmenter_identity()` is anything
  else (the crfcut fallback); the identity and the SaT device are stored in the run summary.
- **Records,** as in the old harness: every call's stage, provider, stop reason, tokens, USD (provider-reported when the
  reply carries it, else the worst-case price), milliseconds, requested max_tokens and thinking setting; the model's own
  reading, judgement and views replies (captured before binding); the bound trace. One run per article per arm.

## Outcomes per target (judge-free; `score_current.py`)

Unchanged from `../README.md` (normalisation, substring matching, the clean filter, the outcome order, the bootstrap),
with the fields mapped to the current trace as follows. Scored on the host, where PyThaiNLP is 5.3.7, the version
`build.py` used.

| Old field (pinned trace) | Current field | Surface | Note |
|---|---|---|---|
| `summary` | `summary` with every `[A-nn, ...]` bracket replaced by a space | R | Brackets are new; 1 of the 298 old summaries had one. Removed so a claim ID cannot match a number fact. |
| `involved_parties[].name`, `.role` | `involved_parties[].name`, `.role` (role may be null: empty) | R | **Provenance changed:** from the views call over checked claims, not from the reading over the source. |
| `timeline[].time`, `.event` | `timeline[].time` (may be null: empty), `.event` | R | Same provenance change. Old `time` was required; now a combined, nullable date/time. |
| `impacts[].description` | `impacts[].description` | R | Same provenance change. |
| `claims[].text`, status `reported` | `claims[].text` where the status the model wrote is `reported` | R | Written status from the captured reading reply. |
| `claims[].text`, other statuses | `claims[].text` where the written status is `suspected`, `contradicted`, `not_established` or `unknown` | F | Same set of statuses as before. |
| `gaps[].description`, `.clarification_question` | same | F | |
| bound status (sensitivity) | `claims[].epistemic_status` after binding; `not_confirmed` counts as non-reported | R/F | `not_confirmed` now means a `reported` claim with no resolved unit, not an unlocated quote. |

- **Model text for the clean filter:** the summary (brackets removed), parties, timeline, impacts and all claim text,
  as before.
- **Where the old category cannot be reproduced exactly:**
  1. **R is built differently.** Old parties, timeline and impacts were written from the source; now they are written
     from checked claims only. A fact that no checked claim states can no longer reach R through the views.
  2. **Hedged claims no longer feed R.** A claim the model wrote as `suspected`, `contradicted` or `not_established`
     fails `claim_uncertain` and reaches neither the summary nor the views. In the old run such a claim was sent to
     Judgement and its fact could appear in the summary. "Flagged" (fact only in F) is defined the same, but the route
     from F into R is now closed for those statuses. `unknown` claims still pass and can feed R, as before.
  3. **The summary is shorter by design** (`summary_sentence_limit`), so fewer facts may reach R through it; a rise in
     "omitted" can come from this rather than from the OCR error. Reported, not corrected.
  4. **M2 verified quotes cannot be reproduced.** The reading writes no quotations and the trace keeps no
     `citations_claimed` / `citations_verified` counters. Reported instead: unit IDs the model selected, citations the
     backend bound, and invalid references by reason (`unknown_unit`, `stale_id`, `duplicate_id`, ...).
  5. **"Written quotes holding a corrupted form" no longer exists.** Bound citations are the source's own text by
     construction, so "bound citations holding a corrupted form" is reported but is not a finding: it is the text the
     model was given.
  6. **Calls to the cap** are counted against each call's own max_tokens (32,608 reading, 34,656 judgement, 4,096
     views), not the old single 40,800.
  7. **Thinking budgets differ** (above).
- **A failed run** (clean or corrupted) gives no outcome, as before. **A failed views call does not fail the run:**
  that run is scored as the system produced it (empty views), and the number of runs with failed views is reported per
  arm.
- **ROUGE-L F1** of the summary (brackets removed) against ThaiSum's reference summary, PyThaiNLP `newmm`, as before.
- **Per arm, added:** views status counts, claims / claims the model wrote as hedged / claims judged, and the verifier
  verdicts (expected: all `unassessed`).

## Predictions

H1, H2 and H3 of `../README.md`, unchanged, with the same thresholds, judged on the point estimate with the interval
shown. None is added.

## Budget

- **Cap (owner's decision): USD 2.00 in total, the smoke included.** The smoke has its own cap of USD 0.10.
- **Estimate** (`estimate_cost.py`, no model call; from the 2026-10-02 run's provider-reported usage):
  - Old run, 100 articles x 3 arms: 610 calls, **USD 1.367** (USD 0.0046 per run). Provider-reported cost was 0.975
    times the list price used for the cap (USD 0.10 per M input, 0.30 per M output).
  - Old per-call means (provider tokens): reading in 1,074, out 8,722 of which thinking 5,284; judgement in 6,257, out
    4,132 of which thinking 3,074.
  - Current reading request: 1.55 times the old one in o200k tokens (3,007 against 1,945 mean; counted on the host with
    crfcut units, SaT units will differ slightly), about 1,700 provider tokens. Input is a small share of the cost.
  - Per run now: reading about 3,400 output tokens with no thinking (old visible output, an upper bound since it
    included quotations and the three views); judgement about 800 visible plus about 2,000-3,000 thinking (budget 2,048,
    which Gemma does not always keep); views about 1,400 input and 1,000-1,500 output. About USD 0.0029 per run (upper
    about 0.0041), plus 2-3% re-asks.
  - **300 runs: about USD 0.90 (upper about 1.26).**
  - Worst case the cap reserves per call: reading about USD 0.010, judgement about 0.0105, views about 0.0013; at
    concurrency 8 up to about USD 0.09 is reserved at once.
- `run_current.py` keeps the old hard cap: before each call it reserves the call's worst case (input tokens x input
  price + max_tokens x output price); if spent + reserved + worst case would pass the cap, the call is refused, the run
  is recorded as stopped by the budget, and every later run is skipped. HTTP 402 stops it too. It refuses to start
  without `--cap-usd` and `--confirm-spend`.

## Order and stops

1. **Smoke:** the first 3 articles x 3 arms, cap USD 0.10, concurrency 3. Check Thai output, that units bind, that the
   views complete, that every verdict is `unassessed`, that SaT on the GPU cut the units, and the cost per article and
   arm. It is rerun as part of the main run.
2. **Projection rule (mechanical, as in 2026-10-02):** if the smoke projects all three arms for 100 articles at or below
   85% of the cap left after the smoke (USD 2.00 minus the smoke's spend), all three arms run. Otherwise only clean and
   targeted run; if even those two do not fit, stop and report.
3. **Main run:** all 100 articles, the arms the rule allows, the rest of the cap, concurrency 8. Only after the owner
   says to go on.
4. `score_current.py`, then a result section appended to this file (counts only).

**Stop and report** (the 2026-10-02 rules, for 100 articles): a harness error; more than 10 failed runs in an arm; a
projection over the cap; a design problem this protocol did not foresee (for example a verdict other than
`unassessed`, which would mean the verifier was not disabled). `run_current.py` enforces the first two and the cap.
Failed views calls are counted and reported, not a stop. Nothing is tuned on outcomes.

## How it is run

On the host, Git Bash, from the repository root (`MSYS_NO_PATHCONV=1` keeps `/tmp` paths as written):

    MSYS_NO_PATHCONV=1 docker exec cybercase-backend mkdir -p /tmp/ocr_rerun/thaisum_ocr
    MSYS_NO_PATHCONV=1 docker cp backend/research/ocr_downstream/thaisum_ocr/data cybercase-backend:/tmp/ocr_rerun/thaisum_ocr/data
    MSYS_NO_PATHCONV=1 docker cp backend/research/ocr_downstream/thaisum_ocr/facts.py cybercase-backend:/tmp/ocr_rerun/thaisum_ocr/facts.py
    MSYS_NO_PATHCONV=1 docker cp backend/research/ocr_downstream/thaisum_ocr/current_2026-10-25 cybercase-backend:/tmp/ocr_rerun/thaisum_ocr/current_2026-10-25
    MSYS_NO_PATHCONV=1 docker exec -w /app -e CYBERCASE_BACKEND=/app \
        -e CLAIM_NLI_PATH=/tmp/ocr_rerun/no_verifier/nli_mdeberta -e CLAIM_SELECTOR_PATH=/tmp/ocr_rerun/no_verifier/source_selector_mpnet \
        cybercase-backend python /tmp/ocr_rerun/thaisum_ocr/current_2026-10-25/run_current.py \
        --articles 3 --cap-usd 0.10 --concurrency 3 --expect-segmenter sat --confirm-spend \
        --code-commit f0fcf37b59244539a388c3a6255b658ad5e54abf --image-id sha256:e7ea0110390bac0a6e328f7773d5816173d33b06e435024c8f6f6e37cfa8f90f
    MSYS_NO_PATHCONV=1 docker cp cybercase-backend:/tmp/ocr_rerun/thaisum_ocr/current_2026-10-25/results/. backend/research/ocr_downstream/thaisum_ocr/current_2026-10-25/results/
    MSYS_NO_PATHCONV=1 docker exec cybercase-backend rm -rf /tmp/ocr_rerun

The main run is the same `docker exec` without `--articles 3`, with `--cap-usd` set to USD 2.00 minus the smoke's
spend and `--concurrency 8`. The OpenRouter key is the container's own `OPENROUTER_CYBERCASE`. Scoring, on the host
from `backend/`: `PYTHONPATH=. python research/ocr_downstream/thaisum_ocr/current_2026-10-25/score_current.py --run run_<stamp>`.

## Dry run (2026-10-25, no network, FAKE output)

`dryrun_stub.py` replaces the provider transport (`app.llm.request.transport`) with an `httpx.MockTransport` whose
replies are built from the request (claims copy unit text; one claim selects a unit that does not exist; one views item
names an unknown claim). Every non-loopback socket connect and name lookup raises. Run on the host, on the first 2
articles x 3 arms, output written outside the repository (the scratchpad), then scored:

- 6 of 6 runs completed; 18 stub calls (reading, views and judgement for each run); 0 network attempts.
- Every claim `unassessed`: 54 `verifier_unavailable`, 6 `claim_uncertain`, 6 `no_resolved_source`; the selector
  reported `selector_asset_missing:model.safetensors` and the NLI model was never loaded.
- The invalid unit was recorded as `unknown_unit` and its claim demoted to `not_confirmed`; the unknown-claim views item
  was dropped and counted.
- The hard cap was checked with the stub at USD 0.012: the run stopped when the next worst case would pass the cap and
  skipped the rest.
- Segmenter on the host: `crfcut:pythainlp=5.3.7` (the host has no `wtpsplit`; the real runs are in the container).
- `score_current.py` produced every table. The outcome shares mean nothing: the stub copies the source. The text-bearing
  dry-run files were deleted.

## Smoke (2026-10-25, `run_20261024_220953`, USD 0.0232)

- Run in `cybercase-backend` by `docker exec`, 22:09-22:18 UTC; code `f0fcf37b`, image `sha256:e7ea0110...`, both
  recorded in the summary. `/tmp/ocr_rerun/` was removed from the container afterwards; the server was not touched.
- **Segmenter:** `sat:sat-3l-sm@137da054...:threshold=0.025:wtpsplit=2.2.2`, SaT on `cuda:0` (the harness checks
  both and was started with `--expect-segmenter sat`).
- The first 3 articles (r284702, r337255, r5339) x 3 arms, concurrency 3: **9 of 9 runs completed**, 29 calls, all
  HTTP 200, all `end_turn`, all on NextBit. No call reached its cap.
- **Re-asks:** 2, both views calls in the targeted arm (one reply was not valid JSON, one carried a `$defs` key); each
  was asked once more and completed. No reading or judgement re-ask. No run had failed views.
- Every summary is in Thai. Every claim bound its units: 9 to 16 claims per run, all written `reported`, no invalid
  reference, every claim judged. Every verdict `unassessed: verifier_unavailable` (117 claims).
- **Judgement thinking passes its budget:** 3,764 to 8,023 thinking tokens per call (mean about 5,600) against a budget
  of 2,048. Judgement is 68% of the cost. Three judgement calls took 130-177 s, longer than the 120 s timeout, and still
  completed (the timeout bounds waiting between bytes, not the whole call).
- **Cost:** USD 0.00258 per run (reading 0.00052, judgement 0.00176, views 0.00030). Median 139 s per run.
- **Projection rule:** 300 runs x USD 0.00258 = USD 0.77. 85% of the USD 1.977 left after the smoke is USD 1.680, so
  **all three arms run**, by the rule. Main run, if the owner says go: 100 articles x 3 arms, cap USD 1.97,
  concurrency 8.

## Result (2026-10-25, `run_20261024_222324`, USD 0.761; USD 0.784 with the smoke, of the 2.00 cap)

- Run in `cybercase-backend`, 22:23-23:58 UTC, SaT `sat-3l-sm` on `cuda:0`, code `f0fcf37b`, image `sha256:e7ea0110...`.
  No stop rule fired. `/tmp/ocr_rerun/` was removed from the container afterwards.
- **300 of 300 runs completed:** clean 100 (USD 0.252), targeted 100 (USD 0.254), realistic 100 (USD 0.255). 957 calls,
  all HTTP 200, all `end_turn`, all on NextBit, none to its cap.
- **Views failed in 30 runs** (clean 6, targeted 15, realistic 9): 26 gave no valid reply in two attempts
  (`case_views_invalid`: invalid JSON, or a `$defs` key), 4 hit the 60 s views deadline. Those runs were scored as the
  system produced them, with empty views.
- **Re-asks:** reading 6, judgement 3, views 49 (51 views replies were not valid JSON and 25 carried `$defs`).
- **Judgement thinking:** configured budget 2,048; used 2,306 to 10,121 tokens per call (median 5,050). Judgement was
  65% of the cost. Reading and views ran without thinking.
- Verifier verdicts: every claim `unassessed` (`verifier_unavailable`, or a structural reason for 9 claims). No invalid
  unit reference in any run.
- **Clean filter:** 155 of 179 targets counted (75 substitutions, 80 deletions); 24 left out because the clean arm's
  model text never stated the fact; none for a failed clean run.
- **Targeted arm, the model's written statuses (primary).** Count (share [95% case-bootstrap interval]):

  | Substitution | n | propagated | restored | mixed | flagged | omitted |
  |---|---|---|---|---|---|---|
  | all | 75 | 26 (0.35 [0.24, 0.46]) | 39 (0.52 [0.41, 0.63]) | 2 (0.03 [0.00, 0.07]) | 0 (0.00) | 8 (0.11 [0.04, 0.18]) |
  | number | 22 | 19 (0.86 [0.70, 1.00]) | 0 (0.00) | 1 (0.05 [0.00, 0.15]) | 0 (0.00) | 2 (0.09 [0.00, 0.25]) |
  | place | 11 | 3 (0.27 [0.00, 0.56]) | 6 (0.55 [0.25, 0.86]) | 1 (0.09 [0.00, 0.30]) | 0 (0.00) | 1 (0.09 [0.00, 0.30]) |
  | other | 42 | 4 (0.10 [0.02, 0.19]) | 33 (0.79 [0.65, 0.90]) | 0 (0.00) | 0 (0.00) | 5 (0.12 [0.03, 0.22]) |

  | Deletion | n | restored | flagged | omitted |
  |---|---|---|---|---|
  | all | 80 | 13 (0.16 [0.09, 0.24]) | 0 (0.00) | 67 (0.84 [0.76, 0.91]) |
  | number | 23 | 0 (0.00) | 0 (0.00) | 23 (1.00 [1.00, 1.00]) |
  | place | 12 | 5 (0.42 [0.12, 0.71]) | 0 (0.00) | 7 (0.58 [0.29, 0.88]) |
  | other | 45 | 8 (0.18 [0.07, 0.29]) | 0 (0.00) | 37 (0.82 [0.71, 0.93]) |

- **Bound-status sensitivity:** identical to the primary in both arms (one claim in the whole run was written as
  hedged, and none was demoted to `not_confirmed`).
- **Realistic arm (primary):** substitutions propagated 0.28, restored 0.56, mixed 0.03, omitted 0.13; numbers
  propagated 19 of 22 (0.86 [0.71, 1.00]); places restored 10 of 11. Deletions omitted 66 of 80 (0.82), every deleted
  number (23 of 23).
- **Predictions:** H1 holds (restored + propagated + mixed 0.89, omitted 0.11; realistic 0.87, 0.13), H2 holds
  (omitted 0.84; realistic 0.82), H3 holds (flagged 0.00 in every type and arm).
- **Per arm:** bound citations holding a corrupted form 311 of 1,626 (targeted) and 282 of 1,621 (realistic), none
  holding the original form; ROUGE-L F1 0.141 clean, 0.135 targeted (−0.006 [−0.015, +0.003]), 0.128 realistic
  (−0.013 [−0.021, −0.005]); median model seconds per run 146, 155, 143.
- **A fact of the system:** a corrupted body is cut into different units from its clean form (in the in-container dry
  run one article gave 5 units clean and 8 realistic), because SaT splits on the text it receives.
- Full tables: `results/score_20261024_222324.md` and `.json` (counts only).
