---
name: experiment-loop
description: Run an iterative, evidence-driven experiment loop on the CyberCase RAG pipeline — propose a method, test it, measure it, decide, repeat for N cycles or until an API budget runs out — in an isolated sandbox, with a dev/test split, a noise floor, paired statistics and a lab notebook. Use this whenever the user asks to "iterate", "run N cycles", "keep trying until credits run out", "try other rerankers / prompts / models", "find something that improves precision / recall / F1", run an ablation or benchmark sweep, or improve any retrieval or reasoning metric of the RAG service — even if they don't say "experiment" or "ablation".
---

# Experiment loop

The user hands over a goal ("raise precision", "test other rerankers") and a stopping
rule ("5 cycles", "until OpenRouter credit runs out"), often before going to sleep.
The job is to come back with a result they can trust: something that held on data it
was not tuned on, measured against production, with every step logged and committed.

The loop that worked here: **diagnose → propose → test one factor → measure paired →
keep/drop → log → commit**, then confirm winners once on held-out data.

## 0. Frame it (no questions if the request is clear)

Settle, from the request and the conversation:
- **Primary metric** and the **guard metrics** a win must not break. For answers:
  technique F1 + Thai four-heading structure, Thai ratio, share of cited IDs absent
  from the context (grounding). For retrieval: StepCoverage@K split by cue type
  (`described` vs `named`) — @15 is what reaches the LLM, @5 is ordering.
- **Stopping rule** — N cycles, or a budget. If it is a budget, check the balance first
  (`GET https://openrouter.ai/api/v1/credits`) and announce model, call count and cost
  before each paid run (the user asked for this). Frozen-context reasoning costs
  ≈ $0.0025 per incident on gpt-5.6-luna; retrieval-only runs are free.
- **What must stay fixed** so that only the component under test varies.

## 1. Isolate

Work in a new git worktree on a new branch (`git worktree add -b sandbox/<topic>
../CyberCase-<topic> <base>`). Other worktrees may hold someone's uncommitted work —
never switch or edit them. Production changes go on their own `feat/...` branch
from `origin/main`, never on the sandbox. A worktree created from `origin/main`
gets `origin/main` as its upstream: run `git branch --unset-upstream` so a bare
`git push` cannot land on main (a push to main triggers the deploy workflow).

## 2. Build the harness before any idea

Reuse one if it fits (they live on sandbox branches, see "Existing harnesses"). A new
harness must:
- **Freeze everything upstream** of the component: frozen served contexts for the
  reasoning step; cached decomposer sub-queries and disk-cached Qdrant results for
  retrieval. This is what makes a cycle cheap and paired.
- **Prove parity**: the `base` arm must reproduce production (report the match rate,
  e.g. "identical top-15 in 41/45"). A harness that does not reproduce production
  measures something else.
- **Measure the noise floor**: re-run `base` (LLM steps are non-deterministic even at
  temperature 0 — identical contexts gave different answers). Use 2–3 reps for LLM arms.
- **Split dev/test**: `precision_lab.split_of(id)` (sha1, dev 55 / test 45 of the 100
  real-CTI incidents). Design on dev only. Test is touched once, at the end.
- Write one JSONL row per (incident, rep) as it finishes, so any run resumes.

## 3. Each cycle

1. **Diagnose first.** Look at the errors of the current best before proposing:
   what kind of mistake, where it enters, how often. The best ideas came from this
   (e.g. "every false positive is in the context", "half the missed steps were
   retrieved and then lost in the merge").
2. **Propose 2–4 arms, one factor each**, each with a written hypothesis. A
   combination arm is fine once its parts have been measured.
3. **Run** (background, ≤ 8 workers; ≤ 3 when the balance is low).
4. **Measure paired** against `base` and against the current best: mean Δ, 95%
   paired-bootstrap CI, Wilcoxon p, wins/ties/losses. Look at the guard metrics.
5. **Decide**: keep only what clears zero on the primary metric without breaking a
   guard. A gain inside the noise floor is not a gain.
6. **Log** a row per arm in `results/<lab>/LAB_NOTES.md` (idea, numbers, verdict),
   **commit** the arms, rows and notes. The next cycle builds on the winner.

Avoid rules written from the dev split's own errors: `primary2` (rules patched from
dev misses) gained on dev and lost −0.030 F1 to its parent on test.

## 4. Confirm on test, then report

Run `base` and the few winners on the test split (same reps as dev). Report honestly
which dev winners did not hold — in the precision lab three of five did not.

Final summary (Thai if the user writes Thai), in this order: what was done; the result
table on test with CIs; what held and what overfit; findings about the measurement
itself; caveats; next steps; branches and files. State plainly that a component-only
result is an ablation: the served agent end to end is the headline, and retrieval
gains have failed to reach the answer before (HyDE: +0.10 retrieval, F1 −0.007).

To ship a winner: a `feat/...` branch from `origin/main`, a parity check that the
production code reproduces the lab arm on real incidents, the full test suite, then a
PR with the evidence and caveats. Merge only when the user says so.

Save a memory for anything non-obvious (results, gotchas) and update `MEMORY.md`.

## Existing harnesses

| harness | branch | measures | cost |
|---|---|---|---|
| `evaluation/precision_lab.py` + `precision_arms.py` | `sandbox/reasoning-precision` | reasoning step on frozen served contexts; F1 / F1v / structure / grounding | paid |
| `evaluation/retrieval_lab.py` + `_arms.py` + `_llm.py` | `sandbox/retrieval-lab` | vector path (candidates, reranker, weights, pool, merge), local Ollama reranker | free |
| `evaluation/hyde_benchmark.py` | `eval/hyde-retrieval` | retrieval with cached sub-queries + HyDE entries | ~200 calls once |
| `evaluation/agentic_ablation.py`, `hyde_agent_ablation.py` | `eval/agentic-ablation`, `eval/hyde-retrieval` | served agent end to end | ≈ $0.5 per arm |

`F1v` (precision_lab) credits an ATT&CK v19 ID as the older gold ID it replaced
(`revoked-by`, e.g. T1685 for T1562/T1070) — the real-CTI gold predates v19.

## Gotchas that cost time before

- Run from `rag_service/app` as a module with `PYTHONUTF8=1`.
- The core LLM key is `OPENROUTER_CYBERCASE`; if only `OPENROUTER_API_KEY` is set,
  export it under the other name for the process. Without it the decomposer silently
  falls back to the whole incident — an old ".105 described@5" came from exactly that.
- OpenRouter 402 `in_flight_budget_exhausted` at a low balance means too many
  parallel requests, not an empty account. The harness ledger under-counts real spend
  by ~15%.
- Neo4j Aura Free pauses when idle (its DNS name disappears) — the user must resume it
  at console.neo4j.io. Retrieval-only work can skip graph expansion.
- 4 GB GPU: keep ONE CrossEncoder and set `max_seq_length` per call; a second instance
  next to BGE-M3 spills to shared memory (190 s/incident). Ollama on the same GPU
  slows both ~2×. The MITRE fine-tune needs an explicit output-format line.
- Background runs: redirected stdout is block-buffered — watch the JSONL row count,
  not the log. Wait with `run_in_background` + an `until` loop, never sleep-polling,
  and make the loop's match string something the command itself doesn't print.
- The auto-mode command classifier fails transiently; after a few failures do
  read-only work and retry later rather than burning attempts.
