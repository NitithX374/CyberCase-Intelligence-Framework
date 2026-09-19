"""Asking the reader about the things the analysis could not settle.

The analysis decides which gaps are worth asking about and writes the question
for each. This adds when to ask them and what to do with the replies.

One question is outstanding at a time, so a reply needs no marking: it answers
the question above it, and becomes a case source bound to that gap. The next
question follows from the same analysis, until the round's questions run out —
only then is the case analysed again, so a round of three costs one analysis
rather than three.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.chat import ChatMessage
from app.models.sources import CaseSource
from app.services.case_analysis.contracts import CaseAnalysisGap, CaseAnalysisTrace


async def rounds_asked(db: AsyncSession, case_id: UUID) -> int:
    """How many analyses have asked. One analysis is one round of questions.

    Counted over the case, and spent only against a chain a reply is continuing:
    an analysis the reader asked for is a fresh start, not the next round of an
    old one.
    """

    return await db.scalar(
        select(func.count(func.distinct(ChatMessage.analysis_result_id))).where(
            ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None)
        )
    )


async def asked_this_round(db: AsyncSession, analysis_result_id: UUID) -> set[str]:
    """The gaps this analysis has already asked about."""

    rows = await db.scalars(
        select(ChatMessage.gap_key).where(
            ChatMessage.analysis_result_id == analysis_result_id,
            ChatMessage.gap_key.is_not(None),
        )
    )
    return set(rows)


def next_gap(
    trace: CaseAnalysisTrace,
    *,
    asked: set[str],
    rounds: int,
) -> CaseAnalysisGap | None:
    """The next gap to ask about, or None when this round is done.

    Priority, askability and the question itself all come from the analysis, so
    there is nothing to rank. The keys come from one trace, so they are
    consistent within a round and matching them needs no normalising.
    """

    if rounds > settings.chat_followup_max_rounds:
        return None
    if len(asked) >= settings.chat_followup_gaps_per_round:
        return None
    return next(
        (
            gap
            for gap in trace.gaps
            if gap.priority == "high"
            and gap.askable
            and gap.clarification_question
            and gap.gap_key not in asked
        ),
        None,
    )


def question_message(
    *,
    case_id: UUID,
    ordinal: int,
    gap: CaseAnalysisGap,
    analysis_result_id: UUID,
) -> ChatMessage:
    return ChatMessage(
        case_id=case_id,
        ordinal=ordinal,
        role="assistant",
        content=gap.clarification_question,
        gap_key=gap.gap_key,
        analysis_result_id=analysis_result_id,
    )


async def pending_question(db: AsyncSession, case_id: UUID) -> ChatMessage | None:
    """The question waiting on a reply. There is never more than one."""

    question = await db.scalar(
        select(ChatMessage)
        .where(ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None))
        .order_by(ChatMessage.ordinal.desc())
    )
    if question is None:
        return None
    reply = await db.scalar(
        select(ChatMessage.id).where(ChatMessage.in_reply_to_message_id == question.id)
    )
    return None if reply else question


def answer_message(
    *,
    case_id: UUID,
    ordinal: int,
    content: str,
    question: ChatMessage,
    client_request_id: str | None,
) -> ChatMessage:
    return ChatMessage(
        case_id=case_id,
        ordinal=ordinal,
        role="user",
        content=content,
        analysis_result_id=question.analysis_result_id,
        in_reply_to_message_id=question.id,
        client_request_id=client_request_id,
    )


def answer_source(*, case_id: UUID, answer: ChatMessage, question: ChatMessage) -> CaseSource:
    """The reply as case material, carrying the question it answers."""

    return CaseSource(
        case_id=case_id,
        source_kind="followup_answer",
        origin_message_id=answer.id,
        exact_text=answer.content,
        provenance_json={
            "origin": "case_followup",
            "gap_key": question.gap_key,
            "question": question.content,
        },
    )


__all__ = [
    "answer_message",
    "answer_source",
    "asked_this_round",
    "next_gap",
    "pending_question",
    "question_message",
    "rounds_asked",
]
