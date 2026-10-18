# Reading workload reduction: implementation and bounded pilot

2026-10-07. Working tree `refactor/evidence-unit-grounding`, HEAD `ca7fc6d6`.
This implements the accepted Reading workload proposal. It does not resume the
stopped projection-validation study or change the local NuExtract/Judgement architecture.

## Applied change

The Reader receives every original Source character, the original `source_id`,
the document/quality header, and source-local unit IDs such as `U001`.
Repeated canonical IDs, text revision hashes and offsets are omitted from the
model payload. Prompt-JSON serialization is compact.

The request captures source revisions before the call. The same address book
expands returned aliases before deterministic binding. Stored IDs remain
`source_id:U001-<revision>`; original text, offsets, document/page provenance,
stale checks, duplicate diagnostics and historical canonical/quote paths remain.
No table, migration, vector store or independent per-document analysis is added.
Judgement still receives canonical Claims, follow-ups and optional external context.
NuExtract still derives display/report views from Claims.

The Reader prompt explicitly retains participant roles and reporting attribution.
It requests the additional context unit when resolving pronouns/relative dates.
These are generation instructions, not a new semantic verifier or a guarantee.

`AnalysisPipelineConfig.reading_thinking_tokens` / `CASE_READING_THINKING_TOKENS`
provide a Reading-only override, retained in the stored pipeline configuration.
Historical configurations without the field inherit the shared thinking budget.
Compose retains **8,192**; Judgement/assessment and the visible output cap **32,608**
are unchanged. Reasoning-off was not selected as default after the observed failure.

## Inputs and protocol

Two controlled development Cases each contain two documents plus an answered QA:
one English Case and one Thai Case with OCR provenance and explicit amount-reading
uncertainty. Each has 11 manually specified expected facts and forbidden
strengthenings. Labels were written before provider calls; NLI did not label gold.
Fixture SHA256: `dbeb36beafc8f648b7347ac4e2abcf525c500d8ea6b49134ec74c66e75ab37e8`.

Within each prompt phase, both conditions use byte-equivalent wire payloads except
`thinking` and the corresponding combined `max_tokens`. They use the same model
`google/gemma-4-26b-a4b-it`, pinned provider order `nextbit/bf16,coreweave/bf16`,
production sampling (temperature omitted), source content, prompt, output cap and
retry behavior. Order is on/off for English and off/on for Thai. The harness checks
paired request equality. It runs Reading only, with direct binding and legacy
meaning recovery disabled for this structural probe; there are no Case writes,
Judgement, NuExtract or RAG calls.

An experiment-only 300-second wall limit bounds each condition; no final matched
condition reached it. Production timeouts/retries are unchanged. Every provider
attempt, raw response, canonical binding result and stage receipt is retained.
Failed schema responses are not stripped into accepted Claims. The harness exits
nonzero if any condition fails, while keeping all comparison receipts.

The old audit Case is absent from the current database, so this is explicitly a
fixture pilot, not a replay or speedup measurement of that historical Case.

## Deterministic payload reduction

These compare canonical-address payloads with compact-address payloads under the
same final prompt. `o200k_base` estimates include the stage payload; they are not
the Gemma tokenizer or provider-billed token counts. Original Source text is identical.

| Fixture | Units | Before estimated tokens | After | Reduction | Message characters before → after |
|---|---:|---:|---:|---:|---:|
| English, 2 documents + QA | 7 | 1,754 | 1,423 | 18.9% | 2,336 → 1,734 (25.8%) |
| Thai, 2 documents + QA | 9 | 1,954 | 1,544 | 21.0% | 2,567 → 1,832 (28.6%) |

This establishes smaller representation with exact text preservation. It does not
establish a proportional latency improvement, semantic citation correctness, or
savings for large real Cases. No remote canonical-vs-compact timing ablation was run.

## Thinking comparison and coverage

Full coverage means the expected fact and its material attribution/qualification
are represented across canonical Claim texts. Partial and missing facts do not
count as full. Coverage is separate from per-Claim qualification, selected-span
semantic completeness and epistemic classification. Schema failures are unscored,
not treated as successful short output or silently recovered.

Initial prompt SHA: `7fe3d7e7e4f332b196683d9a8a099fe0658959a8a8ce6583da57274ac2132e82`.

| Fixture | Thinking | Reading seconds | Provider posts | Claims | Full fact coverage | IDs resolved / selected |
|---|---|---:|---:|---:|---:|---:|
| English | on | 58.6 | 1 | 8 | 10/11 | 10/10 |
| English | off | 10.8 | 1 | 7 | 9/11 | 9/9 |
| Thai | on | 71.4 | 1 | 7 | 11/11 | 13/13 |
| Thai | off | 12.5 | 1 | 8 | 10/11 | 12/12 |

The initial prompt omitted Jane's explicit complainant role in both English
conditions, omitted Somchai's role in Thai/off, and lost Jane's reporting
attribution in English/off. This informed the bounded role/attribution prompt change.
The fixtures were reused for development; resulting coverage is not held-out accuracy.

Final coverage prompt SHA: `e7ffa3f454daf5625f1c2cec20e8add2e06999552aeab0a43116ea85480d7223`.

| Fixture | Thinking | Reading seconds | Provider posts | Result | Full fact coverage | IDs resolved / selected |
|---|---|---:|---:|---|---:|---:|
| English | on | 66.5 | 1 | 8 canonical Claims | 11/11 | 10/10 |
| English | off | 13.9 | 1 | 8 canonical Claims | 11/11 | 10/10 |
| Thai | on | 92.3 | 1 | 9 canonical Claims | 11/11 | 13/13 |
| Thai | off | 38.5 | 2 | schema rejected twice | unscored | no canonical binding |

Thai/off added `note` in one reply and `notes` in the second; both violate the
six-field Claim schema. English/off also marked the explicit payment-log transfer
assertion as `unknown`; the textual fact remains but its classification is wrong.
Reasoning-off is therefore an explicit experimental option, not the new default.
The retained on condition represents all 22 fixture expectations in Claim text,
without establishing full semantic correctness.

Provider-reported output/think counts for the final phase:

| Fixture / mode | Output tokens across attempts | Thinking tokens | Visible output cap |
|---|---:|---:|---:|
| English / on | 5,754 | 4,653 | 32,608 |
| English / off | 1,121 | 0 | 32,608 |
| Thai / on | 6,720 | 5,345 | 32,608 |
| Thai / off, both rejected attempts | 2,744 | 0 | 32,608 |

Thinking is included in reported output tokens here; these columns must not be
added. Queue time, decode time, cache effects and provider execution are not
controlled. Some responses report very small uncached input counts and substantial
cache reads. One observation per Case/condition is insufficient for general
latency claims, confidence intervals or significance testing.

## Remaining failures and limits

- Both final English modes and final Thai/on expand a relative date but cite the
  event unit without its date-referent unit. All IDs resolve, yet selected-span
  semantic completeness is not guaranteed. The context-unit prompt instruction
  was insufficient; no backend semantic repair was introduced in this task.
- Final Thai/on preserves OCR amount uncertainty in a separate Claim rather than
  in the affected amount Claim. Full fact coverage across Claims does not establish
  complete qualification of each individual Claim or downstream view.
- Correct Source identity/unit existence does not prove the selected Source supports
  the generated assertion. This work measures structural resolution separately.
- NuExtract relationship quality and downstream Judgement/Report correctness are
  not measured by this Reading-only pilot. Existing compatibility tests pass, but
  that is not a real-Case downstream quality or total-latency result.

A preliminary temperature-zero diagnostic was excluded from the native-sampling
comparison. Its first English/on attempt reported **40,799 thinking tokens** against
a requested 8,192, hit the combined 40,800 limit and took 419 seconds. The existing
retry succeeded; the complete stage took 479.4 seconds across two posts. English/off
and Thai/off subsequently completed in 12.3/15.1 seconds; the final Thai/on request
was cancelled. A corrected cancellation receipt records that the English retry
had already finished before the stop signal. This proves the requested reasoning
budget was not a hard limit for that particular provider response; it does not
attribute every production delay to the same failure.

## Harness, checks and receipts

- `backend/experiments/reading_load_pilot.py`, with fixed JSON fixtures, implements
  size preparation, matched reasoning conditions, raw attempt receipts and direct binding.
  Default invocation is preparation only; `--execute` explicitly uses the provider.
- New focused tests cover exact text/local-ID stability, Thai/OCR/blank input,
  multi-source scope, multiple units, unknown/malformed/cross-source/stale/duplicate
  pointers, request-revision protection, QA, page provenance, historical canonical
  IDs, message serialization, stage-budget inheritance and matched pilot inputs.
- Linux compatibility: **528 passed**, no skips, including existing direct/legacy
  quote, real pinned NLI and native report tests. Seven warnings are Torch JIT deprecations.
  Final affected-code checks, API type freshness, Ruff and runtime receipts are
  recorded in the task result file.

Local receipts: `tmp/reading-load-reduction/` contains the pre-edit Git/hash/service
baseline; `native-pilot/`, `coverage-pilot/`, manual `*-review.json`,
`pilot-summary.json`, and separate temperature-zero diagnostic. The pipeline was
not replaced, Cases were not written, and no commit/push was requested.
