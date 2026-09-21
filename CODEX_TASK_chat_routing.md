# Task: make the chat message path readable from one file

## Repository

`CyberCase Intelligence Framework`. Work only in `backend/`.
FastAPI + SQLAlchemy (async) + PostgreSQL. Python 3.11.
Formatter/linter: `cd backend && python -m ruff format . && python -m ruff check .`

Read `backend/ARCHITECTURE.md` first. It explains the conventions this codebase keeps,
in particular **read short, think free, write short** — every slow operation is a short
read transaction, then work with no connection held, then a short write transaction.

This task changes **no behaviour**. It is a readability refactor with a hard test gate.

---

## 1. The problem

A person asked "where does a chat message go?" and could not answer it without opening
four files and reconstructing the flow in their head. That is the defect.

Everything lives in `backend/app/services/chat/case_chat.py`:

| line | function |
|---|---|
| 80 | `post_case_message` — the entry point |
| 122 | `messages_of_send` — idempotency: has this send already happened? |
| 141 | `answer_pending_question` |
| 196 | `next_question_of_round` |
| 231 | `messages_from` |

`post_case_message` today reads roughly:

```python
already = await messages_of_send(...)
if already is not None:
    return already, None

answered = await answer_pending_question(...)   # ← the whole problem
if answered is not None:
    return answered

question, answer = await answer_case_question(...)
return [question, answer], None
```

**`answer_pending_question` does four jobs at once**, and the reader cannot see any of them
from the call site:

1. it *decides* whether this message is an answer to a standing question,
2. it *writes* the answer row,
3. it either asks the round's next question **or** runs a whole new analysis,
4. it signals "not my path" by returning `None`.

So the branch that matters most — is this a follow-up answer or ordinary chat? — is encoded
in a return value, not in code anyone can read. There are four possible outcomes for one
message and none of them is named at the top level.

---

## 2. What to build

`post_case_message` must show all four outcomes, in order, in one function. Shape, not
exact text — the factoring is yours as long as the branches are visible:

```python
async def post_case_message(
    *, case_id: UUID, user_id: UUID | None, request: ChatMessageCreate,
    session_factory: Callable = async_session,
) -> tuple[list[ChatMessage], AnalysisStep | None]:
    """One message in. It takes exactly one of four paths, and they are all here."""

    if (already := await messages_of_send(session_factory, case_id, request.client_request_id)):
        return already, None                                   # 1. a retried send

    if await standing_question(session_factory, case_id, user_id) is None:
        return await reply_in_conversation(...)                # 2. ordinary chat

    recorded = await record_answer_and_ask_next(...)           # 3. answer, then next gap
    if recorded.next_question is not None:
        return recorded.messages, None

    return await analyse_after_round(...)                      # 4. round spent: analyse
```

The names are the documentation. A reader must be able to answer "where does my message go?"
by reading this function alone.

---

## 3. The trap that will bite you. Read this twice

Splitting "decide" from "write" naively **introduces a race that does not exist today.**

Right now `answer_pending_question` does everything inside one transaction that has taken a
row lock:

```python
async with session_factory() as db, db.begin():
    case = await owned_case(db, case_id, user_id)   # SELECT ... FOR UPDATE on the case row
    question = await pending_question(db, case.id)
    if question is None:
        return None
    answer = answer_message(...); db.add(answer); await db.flush()
    first_new_ordinal = answer.ordinal
    following = await next_question_of_round(db, case_id=case.id, question=question)
    if following is not None:
        db.add(following)
```

Two sends arriving together are serialised by that lock, so only one of them can be the
answer to a given standing question.

If you read the standing question in one transaction and write the answer in another, two
concurrent sends can both see the same standing question and both record an answer to it.

**Required:** the dispatch read may be lock-free, but the write transaction must take the
case row lock (`owned_case`) and **re-check `pending_question` inside it**. If the question
is gone by then, that send is no longer an answer — fall through to ordinary chat rather
than writing a second answer. Say in a comment why the re-check is there, so the next person
does not delete it as redundant.

---

## 4. Other things that must not change

**4a. The answer and the next question are written in one transaction.** A case must never be
left holding an answer with no next question and no analysis. Keep them atomic.

**4b. The analysis runs outside any transaction.** `run_case_analysis(..., continuing_followup=True)`
is called after the write transaction closes, deliberately — it takes minutes. Do not pull it
inside. This is the "read short, think free, write short" rule.

**4c. `first_new_ordinal`.** The response is every message from the reader's answer onward,
via `messages_from(session_factory, case_id, first_ordinal)`. Preserve exactly which messages
come back; the frontend appends them to the transcript.

**4d. Idempotency stays first.** `messages_of_send` uses `client_request_id` so a client that
gave up and retried gets what its first send produced. It must run before anything is written.

**4e. `CaseWorkflowError` is wrapped as `CaseChatError`.** Both `owned_case` and
`run_case_analysis` raise the workflow error; the chat boundary converts it. Keep the
conversion at both sites.

**4f. Returning from inside `async with db.begin()` commits.** The current `return None` for
"no standing question" opens and commits an empty transaction. Your dispatch read should be a
plain `async with session_factory() as db:` with no `begin()`, so the read path writes nothing.

**4g. Assessment rows.** `next_question_of_round` branches on `result.status == "assessment"`
and parses `CaseAssessmentTrace` instead of `CaseAnalysisTrace`. That branch is new and
correct — carry it over unchanged.

---

## 5. Acceptance criteria

1. **No test file changes.** Every existing test passes untouched. If you believe a test must
   change, stop and say which and why — a required test change means the behaviour moved, and
   this task does not move behaviour.

   ```
   cd backend
   CYBERCASE_TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/cybercase_framework \
     python -m pytest tests -q
   ```
   Baseline right now is **237 passed, 2 failed**. The two failures are
   `tests/test_case_report_presentation.py`, which render a real PDF and need WeasyPrint's
   native libraries (GTK); they fail on a Windows host and pass in the Docker image. Those two,
   and only those two, may still fail.

   **Without `CYBERCASE_TEST_DATABASE_URL` the PostgreSQL tests skip silently** — check the
   summary actually says 237, not a smaller number with skips.

2. The tests that cover the four paths are in `tests/test_case_followup_postgres.py` and
   `tests/test_case_chat_postgres.py`, including:
   - `test_replying_to_the_question_stays_conversation`
   - `test_the_round_asks_the_next_gap_before_spending_an_analysis`
   - `test_a_retried_send_gets_what_it_already_produced`
   - `test_a_question_that_was_answered_is_no_longer_pending`
   - `test_assessment_round_keeps_serving_its_remaining_gaps`
   - `test_asking_a_question_stores_both_messages`

3. Add **one** new test: two concurrent sends against a case with one standing question
   produce **exactly one** `followup_answer` row. Use `asyncio.gather`. This is the race in
   section 3 — without it, nothing stops a later refactor reintroducing it.

4. `python -m ruff format . && python -m ruff check .` clean.

5. `backend/ARCHITECTURE.md` section 4 ("The follow-up loop keeps no state") gains a short
   paragraph naming the four paths a message can take. The document is this backend's reading
   guide; leaving it stale is a defect.

---

## 6. Out of scope

- `services/analysis/` — do not touch. `pipeline.py` is the model this refactor imitates.
- The frontend. No API shape changes.
- The follow-up budget, `decide_followup`, or the gap policy.
- `answer_case_question` in `services/workflow/answer_question.py` — call it, do not rewrite it.
- Merging `services/cases/` or `services/clients/` (a separate cleanup).

## 7. Report back

Paste the final `post_case_message` and state, in one sentence each: what the four paths are,
and where the re-check that closes the race lives. If the concurrency test was hard to write
against the test harness, say so rather than dropping it.
