# CyberCase Chat Backend

The FastAPI backend owns persisted chat, background runs, raw-evidence selection, external RAG orchestration, Main Case Analysis, bounded clarification, and chat-scoped reports.

## Authoritative evidence

`app/services/chat/raw_evidence.py` deterministically projects ordered user messages through a run's request message. It includes the initial incident, clarification answers, and explicit added case information. It excludes ordinary questions and every assistant-authored message.

Fresh-evidence runs call `rag_service POST /query`. Ordinary `ask` runs reuse the latest completed run's durable `RagContext` and do not invoke RAG. Validated analysis claims reference source message IDs, and the analysis trace binds the evidence hash and retrieval context.

## Database

The clean demo migration baseline creates only `chat_threads`, `chat_messages`, `chat_runs`, `rag_contexts`, and `chat_reports`. `RagContext.run_id` is unique, so each completed analysis run owns at most one retrieval snapshot. The baseline is intentionally incompatible with the deleted Case State/extraction schema.

```powershell
cd backend
python -m alembic upgrade head
```

## Routes

All routes use `/api/v1`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend and database health |
| `GET`, `POST` | `/chats` | List or create threads |
| `GET`, `PATCH`, `DELETE` | `/chats/{thread_id}` | Read, rename, or hard-delete a thread |
| `POST` | `/chats/{thread_id}/messages` | Persist a user message and enqueue a run |
| `GET` | `/chats/{thread_id}/runs/{run_id}` | Read run status |
| `POST`, `GET` | `/chats/{thread_id}/reports` | Generate or list report versions |
| `GET` | `/chats/{thread_id}/reports/{report_id}` | Read one report |
| `GET` | `/chats/{thread_id}/reports/{report_id}/pdf` | Download its PDF |

The service has no authentication, standalone case API, upload/OCR API, or frontend-facing RAG proxy.

## Reports

Reports are deterministic and template-first. A report snapshot contains raw source messages, the latest grounded analysis and trace, the associated retrieval context, admitted MITRE rows, and unresolved gaps. Generation does not run extraction or another RAG query.

## Run and verify

```powershell
cd backend
uvicorn app.main:app --reload
..\env_mitre\Scripts\python.exe -m pytest tests -q
..\env_mitre\Scripts\python.exe -m alembic heads
```
