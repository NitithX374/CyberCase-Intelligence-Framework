# AGENTS.md — CyberCase Intelligence Framework

## Where the architecture lives

This file used to carry its own copy of the architecture, and it went stale: it
described `case_analysis/`, `case_workflow/` and `technical_context/` for weeks
after those packages were renamed, and sent people hunting for files that no
longer existed. Two descriptions of one system always drift. There is now one.

| Read this | For |
|---|---|
| `CLAUDE.md` | the whole system — services, endpoints, layout, configuration, commands |
| `backend/ARCHITECTURE.md` | how to read the backend: the one rule behind the file layout, the five files to start with, and the traps |
| `backend/README.md` | the backend's HTTP boundary and persistence |
| `frontend/README.md` | the frontend's folders and its generated API types |

If something here and the code disagree, the code wins — and fix the document
in the same change rather than leaving the next person to discover it.

---

## Coding guidelines

### Modularization

- Organise code around cohesive responsibilities and stable interfaces.
- **There is no line-count limit.** Do not split a file to hit a number. Split
  when it materially improves readability, testing or ownership.
- A package earns its own directory by holding enough to be worth remembering
  where it is. Two small files are usually a module, not a package.

### Python & FastAPI

1. **Async everywhere.** `async def`, and await database work through
   SQLAlchemy's async session. Never block the event loop — CPU-bound work
   (PDF rasterising, image encoding) goes through `asyncio.to_thread`.
2. **Type-safe boundaries.** Every request and response is a Pydantic model.
3. **Sessions come from `get_db`, and no transaction stays open across slow
   work.** `get_optional_user` runs a `SELECT` and commits straight after it,
   so a route starts with no transaction open. A route that writes after slow
   work — a model call, an upload, OCR — does the slow part first and opens
   `async with db.begin()` only around the write. Follow the document upload in
   `sources/routes.py` for a new route. The other writes are shaped differently and still hold no
   transaction across slow work: the case routes and registration make one
   short write and call `db.commit()` in the service
   (`cases/service.py`, `auth/service.py`, which
   hashes the password before the write), and report generation opens
   `db.begin()` inside `CaseReportService.generate_report`. `POST /analysis` and
   `POST /chat/messages` declare no session; the workflow opens its own short
   ones.
4. **Read short, think free, write short.** One short transaction to read, the
   slow work with no connection held, another short transaction to write. This
   is the rule most of `backend/app/` is shaped by; `backend/ARCHITECTURE.md`
   section 1 explains it.
5. **Import heavy native libraries inside the function that needs them.**
   WeasyPrint loads Pango and Cairo through ctypes at import time and raises if
   they are missing; at module level that breaks every import of the package
   around it.
6. **One error type, one ownership check.** A service error is `AppError`
   from `app/errors.py`, or a subclass of it, carrying a code, a message and a
   status; the one handler in `app/main.py` turns it into
   `{"detail": {"code": ..., "message": ...}}`. Load a case through
   `owned_case` in `cases/ownership.py`, which answers 404 for a case
   the user does not own.

### LangGraph agentic loops (`rag_service/`)

1. **State is immutable.** Nodes in `agent_graph.py` return a modified state
   dictionary; they do not mutate keys in place.
2. **The evaluator returns `SUFFICIENT` or `INSUFFICIENT`.** An insufficient
   result picks a bounded recovery — `BROADEN_SEARCH` or `ACKNOWLEDGE_LIMIT`.
   It never pauses for user input; that pipeline has no way to ask anything.
3. **Bound every loop.** Self-reflection runs at most twice. An unbounded loop
   here is unbounded spend.

### Next.js & React (`frontend/`)

1. **React 19 + Tailwind v4.** Utility-first styling with native v4 class names.
2. **Strict TypeScript.** No `any`. Interfaces for props, state and every API
   return value — the generated types in `src/lib/api/generated/` are the
   contract with the backend.
3. **Server state belongs to TanStack Query, not to `useState`.** State that
   describes something the server is doing — an analysis in flight, an answer
   being sent — must survive the component unmounting. `features/analysis/queries.ts`
   reads a running analysis from the mutation cache by its key
   (`useIsMutating`), and `useIsFollowupPending` in
   `features/chat/useCaseChat.ts` does the same for an answer.

### Tests

- Tests never sit beside the code they test. Backend tests are in
  `backend/tests/`, and `tests/test_layout.py` fails on a test file under
  `app/`. Frontend tests are in `frontend/src/test/`, at the path of the file
  they test, import through `@/`, and `npm run lint` fails on a test file
  anywhere else.
- The test tools are in `backend/requirements-dev.txt`, which also pulls in
  `requirements.txt`.
- `cd backend && python -m pytest tests -q` skips the PostgreSQL tests
  **silently** unless `CYBERCASE_TEST_DATABASE_URL` is set. Check the count,
  not just the colour.
- `monkeypatch.setattr` targets written as module-path strings do not fail on a
  rename — they fail as a test that quietly calls the real provider. Grep for
  the old path after moving anything.
