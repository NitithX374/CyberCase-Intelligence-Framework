import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select

from app.models import ChatMessage, ChatRun, ChatThread
from app.services.chat.chat_management import ChatService
from app.services.chat.chat_run_creation import create_message_and_run
from app.services.workflow.chat_run_claim import claim_run
from app.services.workflow.chat_run_completion import complete_run
from app.services.workflow.outcome import AssistantOutcome
from app.services.workflow.run_heartbeat import renew_run_lease
from app.services.workflow.run_recovery import recover_expired_runs
from run_recovery_support import create_request, isolated_database


async def expire_run(factory, run_id):
    async with factory() as db, db.begin():
        run = await db.get(ChatRun, run_id)
        run.lease_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)


def test_interruption_retry_is_atomic_and_preserves_evidence():
    async def exercise():
        async with isolated_database() as factory:
            thread_id, message, run, request = await create_request(factory)
            async with factory() as db:
                assert await claim_run(db, run.id, "old-worker") is not None
            await expire_run(factory, run.id)
            assert await recover_expired_runs(factory) == 1
            async with factory() as db:
                thread = await ChatService(db).get_thread(thread_id)
                assert thread.status == "failed"
                assert thread.retry_request.idempotency_key == request.idempotency_key
                assert thread.retry_request.action is None

            async def retry():
                async with factory() as db:
                    return await create_message_and_run(db, thread_id, request)

            results = await asyncio.gather(retry(), retry())
            assert all(
                pair[0].id == message.id and pair[1].id == run.id for pair in results
            )
            async with factory() as db:
                claimed = await claim_run(db, run.id, "new-worker")
                assert claimed.source_message_ids == (message.id,)
            outcome = AssistantOutcome("Analysis", None, {}, "answered")
            async with factory() as db:
                assert not await complete_run(db, run.id, "old-worker", outcome)
            async with factory() as db:
                assert await complete_run(db, run.id, "new-worker", outcome)
            async with factory() as db:
                assert (
                    await db.scalar(select(func.count()).select_from(ChatMessage)) == 2
                )
                saved = await db.get(ChatRun, run.id)
                assert saved.attempt_count == 2
                assert saved.status == "completed"

    asyncio.run(exercise())


def test_heartbeat_renewal_and_expired_owner_fencing():
    async def exercise():
        async with isolated_database() as factory:
            _, _, run, _ = await create_request(factory)
            async with factory() as db:
                await claim_run(db, run.id, "owner")
            async with factory() as db, db.begin():
                saved = await db.get(ChatRun, run.id)
                saved.lease_expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=2
                )
            await renew_run_lease(factory, run.id, "owner")
            assert await recover_expired_runs(factory) == 0
            await expire_run(factory, run.id)
            with pytest.raises(RuntimeError, match="lost its run lease"):
                await renew_run_lease(factory, run.id, "owner")
            async with factory() as db:
                assert not await complete_run(
                    db, run.id, "owner", AssistantOutcome("Late", None, {}, "answered")
                )
            assert await recover_expired_runs(factory) == 1

    asyncio.run(exercise())


def test_unclaimed_queue_is_recoverable_and_newer_messages_block_retry():
    async def exercise():
        async with isolated_database() as factory:
            thread_id, _, run, request = await create_request(factory)
            async with factory() as db, db.begin():
                saved = await db.get(ChatRun, run.id)
                saved.updated_at = datetime.now(timezone.utc) - timedelta(minutes=7)
            assert await recover_expired_runs(factory) == 1
            async with factory() as db, db.begin():
                thread = await db.get(ChatThread, thread_id)
                db.add(
                    ChatMessage(
                        thread_id=thread_id,
                        ordinal=2,
                        role="user",
                        content="New information",
                        metadata_json={},
                    )
                )
                thread.next_message_ordinal = 3
            async with factory() as db:
                with pytest.raises(HTTPException) as error:
                    await create_message_and_run(db, thread_id, request)
                assert error.value.status_code == 409

    asyncio.run(exercise())
