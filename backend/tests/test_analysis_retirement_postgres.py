import asyncio

import pytest
from app.models import ChatMessage, ChatRun, ChatThread
from app.models.rag_context import RagContext
from app.schemas.chat import ChatMessageCreate
from app.services.chat.chat_run_creation import create_message_and_run
from app.services.workflow.chat_run_claim import claim_run
from run_recovery_support import create_request, isolated_database


@pytest.mark.parametrize("metadata,blocked", [
    ({"analysis_kind": "grounded_main_analysis", "analysis_trace":
      {"version": "analysis_trace_v2"}}, True),
    ({"analysis_state_scope": "canonical_case_overview", "analysis_trace_failure":
      {"version": "analysis_trace_v3"}}, True),
    ({}, False),
])
def test_ask_does_not_recover_context_behind_retired_analysis(metadata, blocked):
    async def exercise():
        async with isolated_database() as factory:
            thread_id, _, original, _ = await create_request(factory)
            async with factory() as db:
                thread = await db.get(ChatThread, thread_id)
                run = await db.get(ChatRun, original.id)
                run.status = "completed"
                thread.status = "answered"
                thread.next_message_ordinal = 3
                db.add(RagContext(retrieval_context_id="old-context", thread_id=thread_id,
                                  run_id=run.id, context="Old external context", mitre_table=[]))
                await db.flush()
                db.add(ChatMessage(thread_id=thread_id, ordinal=2, role="assistant",
                                   content="Old analysis", metadata_json=metadata,
                                   retrieval_context_id="old-context"))
                await db.commit()
            async with factory() as db:
                _, ask = await create_message_and_run(db, thread_id, ChatMessageCreate(
                    content="What happened?", action="ask", idempotency_key="ask"))
            async with factory() as db:
                claimed = await claim_run(db, ask.id, "worker")
                assert (claimed is None) == blocked
            async with factory() as db:
                saved = await db.get(ChatRun, ask.id)
                if blocked:
                    assert saved.error_code == "analysis_context_missing"
                else:
                    assert saved.status == "running"
    asyncio.run(exercise())
