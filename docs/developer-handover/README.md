# CyberCase Developer Handover

## Document status

This handover describes the live working tree on branch `main` at commit `58f2302` on 2026-08-31. The working tree was already materially dirty when this report was created. The uncommitted backend Case Analysis and Stateful Follow-up implementation is part of the described system, but it is not yet a clean, immutable release baseline.

Use this guide for architecture and operational intent. Use [SYMBOL_INDEX.md](SYMBOL_INDEX.md) for the exhaustive file-by-file and function-by-function inventory. The index is generated from the checkout, includes line numbers and signatures, and covers runtime code, tests, migrations, evaluation utilities, research scripts, and repository tooling.

## Executive handover

CyberCase is a single-user, persisted-chat application that turns raw user-authored incident descriptions into a grounded case overview, optional MITRE ATT&CK technical context, bounded clarification, and a versioned chat-scoped report.

The most important rule is the evidence boundary:

- Initial incident messages, direct clarification answers, and messages explicitly submitted as added case information are authoritative incident evidence.
- Ordinary analyst `ask` messages are questions, not evidence.
- Assistant messages, prior model prose, RAG output, MITRE descriptions, and model knowledge are context, not incident facts.
- Every admitted analysis claim must point to persisted source message IDs.
- The backend binds analysis to the SHA-256 of the exact raw-evidence projection.

There is no canonical Case State aggregate, case-version workflow, entity graph, relationship graph, or interactive RAG `/resume` flow in the current product. Historical documents and research folders may describe those older designs. Do not reintroduce them through compatibility code.

The browser calls the FastAPI backend only. The backend owns persistence, run orchestration, evidence projection, LLM calls, optional RAG calls, follow-up policy, and reporting. The standalone RAG service is private infrastructure behind the backend.

## Current status and known handover risks

The latest verified backend implementation includes the v3 Main Case Analysis trace and Phase 5 stateful clarification. The previous validation run passed the full backend suite with 255 tests plus two subtests. That result belongs to the current dirty work and should be re-run before release.

Two behavior defects were still open at handover:

1. A semantically equivalent identity clarification can be re-asked when its wording falls outside the bounded deterministic alias set.
2. `frontend/src/lib/case-overview.ts` recognizes legacy/v2 analysis markers but does not yet project persisted `analysis_trace_v3`, leaving Overview in an analyzing state even when the Chat view has the completed analysis.

There is also contract drift in the root documentation. `backend/app/main.py` currently registers `/api/v1/document-ingestion/preview`, although `README.md` says there are no upload/OCR routes. Treat this endpoint as an isolated preview utility, not as a case-ingestion product workflow. It returns untrusted extracted content and does not create a chat, add evidence, call Main Analysis, call RAG, or generate a report.

Existing source files above the repository's 300-line rule include the RAG agent graph and several evaluation scripts, `frontend/src/lib/case-overview.ts`, `frontend/src/components/ChatWorkspaceLayout.tsx`, `frontend/src/components/ChatWorkspace.tsx`, and `backend/app/services/reports/report_view_model_builder.py`. New work should not make these files larger; split by responsibility behind stable imports.

## System topology

```text
Browser
  |
  | HTTP /api/v1
  v
Next.js frontend :3000
  |
  | chat, run, report, ingestion-preview requests
  v
FastAPI backend :8000
  |              |                 |
  | async SQL    | POST /query     | provider APIs
  v              v                 v
PostgreSQL    GraphRAG :8001    OpenRouter / Anthropic / Typhoon
                 |   |
                 |   +--> Neo4j graph expansion
                 +------> Qdrant vector search
```

PostgreSQL is the durable product state. The RAG service keeps an in-memory retrieval-context cache for its own retrieval snapshot endpoint, while the backend also persists the context and admitted MITRE rows in `rag_contexts` so chat and report behavior is not dependent on the RAG process cache surviving.

## Repository map

| Path | Ownership |
| --- | --- |
| `backend/app/main.py` | Backend ASGI entrypoint, lifecycle, CORS, and router registration. |
| `backend/app/config.py` | Environment-backed application settings for database, LLM, RAG, follow-up, reports, and document preview. |
| `backend/app/database.py` | Async SQLAlchemy engine, session factory, declarative base, and `get_db`. |
| `backend/app/models/` | Five durable application tables and relationships. |
| `backend/app/routers/` | Public backend HTTP surface. Routers should stay thin. |
| `backend/app/schemas/` | Pydantic request/response contracts. |
| `backend/app/services/chat/` | Thread/message persistence, idempotent run creation, raw-evidence projection, and clarification-chain reconstruction. |
| `backend/app/services/workflow/` | Background run leasing, execution, completion/failure transactions, and outcome mapping. |
| `backend/app/services/case_analysis/` | MITRE applicability gate, Main Analysis provider contract, v2/v3 compatibility reads, local validation, and canonical-state selection. |
| `backend/app/services/followup/` | Gap Analysis, claim transport, deterministic clarification state, next-gap selection, and question policy. |
| `backend/app/services/reports/` | Snapshot construction, deterministic template report, validation, persistence, HTML, and PDF. |
| `backend/app/services/document_ingestion/` | Isolated untrusted document extraction preview. No case persistence. |
| `backend/app/services/llm/` | Provider/model routing and structured-output requests. |
| `backend/app/services/clients/rag_client.py` | Backend-to-RAG HTTP client. |
| `backend/alembic/` | Single raw-evidence schema baseline and migration runtime. |
| `backend/tests/` | Backend behavior, provenance, orchestration, ingestion, report, and regression coverage. |
| `frontend/src/app/` | Next.js App Router entrypoints. Route files delegate to shared workspace components. |
| `frontend/src/components/` | End-user views for chat, intake, overview, materials, technical context, and report. |
| `frontend/src/features/chat/` | Chat route parsing, run polling/submission, and workspace lifecycle hooks. |
| `frontend/src/lib/` | API contract, evidence classifier, view projections, ingestion client/store, and error normalization. |
| `frontend/src/test/` | Vitest and Testing Library coverage. |
| `rag_service/app/main.py` | Private RAG FastAPI lifecycle and shared model initialization. |
| `rag_service/app/routers/` | RAG health, `/query`, and retrieval-context snapshot endpoints. |
| `rag_service/app/RAG/GraphRAG/` | STIX ingestion, retrieval, LangGraph reasoning, model configuration, evaluation, and CLI. |
| `Mitre_ATT&CK Doc/` | Source STIX 2.1 bundles. Data, not product runtime code. |
| `research/`, `experiments/`, `evaluation/`, `deliverables/` | Historical research, benchmarks, datasets, and thesis artifacts. They are not automatically active runtime dependencies. |
| `docker-compose.yml` | Local four-service topology: PostgreSQL, backend, RAG service, frontend. |
| `CONTINUITY.md` | Canonical compaction-safe current-work ledger. Read it before changing the code. |

## Product invariants

### Evidence

- Keep user-authored source messages byte-for-byte available in PostgreSQL.
- Build a deterministic ordered evidence projection before analysis.
- Exclude assistant content, `ask` messages, prior analysis, RAG, and MITRE prose from authoritative evidence.
- Persist `source_message_ids` and the evidence hash with analysis output.
- Fail closed when provider output violates provenance or structure.

### Analysis

- Main Analysis is domain-neutral general case review; it is not legal advice or automatic legal decision-making.
- A validated `case_overview` v3 trace is the only canonical v3 case-analysis state.
- A `question_answer` trace is response-scoped and cannot silently replace the canonical overview.
- Main Analysis does not invent source IDs or MITRE IDs.
- MITRE retrieval is optional. Analysis and follow-up must still complete when RAG is skipped or unavailable.

### Clarification

- Clarification improves a grounded summary; it does not block the first summary.
- Ask at most one focused question per completed run.
- Do not copy the assistant question into evidence.
- Store structural linkage from the answer to the exact prior question and selected gap.
- Exhaust an already answered normalized topic for the current chain.
- An explicit unavailable/not-provided answer becomes non-askable.

### Reporting

- Reports are chat-scoped, versioned, provisional, deterministic, and template-first.
- Report generation uses persisted raw messages, validated analysis, and the bound retrieval context; it does not call RAG again.
- Claims remain traceable to source messages.
- One logical generation operation reuses one idempotency key across retries.

### Frontend

- The frontend projects persisted backend state; it does not create a second case-state authority.
- `frontend/src/lib/case-evidence.ts` is the canonical client-side evidence classifier.
- End-user wording should explain meaning before exposing implementation details.
- Technical error strings belong in collapsed diagnostics, not the primary error message.

## End-to-end runtime flows

### 1. Create a chat

1. `POST /api/v1/chats` enters `backend/app/routers/chat.py`.
2. `ChatService.create_thread` creates a `ChatThread` with an idle status and ordinal counter.
3. The frontend invalidates the thread-list query and routes to `/chat/{threadId}/overview` or the selected workspace view.

### 2. Submit a message

1. `createChatMessage` sends content, an idempotency key, and optional action `ask` or `add_case_info`.
2. `ChatMessageService.create_message_and_run` opens the persistence boundary.
3. `create_message_and_run` locks the thread, checks the idempotency key and request fingerprint, rejects a conflicting active run, resolves the action, assigns the next message ordinal, and creates a queued `ChatRun`.
4. The router returns HTTP 202 with both the persisted message and run.
5. A FastAPI background task calls `process_chat_run`.
6. The frontend polls `/api/v1/chats/{threadId}/runs/{runId}` until the run is completed or failed, then refreshes the thread.

Idempotency is not optional. Reusing a key with the same request returns the existing run; reusing it with a different fingerprint is a conflict.

### 3. Claim and execute a run

`backend/app/services/workflow/` divides orchestration into small transaction boundaries:

1. `claim_run` acquires the queued or expired run lease, increments attempts, and reconstructs the request context.
2. `process_chat_run` dispatches to `_run_fresh_analysis` for initial/clarification/add-info work or `_run_question` for ordinary asks.
3. `complete_run` locks the owning thread and run, persists the assistant message, optional `RagContext`, analysis metadata, and final statuses atomically.
4. `fail_run` records a stable error code/message and releases the thread from the active state.

The lease fields permit recovery from a crashed worker. New worker code must preserve lease ownership checks so a stale worker cannot complete another worker's run.

### 4. Build authoritative raw evidence

`backend/app/services/chat/raw_evidence.py` is the trust boundary.

`load_raw_evidence_snapshot` reads ordered messages and `build_raw_evidence_snapshot` returns:

- the exact bounded combined evidence text;
- ordered source records;
- source message IDs;
- an SHA-256 binding;
- enough metadata for downstream provenance checks.

When changing message metadata, change the evidence classifier and its tests first. Do not infer evidence from `role == user` alone because ordinary analyst questions are also user messages.

### 5. MITRE applicability and optional retrieval

Fresh analysis calls `attempt_mitre_applicability` before RAG.

1. `build_mitre_applicability_prompt` provides fixed Thai/English examples and the current attributed evidence spans.
2. `MitreApplicabilityGate` requests structured output.
3. `validate_mitre_applicability` accepts only a valid `RETRIEVE` or a conservative `SKIP` record.
4. Invalid, uncertain, or provider-failed gate output resolves to `SKIP`.
5. Only a valid `RETRIEVE` calls `attempt_optional_rag` and `rag_service POST /query`.
6. RAG failure is recorded as unavailable and analysis continues without retrieval context.

The gate is a precision boundary. Do not replace it with keyword matching or make RAG failure fatal to general case analysis.

### 6. Main Case Analysis

`MainCaseAnalysisService` builds the provider request and parses the structured response.

The v3 provider contract emits visible answer text, summary, grounded claims, and optional MITRE candidates. Provider claim IDs are constrained to `A-01` through `A-64`. The backend—not the model—binds the evidence hash, retrieval context ID, admitted MITRE rows, and local validation result.

`validate_analysis_trace_v3` checks structure, source-message membership, provenance, claim links, and admitted MITRE technique IDs. Invalid output retains safe visible prose when possible but is not selected as canonical state and cannot drive canonical Gap Analysis or stateful follow-up.

`select_latest_canonical_case_overview` scans persisted assistant metadata and returns only the latest validated `case_overview` trace whose evidence binding is valid for the expected state.

### 7. Gap Analysis and Stateful Follow-up

After a valid fresh v3 Main Analysis:

1. `build_gap_analysis_claim_transport` sends only bounded grounded claim material into Gap Analysis.
2. `run_gap_analysis_stage` makes one structured gap-analysis provider call.
3. `assemble_claim_linked_gaps` binds local gap IDs and conservative claim links without changing the Main Analysis evidence binding.
4. `apply_clarification_history` applies persisted question/answer history to the new gap set.
5. `normalize_gap_key` performs deterministic NFKC, case, whitespace, punctuation, and bounded topic-alias normalization.
6. `select_next_gap` chooses the next askable unresolved gap.
7. `evaluate_followup_outcome` applies minimum-evidence and policy gates.
8. The existing question policy may generate one focused question.
9. Follow-up metadata records the gap ID, topic key, question evidence hash, and structural answer linkage.

No embeddings, semantic-dedup model, extra repair call, follow-up table, or Case State table are used.

### 8. Ordinary analyst ask

An explicit `ask` is not added to raw evidence.

The workflow loads the latest durable analysis/RAG context for the thread and calls the analysis provider in question-answer mode. It does not call the RAG service again. The resulting `question_answer` trace is response-scoped and cannot become canonical case overview state.

### 9. Report generation

`POST /api/v1/chats/{threadId}/reports` calls `ChatReportService`, which delegates generation to `run_report_generation`.

1. `build_current_report_snapshot` selects authoritative source messages, the latest valid analysis message, its retrieval context, admitted MITRE rows, and unresolved issues.
2. `source_snapshot_hash` binds the deterministic input.
3. `build_template_report` creates the seven-section structured report without another RAG call.
4. `validate_structured_report` enforces headings, support types, source IDs, and MITRE admission.
5. `ChatReportService` stores a versioned `ChatReport` and idempotency key.
6. `build_report_view_model` creates one presentation model shared by HTML and PDF.
7. `render_chat_report_html` or `render_chat_report_pdf` renders the persisted report.

Current integration debt: report persistence still requires a bound `RagContext`. A fresh analysis that validly skips or cannot reach RAG may therefore be analyzable but not reportable until the planned no-RAG report compatibility work is completed.

### 10. Document ingestion preview

`POST /api/v1/document-ingestion/preview` is intentionally isolated.

1. `_read_limited` enforces upload size while reading.
2. `detect_document` identifies supported PDF, DOCX, or image content.
3. Native DOCX/PDF parsers retain deterministic text and provenance where usable.
4. PDF/image rendering prepares bounded page images.
5. The region segmenter and router select native, OCR, or review-required handling.
6. `TyphoonDocumentRecognizer` performs configured OCR.
7. `ReviewRequiredHTRRecognizer` prevents handwriting transcription; HTR is disabled.
8. Reading-order merge constructs the preview document and block provenance.

The returned content is untrusted. No function in this path should persist a chat message or invoke analysis.

### 11. RAG query

`rag_service/app/main.py` loads one shared BGE-M3 embedding model and one `GraphRAGAgent` during lifespan startup.

`POST /query` runs the synchronous agent in a threadpool under a process-local concurrency limiter:

1. Cross-lingual logic detects response language and prepares English retrieval queries.
2. Query decomposition can create bounded atomic subqueries.
3. `VectorRetriever` searches Qdrant.
4. `Reranker` cross-encodes candidate relevance.
5. `HybridRetriever` applies type weights, deduplicates, and expands selected STIX IDs through Neo4j.
6. `context_builder` formats the evidence context.
7. `ContextEvaluator` returns `SUFFICIENT` or `INSUFFICIENT` with a bounded recovery strategy.
8. The agent may broaden retrieval within its fixed retry budget.
9. The reasoning model returns the best grounded answer or acknowledges the retrieval limit.
10. Thai output is produced directly in the configured single-call path or through the translation node.
11. The router stores an in-memory retrieval snapshot and returns context, MITRE table, and context ID to the backend.

There is no interactive user pause or `/resume` endpoint in this service.

## Persistence model

### `chat_threads`

Owns chat identity, title, thread status, the next message ordinal, timestamps, and cascading relationships to messages, runs, and reports.

Expected statuses are managed by service logic. Do not update thread status independently from run creation/completion transactions.

### `chat_messages`

Stores ordered user/assistant content, role, optional retrieval context ID, JSONB metadata, and timestamp. `metadata_json` carries action/evidence classification, analysis traces, follow-up linkage, and operational metadata without introducing parallel state tables.

### `chat_runs`

Stores one asynchronous processing attempt per accepted user message: request payload/fingerprint, idempotency key, queued/running/completed/failed status, attempt count, lease owner/expiry, error details, and timing.

### `rag_contexts`

Stores the retrieval context ID, owning thread/run, full context text, admitted MITRE rows, and creation time. It is one-to-one with the run.

### `chat_reports`

Stores the version, idempotency key, immutable source snapshot/hash, analysis message ID, retrieval context ID, prompt/provider/model settings, structured report, validation/failure state, timing, and token counts.

The baseline migration is `backend/alembic/baseline_versions/0001_raw_evidence_chat.py`. The intended demo database starts from that clean five-table schema; compatibility with deleted Case State schemas is not maintained.

## Public backend HTTP contract

All paths below are prefixed with `/api/v1`.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Database-backed backend health. |
| `GET` | `/chats` | List chat summaries. |
| `POST` | `/chats` | Create a chat. |
| `GET` | `/chats/{thread_id}` | Read the thread and ordered messages. |
| `PATCH` | `/chats/{thread_id}` | Rename the chat. |
| `DELETE` | `/chats/{thread_id}` | Delete the chat and cascading state. |
| `POST` | `/chats/{thread_id}/messages` | Persist a user message and queue an idempotent run. |
| `GET` | `/chats/{thread_id}/runs/{run_id}` | Poll run status. |
| `POST` | `/chats/{thread_id}/reports` | Generate and persist a report version. |
| `GET` | `/chats/{thread_id}/reports` | List report versions. |
| `GET` | `/chats/{thread_id}/reports/{report_id}` | Read one persisted report. |
| `GET` | `/chats/{thread_id}/reports/{report_id}/pdf` | Render/download the report PDF. |
| `POST` | `/document-ingestion/preview` | Isolated untrusted extraction preview; not a case workflow. |

The RAG service exposes private `/health`, `/query`, and `/retrieval-contexts/{context_id}` routes on port 8001. The frontend must not call them directly.

## Backend package handover

### Routers and schemas

`routers/chat.py` translates service errors into HTTP status/detail and otherwise delegates. `routers/document_ingestion.py` assembles the preview recognizer/pipeline per request. `routers/health.py` verifies the database.

`schemas/chat.py` defines message actions, thread/message/run responses, and acceptance payloads. `schemas/rag.py` mirrors the private backend-to-RAG contract. `schemas/reports.py` defines the fixed report version, seven section IDs/headings, claim support types, and API representation.

### Chat services

`chat_management.py` owns thread CRUD. `chat_message.py` is the facade used by the router. `chat_run_creation.py` owns idempotent message/run creation and action resolution. `clarification_chain.py` reconstructs question/answer exchanges exclusively from persisted metadata. `raw_evidence.py` owns evidence inclusion and hashing.

### Workflow services

`pipeline.py` constructs dependencies and retains the stable public entrypoint. `pipeline_dependencies.py` defines injectable persistence/provider functions for tests. `pipeline_execution.py` is the orchestration core. `rag_routing.py` contains non-fatal MITRE/RAG attempts. `chat_run_claim.py`, `chat_run_locks.py`, `chat_run_completion.py`, and `chat_run_failure.py` enforce transaction and lease boundaries. `outcome.py` builds immutable assistant outcome payloads. `worker.py` supplies the worker identifier and compatibility surface.

### Case Analysis services

`contracts.py` contains provider and persisted v2/v3 trace models. `case_analysis_prompt_builder.py` builds bounded separated evidence/context prompts. `case_analysis_executor.py` routes the structured request. `case_analysis_response_parser.py` normalizes provider IDs and constructs locally bound results. `validation.py` is the fail-closed provenance/structure gate. `compatibility.py` reads v2 or v3 without fabricating semantics. `state_selector.py` selects only canonical validated overview state. `mitre_applicability_*` implements the fixed gate contract/prompt/validation. `gap_assembly.py` conservatively connects canonical gaps to analysis claims. `personalization.py` limits language selection behavior.

### Follow-up services

`schemas.py` defines Gap Analysis and policy contracts. `gap_analysis.py` and `gap_stage.py` perform one gap call and normalize its result. `claim_transport.py` limits what analysis material reaches Gap Analysis. `stateful.py` applies persisted clarification history and selects the next gap. `decision.py` combines deterministic state with the policy result. `policy.py` calls the existing question model and builds a clarified query. `metadata.py` serializes stable trace/linkage fields. `context.py` bounds provider context. `helpers.py` centralizes response coercion. `compatibility.py` preserves the public follow-up result shape without restoring deleted architecture.

### Report services

`report_snapshot.py` is the trust boundary for report inputs. `report_template.py` is the deterministic content assembler. `report_validation.py` prevents unsupported claims. `report_generation.py` coordinates one run. `report_persistence.py` owns report version/idempotency state. `report_view_model_*` converts structured data into document-ready rows. `report_html.py` and `report_pdf.py` are stable render entrypoints; `pdf_design.py`, `pdf_chrome.py`, and `report_pdf_story.py` isolate layout details.

### LLM and clients

`llm/model_registry.py` resolves approved aliases/models. `llm/core_llm.py` constructs provider clients. `structured_output.py` defines structured response handling. `structured_output_router.py` and `structured_output_request_router.py` route provider-specific requests. `clients/rag_client.py` performs the backend-to-RAG HTTP request and validates its response.

## Frontend handover

### Route tree

| Route | View |
| --- | --- |
| `/` | Public landing page. |
| `/chat` | Chat workspace with no selected thread. |
| `/chat/{threadId}` | Redirect/default projection to Overview. |
| `/chat/{threadId}/overview` | Grounded case overview. |
| `/chat/{threadId}/chat` | Conversation transcript and composer. |
| `/chat/{threadId}/intake` | Case intake and document preview. |
| `/chat/{threadId}/materials` | Source-message material projection. |
| `/chat/{threadId}/technical-context` | RAG/MITRE technical context projection. |
| `/chat/{threadId}/report` | Report generation, history, and PDF access. |

`chat-route.ts` is the canonical path-to-view mapping. Route `page.tsx` files remain thin and render shared workspace components.

### State and API

`app/providers.tsx` installs React Query. `hooks/use-chat-queries.ts` owns query/mutation hooks. `lib/api-client.ts` is the low-level Axios boundary and is the only normal place to add backend calls. `lib/api-types.ts` mirrors backend payloads. `lib/query-keys.ts` stabilizes React Query cache keys.

`use-chat-submission.ts` creates one idempotency key, submits, polls the run, and refreshes state. `chat-polling.ts` contains terminal status and polling behavior. Workspace selection/deletion hooks isolate navigation and mutation side effects.

### View projections

`case-evidence.ts` decides which persisted messages are source evidence. `case-overview.ts` converts analysis metadata into Overview sections. `case-materials.ts` projects source evidence for human review. `technical-context.ts` presents RAG/MITRE as external technical context. `chat-followup.ts` recognizes follow-up metadata. `mitre-candidate.ts` parses candidate mappings. These are read projections only.

### UI components

`ChatWorkspace.tsx` coordinates server state and selection. `ChatWorkspaceLayout.tsx` owns the responsive shell/sidebar/view selection. Conversation components render markdown, transcripts, composer state, and MITRE candidate cards. Overview components render the case story, established versus unclear facts, investigation points, simple MITRE explanations, and source popovers. Report components manage generation/idempotency, persisted versions, and download. `MeaningfulErrorModal.tsx` presents user-facing recovery plus collapsed diagnostics.

## RAG package handover

### Configuration and models

`GraphRAG/config.py` reads provider, model, Qdrant, Neo4j, embedding, reranker, and retry settings. `model_registry.py` resolves aliases. `models.py` defines graph state and retrieval/evaluation records. `llm_provider.py` constructs provider-specific chat models. `llm_content.py` extracts text safely.

### Ingestion

`ingestion/stix_parser.py` parses STIX 2.1 bundles into nodes, relationships, and vector documents. `graph_loader.py` writes graph entities/edges to Neo4j. `vector_loader.py` embeds and upserts Qdrant points. `GraphRAG/main.py --ingest` is the operational entrypoint.

### Retrieval

`vector_retriever.py` embeds queries and searches Qdrant. `reranker.py` cross-encodes candidates. `graph_retriever.py` expands STIX seeds in Neo4j. `hybrid_retriever.py` merges vector and graph results, supports multi-query deduplication, and quota-based coverage.

### Pipeline

`agent_graph.py` is the LangGraph state machine and currently exceeds the line limit. `router.py` classifies query type but incident routing is currently forced. `cross_lingual.py` detects/normalizes language and prompt roles. `query_decomposer.py` creates bounded retrieval subqueries. `query_sanitizer.py` rejects unusable rewrites. `context_builder.py` formats combined evidence. `evaluator.py` judges sufficiency and recovery. `chain.py` contains the simpler non-agent chain. `mitre_table.py` converts retrieval results into backend-facing MITRE rows.

### Evaluation

Files under `GraphRAG/evaluation/` are offline benchmarking utilities and datasets, not request-path modules. Several are intentionally large historical scripts. Run them explicitly; importing the web service does not execute them.

## Configuration and secrets

Important environment values:

| Variable | Consumer | Meaning |
| --- | --- | --- |
| `DATABASE_URL` or `POSTGRES_*` | Backend | Async PostgreSQL connection. |
| `CORE_LLM_PROVIDER` | Backend and RAG | `openrouter` or `anthropic`. |
| `OPENROUTER_CYBERCASE` | Backend and RAG | OpenRouter credential. |
| `ANTHROPIC_API_KEY` | Backend and RAG | Anthropic credential. |
| `RAG_SERVICE_URL` | Backend | Private RAG base URL. |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | RAG | Graph database. |
| `QDRANT_URL`, `QDRANT_API_KEY` | RAG | Vector database. |
| `HF_TOKEN`, `HF_HOME` | RAG | Model download/cache. |
| `NEXT_PUBLIC_API_URL` | Frontend | Browser-facing backend `/api/v1` URL. Required at runtime. |
| `TYPHOON_OCR_API_KEY` | Backend preview | OCR credential. |

Use Doppler for local secrets. Do not commit `.env` or paste provider payloads containing source evidence into tickets.

## Local setup

### Docker Compose

```powershell
doppler run -- docker compose up --build
```

Expected ports:

- Frontend: `http://localhost:3000`
- Backend/OpenAPI: `http://localhost:8000/docs`
- RAG service: `http://localhost:8001`
- PostgreSQL host port: `5433`

The backend and frontend are bind-mounted for development. The RAG service expects the host Hugging Face cache and, in Compose, an NVIDIA device reservation. Cloud Neo4j and Qdrant credentials are required.

### Separate processes

```powershell
.\env_mitre\Scripts\Activate.ps1
python install_deps.py
cd backend
doppler run -- python -m alembic upgrade head
doppler run -- uvicorn app.main:app --reload
```

```powershell
cd rag_service
doppler run -- uvicorn app.main:app --host 0.0.0.0 --port 8001
```

```powershell
cd frontend
npm install
npm run dev
```

## Validation matrix

Run the narrowest relevant checks first, then the full suite before handoff.

```powershell
.\env_mitre\Scripts\python.exe -m pytest backend\tests -q
```

```powershell
cd frontend
npm run test
npm run lint
npm run build
```

```powershell
.\env_mitre\Scripts\python.exe -m pytest rag_service\tests -q
```

For RAG changes, also run the relevant offline retrieval/generation evaluation. Do not describe a benchmark as passing unless the model, dataset, credentials, and external stores actually ran.

For database work:

```powershell
cd backend
python -m alembic heads
python -m alembic upgrade head
```

For diff hygiene:

```powershell
git diff --check
git status --short
```

## Debugging playbook

### A run remains queued or running

1. Read `chat_runs.status`, `lease_owner`, `lease_expires_at`, `attempt_count`, `error_code`, and `error_message`.
2. Confirm the background task was scheduled by the message router.
3. Check backend logs for claim, RAG, provider, validation, and completion markers.
4. Confirm the worker still owns the lease before changing completion logic.
5. Do not manually insert assistant messages; repair the run transition.

### Analysis prose exists but no canonical trace

1. Inspect assistant `metadata_json` for `analysis_trace_v3` and failure metadata.
2. Capture the raw provider response shape from safe logs.
3. Check claim IDs, source-message IDs, evidence hash, MITRE admission, and trace kind.
4. Reproduce the exact local validator failure.
5. Fix the narrow provider/parser/validator boundary; do not add retries or a repair LLM call.

### Overview says it is still analyzing

1. Verify the run completed and the assistant message contains v3 trace metadata.
2. Trace `frontend/src/lib/case-overview.ts` recognition and `CaseOverviewView.tsx` rendering.
3. Confirm React Query refreshed the selected thread.
4. Remember the current known v3 projection defect before diagnosing persistence.

### RAG is unavailable

1. Call RAG `/health` and inspect service startup logs.
2. Verify the BGE model loaded and the shared agent exists.
3. Check Qdrant and Neo4j credentials/DNS independently.
4. Confirm the backend recorded RAG as unavailable and continued general analysis.
5. Do not turn external retrieval failure into loss of raw case evidence.

### Report generation fails

1. Inspect the latest validated analysis message ID and retrieval context ID.
2. Confirm the persisted `RagContext` belongs to the same thread/run.
3. Build the report snapshot and inspect validation errors before rendering.
4. Reuse the same idempotency key for a retry of the same logical operation.
5. Distinguish snapshot/validation failure from PDF rendering failure.

### Document preview fails

1. Identify the detected document kind and enforced limits.
2. Separate native parser, renderer, segmentation, routing, and recognition failures.
3. Check Typhoon configuration and timeout without logging document contents.
4. Keep handwriting review-required; do not silently enable HTR.

## Safe change playbooks

### Add or change a backend endpoint

1. Confirm the route belongs inside the chat-first public boundary.
2. Define or update Pydantic schemas.
3. Put business logic in a service module, not the router.
4. Preserve async database sessions and transaction boundaries.
5. Add router and service tests.
6. Update `frontend/src/lib/api-types.ts` and `api-client.ts` if browser-facing.
7. Update this handover and regenerate the symbol index.

### Change evidence semantics

1. Update backend raw-evidence classification and characterization tests.
2. Update `frontend/src/lib/case-evidence.ts` to match.
3. Verify existing hashes and source IDs are not silently reinterpreted.
4. Re-run analysis, follow-up, report, materials, and overview tests.
5. Document the decision in `CONTINUITY.md`.

### Change Main Analysis

1. Keep provider and persisted contracts separate.
2. Keep source-ID and MITRE-ID validation fail closed.
3. Preserve safe visible prose without promoting invalid canonical state.
4. Verify question-answer traces cannot replace case-overview state.
5. Prove provider call counts; do not add hidden repair stages.

### Change follow-up behavior

1. Start from canonical v3 gaps and persisted structural linkage.
2. Preserve deterministic exhaustion and unknown handling.
3. Add characterization tests for wording variations and each case domain.
4. Keep at most one question generation call.
5. Do not make follow-up dependent on RAG availability.

### Change reports

1. Keep snapshot construction deterministic and evidence-bound.
2. Change the typed report contract and validators together.
3. Keep one shared view model for HTML/PDF.
4. Test idempotency, versioning, source IDs, MITRE admission, and PDF output.
5. Do not call RAG during report generation.

### Change RAG

1. Keep the backend-facing `QueryResponse` stable or update both services atomically.
2. Bound agent retries and model cost.
3. Test retrieval, graph expansion, context construction, and sufficiency separately.
4. Run evaluation before claiming ranking or answer-quality improvement.
5. Preserve graceful backend behavior when RAG is unavailable.

## New developer first week

Day 1:

- Read `AGENTS.md`, `CONTINUITY.md`, this guide, and the current Git diff.
- Run the backend and frontend tests without changing code.
- Create a chat, submit an incident, and inspect all five tables.

Day 2:

- Trace one fresh run from the HTTP request through completion.
- Compare raw source messages, evidence snapshot/hash, RAG context, v3 analysis trace, gap metadata, and assistant output.

Day 3:

- Trace the same persisted thread through Overview, Materials, Technical Context, and Report.
- Reproduce the current v3 Overview projection defect in a disposable thread.

Day 4:

- Run one RAG query and inspect vector hits, graph expansion, evaluator verdict, context snapshot, and admitted MITRE rows.
- Review offline evaluation code without treating it as production runtime.

Day 5:

- Take one small bug with an existing failing characterization test.
- Preserve the dirty-worktree ownership boundary and avoid broad cleanup.
- Report exactly which checks ran and what was not validated live.

## Handover checklist before release

- Confirm branch, commit, remote parity, and dirty-file ownership.
- Resolve or explicitly defer the v3 Overview projection defect.
- Resolve or explicitly defer equivalent-topic clarification re-asking.
- Decide whether no-RAG analyses must be reportable and implement/test that decision.
- Reconcile the document-ingestion preview route with the stated public API boundary.
- Split production files that violate the 300-line rule before extending them.
- Run full backend, frontend, and relevant RAG checks.
- Run a live end-to-end incident through chat, clarification, overview, materials, technical context, report, and PDF.
- Verify secrets and raw evidence are absent from logs, commits, and generated documentation.
- Update `CONTINUITY.md` with the release state and exact receipts.

## Maintaining this report

Regenerate the exhaustive index after moving, adding, or changing source symbols:

```powershell
python docs\developer-handover\generate_symbol_index.py
```

The generator reads tracked and untracked first-party `.py`, `.ts`, `.tsx`, `.js`, `.jsx`, and `.mjs` files, uses Python and TypeScript syntax trees, and rewrites `SYMBOL_INDEX.md`. Generated one-line descriptions are navigation summaries. For complex business semantics, update this handover narrative as well.

Keep the generator scripts under 300 lines and do not add generated data, dependencies, virtual environments, or build outputs to the source index.
