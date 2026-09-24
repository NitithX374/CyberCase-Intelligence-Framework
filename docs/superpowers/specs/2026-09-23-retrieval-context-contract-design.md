# Retrieval Context Contract Cleanup Design

## Goal

Make the chat, analysis, and RAG persistence contracts reflect their actual ownership:

- Chat messages contain conversation content and delivery metadata, not analysis retrieval identity.
- Analysis results retain the retrieval identity that produced their external technical context.
- `external_context_json` stores legal relevance from RAG and keeps technical augmentation nested.
- `retrieval_context_json` is the reusable snapshot of the RAG context that was actually retrieved.
- Historical source archiving remains available for source-bound analysis reconstruction.

## Scope

This change covers the backend ORM/schema contract, the RAG response and retrieval-context snapshot contract, frontend generated chat types, persistence logic, reuse validation, database migration, and focused tests.

This change does not redesign the chat transcript, change the analysis prompt, turn legal references into case sources, or make legal relevance an admission gate or legal decision.

## Current contract and confirmed decisions

`chat_messages.retrieval_context_id` has no production writer. The retrieval identity is meaningful at the analysis-result and analysis-trace levels, so only the chat-message column and its API/frontend representations are removed.

`case_sources.archived_at` is a soft archival boundary. New source bundles exclude archived sources, while historical analysis reconstruction can retain sources that were active when the analysis was created. The field remains unchanged.

The current analysis persistence duplicates `mitre_table` in two places inside `external_context_json`: the top level and `technical_augmentation`. The top-level duplicate is removed. `technical_augmentation.mitre_table` remains the technical augmentation payload used by report projection. `retrieval_context_json.mitre_table` also remains the reusable RAG snapshot payload.

The RAG wire response already provides `legal_reference`. The wire name remains stable. Persistence normalizes that payload under the key `legal_relevance`.

## Proposed persisted shapes

### `external_context_json`

For an analysis with successful RAG retrieval:

```json
{
  "source_reference_type": "case_source",
  "source_revision": 4,
  "legal_relevance": {
    "provisions": [],
    "provider": "thanoy",
    "query_sent": "...",
    "degraded": "",
    "disclaimer": "..."
  },
  "technical_augmentation": {
    "version": "case_mitre_augmentation_v1",
    "status": "retrieved_with_matches",
    "applicability": {},
    "retrieval_context_id": "...",
    "retrieval_context_reused": false,
    "mitre_table": [],
    "association_ids": []
  }
}
```

There is no top-level `mitre_table`. The complete legal result, including a degraded result or disclaimer, is persisted when the technical retrieval itself succeeded. Legal relevance is external context and is not treated as authoritative case information.

For analyses without a valid retrieval, `external_context_json` contains the existing source metadata and technical augmentation status, but does not invent a legal result.

### `retrieval_context_json`

When a valid retrieval is performed or reused:

```json
{
  "context_key": "...",
  "retrieval_context_id": "...",
  "context": "...",
  "mitre_table": [],
  "legal_relevance": {
    "provisions": [],
    "provider": "thanoy",
    "query_sent": "...",
    "degraded": "",
    "disclaimer": "..."
  }
}
```

When no retrieval is admitted, the column remains `null`. This is the persistence rule for “when retrieval occurs, write it to `retrieval_context_json`.”

## RAG service flow

The RAG `/query` flow currently stores the retrieval snapshot before calling the legal-reference client. The order will become:

1. Run GraphRAG and build the MITRE table.
2. Run the existing legal-reference lookup.
3. Store the retrieval snapshot with the legal-reference result.
4. Return the existing `QueryResponse`, including the unchanged `legal_reference` field.

The in-memory retrieval-context store and `RetrievalContextSnapshot` schema will carry the legal result so that a context fetched by ID is complete. The RAG snapshot may retain the wire-oriented name `legal_reference`; the backend persistence boundary maps it to `legal_relevance`.

The existing retrieval-context ID remains in RAG responses, analysis results, traces, and technical augmentation metadata. It is removed only from chat messages.

## Backend flow and reuse

The validated RAG response becomes a typed internal context containing:

- retrieval context ID;
- retrieved text context;
- normalized MITRE table;
- normalized legal relevance.

The analysis pipeline carries the legal relevance alongside the technical context for persistence, without adding it to the main case-analysis evidence contract. `analysis_storage` writes the legal payload into both `external_context_json.legal_relevance` and `retrieval_context_json.legal_relevance` when retrieval is valid.

Retrieval reuse requires the stored snapshot to contain a valid context ID, context text, MITRE table shape, and `legal_relevance` key. Existing snapshots created before this change do not contain legal relevance and therefore are not reused; the workflow performs a fresh retrieval instead of manufacturing an empty result. This prevents old data from silently violating the new contract.

Report projection continues to read `technical_augmentation.mitre_table`. Legal relevance is persisted for inspection and downstream context, but is not added to report admission, report claims, or legal conclusions in this change.

## Database migration

Add the next single-head Alembic migration after `0012_analysis_assessment_status`, tentatively named `0013_retrieval_context_contract.py`.

The upgrade will:

1. Drop `chat_messages.retrieval_context_id`.
2. Remove only the top-level `mitre_table` key from `case_analysis_results.external_context_json` with a JSONB update.
3. Leave nested `technical_augmentation.mitre_table` untouched.
4. Leave `case_analysis_results.retrieval_context_json` and its `mitre_table` untouched.
5. Leave `case_sources.archived_at` untouched.

The migration cannot backfill legal relevance for old analysis rows because the historical legal-reference payload was not persisted. The implementation must not synthesize it. A downgrade may reconstruct the removed top-level MITRE duplicate from the nested technical augmentation where available, but the new application contract must not depend on that duplicate.

## API and frontend changes

Remove `retrieval_context_id` from the chat-message ORM model, read schema, generated frontend chat type, optimistic message object, and affected fixtures/tests.

Do not remove retrieval IDs from analysis read schemas, RAG response schemas, analysis traces, technical augmentation, or retrieval-context snapshots.

No public route is added or removed. The existing RAG `legal_reference` response shape remains compatible.

## Verification

Focused verification must cover:

- ORM and schema absence of chat-message retrieval ID;
- migration upgrade and JSONB cleanup, including preservation of both nested MITRE locations;
- successful RAG response persistence of legal relevance;
- degraded legal lookup persistence without losing the retrieval snapshot;
- no retrieval producing a null `retrieval_context_json` and no fabricated legal payload;
- old retrieval snapshots without legal relevance forcing fresh retrieval;
- reuse preserving legal relevance and the retrieval ID;
- archived-source behavior remaining unchanged;
- frontend TypeScript/tests after removing the optimistic chat field;
- report projection continuing to validate nested technical augmentation.

Final validation will include focused backend/RAG/frontend tests, Python compilation, frontend lint/type/build checks as available, migration/schema inspection against the active database, and a final diff review limited to this contract change plus the design/spec artifacts.

## Acceptance criteria

The change is complete when:

1. No chat message model, schema, response, optimistic object, or database row carries `retrieval_context_id`.
2. Analysis-level retrieval IDs remain intact and traceable.
3. `external_context_json` has no top-level `mitre_table` after migration and new writes.
4. `technical_augmentation.mitre_table` and `retrieval_context_json.mitre_table` remain available.
5. A successful RAG retrieval writes legal relevance to `retrieval_context_json` and `external_context_json`.
6. Old snapshots without legal relevance are not silently reused.
7. `archived_at` continues to preserve the current source-history behavior.
8. Legal relevance remains external context, not authoritative case evidence or an automatic legal decision.
