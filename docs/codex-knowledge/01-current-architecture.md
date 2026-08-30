# Current architecture

## Product boundary

CyberCase is a single-user persisted chat with a chat-scoped report workspace. The backend is the orchestration and persistence boundary; the frontend never calls `rag_service` directly.

## Evidence model

The authoritative incident evidence is a deterministic projection of ordered raw user messages:

1. Include the first user incident statement.
2. Include user answers to persisted clarification questions.
3. Include messages explicitly submitted with `add_case_info`.
4. Exclude messages submitted as ordinary `ask` questions.
5. Exclude all assistant, RAG, MITRE, and model-authored text.

Each projection carries its ordered source message IDs and SHA-256. It is computed when needed and is not persisted as another case-state object.

## Run lifecycle

- Initial, clarification-answer, and add-information runs build the raw-evidence projection, call `rag_service /query`, run Main Case Analysis, and evaluate bounded follow-up.
- Ask runs load the latest completed run-bound `RagContext`, answer against that durable context, and do not invoke RAG.
- Completion persists the assistant message, analysis trace, and one `RagContext` bound to the completing `ChatRun`.
- The trace version is `analysis_trace_v2`; reported claims cite `source_message_ids`.

## Persistence

The clean demo baseline has five application tables:

- `chat_threads`
- `chat_messages`
- `chat_runs`
- `rag_contexts`
- `chat_reports`

There are no Case State, state version, extraction, entity, relationship, delta, audit-mutation, or user-ownership tables.

## Reports

The report snapshot reads the included raw source messages, latest grounded assistant analysis, its analysis trace, the matching `RagContext`, admitted MITRE rows, and unresolved gaps. The deterministic template validates source-message and MITRE references before persistence and PDF rendering.

## Frontend

The frontend exposes Chat and Report only. Removed extraction, Case State, and relationship URLs are not routes and resolve to Chat through route parsing.
