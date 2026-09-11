# Case-first implementation — Checkpoint A

Date: 2026-09-10
Status: COMPLETE — audit and contracts gate passed
Plan: `docs/developer-handover/CASE_FIRST_LUNA_IMPLEMENTATION_PLAN.md`

## Scope and evidence

This checkpoint records the implementation baseline before changing the Case-first schema. It is based on the current `main` checkout, the current working-tree diff, the running Docker stack, the live PostgreSQL catalog, and the backend OpenAPI document. It does not treat a filename search or an old test result as proof of runtime behavior.

The implementation scope is now authorized by the user. The handover plan remains the design baseline; this artifact resolves the items that must not remain ambiguous when Checkpoint B starts.

## Repository baseline

| Item | Observed value |
| --- | --- |
| Branch | `main` |
| HEAD | `e4f179192f812840dc99ea3c1e914f7b5507af86` |
| Applied migration head | `0005_case_domain` |
| Working tree | Dirty before this implementation; all existing modifications and untracked files are user-owned and preserved |
| Protected path | `rag_service/**` remains out of scope |
| Code-size rule | Every modified/new code file must remain at or below 300 physical lines |
| Runtime database | PostgreSQL 16.15 in `cybercase-postgres` |

The dirty baseline includes the existing Case/Chat naming changes, authentication changes, frontend routing/workspace changes, document-ingestion changes, tests, and handover artifacts. No baseline file is to be reset, checked out, staged, or deleted as part of this work merely because it is already dirty.

## Live PostgreSQL baseline

The following values were queried from the running PostgreSQL container on 2026-09-10 before the new migration was created:

| Relation | Rows |
| --- | ---: |
| `cases` | 2 |
| `chat_threads` | 2 |
| `chat_messages` | 0 |
| `chat_runs` | 0 |
| `rag_contexts` | 0 |
| `chat_reports` | 0 |

Additional checks:

- orphan `chat_threads` without a matching `cases.id`: `0`
- `cases` without a matching shared-identity `chat_threads.id`: `0`
- active legacy `chat_runs` (`queued` or `running`): `0`
- no persisted legacy messages, runs, contexts, or reports currently exist in this environment

The current database therefore cannot prove a historical analysis backfill. The migration must still handle a populated legacy database by preserving only references that exist in the source rows; unresolved legacy records must remain explicitly unresolved instead of being assigned invented evidence or message IDs.

## Current schema and ownership findings

The current `0005_case_domain` migration:

- creates `cases` and copies every existing `chat_threads` row into a Case;
- changes `New chat` to `New case`;
- adds `fk_chat_threads_id_cases`, so the shared UUID is currently the only Case-to-Chat relationship;
- leaves ChatThread as the owner of processing status;
- has no native Case document, extraction, admitted evidence, snapshot, CaseRun, or AnalysisResult relations.

The current application contract still has these Case-first blockers:

- `CaseService.create_case` eagerly creates a ChatThread;
- `CaseRead.chat_thread_id` is non-null;
- `CaseRead.status` is serialized from `ChatThread.status`;
- `ChatRun` requires both `thread_id` and `request_message_id`;
- `chat_run_creation.py` combines user-message creation, evidence classification, run creation, ordinal allocation, and thread processing state;
- `raw_evidence.py` reconstructs authoritative evidence from user messages and first-message/evidence-kind rules;
- workflow claim/completion is ChatThread/ChatRun based;
- canonical analysis selection reads assistant messages and trace metadata;
- reports require `analysis_message_id` as the current authority;
- the Case frontend still passes thread/message state through `ChatWorkspace` and blocks some views on message presence.

These are recorded as work to be changed in later checkpoints, not silently treated as already migrated.

## Confirmed ownership contract

| Domain | Authoritative ownership | Explicit boundary |
| --- | --- | --- |
| Case | identity, owner, title, evidence revision, latest successful analysis pointer | no worker or message orchestration |
| Materials/Evidence | documents, extraction revisions, admitted evidence revisions, immutable snapshots | extraction is not admission; no assistant/RAG evidence |
| Analysis | immutable validated result and source references | no required ChatThread; no fabricated ChatMessage |
| Workflow | CaseRun queue, lease, retry, completion transaction | reads pinned snapshot; no rebuild from mutable materials |
| Chat | optional transcript, ordinal allocation, user/assistant messages | does not own Case processing status |
| Clarification | durable question state and answer linkage | stale questions cannot silently target another result |
| Reporting | report snapshot bound to AnalysisResult and evidence snapshot | legacy message link is compatibility metadata only |

Resolved decisions for implementation:

- **A-01:** Case creation creates no ChatThread. Opening Chat or publishing the first successful result creates the one allowed thread transactionally.
- **A-02:** New worker ownership is a Case-owned `case_runs` relation. Existing `chat_runs` remains a legacy compatibility relation until validated migration and caller cutover are complete.
- **A-03:** A Case has at most one active CaseRun. ASK is serialized with analysis to keep evidence/result context deterministic.
- **A-04:** Evidence edits during a run create new immutable revisions. The run is pinned to its enqueue-time snapshot and may finish stale relative to newer evidence.
- **A-05:** Native Case evidence uses native evidence-source/revision UUIDs. No document or Case-page action inserts a hidden user ChatMessage or supplies a synthetic `source_message_id`.
- **A-06:** Legacy message evidence is mapped only when the actual message row and its established evidence role are present. Otherwise the migration preserves an explicit `legacy_unbound` record/receipt and does not claim provenance.
- **A-07:** The existing analysis provider operation is reused. Summarize/Analyze is one CaseRun operation for this phase; wording does not create a second provider pipeline.
- **A-08:** Chat publication stores an immutable display copy plus the AnalysisResult reference. It never calls an LLM to rewrite the result.
- **A-09:** PostgreSQL constraints and real transaction/race tests are mandatory before cutover. SQLite-only checks are insufficient for migration/concurrency gates.

## Endpoint and type inventory

The live backend currently exposes:

`/api/v1/auth/*`, `/api/v1/health`, `/api/v1/cases`, `/api/v1/cases/{case_id}`, `/api/v1/chats`, `/api/v1/chats/{thread_id}`, `/api/v1/chats/{thread_id}/messages`, `/api/v1/chats/{thread_id}/reports`, `/api/v1/chats/{thread_id}/reports/{report_id}`, `/api/v1/chats/{thread_id}/reports/{report_id}/pdf`, `/api/v1/chats/{thread_id}/runs/{run_id}`, and `/api/v1/document-ingestion/preview`.

Checkpoint B will add Case-owned material/evidence and snapshot contracts. Checkpoint C will add Case analysis enqueue/read/run contracts. Existing Chat routes remain readable and writable only through an explicit compatibility adapter until their ownership no longer conflicts with the Case workflow contract. No standalone RAG proxy or `rag_service` route is added.

The frontend inventory confirms that `CaseRead` currently carries `id`, `user_id`, `title`, thread-derived `status`, non-null `chat_thread_id`, and timestamps. The new type contract must make `chat_thread_id` nullable and add explicit Case processing/freshness fields without making Chat a prerequisite for rendering Case Intake or Overview.

## Provenance and migration fixture strategy

The implementation test fixtures will include:

1. A fresh Case with no ChatThread and no evidence.
2. One Case with two native document sources, separate extraction revisions, admitted evidence revisions, archive/edit operations, and deterministic snapshot/hash assertions.
3. A concurrent enqueue fixture using the same Case and two PostgreSQL transactions, asserting one active CaseRun and one idempotent winner.
4. A worker completion fixture with a pinned snapshot plus a later evidence revision, asserting the result remains reproducible and is marked stale/current according to the stored snapshot.
5. A legacy populated fixture containing real ChatMessage IDs, a clarification chain, an ASK message, a failed run, a RagContext, and a report. The migration must preserve exact IDs/counts/FKs and mark any source without an established evidence role as `legacy_unbound`.
6. A negative fixture where a message/document reference is missing or ambiguous. It must fail closed or retain an unresolved receipt; it must never pass a fabricated message ID to analysis or reports.

Every snapshot assertion compares both the exact input-text hash and the ordered manifest/provenance hash. A text match with a changed provenance manifest is not accepted as the same snapshot.

## Checkpoint A exit gate

Status: **PASS**.

- Every confirmed requirement is mapped to an owner and a later checkpoint.
- The optional-Chat lifecycle is resolved; Case creation no longer has to imply Chat creation.
- Worker ownership, active-run serialization, snapshot pinning, publication, and report authority are resolved.
- Legacy mapping is explicitly evidence-bound and has a `legacy_unbound` outcome for anything that cannot be proven.
- The fixture strategy includes multi-document, edit/archive, migration, PostgreSQL race, stale-worker, and publication cases.
- No fake message-ID shortcut, hidden transcript message, automatic assistant evidence admission, or RAG/OCR redesign is part of the implementation.

Checkpoint B may now begin. This pass did not claim that the application has already met the Case-first contract; the current blockers above remain until their respective code and exit gates are completed.
