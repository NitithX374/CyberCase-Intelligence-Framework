from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.caseMaterials import EvidenceSource
from app.services.case_materials.materialService import CaseMaterialsError


def _source_label(source: EvidenceSource) -> str:
    if source.document is not None:
        return f"DOCUMENT {source.document.filename}"
    return {
        "narrative": "CASE NARRATIVE",
        "followup_answer": "FOLLOW-UP ANSWER",
    }.get(source.source_kind, "CASE MATERIAL")


@dataclass(frozen=True)
class AssembledCaseEvidence:
    input_text: str
    active_sources: list[EvidenceSource]
    evidence_revision: int


async def assembleCaseEvidence(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> AssembledCaseEvidence:
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.evidence_sources).selectinload(EvidenceSource.document))
        .where(Case.id == case_id)
        .with_for_update()
    )
    case = result.scalar_one_or_none()
    if case is None or (user_id is not None and case.user_id != user_id):
        raise CaseMaterialsError("case_not_found", "Case not found", 404)

    selected: list[EvidenceSource] = []
    for source in sorted(case.evidence_sources, key=lambda item: (item.created_at, str(item.id))):
        if source.archived_at is not None:
            continue
        if not source.exact_text.strip():
            raise CaseMaterialsError("evidence_text_empty", "Admitted evidence text is empty")
        selected.append(source)
    if not selected:
        raise CaseMaterialsError("case_evidence_missing", "Add and admit case material before analysis")

    input_text = "\n\n".join(
        f"[{_source_label(source)} · SOURCE {source.id}]\n{source.exact_text.strip()}"
        for source in selected
    )
    return AssembledCaseEvidence(
        input_text=input_text,
        active_sources=selected,
        evidence_revision=case.evidence_revision,
    )


__all__ = ["AssembledCaseEvidence", "assembleCaseEvidence"]
