# Task: add an `assess` stage so a case that needs a question does not pay for a full analysis

## Repository

`CyberCase Intelligence Framework`. Work only in `backend/`.
FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic. Python 3.11. Formatter/linter: `ruff`
(`cd backend && python -m ruff format . && python -m ruff check .`).
Tests: `cd backend && python -m pytest tests -q`.

Read `backend/ARCHITECTURE.md` first. It is accurate and explains the conventions you must keep.

---

## 1. What happens today

An analysis is three steps, in `backend/app/services/analysis/pipeline.py`:

```python
async def analyse_case(data: AnalysisInput) -> AnalysisArtifacts:
    artifacts = AnalysisArtifacts()
    artifacts = await retrieve_technical_context(data, artifacts)  # MITRE gate, then RAG over HTTP
    artifacts = await write_analysis(data, artifacts)              # the one big model call
    artifacts = await bind_to_case(data, artifacts)                # bind claims to source quotes
    return artifacts
```

The caller is `run_case_analysis` in `backend/app/services/workflow/run_analysis.py`:

```
read_case_for_analysis(...)      # short transaction, then released
  → pipeline(AnalysisInput(...)) # minutes, no DB connection held
  → store_analysis(...)          # short transaction
```

`store_analysis` then calls `decide_followup(gaps=artifacts.trace.gaps, ...)`
(`backend/app/services/analysis/clarification.py`, pure policy, no I/O, no model) which returns
either `Ask(gap)` or `Proceed(reason)`.

**The problem:** the decision to ask happens *after* the full analysis has already run. A case
that is going to bounce back with one clarification question has already paid for the MITRE
gate, possibly a RAG retrieval, the large grounded model call, and claim binding. Measured
end to end that is ~140 seconds for a single question. Cases with the least information — the
ones most likely to need questions — pay the full price on every round.

---

## 2. What to build

A fourth stage, `assess`, that runs **before** the expensive work and can short-circuit it.

```
advance:
  assess(sources, followup_history)        → gaps only, one small model call
  decide_followup(gaps, ...)
    ├── Ask(gap)  → persist the assessment + the question, return NEED_FOLLOWUP.
    │               Do NOT run technical context, the full analysis, or binding.
    └── Proceed   → retrieve_technical_context → write_analysis → bind_to_case → COMPLETED
```

`assess` reads the case sources and the follow-up history and returns **only** a list of
`CaseAnalysisGap`. It must not produce claims, a timeline, involved parties, impacts or MITRE
associations. It is a cheap triage call, not a small analysis.

---

## 3. Decisions already made — do not relitigate these

- **`decide_followup` does not change.** It is pure policy and already takes gaps as input.
  Its signature, its ordering of checks and its `ProceedReason` values stay exactly as they are.
- **The gap contract does not change.** `CaseAnalysisGap`
  (`backend/app/services/analysis/contracts/claims.py`) is what `assess` returns and what the
  full analysis returns. One type, one meaning.
- **No step under `services/analysis/` may touch the database.** Each step is handed what it
  needs and returns what it produced. This is what lets ablations run the same steps over a
  dataset file. `assess` follows the same rule.
- **`experiments/` may import `app/`; `app/` must never import `experiments/`.**
- **One question outstanding at a time.** `store_analysis` already checks `pending_question`
  before writing a new question and re-offers the standing one instead. Keep that behaviour.

---

## 4. Traps. Each of these will break something if you miss it

### 4a. `gap_key` is the identity, `gap_id` is not

`gap_id` (`G-01`) is only meaningful inside one trace. `gap_key` is the stable identity across
analyses and is what the dedup uses:

- `asked_gap_keys(db, case_id)` reads `chat_messages.gap_key` to avoid asking the same thing twice.
- `next_question_of_round` matches on it.

If `assess` invents different `gap_key` values than `write_analysis` would for the same
underlying gap, the case will ask the same question twice under two names. **The gap-identifying
part of the prompt must be shared text, not two prompts that happen to look similar.** Extract it
in `backend/app/services/analysis/prompts.py` and have both system prompts include it.

### 4b. The ASK path must still persist a row, and that row is read later

You cannot simply skip persistence on the ASK path:

- `question_message(...)` requires an `analysis_result_id`.
- `rounds_asked` is `COUNT(DISTINCT analysis_result_id)` over messages that have a `gap_key`.
- `next_question_of_round` does `db.get(CaseAnalysisResult, question.analysis_result_id)` and
  reads `trace_json` to find the round's remaining gaps.

So the assessment has to be stored as a `CaseAnalysisResult` whose `trace_json` carries the gaps.

### 4c. An assessment is not an analysis, and `GET /analysis` must not return one

`get_latest_case_analysis` returns `case.latest_analysis_result`, i.e. whatever
`case.latest_analysis_result_id` points at. If an assessment row sets that pointer, the analysis
page will render a gap-only trace as the case's analysis, and `reports/` will try to build a
seven-section report out of it.

Required: an assessment row must be distinguishable, and `latest_analysis_result_id` must keep
pointing at the last **full** analysis.

### 4d. There is a CHECK constraint on `status`

`backend/app/models/analysis.py`:

```python
CheckConstraint("status IN ('validated')", name="ck_case_analysis_results_status")
```

Adding a second status needs an Alembic migration that drops and recreates the constraint.
Migrations live in `backend/alembic/baseline_versions/`, numbered sequentially; the current head
is `0011_retrieval_context_reuse`. Follow the house style: a prose docstring saying *why*, and
plain SQL in `upgrade()`.

### 4e. `CaseAnalysisTrace` requires fields an assessment does not have

`CaseAnalysisTrace` has three required fields, checked against the model just now:
`analysis_mode`, `summary` (`min_length=1`, so empty string is rejected) and `claims`. An
assessment has none of them honestly.

Either give the assessment a schema of its own that serialises into `trace_json`, or make the
trace tolerate a gaps-only shape — but if you choose the second, every consumer of the trace has
to stay correct. There are five:
the provider contract, the stored row, `reports/content.py`, the frontend overview, and the chat
message that announces a finished analysis.

### 4f. `monkeypatch` targets written as strings

Several tests patch module paths as strings, e.g.
`"app.services.analysis.steps.write.request_analysis_stage"`. These do not fail at import when a
name moves — they fail as a test that silently calls the real provider. After any move, grep for
the old path.

---

## 5. Where the pieces go

Follow the existing layout:

```
app/services/analysis/
  pipeline.py            AnalysisInput / AnalysisArtifacts, the stage functions, analyse_case
  steps/
    assess.py            ← new: the cheap gaps-only model call
    technical_context.py
    write.py
    bind.py
  prompts.py             ← add the assess system prompt; extract the shared gap section
  contracts/
```

The model call goes through `request_stage`
(`backend/app/services/analysis/provider.py`), the same way `write.py` does it:

```python
async def request_stage(
    *, client: httpx.AsyncClient, target: CoreLlmTarget, config: AnalysisPipelineConfig,
    stage: str, system: str, content: dict[str, object],
    schema: type[ProviderResult], calls: list[dict[str, object]],
    checkpoint: Callable[[], Awaitable[None]] | None = None,
) -> ProviderResult
```

Use a distinct `stage` label (e.g. `"assess"`) so the receipt shows it separately.
The sources payload builder to reuse is `provider_source_payload` in `steps/write.py`.
Follow-up history is passed as `followup_history` on `AnalysisInput` and rendered by
`followup_payload` in `contracts/exchange.py`.

`analyse_case` should keep reading top to bottom, with the short-circuit visible in it rather than
hidden in a helper. Something of this shape — the exact factoring is yours, but the ASK path must
not call the three expensive steps:

```python
async def advance_case(data: AnalysisInput) -> AnalysisArtifacts:
    """One step: triage first, and only analyse in full when nothing is worth asking."""
```

Keep `analyse_case` itself available as the full-analysis composition, because
`backend/experiments/analysis_arms.py` composes these same step functions for ablations and
`run_case_analysis(pipeline=...)` takes a composition as an argument.

---

## 6. Acceptance criteria

1. A case whose assessment yields an askable gap returns a question **without** calling the MITRE
   gate, the RAG service, or the main analysis model call. Prove it with a test that injects
   fakes for those and asserts they were not called.
2. A case whose assessment yields nothing worth asking runs the full three steps and completes.
3. `GET /cases/{case_id}/analysis` never returns an assessment row.
4. `rounds_asked`, `asked_gap_keys` and `next_question_of_round` keep working across a full
   three-round follow-up loop. `backend/tests/test_case_followup_postgres.py` covers this; run it
   with a real database:
   ```
   CYBERCASE_TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/cybercase_framework \
     python -m pytest tests -q
   ```
   (Without that variable the PostgreSQL tests skip silently — make sure they actually ran.)
5. `python -m pytest tests -q` passes. Two tests in `tests/test_case_report_presentation.py`
   render a real PDF and need WeasyPrint's native libraries; they fail on a Windows host without
   GTK and pass inside the Docker image. Those two are the only acceptable failures.
6. `python -m ruff format . && python -m ruff check .` clean.
7. `backend/ARCHITECTURE.md` updated: section 3 ("การวิเคราะห์หนึ่งครั้ง" equivalent — the
   pipeline section) and the model-call table in section 5 must describe the new stage. The
   document is the reading guide for this backend; leaving it stale is a defect.

## 7. Out of scope

- The frontend. No API response shape changes: `AnalysisStepRead` already has
  `status: "need_followup" | "completed"`.
- `rag_service/`.
- Changing the follow-up budget (`chat_followup_max_rounds`, `chat_followup_gaps_per_round`).
- The known validator gaps in `validate_case_structured_report` (it does not check
  `claim_id ⊆ trace`). Leave them; they are tracked separately.

## 8. Report back

State plainly: how many model calls a three-round follow-up loop costs before and after, and
which of the traps in section 4 required a design decision you had to make. If you could not
satisfy an acceptance criterion, say which and why rather than weakening the test.
