from __future__ import annotations

import logging
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case_state import CaseStateVersion
from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.models.rag_context import RagContext
from app.services.case_state.raw_evidence import resolve_raw_case_evidence_history
from app.services.chat.chat_message import reconstruct_clarification_chain
from app.services.extraction.llm_extraction import (
    ExtractionInput, ExtractionSourceMessage, build_extraction_input,
)
from app.services.followup.schemas import ClarificationExchange
from app.services.workflow.chat_run_contracts import ClaimedChatRun, RUN_LEASE_DURATION

logger = logging.getLogger("app.chat")

async def claim_run(
    db: AsyncSession,
    run_id: UUID,
    worker_id: str,
) -> ClaimedChatRun | None:
    now = datetime.now(timezone.utc)

    async with db.begin():
        statement = (
            select(ChatRun)
            .where(
                ChatRun.id == run_id,
                ChatRun.status == "queued",
            )
            .with_for_update(skip_locked=True)
        )
        result = await db.execute(statement)
        run = result.scalar_one_or_none()
        if run is None:
            return None

        run.status = "running"
        run.attempt_count += 1
        run.lease_owner = worker_id
        run.lease_expires_at = now + RUN_LEASE_DURATION
        run.started_at = now

        request_payload = run.request_payload
        content = (
            request_payload.get("content")
            if isinstance(request_payload, dict)
            else None
        )
        rag_query = (
            request_payload.get("rag_query", content)
            if isinstance(request_payload, dict)
            else None
        )
        requested_root_ordinal = (
            request_payload.get("followup_root_ordinal")
            if isinstance(request_payload, dict)
            else None
        )
        if (
            not isinstance(requested_root_ordinal, int)
            or isinstance(requested_root_ordinal, bool)
            or requested_root_ordinal < 1
        ):
            requested_root_ordinal = None
        requested_round = (
            request_payload.get("followup_round")
            if isinstance(request_payload, dict)
            else None
        )
        if (
            not isinstance(requested_round, int)
            or isinstance(requested_round, bool)
            or requested_round < 0
        ):
            requested_round = None
        legacy_followup = (
            request_payload.get("skip_followup_policy") is True
            if isinstance(request_payload, dict)
            else False
        )
        post_answer_action = (
            request_payload.get("action")
            if isinstance(request_payload, dict)
            else None
        )
        if post_answer_action not in (None, "ask", "add_case_info"):
            post_answer_action = None
        clarification_answer = (
            isinstance(request_payload, dict)
            and request_payload.get("clarification_answer") is True
        )

        case_state_json: dict[str, object] | None = None
        analysis_context: dict[str, object] | None = None
        case_state_version_id: UUID | None = None
        requested_parent_version_id: UUID | None = None
        if isinstance(request_payload, dict):
            raw_parent_version_id = request_payload.get("case_state_version_id")
            if raw_parent_version_id is not None:
                try:
                    requested_parent_version_id = UUID(str(raw_parent_version_id))
                except (TypeError, ValueError, AttributeError):
                    requested_parent_version_id = None
        if post_answer_action in ("ask", "add_case_info"):
            pointer_result = await db.execute(
                select(ChatThread.current_case_state_version_id).where(
                    ChatThread.id == run.thread_id,
                )
            )
            current_state_version_id = pointer_result.scalar_one_or_none()
            state_lookup_id = (
                requested_parent_version_id
                if post_answer_action == "add_case_info"
                and requested_parent_version_id is not None
                else current_state_version_id
            )
            if state_lookup_id is not None:
                case_state_version_id = state_lookup_id
                state_result = await db.execute(
                    select(CaseStateVersion).where(
                        CaseStateVersion.id == state_lookup_id,
                        CaseStateVersion.thread_id == run.thread_id,
                    )
                )
                case_state = state_result.scalar_one_or_none()
                if case_state is not None and isinstance(
                    case_state.state_json,
                    dict,
                ):
                    case_state_json = deepcopy(case_state.state_json)
                    if post_answer_action == "ask":
                        rag_context_result = await db.execute(
                            select(RagContext).where(
                                RagContext.thread_id == run.thread_id,
                                RagContext.case_state_version_id
                                == state_lookup_id,
                            )
                        )
                        rag_context = rag_context_result.scalar_one_or_none()
                        if rag_context is not None:
                            mitre_table = rag_context.mitre_table
                            analysis_context = {
                                "retrieved_context": (
                                    rag_context.context
                                    if isinstance(rag_context.context, str)
                                    else ""
                                ),
                                "retrieval_context_id": rag_context.retrieval_context_id,
                                "mitre_table": (
                                    deepcopy(mitre_table)
                                    if isinstance(mitre_table, list)
                                    else []
                                ),
                                "previous_analysis": None,
                            }

        original_user_content: object = content
        clarification_exchanges: tuple[ClarificationExchange, ...] = ()
        pending_question: str | None = None
        followup_root_ordinal = requested_root_ordinal
        history: list[ChatMessage] | None = None
        if requested_root_ordinal is not None and requested_round == 0:
            pass
        elif requested_root_ordinal is None and not legacy_followup:
            request_message_result = await db.execute(
                select(ChatMessage).where(
                    ChatMessage.id == run.request_message_id
                )
            )
            request_message = request_message_result.scalar_one_or_none()
            if request_message is not None:
                original_user_content = request_message.content
                followup_root_ordinal = request_message.ordinal
        else:
            history_result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.thread_id == run.thread_id)
                .order_by(ChatMessage.ordinal)
            )
            history = history_result.scalars().all()
            request_index = next(
                (
                    index
                    for index, message in enumerate(history)
                    if message.id == run.request_message_id
                ),
                None,
            )
            if request_index is None:
                thread_result = await db.execute(
                    select(ChatThread)
                    .where(ChatThread.id == run.thread_id)
                    .with_for_update()
                )
                thread = thread_result.scalar_one_or_none()
                if thread is not None:
                    thread.status = (
                        "awaiting_followup"
                        if isinstance(requested_round, int)
                        and not isinstance(requested_round, bool)
                        and requested_round > 0
                        else "failed"
                    )
                    thread.active_rag_session_id = None
                run.status = "failed"
                run.error_code = "chat_followup_request_missing"
                run.error_message = (
                    "The persisted chat request could not be reconstructed."
                )
                run.finished_at = now
                run.lease_owner = None
                run.lease_expires_at = None
                await db.flush()
                return None
            history = history[: request_index + 1]
            chain = reconstruct_clarification_chain(
                history,
                root_ordinal=requested_root_ordinal,
            )
            if chain is not None:
                original_user_content = chain.original_user_content
                clarification_exchanges = chain.exchanges
                pending_question = chain.pending_question
                followup_root_ordinal = chain.root_ordinal
            if followup_root_ordinal is None:
                request_message = next(
                    (
                        message
                        for message in history
                        if message.id == run.request_message_id
                    ),
                    None,
                )
                if request_message is not None:
                    original_user_content = request_message.content
                    followup_root_ordinal = request_message.ordinal
        if followup_root_ordinal is None:
            followup_root_ordinal = 1

        extraction_input: ExtractionInput | None = None
        if post_answer_action in (None, "add_case_info"):
            try:
                if history is not None:
                    extraction_input = build_extraction_input(
                        thread_id=run.thread_id,
                        messages=history,
                        root_ordinal=followup_root_ordinal,
                    )
                elif isinstance(content, str):
                    extraction_input = ExtractionInput(
                        thread_id=run.thread_id,
                        messages=[
                            ExtractionSourceMessage(
                                message_id=run.request_message_id,
                                ordinal=followup_root_ordinal,
                                source_type="user_case_statement",
                                content=content,
                            )
                        ],
                    )
            except (TypeError, ValueError):
                logger.warning(
                    "Chat extraction source packet could not be built "
                    "run_id=%s",
                    run.id,
                )

        if requested_round == 0 and post_answer_action is None and isinstance(content, str) and content.strip():
            raw_case_narrative = content.strip()
        else:
            raw_case_narrative = await resolve_raw_case_evidence_history(
                db,
                thread_id=run.thread_id,
                current_request_message_id=run.request_message_id,
                current_request_payload=(
                    request_payload if isinstance(request_payload, dict) else {}
                ),
                current_content=content if isinstance(content, str) else None,
                history=history,
            )

        claimed_run = ClaimedChatRun(
            id=run.id,
            operation=run.operation,
            input_rag_session_id=run.input_rag_session_id,
            content=content,
            rag_query=rag_query,
            original_user_content=original_user_content,
            clarification_exchanges=clarification_exchanges,
            pending_question=pending_question,
            followup_root_ordinal=followup_root_ordinal,
            extraction_input=extraction_input,
            post_answer_action=post_answer_action,
            clarification_answer=clarification_answer,
            request_message_id=run.request_message_id,
            case_state_version_id=case_state_version_id,
            case_state_json=case_state_json,
            analysis_context=analysis_context,
            raw_case_narrative=raw_case_narrative,
        )
        await db.flush()

    return claimed_run
