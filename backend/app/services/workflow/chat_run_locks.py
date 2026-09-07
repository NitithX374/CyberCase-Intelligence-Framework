from __future__ import annotations

from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatRun, ChatThread


async def lock_run_thread(
    db: AsyncSession,
    run_id: UUID,
) -> ChatThread | None:
    """Lock the parent thread before the run to match message creation order."""

    thread_id_result = await db.execute(
        select(ChatRun.thread_id).where(ChatRun.id == run_id)
    )
    thread_id = thread_id_result.scalar_one_or_none()
    if thread_id is None:
        return None

    thread_result = await db.execute(
        select(ChatThread).where(ChatThread.id == thread_id).with_for_update()
    )
    return thread_result.scalar_one_or_none()


async def lock_owned_running_run(
    db: AsyncSession,
    run_id: UUID,
    worker_id: str,
) -> ChatRun | None:
    result = await db.execute(
        select(ChatRun).where(ChatRun.id == run_id).with_for_update()
    )
    run = result.scalar_one_or_none()
    if (
        run is None
        or run.status != "running"
        or run.lease_owner != worker_id
        or run.lease_expires_at is None
        or run.lease_expires_at <= datetime.now(timezone.utc)
    ):
        return None
    return run
