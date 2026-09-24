# Retrieval Context Contract Cleanup Implementation Plan

## Approved contract

Implement the reviewed design in `docs/superpowers/specs/2026-09-23-retrieval-context-contract-design.md`.

## Work sequence

1. Add Alembic revision `0013_retrieval_context_contract.py` after 0012. Drop `chat_messages.retrieval_context_id`; remove only the top-level `mitre_table` JSONB key from `case_analysis_results.external_context_json`; make downgrade restore the column and reconstruct the duplicate only where the nested table exists. Extend the migration-chain/schema tests.
2. Extend the typed backend RAG context with its existing `legal_reference` payload. Carry that value in augmentation receipt metadata, move it to top-level `external_context_json.legal_relevance` when shaping persisted external context, and persist it in `retrieval_context_json` without adding it to the analysis prompt input.
3. Extend RAG retrieval-context storage and snapshot schema with `legal_reference`. Run the legal lookup before storing the retrieval snapshot, then store and return the same result. Add route, export, and response tests, including a degraded legal lookup.
4. Require `legal_relevance` in reusable backend snapshots. Carry it back into the typed RAG context; snapshots from before this change trigger a new retrieval. Add reuse and persistence tests.
5. Remove the chat-only retrieval ID from the SQLAlchemy model, Pydantic read schema, generated frontend type, optimistic chat message, and fixtures. Preserve analysis, RAG, report, and trace IDs. Add schema/frontend assertions.
6. Keep `archived_at` behavior unchanged and cover it with the existing source-bundle tests.
7. Run focused backend, RAG, and frontend verification; inspect the migration effect and final scoped diff. Confirm touched code files remain at or below 300 lines.

## Likely files

- `backend/alembic/baseline_versions/0013_retrieval_context_contract.py`
- `backend/app/models/chat.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/analysis/steps/technical_context.py`
- `backend/app/services/workflow/analysis_storage.py`
- `backend/app/services/workflow/run_analysis.py`
- `backend/tests/test_database_schema.py`
- `backend/tests/test_migration_chat_only_cleanup.py`
- `backend/tests/test_case_mitre_augmentation.py`
- `backend/tests/test_retrieval_context_contract.py`
- `backend/tests/test_chat_rag_client.py`
- `rag_service/app/routers/rag.py`
- `rag_service/app/routers/context_store.py`
- `rag_service/app/schemas/rag.py`
- `rag_service/tests/test_rag_query_route.py`
- `frontend/src/lib/api/generated/chatTypes.ts`
- `frontend/src/hooks/useCaseChat.ts`
- affected chat fixtures and tests

## Constraints

- Preserve pre-existing dirty files and unrelated user work.
- Keep every changed code file at or below 300 lines.
- Do not expose legal relevance to the main analysis prompt or treat it as case evidence.
- Remove no MITRE table except the top-level duplicate in `external_context_json`.
- Keep all `archived_at` behavior intact.
