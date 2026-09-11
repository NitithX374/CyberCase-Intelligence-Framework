from __future__ import annotations

import hashlib
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.caseClarification import CaseClarification
from app.models.caseMaterials import EvidenceSource
from app.services.followup.schemas import ClarificationExchange


class CaseClarificationHistoryError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


async def load_case_clarification_exchanges(
    db: AsyncSession,
    case_id: UUID,
) -> tuple[ClarificationExchange, ...]:
    result = await db.execute(
        select(CaseClarification)
        .options(
            selectinload(CaseClarification.answer_evidence_source).selectinload(
                EvidenceSource.revisions
            ),
            selectinload(CaseClarification.origin_snapshot),
        )
        .where(
            CaseClarification.case_id == case_id,
            CaseClarification.state == "answered",
        )
        .order_by(CaseClarification.answered_at, CaseClarification.created_at, CaseClarification.id)
    )
    exchanges: list[ClarificationExchange] = []
    for clarification in result.scalars().all():
        source = clarification.answer_evidence_source
        snapshot = clarification.origin_snapshot
        metadata = clarification.metadata_json
        revision_number = metadata.get("answer_evidence_revision") if isinstance(metadata, dict) else None
        if source is None or type(revision_number) is not int or revision_number < 1:
            raise CaseClarificationHistoryError(
                "clarification_history_invalid",
                "Answered clarification evidence provenance is incomplete",
            )
        revision = next(
            (item for item in source.revisions if item.revision == revision_number),
            None,
        )
        if (
            revision is None
            or not revision.exact_text.strip()
            or source.case_id != case_id
            or snapshot is None
            or snapshot.case_id != case_id
            or hashlib.sha256(revision.exact_text.encode("utf-8")).hexdigest() != revision.text_sha256
            or hashlib.sha256(snapshot.input_text.encode("utf-8")).hexdigest() != snapshot.text_sha256
        ):
            raise CaseClarificationHistoryError(
                "clarification_history_invalid",
                "Answered clarification evidence history is unavailable",
            )
        exchanges.append(
            ClarificationExchange(
                question=clarification.question,
                answer=revision.exact_text,
                gap_id=clarification.gap_id,
                gap_topic=clarification.topic,
                gap_key=clarification.gap_key,
                evidence_sha256=snapshot.text_sha256,
                question_message_id=(
                    str(clarification.question_message_id)
                    if clarification.question_message_id
                    else None
                ),
                answer_message_id=(
                    str(clarification.answer_message_id)
                    if clarification.answer_message_id
                    else None
                ),
            )
        )
    return tuple(exchanges)


__all__ = [
    "CaseClarificationHistoryError",
    "load_case_clarification_exchanges",
]
