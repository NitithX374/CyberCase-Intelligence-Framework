from __future__ import annotations

from collections.abc import Awaitable, Callable
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.models.rag_context import RagContext
from app.schemas.message_metadata import serialize_message_metadata
from app.services.case_analysis.contracts import AnalysisTrace, AnalysisTraceV3
from app.services.workflow.chat_run_locks import lock_owned_running_run, lock_run_thread
from app.services.workflow.outcome import AssistantOutcome


async def complete_run(
    db: AsyncSession,
    run_id: UUID,
    worker_id: str,
    outcome: AssistantOutcome,
    *,
    lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None = None,
    lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]]
    | None = None,
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
        serialized_trace = _serialize_analysis_trace(outcome)
        if serialized_trace is not None:
            metadata["analysis_trace"] = serialized_trace
        elif outcome.analysis_trace_failure is not None:
            metadata["analysis_trace_failure"] = (
                outcome.analysis_trace_failure.model_dump(mode="json")
            )
        db.add(
            ChatMessage(
                thread_id=thread.id,
                ordinal=thread.next_message_ordinal,
                role="assistant",
                content=outcome.content,
                retrieval_context_id=outcome.retrieval_context_id,
                metadata_json=serialize_message_metadata(metadata),
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


def _serialize_analysis_trace(outcome: AssistantOutcome) -> dict[str, object] | None:
    trace = outcome.analysis_trace_draft
    if trace is None:
        return None
    if isinstance(trace, AnalysisTraceV3):
        if trace.evidence_sha256 != outcome.evidence_sha256:
            raise ValueError(
                "Analysis trace evidence binding does not match the outcome"
            )
        if trace.retrieval_context_id != outcome.retrieval_context_id:
            raise ValueError(
                "Analysis trace retrieval binding does not match the outcome"
            )
        return trace.model_dump(mode="json")
    if not outcome.retrieval_context_id or not outcome.evidence_sha256:
        raise ValueError("A v2 analysis trace requires retrieval and evidence bindings")
    return AnalysisTrace(
        **trace.model_dump(mode="python"),
        retrieval_context_id=outcome.retrieval_context_id,
        evidence_sha256=outcome.evidence_sha256,
    ).model_dump(mode="json")


__all__ = ["_serialize_analysis_trace", "complete_run"]
