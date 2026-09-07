import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.workflow.chat_run_contracts import RUN_LEASE_DURATION
from app.services.workflow.chat_run_locks import lock_owned_running_run, lock_run_thread


async def renew_run_lease(
    session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str
) -> None:
    async with session_factory() as db, db.begin():
        thread = await lock_run_thread(db, run_id)
        run = await lock_owned_running_run(db, run_id, worker_id)
        if thread is None or run is None:
            raise RuntimeError("Chat worker lost its run lease")
        run.lease_expires_at = datetime.now(timezone.utc) + RUN_LEASE_DURATION


async def _heartbeat(
    session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str
) -> None:
    while True:
        await asyncio.sleep(30)
        await renew_run_lease(session_factory, run_id, worker_id)


@asynccontextmanager
async def maintain_run_lease(
    session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str
) -> AsyncIterator[None]:
    async with asyncio.TaskGroup() as group:
        heartbeat = group.create_task(_heartbeat(session_factory, run_id, worker_id))
        try:
            yield
        finally:
            heartbeat.cancel()
