from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatRun, ChatThread

from app.services.workflow.chat_run_claim import claim_run
from app.services.workflow.chat_run_completion import complete_run
from app.services.workflow.chat_run_contracts import ClaimedChatRun
from app.services.workflow.chat_run_failure import fail_run
from app.services.workflow.chat_run_locks import lock_owned_running_run, lock_run_thread


class ChatRunWorker:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def claim_run(
        self,
        run_id: UUID,
        worker_id: str,
    ) -> ClaimedChatRun | None:
        return await claim_run(self.db, run_id, worker_id)

    async def complete_run(
        self,
        run_id: UUID,
        worker_id: str,
        outcome: Any,
    ) -> bool:
        return await complete_run(
            self.db,
            run_id,
            worker_id,
            outcome,
            lock_run_thread_fn=self._lock_run_thread,
            lock_owned_running_run_fn=self._lock_owned_running_run,
        )

    async def fail_run(
        self,
        run_id: UUID,
        worker_id: str,
        error_code: str,
        error_message: str,
        followup_metadata_json: dict[str, Any] | None = None,
    ) -> bool:
        return await fail_run(
            self.db,
            run_id,
            worker_id,
            error_code,
            error_message,
            followup_metadata_json,
            lock_run_thread_fn=self._lock_run_thread,
            lock_owned_running_run_fn=self._lock_owned_running_run,
        )

    async def _lock_run_thread(self, run_id: UUID) -> ChatThread | None:
        return await lock_run_thread(self.db, run_id)

    async def _lock_owned_running_run(
        self,
        run_id: UUID,
        worker_id: str,
    ) -> ChatRun | None:
        return await lock_owned_running_run(self.db, run_id, worker_id)
