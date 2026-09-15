from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.caseMaterials import EvidenceSource
from app.models.caseRun import CaseAnalysisResult
from app.models.chat import ChatMessage
from app.schemas.caseClarifications import (
    CaseClarificationAnswer,
    CaseClarificationRead,
    ClarificationState,
)
from app.services.followup.caseClarificationSupport import (
    CaseClarificationHistoryError,
    answer_fingerprint,
    owned_case,
)
from app.services.followup.contracts import ClarificationExchange


async def load_case_clarification_exchanges(
    db: AsyncSession,
    case_id: UUID,
) -> tuple[ClarificationExchange, ...]:
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case_id,
            ChatMessage.role == "user",
            ChatMessage.message_kind.in_(
                ("followup_answer",)
            ),
        )
        .order_by(ChatMessage.ordinal)
    )
    answer_messages = list(result.scalars().all())
    if not answer_messages:
        return ()

    exchanges: list[ClarificationExchange] = []
    for answer_message in answer_messages:
        question_message = None
        if answer_message.in_reply_to_message_id:
            question_message = await db.get(ChatMessage, answer_message.in_reply_to_message_id)
        if question_message is None:
            question_message = await db.scalar(
                select(ChatMessage)
                .where(
                    ChatMessage.case_id == case_id,
                    ChatMessage.ordinal < answer_message.ordinal,
                    ChatMessage.role == "assistant",
                    ChatMessage.message_kind == "followup_question",
                )
                .order_by(ChatMessage.ordinal.desc())
            )
        if question_message is None:
            continue

        metadata = question_message.metadata_json if isinstance(question_message.metadata_json, dict) else {}
        identity = followup_identity(metadata)
        if identity is None:
            continue
        gap_id, topic, gap_key = identity
        exchanges.append(
            ClarificationExchange(
                question=question_message.content,
                answer=answer_message.content,
                gap_id=gap_id,
                gap_topic=topic,
                gap_key=gap_key,
                question_message_id=str(question_message.id),
                answer_message_id=str(answer_message.id),
            )
        )
    return tuple(exchanges)


async def get_owned_clarifications(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None = None,
) -> list[CaseClarificationRead]:
    case = await owned_case(db, case_id, user_id)
    question_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case.id,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "followup_question",
        )
        .order_by(ChatMessage.created_at, ChatMessage.ordinal)
    )
    question_messages = list(question_result.scalars().all())
    if not question_messages:
        return []

    answer_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case.id,
            ChatMessage.role == "user",
            ChatMessage.message_kind.in_(
                ("followup_answer",)
            ),
        )
        .order_by(ChatMessage.ordinal)
    )
    answer_messages = list(answer_result.scalars().all())
    answer_source_by_message_id = await answer_sources_by_message_id(db, answer_messages)
    answers_by_question = {
        answer.in_reply_to_message_id: answer
        for answer in answer_messages
        if answer.in_reply_to_message_id
    }

    clarifications: list[CaseClarificationRead] = []
    for question_message in question_messages:
        metadata = question_message.metadata_json if isinstance(question_message.metadata_json, dict) else {}
        answer_message = answers_by_question.get(question_message.id)
        if answer_message is None:
            answer_message = next(
                (
                    answer for answer in answer_messages
                    if answer.ordinal > question_message.ordinal
                    and (
                        answer.in_reply_to_message_id is None
                        or answer.in_reply_to_message_id == question_message.id
                    )
                ),
                None,
            )

        origin_result_id = question_message.analysis_result_id
        if origin_result_id is None:
            raise CaseClarificationHistoryError(
                "clarification_context_invalid",
                "Clarification question has no pinned analysis result",
            )
        origin_result = await db.get(CaseAnalysisResult, origin_result_id)
        if origin_result is None or origin_result.case_id != case.id:
            raise CaseClarificationHistoryError(
                "clarification_context_invalid",
                "Clarification question has an invalid analysis result",
            )

        identity = followup_identity(metadata)
        if identity is None:
            raise CaseClarificationHistoryError(
                "clarification_context_invalid",
                "Clarification question has no follow-up identity",
            )
        gap_id, topic, gap_key = identity
        if answer_message is not None:
            state: ClarificationState = "answered"
            answer_source_id = answer_source_by_message_id.get(answer_message.id)
            answer_message_id = answer_message.id
            answered_at = answer_message.created_at
            fingerprint = answer_fingerprint(
                CaseClarificationAnswer(answer=answer_message.content, idempotency_key="read")
            )
        else:
            state = "superseded" if case.latest_analysis_result_id and case.latest_analysis_result_id != origin_result_id else "pending"
            answer_source_id = None
            answer_message_id = None
            answered_at = None
            fingerprint = None

        clarifications.append(
            CaseClarificationRead(
                id=question_message.id,
                case_id=case.id,
                origin_analysis_result_id=origin_result_id,
                gap_key=gap_key,
                gap_id=gap_id,
                topic=topic,
                question=question_message.content,
                metadata_json=metadata,
                state=state,
                answer_evidence_source_id=answer_source_id,
                question_message_id=question_message.id,
                answer_message_id=answer_message_id,
                answer_fingerprint=fingerprint,
                answered_at=answered_at,
                created_at=question_message.created_at,
                updated_at=answered_at or question_message.created_at,
            )
        )
    return clarifications


def followup_identity(
    metadata: dict[str, object],
) -> tuple[str, str, str] | None:
    followup = metadata.get("chat_followup")
    if not isinstance(followup, dict):
        return None
    gap_id = followup.get("gap_id")
    topic = followup.get("topic")
    gap_key = followup.get("gap_key")
    if not all(isinstance(value, str) and value.strip() for value in (gap_id, topic, gap_key)):
        return None
    return gap_id.strip(), topic.strip(), gap_key.strip()


async def answer_sources_by_message_id(
    db: AsyncSession,
    answer_messages: list[ChatMessage],
) -> dict[UUID, UUID]:
    message_ids = [message.id for message in answer_messages]
    if not message_ids:
        return {}
    result = await db.execute(
        select(EvidenceSource).where(EvidenceSource.origin_message_id.in_(message_ids))
    )
    return {
        source.origin_message_id: source.id
        for source in result.scalars().all()
        if source.origin_message_id is not None
    }


__all__ = ["get_owned_clarifications", "load_case_clarification_exchanges"]
