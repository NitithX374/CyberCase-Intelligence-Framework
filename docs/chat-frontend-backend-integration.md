# Chat frontend-backend integration

## Ownership

- Frontend: selection, presentation, request cancellation, and polling.
- Backend: message ordering, action semantics, raw-evidence projection, run lifecycle, RAG orchestration, follow-up, analysis, and reports.
- PostgreSQL: threads, messages, runs, run-bound retrieval contexts, and reports.
- `rag_service`: external retrieval and MITRE context through backend-only `/query` calls.

## Message flow

```text
POST /api/v1/chats/{thread_id}/messages
  -> lock thread
  -> persist ordered user message with evidence_kind/action metadata
  -> create queued ChatRun
  -> return 202
  -> worker claims run
  -> build raw evidence through request message
  -> fresh RAG or ask-context reuse
  -> Main Case Analysis
  -> follow-up decision
  -> persist assistant message, RagContext, and completed run
```

The frontend polls thread/run state and renders persisted results. It holds no RAG session or case representation.

## Actions

The composer exposes ordinary `ask` and `add_case_info` after an answered analysis. Ask is excluded from the incident evidence and reuses the latest durable retrieval context. Added information is evidence and triggers fresh retrieval. A message answering a backend clarification is classified automatically as a clarification answer.

## Workspace routes

- `/chat`
- `/chat/{thread_id}`
- `/chat/{thread_id}/report`

There are no extraction or relationship workspaces.

## Reports

The Report tab uses chat-scoped backend endpoints. Generation reads raw evidence, latest grounded analysis, the matching retrieval context, admitted MITRE rows, and unresolved gaps. It does not run another RAG query.

## Current limits

- single-user with no authentication or ownership filter;
- thread deletion is permanent;
- deleting a processing thread cannot cancel an already-running upstream request;
- reports remain provisional and unverified.
