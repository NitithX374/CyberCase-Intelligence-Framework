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
started = await read_case_for_analysis(...)  # one short transaction, then released
outcome = await think(pipeline, started)     # minutes, no connection held
step    = await store_outcome(...)           # another short transaction
```

**This is why there are three functions where you expected one.** Once you see
it, most of the layout stops looking arbitrary: anything that calls a model or
another service is surrounded by two small database functions.

The corollary is the rule the pipeline lives by: **no step of the pipeline
touches the database.** `pipeline.py`, `assess.py`, `write.py`,
`technical_context/` and `trace/` are handed what they need and return what
they produced; only `run.py`, `store.py` and `latest.py` read or write rows. That is also what lets an experiment run the same
steps over a dataset file instead of a case row.

---

## 2. Five files, in this order

| # | File | What you learn |
|---|------|----------------|
| 1 | `app/analysis/pipeline.py` | How a request assesses first, then either asks or runs the three full-analysis steps |
| 2 | `app/analysis/run.py` | The read/think/write split, and the follow-up loop |
| 3 | `app/trace/trace.py` | `CaseAnalysisTrace` — the object everything downstream reads |
| 4 | `app/followup/clarification.py` | Whether to ask the reader another question. Pure policy, no I/O |
| 5 | `app/reports/display.py` | How a stored trace becomes the report snapshot the HTML and PDF print |

After those five, the rest is plumbing you can read on demand.

---

## 3. The production advance and full analysis

```python
async def advance_case(data: AnalysisInput) -> AnalysisAdvance:
    assessment = await assess_gaps(data)                         # one small model call
    decision = decide_followup(gaps=assessment.gaps, ...)
    if not isinstance(decision, Proceed):
        return AnalysisAdvance(assessment=assessment, decision=decision)

    artifacts = AnalysisArtifacts()
    artifacts = await retrieve_technical_context(data, artifacts)
    artifacts = await write_analysis(data, artifacts)
    artifacts = await bind_to_case(data, artifacts)
    return AnalysisAdvance(assessment, decision, artifacts)
```

`advance_case` is the production request path. An askable gap stops it before
the MITRE gate, RAG retrieval, the two analysis calls, and claim binding. The
assessment row is stored with `status="assessment"` so its questions retain an
`analysis_result_id`, but it never moves `Case.latest_analysis_result_id`. Once the
rounds are spent the assessment is skipped too (`rounds_are_spent` in
`followup/clarification.py`), since `decide_followup` would proceed whatever it
found, and `AnalysisAdvance.assessment` is then `None`. A question is never stored
without its assessment.

`write_analysis` calls `write_trace` in `analysis/write.py`, which writes the
trace with a claims-only `case_reading` call selecting source-unit IDs,
then deterministic binding and NLI Claim/Source validation, followed by independent `case_views` and
`case_judgement` calls in parallel. The latter writes summary, gaps and ATT&CK
associations over the Claims; the former writes presentation views only.

`analysis/reading_sources.py` captures each source's revision before Reading and
sends exact unit text with source-local IDs (`U001`, etc.), unchanged Source IDs
and document quality headers. The same request-owned mapping expands selected
aliases to canonical revision-bearing IDs before `reading_from` builds claims.
Offsets and hashes stay backend-owned; stored citation IDs and stale checks are
unchanged. The prompt-JSON user message is minified without altering its values.

Between the two calls, `bound_claims` in `trace/bind.py` checks the reading
against the sources:
- `sources/evidence.py` partitions each source into exact-offset Evidence Units;
- `trace/evidence_binding.py` resolves selected IDs to original text and document/page locators;
- a `reported` claim left with no resolved supporting evidence becomes `not_confirmed`;
- the grounding counts are taken.

`analysis/claim_gate.py` runs `trace/claim_validation.py` after binding, in a worker
thread. Frozen B1-LR selects resolved Source units with pinned multilingual
MPNet cosine >=0.20, retaining the first maximum when none pass. Original
retained units are joined with a single newline. Pinned mDeBERTa applies
longest-first truncation512 and returns E/N/C probabilities; the frozen WiCE
TRAIN-fitted LR scores at0.50: `supported` at or above, `not_supported` below.
This is a task-specific decision boundary, not calibrated factual confidence.
The verdict is a warning label: it filters nothing and is never sent to a model.
The check runs concurrently with Judgement and the Views. Structural blockers
still withhold missing, unresolved, conflicting or uncertain support before
inference. An unavailable model is logged and the Claims are marked `unassessed`
(`verifier_unavailable`) without failing the analysis. All Claims/citations remain
stored, with selected indices/IDs, probabilities, LR score, artifact hash and
truncation diagnostics. Grounding counts passed and withheld Claims, selection,
calls and duration. An analysis abstains without Views/Judgement only when no
Claim passes the structural checks. Historical .80 verdicts remain historical.
See [the exact method and experiments](../research/attribution_benchmark/B1_INTEGRATION.md).

`analysis/views.py` batches the Claims supplied to Judgement from the same reading into one
prompt-structured LLM call. Input is only Claim IDs and text. Parties, Timeline and
Impacts use the existing `claim_ids` public shape.
Roles and combined date/time may be null. The backend validates schema and known
nonempty links, dropping an entire row if any link is unknown. It invents no field
offsets, confidence or semantic verdict. Structural binding is not Claim semantic
verification, and these views are not authoritative factual records.

Extraction runs concurrently with Judgement, using the existing model/provider,
thinking disabled, at most 4,096 output tokens and an overall 60-second deadline.
On failure, a recorded warning/status and empty views allow Judgement to complete.
Its failure cancels outstanding extraction. UI/Report views trace through Claims
to their Source units; no views enter Judgement/chat. Stored analysis snapshots
cache the output for reads/reports, without a new table or revision mechanism.
Historical local-extraction metadata and offsets remain readable. The former
local loader/per-Claim runtime and Compose service are removed. The encoder
and Claim support verifier have separate purposes; the stopped research experiments remain separate.

The judgement therefore reads only claims that pass the structural checks: their statuses, and only the
source spans that were resolved. Its payload retains Claim IDs but citation records
contain only original Source text. Source IDs, Evidence Unit IDs and document/page/
offset locators stay on the original Claims for binding, NLI, traceability and reports.
The backend derives source-ID lists from selected citations; the Reader generates
no source lists, reasoning summaries or independent
party, timeline or impact structures. Historical structured views remain readable
in saved traces and reports but do not enter Judgement or chat as factual authority.
`support=bound` describes evidence binding, not semantic support or factual
confirmation. Judgement is given neither the complete case sources nor the
separate context around each quotation. Attached Source spans can contain content
beyond the Claim text; valid Claim references do not verify every generated fact.
Follow-up input is limited to QA IDs, gap keys and answered flags; raw
questions/answers remain Reader Sources and stored provenance, preventing that
route from bypassing the structural checks. Technical context remains external. Judgement
references to withheld/unknown Claim IDs fail before joining the trace. Every
summary sentence ends with the IDs of the claims it rests on. Older saved Claims
without `semantic_grounding` remain unassessed; reads/reports do not run NLI.

`bind_to_case` then checks the judgement's references with `bound_references`:
- the `affected_claim_ids` of a gap;
- the claim IDs of each ATT&CK association, and its technique against the
  retrieved context;
- the claim IDs at the end of each summary sentence: `summary_units` is derived
  from the summary, each unit with its known claim IDs and a `support`, and the
  IDs that name no claim are counted in `grounding.summary_ids_unknown`.

A trace written without the middle step, as the one-call writer in
`experiments/analysis_arms.py` writes it, is bound in full there. The `verify` arm in
`experiments/analysis_arms.py` runs the same three steps without the
assessment. There is no arm switch or config value. The alternative compositions the thesis measures live in
`backend/experiments/analysis_arms.py`; each arm calls these same functions on
an `AnalysisInput` directly, with no case row. `run_case_analysis(pipeline=...)`
also accepts a substitute composition, as `tests/test_case_followup_postgres.py`
does. When that composition returns bare `AnalysisArtifacts`, `think` in
`analysis/run.py` wraps them as a `Proceed` with an empty assessment,
so `store_outcome` only ever sees an `AnalysisAdvance`.

**`experiments/` imports `app/`. `app/` never imports `experiments/`.** If that
ever reverses, an ablation has become production.

---

## 4. The follow-up loop keeps no state

One HTTP request advances the loop by exactly one step. Between steps, nothing
is held in memory and no table records "a loop is in progress". Everything is
re-derived from rows that already exist:

| Question | Answered by |
|---|---|
| How many rounds have been spent? | the number of distinct `analysis_result_id`s on messages with a `gap_key` (`rounds_asked` in `followup/conversation.py`) — one analysis is one round, however many questions it asked |
| Which gaps were already asked? | every `gap_key` on the case's messages, as a set |
| What did the reader answer? | the message whose `in_reply_to_message_id` is that question |
| Why did it stop? | `trace_json.stop_reason` on the analysis row |

`run_case_analysis` carries the rounds spent and the asked gaps only when it
continues a round: a reply closed the round, or the last question is answered and no
analysis has been stored since (`last_question_awaiting_analysis` in
`followup/conversation.py`). A fresh Analyze starts at round 1 with no gap marked
asked (`read_case_for_analysis` in `analysis/run.py`).
`next_question_of_round` in `chat/reply.py`, which picks the next question
inside a round, always uses the case-wide counts.

`post_case_message` in `chat/reply.py` makes the message paths explicit. A
new message with no question pending is ordinary chat and goes through
`answer_case_question`. A question stops being pending once an analysis has been
stored after it (`pending_question` in `followup/conversation.py`), so a message sent
after that analysis is not taken as its answer. A reply to the pending question
is stored, and the next question of the round is written in the same
transaction. A reply that spends the round closes that transaction before
calling `run_case_analysis`. A retried send, matched by `client_request_id`,
runs the round's analysis if that analysis was lost, answers a chat question
whose answer was lost, and otherwise returns the messages already stored. Two
sends with the same key at the same moment both pass that lookup; the one the
unique index refuses returns what the other stored and starts nothing.

A provider that fails for now (timeout, dropped connection, a 429 or 5xx, or a reply
that cannot be read, stops short of its end or breaks the stage's schema)
reaches the client as 502 or 504 (an analysis keeps a provider's 429), which the
frontend offers to retry: the model is not deterministic, so asking again often
succeeds. A dropped connection or a 429, 500, 502, 503 or 504 has already been asked
once more by then; a timeout has not. A refusal that retrying
cannot fix, such as an input over budget, rejected credentials, a model that
declines, or a changed case, stays a 4xx. A trace that binding cannot store is
our own fault and a coded 500 (`case_bind_invalid`), logged with its cause.

This is why the loop was **not** built with a state machine library. There is no
state to machine — each step reads the world, decides once, and writes.

The only state held in memory is what is in flight inside one request:
`analysing` in `cases/running.py` counts the analyses running per case,
and `answering` in `chat/answer.py` marks the questions being
answered. A retry reads them so that it returns what is stored instead of
starting the same work twice. This holds because the backend runs one process.
`POST /analysis`, through `sole_analysis` in the same module, and adding a source
answer 409 `analysis_in_progress` while the count is above zero. An answer in the
chat that closes a round is not covered: it still starts its own analysis.

`followup/clarification.py` holds the decision and nothing else: given the gaps, what has
been asked, and the budget, return `Ask` or `Proceed`. No database, no settings,
no model. It is the easiest file in the backend to test and the easiest to
reason about; keep it that way.

### Follow-up answers are conversation, not sources

A reader's answer becomes a **`ChatMessage`**, never a `CaseSource`. It is cited
as `QA-01`, `QA-02`. Reading and binding expose the answered text through the same
Evidence Unit abstraction as native sources, for example `QA-01:U001-<text hash>`.
It does not enter the persisted source bundle or bump `source_revision`.

This matters more than it sounds. `source_revision` is the case's "have the
facts changed" counter: an analysis is refused if the revision moved underneath
it. If answers were sources, every answer would invalidate the analysis that
asked for it.

---

## 5. Where a model is actually called

Five stages in four files, and all of them go through `request_stage` in
`llm/request.py`:

| Call | File | `stage` |
|---|---|---|
| The gap-only assessment | `analysis/assess.py` | `assess` |
| The reading: canonical claims with selected Source units | `analysis/write.py` | `case_reading` |
| The judgement: summary, gaps, ATT&CK associations | `analysis/write.py` | `case_judgement` |
| A chat answer, before or after an analysis | `chat/compose.py` | `chat_answer` |
| The MITRE applicability gate, when `MITRE_GATE_MODE=llm` | `analysis/technical_context/gate_llm.py` | `mitre_applicability` |

`request_stage` is the one transport: it checks the input against the token
budget, posts to OpenRouter's messages endpoint, retries once on a dropped
connection, and validates the reply against the stage's schema. All structured
stages append the complete JSON contract to the system prompt; no provider
`output_config`, `response_format` or schema grammar is sent. `llm/schema.py`
uses Pydantic to require every contract field recursively, forbid extra fields,
and check types, enums and bounds before applying the original DTO validators.
This prevents DTO defaults or coercion from hiding malformed model output.
`llm/payload.py` preserves exact source values in compact JSON and counts the
contract against the input budget. `llm/response.py` decodes provider envelopes.
Replies may be fence-stripped, then locally validated. A malformed or truncated
reply is asked again at most once; exhaustion raises `<stage>_invalid` for schema
violations or `<stage>_incomplete` for token limits. Refusals and timeouts are not
generation retries. Model, provider, temperature and token settings are unchanged.
A caller's `calls` list receives model, estimated input tokens, output mode,
request max_tokens, generation attempts, usage, status and elapsed time. Production
logs output mode and the request cap without prompt or source text. The encoder
gate (`MITRE_GATE_MODE=encoder`) runs a local model and calls no provider.

A chat answer reads what the analysis reads — the case sources, the answered
follow-ups and the technical context the latest analysis retrieved — and that
analysis too when there is one. The model returns units, each with a basis
(`case_fact`, `interpretation`, `technical` or `general`), the `claim_ids` it
rests on and exact quotes. `chat/compose.py` builds the request and invokes the
model; `chat/answer_contract.py` defines its reply. `chat/grounding.py` keeps only
claim ids of that analysis, verifies quotes against the original Source text,
and derives their locations. `chat/answer.py` stores the units on the message;
a unit whose citation fails keeps its text
without the citation. The log line `Chat answer grounding` counts cited and
uncited case facts per answer.

Retrieval is separate again: **one** call site, `analysis/technical_context/retrieve.py`,
over HTTP to the RAG service. The frontend never calls the RAG service.

---

## 6. Rules that look arbitrary and are not

**Package `__init__.py` files are empty, deliberately.** Python runs one on any
import below it. When they re-exported their modules, a router that wanted a
JWT helper loaded the PDF renderer and the whole analysis pipeline — and one
broken leaf broke the application. Import from the module that defines the
name. Only `models/__init__` holds code: it registers the tables.

**Data shapes live in contract files, never in a step.** `contracts.py` in a
feature folder, `trace/claims.py` and `trace/trace.py` hold types only. When the
technical-context record lived in the retrieval step, a report that only read it
imported the MITRE gate and the model transport, and case CRUD imported the
whole pipeline for a three-line freshness check. A type imports no behaviour.

**`app/main.py` refuses to start with more than one worker.** The analysis runs
inside the request that asked for it. Two workers would mean two analyses of the
same case racing for the same row.

**Heavy native libraries are imported inside the function that needs them.**
`reports/render.py` imports WeasyPrint inside `render_case_report_pdf`, because
WeasyPrint loads Pango and Cairo through `ctypes` at import time and raises if
they are missing. At module level, one absent system library would break every
import of `app.reports`. Same reasoning as the empty barrel.

**The MITRE retrieval is reused when the input has not changed.** The key is
`{source_revision, followup_answers}`, stored in `retrieval_context_json`
alongside the context it belongs to. Without this, every follow-up round
re-queried the RAG service with a byte-identical query and got a different
answer each time — one case in the database holds six analyses at revision 1
whose technique tables read 6, 6, 11, 10, 9, 9. The pipeline behind `/query` is
not deterministic, so "ask again" is not free and not neutral.

**A quotation's context is exact; only its display is cleaned.** When a quote
binds, `trace/bind.py` stores beside it the text around it, cut from the same
stored source by `trace/sentences.py`: the sentence before and the sentences the
quote touches, SaT at threshold 0.05 (PyThaiNLP `crfcut` when SaT cannot load)
line by line, at most 400 characters besides
the quote, with a trimmed side flagged. A quote found more than once gets none, because nothing
says which occurrence was meant. The drawer and the report show the OCR's own
markup — `<table>` rows and cells, `<page_number>` — as plain text, and leave
every other tag visible: in a phishing email the link is the point. The stored
context keeps every tag, so what is shown can always be traced back to the
source.

---

## 7. Things that will trip you

**A report prints what was stored, not the analysis as it is now.**
`reports/display.py` assembles one `CaseReportContent` snapshot when the report is
generated, and `case_reports.structured_report` holds it. The HTML and the PDF
render from that stored copy only. It delegates Source labels and quotes to
`reports/findings.py`, MITRE rows and notices to `reports/technical.py`, and
caveats to `reports/limitations.py`. A row stored in an older shape is refused
with `case_report_outdated` by the HTML, PDF and generate paths rather than rebuilt from current code,
and the report list leaves it out so the valid versions still load. A field added
later is optional, so an older row still validates: a report stored before
quotations carried context has no `supporting_contexts`, and its quotes print
alone. `supporting_quotes` stays a list of strings for that reason, with the
contexts beside it.

**The validator belongs to the report-fidelity experiment, not to the app.**
`StructuredReport`, `build_case_template_report` and
`validate_case_structured_report` live in
`experiments/report_fidelity/structured_report.py`, which is kept locally and
not tracked in git; nothing in `app/` builds or checks that shape. The
validator also checks less than it looks like. It does not check that a
report's `claim_id` exists in the trace, and every subset check passes
trivially for an empty list — so a claim the model invented, with no
sources and no techniques, is accepted. A report whose seven sections are all
empty is also accepted.

**`mitre_table` is not only techniques.** Entries include tactics (`TA0006`),
mitigations (`M1026`) and software (`S0008`) as they come back from retrieval.
Anything that renders "the techniques" should say which kinds it means.

**No transaction stays open across slow work.** `get_optional_user` runs a
`SELECT` on the request-scoped session and commits straight after it, so a route
starts with no transaction open. The document route in `sources/routes.py`
reads the upload and runs the OCR first and opens `async with db.begin()` only
around the write after it, and the source route beside it wraps only the
insert; a new route that writes after slow work follows the document route. The other writes are
shaped differently and still hold no transaction across slow work: `CaseService`
(`cases/service.py`) and `register_user`
(`auth/service.py`, which hashes the password before the write)
make one short write and call `db.commit()`, and
`CaseReportService.generate_report` opens `db.begin()` itself rather than in
the router. `POST /analysis` and `POST /chat/messages`
declare no request session; `run_case_analysis` and `send_case_message` open
their own short sessions around each read and each write, and none is open
during a model call. When the document route kept its transaction open
across the upload and the OCR, a cancelled upload left Postgres logging
`unexpected EOF on client connection with an open transaction`.

**Patch targets written as strings fail silently on a rename.**
Several tests patch `"app.analysis.write.request_stage"` or
`"app.llm.settings.settings.case_analysis_model"`. A rename that
misses one of these does not fail at import; it fails as a test that quietly
hits the real provider. Grep for the old module path after any move.

**No request carries a language; the backend decides it.** `analysis/language.py`
reads it from the case: `case_language()` is Thai when any source has a Thai
character, and `question_language()` answers a chat question in its own
language, keeping the case's language when the question has no letters (a reply
such as `02:00`). The real prompts are in `analysis/prompts.py`.

---

## 8. One trace, five readers

`CaseAnalysisTrace` is a single object, and changing it touches all five:

1. the model's structured-output contract (what the provider must return),
2. the stored record (`case_analysis_results.trace_json`),
3. the report's input (`reports/display.py` builds the report snapshot from it),
4. the overview the frontend renders,
5. the attachment on the chat message that announces a finished analysis.

Adding a field is cheap. Changing or removing one is not: check all five before
you do.

---

## 9. Running it

```powershell
cd backend
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
python -m pytest tests -q
python -m ruff format . ; python -m ruff check .
```

`requirements.txt` holds the backend, the verifier stack and the test tools
(pytest, pytest-asyncio, ruff, reportlab, pypdf). The schema comes from one migration,
`alembic/versions/0001_initial_schema.py`, and
`tests/test_database_schema_parity_alembic.py` checks that it matches the
models. The PostgreSQL tests skip unless `CYBERCASE_TEST_DATABASE_URL` is set.

Two tests in `tests/test_case_report_presentation.py` render a real PDF and need
WeasyPrint's native libraries (GTK on Windows). They pass inside the Docker
image, which installs them; without GTK they fail on the host and nothing else
does.
