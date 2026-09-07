import asyncio
import logging
from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatRun
from app.services.workflow.chat_run_contracts import RUN_LEASE_DURATION
from app.services.workflow.chat_run_locks import lock_run_thread

RECOVERY_INTERVAL_SECONDS = 30
INTERRUPTED_RUN_CODE = "chat_run_interrupted"
logger = logging.getLogger("app.chat")


def run_has_expired(run: ChatRun, now: datetime) -> bool:
    if run.status == "queued":
        return run.updated_at <= now - RUN_LEASE_DURATION
    if run.status == "running":
        return run.lease_expires_at is None or run.lease_expires_at <= now
    return False


async def recover_expired_runs(session_factory: Callable[[], AsyncSession]) -> int:
    now = datetime.now(timezone.utc)
    async with session_factory() as db:
        candidates = await db.execute(
            select(ChatRun.id)
            .where(
                or_(
                    (ChatRun.status == "queued")
                    & (ChatRun.updated_at <= now - RUN_LEASE_DURATION),
                    (ChatRun.status == "running")
                    & or_(
                        ChatRun.lease_expires_at <= now,
                        ChatRun.lease_expires_at.is_(None),
                    ),
                )
            )
            .limit(100)
        )
        run_ids = list(candidates.scalars())
    recovered = 0
    for run_id in run_ids:
        async with session_factory() as db, db.begin():
            thread = await lock_run_thread(db, run_id)
            if thread is None:
                continue
            result = await db.execute(
                select(ChatRun).where(ChatRun.id == run_id).with_for_update()
            )
            run = result.scalar_one_or_none()
            if run is None or not run_has_expired(run, datetime.now(timezone.utc)):
                continue
            run.status = "failed"
            run.error_code = INTERRUPTED_RUN_CODE
            run.error_message = "Processing was interrupted. Retry the saved request."
            run.finished_at = datetime.now(timezone.utc)
            run.lease_owner = None
            run.lease_expires_at = None
            thread.status = "failed"
            recovered += 1
    return recovered


async def monitor_interrupted_runs(session_factory: Callable[[], AsyncSession]) -> None:
    while True:
        try:
            recovered = await recover_expired_runs(session_factory)
            if recovered:
                logger.warning("Marked %s interrupted chat runs as failed", recovered)
        except Exception:
            logger.exception("Interrupted chat run recovery failed")
        await asyncio.sleep(RECOVERY_INTERVAL_SECONDS)
