# Does asking help, and what does asking cost?

An evaluation harness for one question:

> Does explicit information-sufficiency assessment with bounded clarification
> improve downstream task performance, compared with direct and non-interactive
> multi-stage baselines?

Four arms, one sample list, paired on sample id. Nothing here imports the
production database, and nothing in `backend/` changed to make it run.

## The pipeline

```text
                    ┌──────────────────────── leakage boundary ────────────────────────┐
                    │                                                                  │
  benchmark row ────┤  CandidateView                        HiddenContext              │
                    │    sample_id                            full_input               │
                    │    initial_input                        required_points          │
                    │                                         hidden_summary           │
                    │                                         gold_answer              │
                    │       │                                 should_ask               │
                    └───────┼──────────────────────────────────────┼──────────────────-┘
                            │                                      │
                            ▼                                      ▼
              ┌──────────────────────────┐              ┌────────────────────┐
              │  Stage 1 — Understanding │              │   UserSimulator    │
              │  understanding_v1        │              │   simulator_v1     │
              └────────────┬─────────────┘              └─────────┬──────────┘
                           ▼                                      │
                    structured state (prose notes)                │
                           │                                      │
                           ▼                                      │
              ┌──────────────────────────┐                        │
     ┌───────►│  Stage 2 — Sufficiency   │                        │
     │        │  sufficiency_v1          │                        │
     │        └────────────┬─────────────┘                        │
     │                     │                                      │
     │        SUFFICIENT ──┴── NEED_CLARIFICATION                 │
     │             │                    │                         │
     │             │                    ▼                         │
     │             │      ┌──────────────────────────┐            │
     │             │      │  Select one gap + ask     │           │
     │             │      │  gap_selection_v1         │           │
     │             │      │  (question_generation_v1) │           │
     │             │      └────────────┬──────────────┘           │
     │             │                   │  one question            │
     │             │                   ▼                          │
     │             │            ═══════════════════ ◄─────────────┘
     │             │              simulated user       answers only
     │             │            ═══════════════════    what was asked
     │             │                   │
     │             │                   ▼
     │             │      ┌──────────────────────────┐
     │             │      │  Update state             │
     │             │      │  state_update_v1          │
     │             │      └────────────┬──────────────┘
     │             │                   │
     └─────────────┼───────────────────┘  bounded: budget, repeat gap,
                   │                      repeat question, unknown, error
                   ▼
        ┌──────────────────────────┐
        │  Final answer            │
        │  final_answer_v1         │
        └────────────┬─────────────┘
                     ▼
        ┌──────────────────────────┐      ┌─────────────────────────┐
        │  Exact match             │  or  │  judge_v1 / coverage_v1 │
        │  (300 of 400 AskMind)    │      │  labelled scored_by     │
        └──────────────────────────┘      └─────────────────────────┘
```

## The four arms

| Arm | Flow | Calls per sample | What it isolates |
|---|---|---:|---|
| `direct` | task → answer | 1 | the floor |
| `multi_stage` | task → notes → answer | 2 | whether a second pass alone helps |
| `gap_aware` | task → notes → sufficiency → answer | 3 | whether *reasoning about* gaps helps, with no way to act |
| `followup` | task → notes → (sufficiency → ask → update)\* → answer | 3 + 3·turns | whether *acting on* gaps helps |

`gap_aware` and `followup` run the same function. Gap-aware is bounded follow-up
with `budget=0` and a simulator that raises if asked, so the difference between
them is one integer rather than a second implementation that can drift.

## The benchmark

**AskMind**, the intent-deficient half of AskBench — [paper](https://arxiv.org/abs/2602.11199)
(ACL Findings 2026), [data](https://huggingface.co/datasets/jialeuuz/askbench_bench) (MIT),
[code](https://github.com/jialeuuz/askbench). `data/ask_mind.jsonl` is the
published `ask_bench_data/ask_mind.jsonl`, committed so a run is reproducible;
its SHA-256 goes into every run manifest.

400 rows, 100 each from MedQA, GPQA-d, BBH and Math500. Verified fields (three
key-set variants; everything but the five required fields is read defensively):

```text
id  ori_question  degraded_question  degraded_info  required_points
expected_answer  source_task        [solution] [category] [err_info]
```

Two properties of the published data the harness leans on:

**The ask label is free.** 53 of the 400 rows were never degraded — the question
the candidate sees is character for character the full one, and `degraded_info`
says as much. Nothing is missing, so asking is unnecessary. That gives a gold
should-ask label (347 positive, 53 negative) at no annotation cost. Note that
`required_points` is populated on those 53 anyway, so the rubric cannot be used
for this; the label comes from comparing the two questions.

**Only a quarter needs a judge.**

| subset | n | answers look like | scored by |
|---|---:|---|---|
| MedQA | 100 | `The answer is B.` | exact match |
| BBH | 100 | `False`, `Yes`, `E` | exact match |
| Math500 | 100 | `12`, `\sqrt{51}`, `\frac{\sqrt{3}}{3}` | exact match + LaTeX normalisation |
| GPQA-d | 100 | `The crude compound exists as a mixture of diastereoisomers` | **judge** |

Every scored row carries `scored_by`, and the report prints the deterministic
subset in its own column.

### Domain case study

`--benchmark cybercase` runs the same four arms over
`research/attribute_first_pilot/benchmark.json` — 33 items, 7 base scenarios,
already in this repository. `gold_attributes.answerability` is the ask label
(INSUFFICIENT and CONFLICTING mean ask; 9 of 33), `missing_information` is the
checkpoint list, and each perturbed item is paired with its `ORIGINAL` by
`base_case_id`, which is what the simulator answers from.

Expectations there are written as behaviour ("abstain from confirming
exfiltration"), so **every cyber item is judge-scored**. It is a demonstration
that the architecture runs on cyber-case input, not a powered benchmark.

## Stop conditions

The loop ends on the first of:

| `stop_reason` | when |
|---|---|
| `sufficient` | the sufficiency stage says so, or returns no gaps |
| `budget_exhausted` | the turn budget is spent |
| `repeat_gap` | the selector chose a gap it already chose |
| `repeat_question` | the same question, whitespace and case normalised |
| `unknown_information` | the simulator said it did not know, `--unknown-tolerance` times running |
| `error` | a structured stage could not be parsed |

Every path still produces a final answer. An arm that declined to answer would
score zero for a reason that has nothing to do with clarification.

## Leakage design

The candidate can never read the rubric, the full question or the gold answer,
because it is never handed the object that holds them:

* `CandidateView` has two fields, `sample_id` and `initial_input`.
* `HiddenContext` holds everything else and is given only to `UserSimulator`
  and to the scorer.
* An arm receives the simulator's `answer` **method**, not the simulator and not
  the context. Hidden information reaches the candidate only as whatever the
  simulator chooses to say.
* Non-interactive arms are given `SilentSimulator`, which raises rather than
  answering. "Does not ask" is a property of the run, not a promise.
* Every `CallRecord` carries `role`. Candidate, simulator and judge prompts are
  logged separately, and candidate cost is reported without the apparatus.

`tests/test_leakage.py` runs all four arms and asserts that no candidate-role
prompt contains any hidden string, that only simulator and judge prompts do, and
that information the simulator *did* reveal reaches the later candidate prompts
— otherwise the loop would not be feeding anything back and a gain would just be
the extra calls.

## Metrics

* **Final task performance** — exact match where the benchmark allows, judge
  elsewhere, `scored_by` on every row. Primary outcome.
* **Ask decision** — accuracy, precision, recall and F1 against the gold
  should-ask label, over the arms that make the decision. `direct` and
  `multi_stage` report nothing rather than being scored as "never asks".
* **Checkpoint coverage** — of `required_points`, how many the questions
  actually raised. Judge-scored, and labelled as such.
* **Interaction** — mean, median and max turns, questions per solved sample,
  unnecessary-ask rate over the undegraded items, stop-reason counts.
* **Recovery gain** — `followup` minus each baseline, paired on sample id, with
  a percentile bootstrap interval and an exact McNemar test.
* **Cost** — candidate calls, input and output tokens, latency, per arm.
* **Failure categories** — counted from records, not judged: `failed_to_ask`,
  `asked_unnecessarily`, `asked_irrelevant`, `repeated_gap_or_question`,
  `informed_but_still_wrong`, `no_gain_over_baseline`.

Statistics are standard library only: exact McNemar for the paired binary
outcome, percentile bootstrap for the mean difference, Wilcoxon signed-rank
(normal approximation) for turn counts.

## Running it

From `research/`:

```bash
python -m pytest clarification_pilot/tests -q
```

```bash
python -m clarification_pilot.runner --dry-run --limit 8 --budgets 1 2 3
```

```bash
python -m clarification_pilot.runner --limit 40 --budgets 1 2 3 --concurrency 6
```

```bash
python -m clarification_pilot.runner --benchmark cybercase --budgets 2
```

`--dry-run` needs no API key and touches no network. A live run reads
`OPENROUTER_CYBERCASE` or `OPENROUTER_API_KEY` from the environment or the
repository `.env`.

Useful flags: `--model`, `--simulator-model`, `--judge-model`, `--temperature`
(default 0), `--seed` (default 42), `--unknown-tolerance`, `--judge-fallback`
(send exact-match misses to the judge, relabelled), `--no-coverage`,
`--separate-question-call` (split gap selection from question writing),
`--log-prompts`.

Each run writes `results/run_<stamp>.json` (manifest + every call),
`results/scored_<stamp>.json` (one row per sample × arm × budget) and
`results/report_<stamp>.md`.

### Cost

One sample costs roughly 1 + 2 + 3 + (3 + 3·turns) candidate calls across the
four arms, plus one simulator call per turn and one or two judge calls per row.
At `--limit 40 --budgets 1 2 3` that is about 1,200 calls. The full 400 rows at
three budgets is roughly 12,000. Start small.

## What this does and does not establish

It tests whether explicit sufficiency assessment plus bounded clarification
improves final task performance under incomplete information, on this benchmark,
with these prompts, at this budget.

It does not establish that the system asks the best possible question, that it
understands what is missing, that it generalises to other domains, or that
clarification is worth its cost — the cost table is printed precisely so that
last one stays an open question rather than a silent assumption.

No results are claimed here. Nothing but dry runs has been executed.
