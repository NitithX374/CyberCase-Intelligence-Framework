from __future__ import annotations

from collections.abc import Awaitable, Callable
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.models.rag_context import RagContext
from app.services.case_analysis.contracts import AnalysisTrace
from app.services.workflow.chat_run_locks import lock_owned_running_run, lock_run_thread
from app.services.workflow.outcome import AssistantOutcome


async def complete_run(
    db: AsyncSession,
    run_id: UUID,
    worker_id: str,
    outcome: AssistantOutcome,
    *,
    lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None = None,
    lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None = None,
) -> bool:
    now = datetime.now(timezone.utc)
    async with db.begin():
        thread = await (
            lock_run_thread_fn(run_id)
            if lock_run_thread_fn is not None
            else lock_run_thread(db, run_id)
        )
        run = await (
            lock_owned_running_run_fn(run_id, worker_id)
            if lock_owned_running_run_fn is not None
            else lock_owned_running_run(db, run_id, worker_id)
        )
        if thread is None or run is None or run.thread_id != thread.id:
            return False
        if outcome.rag_context_payload is not None:
            payload = outcome.rag_context_payload
            db.add(
                RagContext(
                    retrieval_context_id=payload.retrieval_context_id,
                    run_id=run.id,
                    thread_id=thread.id,
                    context=payload.context,
                    mitre_table=deepcopy(list(payload.mitre_table)),
                )
            )
        metadata = deepcopy(outcome.metadata_json)
        if outcome.analysis_trace_draft is not None:
            if not outcome.retrieval_context_id or not outcome.evidence_sha256:
                raise ValueError("A validated analysis trace requires retrieval and evidence bindings")
            metadata["analysis_trace"] = AnalysisTrace(
                **outcome.analysis_trace_draft.model_dump(mode="python"),
                retrieval_context_id=outcome.retrieval_context_id,
                evidence_sha256=outcome.evidence_sha256,
            ).model_dump(mode="json")
        elif outcome.analysis_trace_failure is not None:
            metadata["analysis_trace_failure"] = outcome.analysis_trace_failure.model_dump(
                mode="json"
            )
        db.add(
            ChatMessage(
                thread_id=thread.id,
                ordinal=thread.next_message_ordinal,
                role="assistant",
                content=outcome.content,
                retrieval_context_id=outcome.retrieval_context_id,
                metadata_json=metadata,
            )
        )
        thread.next_message_ordinal += 1
        thread.status = outcome.thread_status
        run.status = "completed"
        run.error_code = None
        run.error_message = None
        run.finished_at = now
        run.lease_owner = None
        run.lease_expires_at = None
        await db.flush()
    return True


__all__ = ["complete_run"]
