from __future__ import annotations

from hashlib import sha256
from uuid import UUID

from sqlalchemy import select

from app.models.case_materials import CaseSource
from app.models.chat import ChatMessage
from app.services.gap_clarification.contracts import (
    ClarificationResumeAnswer,
    GapAnswerInterpretation,
)


def acknowledgement_message(interpretation: GapAnswerInterpretation) -> str:
    return {
        "case_fact": "รับทราบข้อมูลเพิ่มเติมแล้วครับ",
        "explicitly_unknown": "รับทราบครับ ว่าข้อมูลส่วนนี้ยังไม่ทราบ",
        "skip": "รับทราบครับ ข้ามข้อมูลส่วนนี้ไว้ก่อน",
        "unrelated": "รับทราบข้อมูลแล้วครับ",
    }.get(interpretation.response_type, "รับข้อมูลแล้วครับ")


async def find_session_message(
    db,
    case_id: UUID,
    session_id: str,
    kind: str,
    attempt: int,
) -> ChatMessage | None:
    messages = await db.scalars(
        select(ChatMessage).where(
            ChatMessage.case_id == case_id,
            ChatMessage.message_kind == kind,
        )
    )
    for message in messages:
        followup = (
            message.metadata_json.get("chat_followup", {})
            if isinstance(message.metadata_json, dict)
            else {}
        )
        if (
            isinstance(followup, dict)
            and followup.get("clarification_session_id") == session_id
            and followup.get("round") == attempt
        ):
            return message
    return None


async def find_reply_message(
    db,
    case_id: UUID,
    answer_id: UUID,
) -> ChatMessage | None:
    return await db.scalar(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case_id,
            ChatMessage.in_reply_to_message_id == answer_id,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "conversation",
        )
        .order_by(ChatMessage.ordinal)
    )


async def find_matching_source(
    db,
    case_id: UUID,
    gap: dict[str, object],
    fingerprint: str,
) -> CaseSource | None:
    sources = await db.scalars(
        select(CaseSource).where(
            CaseSource.case_id == case_id,
            CaseSource.source_kind == "followup_answer",
        )
    )
    for source in sources:
        provenance = source.provenance_json if isinstance(source.provenance_json, dict) else {}
        if provenance.get("gap_id") == gap.get("gap_id") and provenance.get("answer_fingerprint") == fingerprint:
            return source
    return None


def answer_fingerprint(value: str) -> str:
    return sha256(" ".join(value.split()).casefold().encode("utf-8")).hexdigest()


def answer_message_content(answer: ClarificationResumeAnswer) -> str:
    if answer.disposition == "answered":
        return answer.content
    return {
        "unavailable": "I don’t have this information",
        "skipped": "Skip clarification",
    }[answer.disposition]


__all__ = [
    "acknowledgement_message",
    "answer_fingerprint",
    "answer_message_content",
    "find_matching_source",
    "find_reply_message",
    "find_session_message",
]
