# Reading this backend

`README.md` says what the backend exposes. This says how to read it: the one
rule that explains the file layout, the five files worth reading first, and the
places where the code does something for a reason you cannot see from the code.

---

## 1. The rule that explains everything else

> **Read short. Think free. Write short.**

An analysis takes minutes, because it waits on a language model. A database
connection held for those minutes is a connection nothing else can use, and a
transaction held open for them is a lock nothing else can pass.

So every slow operation is split into three:

```python
started   = await read_case_for_analysis(...)   # one short transaction, then released
artifacts = await pipeline(AnalysisInput(...))  # minutes, no connection held
step      = await store_analysis(...)           # another short transaction
```

**This is why there are three functions where you expected one.** Once you see
it, most of `services/` stops looking arbitrary: anything that calls a model or
another service is surrounded by two small database functions.

The corollary is the rule the pipeline lives by: **no step in
`services/analysis/` touches the database.** Each one is handed what it needs
and returns what it produced. That is also what lets an experiment run the same
steps over a dataset file instead of a case row.

---

## 2. Five files, in this order

| # | File | What you learn |
|---|------|----------------|
| 1 | `app/services/analysis/pipeline.py` | What an analysis *is* — three named steps, top to bottom |
| 2 | `app/services/workflow/run_analysis.py` | The read/think/write split, and the follow-up loop |
| 3 | `app/services/analysis/contracts/trace.py` | `CaseAnalysisTrace` — the object everything downstream reads |
| 4 | `app/services/analysis/clarification.py` | Whether to ask the reader another question. Pure policy, no I/O |
| 5 | `app/services/reports/content.py` | How a stored trace becomes the seven report sections |

After those five, the rest is plumbing you can read on demand.

---

## 3. The production analysis, in full

```python
async def analyse_case(data: AnalysisInput) -> AnalysisArtifacts:
    artifacts = AnalysisArtifacts()
    artifacts = await retrieve_technical_context(data, artifacts)  # MITRE, if the gate says so
    artifacts = await write_analysis(data, artifacts)              # the one model call
    artifacts = await bind_to_case(data, artifacts)                # bind claims to sources
    return artifacts
```

That is the whole production path. There is no arm switch, no stage list, no
config value that changes the shape. The alternative compositions the thesis
measures live in `backend/experiments/analysis_arms.py` and call these same
functions.

**`experiments/` imports `app/`. `app/` never imports `experiments/`.** If that
ever reverses, an ablation has become production.

---

## 4. The follow-up loop keeps no state

One HTTP request advances the loop by exactly one step. Between steps, nothing
is held in memory and no table records "a loop is in progress". Everything is
re-derived from rows that already exist:

| Question | Answered by |
|---|---|
| How many rounds have been spent? | `COUNT(DISTINCT analysis_result_id)` over messages with a `gap_key` — one analysis is one round, however many questions it asked |
| Which gaps were already asked? | every `gap_key` on the case's messages, as a set |
| What did the reader answer? | The message following each question |
| Why did it stop? | `trace_json.stop_reason` on the analysis row |

This is why the loop was **not** built with a state machine library. There is no
state to machine — each step reads the world, decides once, and writes.

`clarification.py` holds the decision and nothing else: given the gaps, what has
been asked, and the budget, return `Ask` or `Proceed`. No database, no settings,
no model. It is the easiest file in the backend to test and the easiest to
reason about; keep it that way.

### Follow-up answers are conversation, not sources

A reader's answer becomes a **`ChatMessage`**, never a `CaseSource`. It is cited
as `QA-01`, `QA-02` so a claim can quote it, but it does not enter the source
bundle and does not bump `source_revision`.

This matters more than it sounds. `source_revision` is the case's "have the
facts changed" counter: an analysis is refused if the revision moved underneath
it. If answers were sources, every answer would invalidate the analysis that
asked for it.

---

## 5. Where a model is actually called

Four places, and they do not share a path:

| Call | File | Goes through |
|---|---|---|
| The analysis | `analysis/steps/write.py` | `request_stage` |
| A chat answer about an analysis | `chat/case_answer.py` | `request_stage` |
| A chat answer before any analysis | `chat/case_answer.py` | `request_stage` |
| The MITRE applicability gate | `analysis/mitre_gate/llm.py` | **its own `httpx` client** |

The gate is the odd one out: it builds its own client and speaks to OpenRouter
directly, so it does not appear in any receipt `request_stage` writes. If you
are counting model calls and the numbers do not add up, the gate is the one you
forgot.

Retrieval is separate again: **one** call site, `analysis/steps/technical_context.py`,
over HTTP to the RAG service. The frontend never calls the RAG service.

---

## 6. Rules that look arbitrary and are not

**`app/services/__init__.py` is empty, deliberately.** Python runs it on any
`app.services.*` import. When it re-exported the subpackages, a router that
wanted a JWT helper loaded the PDF renderer and the whole analysis pipeline —
and one broken leaf broke the application. Leave it empty.

**`app/main.py` refuses to start with more than one worker.** The analysis runs
inside the request that asked for it. Two workers would mean two analyses of the
same case racing for the same row.

**Heavy native libraries are imported inside the function that needs them.**
`render_pdf.py` imports WeasyPrint inside `render_case_report_pdf`, because
WeasyPrint loads Pango and Cairo through `ctypes` at import time and raises if
they are missing. At module level, one absent system library would break every
import of `app.services.reports`. Same reasoning as the empty barrel.

**The MITRE retrieval is reused when the input has not changed.** The key is
`{source_revision, followup_answers}`, stored in `retrieval_context_json`
alongside the context it belongs to. Without this, every follow-up round
re-queried the RAG service with a byte-identical query and got a different
answer each time — one case in the database holds six analyses at revision 1
whose technique tables read 6, 6, 11, 10, 9, 9. The pipeline behind `/query` is
not deterministic, so "ask again" is not free and not neutral.

---

## 7. Things that will trip you

**`build_case_template_report` does not validate. `build_case_report` does.**
The names are one word apart and the difference is whether the report is
checked. Reach for `build_case_report` unless you specifically want the
unvalidated render.

**`validate_case_structured_report` checks less than it looks like.** It does
not check that a report's `claim_id` exists in the trace, and every subset check
passes trivially for an empty list — so a claim the model invented, with no
sources and no techniques, is accepted. A report whose seven sections are all
empty is also accepted.

**`mitre_table` is not only techniques.** Entries include tactics (`TA0006`),
mitigations (`M1026`) and software (`S0008`) as they come back from retrieval.
Anything that renders "the techniques" should say which kinds it means.

**Commit the dependency's transaction before slow work, not after.**
`get_current_user` runs a `SELECT`, which opens a transaction on the
request-scoped session. Any route that then does something slow must call
`commit_dependency_transaction(db)` *first* — `routers/analysis.py` is the
pattern. When `routers/documents.py` called it last, the transaction stayed open
across the upload and the OCR, and a cancelled upload left Postgres logging
`unexpected EOF on client connection with an open transaction`.

**`monkeypatch.setattr` targets written as strings fail silently on a rename.**
Several tests patch `"app.services.analysis.steps.write.request_analysis_stage"`
and similar. A rename that misses one of these does not fail at import; it fails
as a test that quietly hits the real provider. Grep for the old module path after
any move.

**`analysis_instruction()` is not a prompt.** It turns `response_language` into
a short sentence so that `resolve_response_language()` can read the language back
out of it by looking for Thai codepoints. The sentence never reaches the model —
`execute_analysis_pipeline` takes `language`, not the message. The real prompts
are in `analysis/prompts.py`.

---

## 8. One trace, five readers

`CaseAnalysisTrace` is a single object, and changing it touches all five:

1. the model's structured-output contract (what the provider must return),
2. the stored record (`case_analysis_results.trace_json`),
3. the report's input (`reports/content.py` builds the seven sections from it),
4. the overview the frontend renders,
5. the attachment on the chat message that announces a finished analysis.

Adding a field is cheap. Changing or removing one is not: check all five before
you do.

---

## 9. Running it

```powershell
cd backend
python -m alembic upgrade head
uvicorn app.main:app --reload
python -m pytest tests -q
python -m ruff format . ; python -m ruff check .
```

Two tests in `tests/test_case_report_presentation.py` render a real PDF and need
WeasyPrint's native libraries (GTK on Windows). They pass inside the Docker
image, which installs them; without GTK they fail on the host and nothing else
does.
