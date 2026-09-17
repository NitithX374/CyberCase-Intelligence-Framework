from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from sqlalchemy import func, select

from app.models.case_materials import CaseSource
from app.models.chat import ChatMessage
from app.schemas.message_metadata import serialize_message_metadata
from app.services.gap_clarification.context import load_gap_context
from app.services.gap_clarification.contracts import (
    ClarificationResumeAnswer,
    GapAnswerInterpretation,
    GapClarificationState,
)
from app.services.gap_clarification.runtime import (
    GapClarificationError,
    current_session_factory,
    parse_uuid,
    session_id_from_config,
)
from app.services.gap_clarification.persistence_helpers import (
    acknowledgement_message,
    answer_fingerprint,
    answer_message_content,
    find_matching_source,
    find_reply_message,
    find_session_message,
)


async def persist_question(
    state: GapClarificationState,
    config: RunnableConfig,
    *,
    question: str,
    target_information: str,
    rationale_summary: str | None,
    attempt: int,
) -> str:
    session_id = session_id_from_config(config)
    case_id = parse_uuid(state["case_id"], "case_id")
    analysis_id = parse_uuid(state["source_analysis_id"], "source_analysis_id")
    async with current_session_factory()() as db:
        async with db.begin():
            context = await load_gap_context(
                db,
                state,
                session_id=session_id,
                lock_case=True,
                include_history=False,
            )
            existing = await find_session_message(db, case_id, session_id, "followup_question", attempt)
            if existing is not None:
                return str(existing.id)

            ordinal = (
                await db.scalar(
                    select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                        ChatMessage.case_id == case_id
                    )
                )
                or 0
            ) + 1
            metadata = serialize_message_metadata(
                {
                    "action": "follow_up",
                    "chat_followup": {
                        "root_ordinal": ordinal,
                        "round": attempt,
                        "source_analysis_id": str(analysis_id),
                        "source_revision": state["source_evidence_revision"],
                        "gap": context.gap.model_dump(mode="json"),
                        "clarification_session_id": session_id,
                        "workflow_thread_id": session_id,
                        "target_information": target_information,
                        "rationale_summary": rationale_summary or context.gap.reason,
                    },
                }
            )
            message = ChatMessage(
                case_id=case_id,
                client_request_id=f"{session_id}:question:{attempt}",
                ordinal=ordinal,
                role="assistant",
                content=question,
                message_kind="followup_question",
                analysis_result_id=analysis_id,
                metadata_json=metadata,
            )
            db.add(message)
            await db.flush()
            return str(message.id)


async def commit_answer(
    state: GapClarificationState,
    config: RunnableConfig,
) -> dict[str, object]:
    raw = ClarificationResumeAnswer.model_validate(
        {
            **(state.get("latest_answer") or {}),
            "question_message_id": state["pending_question_message_id"],
        }
    )
    interpretation = GapAnswerInterpretation.model_validate(state["latest_interpretation"])
    session_id = session_id_from_config(config)
    case_id = parse_uuid(state["case_id"], "case_id")
    analysis_id = parse_uuid(state["source_analysis_id"], "source_analysis_id")
    question_id = parse_uuid(raw.question_message_id, "question_message_id")
    fingerprint = answer_fingerprint(interpretation.normalized_fact or raw.content)
    current_revision = state["source_evidence_revision"]

    async with current_session_factory()() as db:
        async with db.begin():
            context = await load_gap_context(
                db,
                state,
                session_id=session_id,
                lock_case=True,
                include_history=False,
            )
            gap = context.gap.model_dump(mode="json")
            answer_record = {
                "gap_id": context.gap.gap_id,
                "answer": raw.content if raw.disposition == "answered" else None,
                "disposition": raw.disposition,
                "response_type": interpretation.response_type,
                "normalized_fact": interpretation.normalized_fact,
                "resolved_information": interpretation.resolved_information,
                "gap_resolution": interpretation.gap_resolution,
            }
            question = await db.scalar(
                select(ChatMessage).where(
                    ChatMessage.id == question_id,
                    ChatMessage.case_id == case_id,
                    ChatMessage.message_kind == "followup_question",
                    ChatMessage.role == "assistant",
                )
            )
            if question is None:
                raise GapClarificationError(
                    "clarification_question_missing",
                    "Clarification question is missing",
                )
            existing = await db.scalar(
                select(ChatMessage).where(
                    ChatMessage.case_id == case_id,
                    ChatMessage.client_request_id == raw.request_key,
                )
            )
            answered_question = await db.scalar(
                select(ChatMessage.id).where(
                    ChatMessage.case_id == case_id,
                    ChatMessage.in_reply_to_message_id == question.id,
                    ChatMessage.message_kind == "followup_answer",
                )
            )
            if answered_question is not None and existing is None:
                raise GapClarificationError(
                    "clarification_already_answered",
                    "This clarification question already has an answer",
                )
            if existing is None:
                ordinal = (
                    await db.scalar(
                        select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                            ChatMessage.case_id == case_id
                        )
                    )
                    or 0
                ) + 1
                metadata = serialize_message_metadata(
                    {
                        "action": "follow_up",
                        "chat_followup": {
                            "root_ordinal": question.ordinal,
                            "round": state["attempt_count"],
                            "source_analysis_id": str(analysis_id),
                            "source_revision": state["source_evidence_revision"],
                            "gap": gap,
                            "clarification_session_id": session_id,
                            "workflow_thread_id": session_id,
                            "answer": answer_record,
                        },
                    }
                )
                existing = ChatMessage(
                    case_id=case_id,
                    client_request_id=raw.request_key,
                    ordinal=ordinal,
                    role="user",
                    content=answer_message_content(raw),
                    message_kind="followup_answer",
                    analysis_result_id=analysis_id,
                    in_reply_to_message_id=question.id,
                    metadata_json=metadata,
                )
                db.add(existing)
                await db.flush()
            if interpretation.response_type == "case_fact" and interpretation.normalized_fact:
                source = await find_matching_source(db, case_id, gap, fingerprint)
                if source is None:
                    source = CaseSource(
                        case_id=case_id,
                        source_kind="followup_answer",
                        origin_message_id=existing.id,
                        exact_text=raw.content,
                        provenance_json={
                            "origin": "adaptive_gap_clarification",
                            "source_analysis_id": str(analysis_id),
                            "source_revision": state["source_evidence_revision"],
                            "gap_id": context.gap.gap_id,
                            "gap_key": context.gap.gap_key,
                            "topic": context.gap.topic,
                            "question": question.content,
                            "clarification_question": question.content,
                            "question_message_id": str(question.id),
                            "clarification_session_id": session_id,
                            "answer_fingerprint": fingerprint,
                        },
                        source_metadata_json={
                            "disposition": raw.disposition,
                            "response_type": interpretation.response_type,
                        },
                    )
                    db.add(source)
                    context.case.evidence_revision += 1
                    current_revision = context.case.evidence_revision
                    await db.flush()
            reply_content = acknowledgement_message(interpretation)
            if await find_reply_message(db, case_id, existing.id) is None:
                reply = ChatMessage(
                    case_id=case_id,
                    client_request_id=f"{raw.request_key}:reply",
                    ordinal=(
                        await db.scalar(
                            select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                                ChatMessage.case_id == case_id
                            )
                        )
                        or 0
                    ) + 1,
                    role="assistant",
                    content=reply_content,
                    message_kind="conversation",
                    analysis_result_id=None,
                    in_reply_to_message_id=existing.id,
                    metadata_json=serialize_message_metadata({"action": "conversation"}),
                )
                db.add(reply)
                await db.flush()
    return {"source_evidence_revision": current_revision}


__all__ = [
    "acknowledgement_message",
    "answer_message_content",
    "commit_answer",
    "find_matching_source",
    "find_reply_message",
    "find_session_message",
    "persist_question",
]
