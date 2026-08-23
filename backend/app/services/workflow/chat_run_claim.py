from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun
from app.models.rag_context import RagContext
from app.services.chat.clarification_chain import reconstruct_clarification_chain
from app.services.chat.raw_evidence import build_raw_evidence_snapshot
from app.services.workflow.chat_run_contracts import ClaimedChatRun, RUN_LEASE_DURATION


async def claim_run(
    db: AsyncSession,
    run_id: UUID,
    worker_id: str,
) -> ClaimedChatRun | None:
    now = datetime.now(timezone.utc)
    async with db.begin():
        result = await db.execute(
            select(ChatRun)
            .where(ChatRun.id == run_id, ChatRun.status == "queued")
            .with_for_update(skip_locked=True)
        )
        run = result.scalar_one_or_none()
        if run is None:
            return None
        request_message = await db.get(ChatMessage, run.request_message_id)
        if request_message is None:
            await _fail_missing_request(run, now)
            return None
        history_result = await db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.thread_id == run.thread_id,
                ChatMessage.ordinal <= request_message.ordinal,
            )
            .order_by(ChatMessage.ordinal)
        )
        history = list(history_result.scalars().all())
        evidence = build_raw_evidence_snapshot(history)
        if not evidence.text:
            await _fail_missing_evidence(run, now)
            return None
        payload = run.request_payload if isinstance(run.request_payload, dict) else {}
        action = payload.get("action")
        if action not in {"initial_analysis", "ask", "add_case_info"}:
            action = "add_case_info"
        root_ordinal = payload.get("followup_root_ordinal")
        if not isinstance(root_ordinal, int) or root_ordinal < 1:
            root_ordinal = request_message.ordinal
        chain = reconstruct_clarification_chain(history, root_ordinal=root_ordinal)
        first_user = next(message for message in history if message.role == "user")
        original_user_content = first_user.content
        clarification_exchanges = ()
        if chain is not None:
            original_user_content = chain.original_user_content
            clarification_exchanges = chain.exchanges
            root_ordinal = chain.root_ordinal
        analysis_context = None
        if action == "ask":
            analysis_context = await _latest_analysis_context(db, run)
            if analysis_context is None:
                await _fail_missing_context(run, now)
                return None
        run.status = "running"
        run.attempt_count += 1
        run.lease_owner = worker_id
        run.lease_expires_at = now + RUN_LEASE_DURATION
        run.started_at = now
        await db.flush()
        return ClaimedChatRun(
            id=run.id,
            thread_id=run.thread_id,
            request_message_id=run.request_message_id,
            content=request_message.content,
            action=action,
            raw_evidence=evidence.text,
            evidence_sha256=evidence.sha256,
            source_message_ids=evidence.source_message_ids,
            original_user_content=original_user_content,
            clarification_exchanges=clarification_exchanges,
            followup_root_ordinal=root_ordinal,
            analysis_context=analysis_context,
        )


async def _latest_analysis_context(
    db: AsyncSession,
    current_run: ChatRun,
) -> dict[str, object] | None:
    result = await db.execute(
        select(RagContext)
        .join(ChatRun, ChatRun.id == RagContext.run_id)
        .where(
            RagContext.thread_id == current_run.thread_id,
            ChatRun.status == "completed",
            ChatRun.created_at < current_run.created_at,
        )
        .order_by(ChatRun.created_at.desc())
        .limit(1)
    )
    context = result.scalar_one_or_none()
    if context is None:
        return None
    message_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.thread_id == current_run.thread_id,
            ChatMessage.role == "assistant",
            ChatMessage.retrieval_context_id == context.retrieval_context_id,
        )
        .order_by(ChatMessage.ordinal.desc())
        .limit(1)
    )
    previous = message_result.scalar_one_or_none()
    return {
        "retrieved_context": context.context,
        "retrieval_context_id": context.retrieval_context_id,
        "mitre_table": deepcopy(context.mitre_table),
        "previous_analysis": previous.content if previous is not None else None,
    }


async def _fail_missing_request(run: ChatRun, now: datetime) -> None:
    await _mark_claim_failure(run, now, "chat_request_missing", "Request message is missing")


async def _fail_missing_evidence(run: ChatRun, now: datetime) -> None:
    await _mark_claim_failure(run, now, "case_evidence_missing", "Raw case evidence is missing")


async def _fail_missing_context(run: ChatRun, now: datetime) -> None:
    await _mark_claim_failure(
        run,
        now,
        "analysis_context_missing",
        "No completed analytical context is available for ASK",
    )


async def _mark_claim_failure(
    run: ChatRun,
    now: datetime,
    code: str,
    message: str,
) -> None:
    run.status = "failed"
    run.error_code = code
    run.error_message = message
    run.finished_at = now
    run.lease_owner = None
    run.lease_expires_at = None


__all__ = ["claim_run"]
