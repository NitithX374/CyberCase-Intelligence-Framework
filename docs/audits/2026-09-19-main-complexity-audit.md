# Where the complexity comes from — `main` @ `9c79521`

2026-09-19 [USER] Audit backend and frontend for where complexity originates. Removing
`CaseRun` is permitted this time. This is a thesis prototype: readability first, reduce
whatever can be reduced.

2026-09-19 [TOOL] Inspection only, on a clean `main` working tree. Backend is 98 Python
files / 11,643 lines; frontend is 65 production TS/TSX files / 9,203 lines plus 33 test
files. Note this is a different codebase from `audiit` — there is no `gap_clarification/`
package here and no LangChain anywhere.

---

## Summary: eight sources, ranked by what they cost a reader

| # | Source | Lines implicated | Removable |
|---|---|---|---|
| 1 | An ordinary question is a background job | ~700 | Yes, entirely |
| 2 | `CaseRun` is a job queue in a single-process app | 1,438 (`workflow/`) | Mostly |
| 3 | Follow-up has two engines and its own HTTP client | 1,350 (`followup/`) | ~60% |
| 4 | Four hand-written ways to call an LLM | ~500 duplicated | Yes |
| 5 | The frontend mirrors the backend's job machinery | 1,068 | ~70% |
| 6 | The analysis output is parsed and re-validated four times | ~800 | ~60% |
| 7 | Defensive code guarding against its own types | ~400 | Mostly |
| 8 | One concept, three names | — | Rename only |

---

## 1. Asking a question is a background job

`POST /cases/{id}/chat/messages` does not answer the question. It writes a `ChatMessage`,
creates a `CaseRun` with `operation="ask"`, and returns 202 with the run attached
(`case_chat.py:205-235`). A FastAPI background task then claims the run, loads the answer
context, calls the model, and writes the assistant message in `complete_case_ask`
(`case_ask_completion.py`, 102 lines).

The frontend then **polls that run until it settles** (`chatPolling.ts`,
`useCaseChatSubmission.ts:139`) before refetching the conversation to find the answer.

So a request/response — ask, get an answer — is implemented as: insert row, create job,
return, dispatch, claim, execute, complete, poll, refetch. Everything that follows in this
list exists partly to hold that up.

Nothing requires it. The answer is one model call with no fan-out, and the client is
already waiting. Making the route return the answer deletes `case_ask_completion.py`, the
`ask` branch of `case_run_execution.py`, `chatPolling.ts`, and the `operation` column with
every `if operation == "ask"` that reads it.

## 2. `CaseRun` is a job queue for a queue of one

`case_runs` carries `operation`, `idempotency_key`, `request_payload`, `pipeline_config`,
`attempt_count`, `evidence_revision` and `request_message_id`. `claim_case_run` moves a row
from `queued` to `running` with an attempt increment and a supersede check
(`case_run_claim.py`, 107 lines). Failures re-check `attempt_count` to prove they still own
the row. `CaseRun` or `run_id` appears in **23 files, 239 times**.

This is the machinery of a distributed worker pool. The application is not one:
`app/main.py:41` calls `validate_single_process_runtime()`, which *refuses to start* if
`WEB_CONCURRENCY`, `UVICORN_WORKERS` or `GUNICORN_WORKERS` is set, because work runs in
FastAPI background tasks inside the same process. There is exactly one worker, by
enforcement. Claiming protects against a second worker that cannot exist.

What the run genuinely provides:
- the UI can show "analysis in progress" and a failure reason,
- boot can fail anything interrupted by a restart (`cleanup_abandoned_case_runs`).

Both survive a table of `id, case_id, status, error_code, error_message, timestamps`.
Everything else — operation, idempotency, attempts, payload, config, the claim protocol —
is removable, and with it most of `case_run_claim.py`, the attempt threading through every
failure path in `case_run_execution.py` (307 lines, mostly error plumbing), and the
`owns_run` checks in completion.

## 3. Follow-up: two engines, and a third way to reach the model

`followup/` is 1,350 lines: `case_followup.py` 537, `policy.py` 315, `decision.py` 300,
`contracts.py` 157.

- `decision.py` ranks gaps deterministically — and hardcodes Thai keyword tables
  (`_THAI_INCIDENT_TIME_KEYS` and friends) to recognise "time of incident" gaps by string
  matching.
- `policy.py` then asks a model to *phrase* the gap the backend already chose, using **raw
  `httpx` with a hand-written JSON schema** and its own prompt constants.

So choosing what to ask and wording it are separate subsystems with separate failure modes,
and the wording step reaches the provider through a fourth transport (see §4). For a
prototype, one function that takes the analysis and returns the next question — or nothing —
is the whole feature.

## 4. Four hand-written ways to call an LLM

There is no LangChain on `main`; every call is hand-rolled `httpx` with its own retry,
timeout, JSON-schema and parsing:

| Call site | Lines | Shares code with |
|---|---|---|
| `case_analysis/provider_stage.py` | 128 | `llm/structured_output.py` |
| `case_analysis/mitre_applicability_gate.py` | 401 | `llm/structured_output.py` |
| `chat/case_answer.py` | 214 | nothing |
| `followup/policy.py` | 315 | `llm/structured_output.py` |

`case_answer.py` builds its request from scratch. Four prompts, four schemas, four error
vocabularies, four places to change when the provider changes. One client function taking
(system, payload, schema) collapses the duplicated half of each.

## 5. The frontend mirrors the machinery

1,068 lines of chat and query state: `useCaseChatSubmission.ts` 356, `useCaseChat.ts` 229,
`hooks/useCaseQueries.ts` 214, `useChatDraft.ts` 190, `chatPolling.ts` 79. react-query
appears 76 times across 11 files; run/polling identifiers appear 45 times.

Most of it is downstream of §1 and §2: an optimistic message, then a run id, then polling,
then cache invalidation, then reconciling the optimistic message against what came back —
plus a pending submission persisted to `localStorage` so a reload can resume it. If the send
returns the answer, the optimistic message and the reconcile step are all that remain, and
they fit in one hook.

A separate cost: **1,034 lines of runtime parsing** — `caseOverview.ts` 298,
`chat-followup.ts` 283, `technicalContext.ts` 233, `caseOverviewSource.ts` 220 — re-derive
typed objects from JSON the backend already types and generates contracts for in
`lib/generated/`.

## 6. The analysis output is inspected four times

`case_analysis/` is 2,119 lines. The path from provider response to stored trace runs
through `case_analysis_response_parser.py` (158) → `analysis_source_contracts.py` (232) →
`source_quote_resolver.py` (227) → `validation.py` (200, 9 raise sites) → 
`analysis_trace_contracts.py` (176). "Quote" appears 44 times in this package.

This is the exact-quote architecture: the model is asked for verbatim quotes, the quotes are
resolved back to source offsets, and a mismatch fails the analysis. It is the single largest
subsystem in the backend and it exists to distrust the model's citations. The `audiit`
branch already replaced it with `claim -> source_ids[]`, where an unresolvable reference is
dropped rather than raised (D048). Carrying that decision here removes the quote resolver
and most of the validation module.

## 7. Defensive code guarding against the app's own types

`AGENTS.md` already says: *"Let development failures surface instead of hiding them with
broad default fallbacks or empty exception handlers."* The code does the opposite.

| Pattern | Backend | Frontend |
|---|---|---|
| `isinstance(...)` / `typeof` + `Array.isArray` | 170 | 59 |
| `try:` / `try {` blocks | 70 | 26 |
| `except Exception` | 21 | — |
| `or {}` / `?? []` style fallbacks | 6 | 100 |

Most of these guard values the application itself produced and already typed. A Pydantic
model comes out of the database and is then `isinstance`-checked before use; a generated
TypeScript contract is re-narrowed with `typeof` before it is read. The guards are
concentrated exactly where the code is hardest to follow: `policy.py` (19), 
`analysis_source_contracts.py` (16), `case_followup.py` (14), `case_answer.py` (14),
`case_analysis_response_parser.py` (13).

Two specific habits to stop:

- **Swallowing to continue.** `case_run_execution.py:155` catches every exception from
  loading follow-up history, logs a warning, and continues with an empty tuple — so an
  analysis silently runs without the history it was supposed to use. In a prototype this
  turns a bug into a mystery.
- **Re-narrowing typed data.** The frontend's 1,034-line parsing layer exists almost
  entirely to re-check JSON that `lib/generated/` already describes.

Untrusted input — the model's response and uploaded files — is worth validating once, at the
boundary. Everything after that boundary is the application's own data, and checking it again
costs a reader more than it ever saves.

## 8. One concept, three names

Unchanged from the earlier assessment, and independent of branch: *material* / *evidence* /
*source* name one thing (the table is `case_evidence_sources`, the package is
`case_materials/`, the module inside is `case_source_bundle.py`, the route is `/materials`);
*gap* / *clarification* / *followup* name another. Costs nothing to fix and pays back on
every read.

---

## What reduction looks like, in order

Each step is independently shippable, and each one makes the next smaller.

1. **Answer an ask in the request.** Delete `case_ask_completion.py`, the `ask` branch of
   execution, `chatPolling.ts`, and the `operation` column. (~700 lines, no schema loss)
2. **Slim `CaseRun` to status + error.** Delete `case_run_claim.py`, the attempt threading,
   idempotency, `request_payload`, `pipeline_config`. Keep boot cleanup. (~500 lines)
3. **One LLM client.** One function, four callers. (~300 lines)
4. **One follow-up function.** Merge `decision.py` + `policy.py`; drop the Thai keyword
   tables. (~500 lines)
5. **Citations as `source_ids`.** Retire the quote resolver and quote validation. (~500 lines)
6. **Collapse the frontend state layer** once the backend stops returning jobs, and delete
   the parsing layer the generated contracts already cover. (~1,200 lines)
7. **Drop the defensive layer** — validate the model response and uploaded files once, trust
   the app's own types after that. (~400 lines, and most of the remaining `try` blocks)
8. **One vocabulary**, applied from table to component.

Rough total: **~4,100 lines removed** from ~20,800, with no feature lost — the user can still
add evidence, get an analysis, be asked a clarifying question, answer it, chat about the
case, and generate a report.
