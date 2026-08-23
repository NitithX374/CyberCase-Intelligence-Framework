from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatRun, ChatThread
from app.services.workflow.chat_run_locks import lock_owned_running_run, lock_run_thread

async def fail_run(
    db: AsyncSession,
    run_id: UUID,
    worker_id: str,
    error_code: str,
    error_message: str,
    followup_metadata_json: dict[str, Any] | None = None,
    *,
    lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None = None,
    lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None = None,
) -> bool:
    """Persist a safe failure without exposing upstream response content."""

    now = datetime.now(timezone.utc)
    async with db.begin():
        thread = await (
            lock_run_thread_fn(run_id)
            if lock_run_thread_fn is not None
            else lock_run_thread(db, run_id)
        )
        if thread is None:
            return False

        run = await (
            lock_owned_running_run_fn(run_id, worker_id)
            if lock_owned_running_run_fn is not None
            else lock_owned_running_run(db, run_id, worker_id)
        )
        if run is None or run.thread_id != thread.id:
            return False

        request_payload = run.request_payload
        if followup_metadata_json:
            updated_payload = dict(request_payload or {})
            for audit_key in ("chat_followup",):
                audit_value = followup_metadata_json.get(audit_key)
                if isinstance(audit_value, dict):
                    updated_payload[audit_key] = audit_value
            if updated_payload != dict(request_payload or {}):
                run.request_payload = updated_payload
        followup_round = (
            request_payload.get("followup_round")
            if isinstance(request_payload, dict)
            else None
        )
        thread.status = (
            "awaiting_followup"
            if isinstance(followup_round, int)
            and not isinstance(followup_round, bool)
            and followup_round > 0
            else "failed"
        )

        run.status = "failed"
        run.error_code = error_code
        run.error_message = error_message
        run.finished_at = now
        run.lease_owner = None
        run.lease_expires_at = None
        await db.flush()

    return True
