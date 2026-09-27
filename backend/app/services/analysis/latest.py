from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.schemas.rag import LegalReferenceResult
from app.services.analysis.technical_context_contracts import (
    CaseRagContextPayload,
    CaseTechnicalAugmentation,
)
from app.services.cases.ownership import owned_case


class RecordedRetrieval(BaseModel):
    context: str = Field(min_length=1)
    technical_augmentation: CaseTechnicalAugmentation
    legal_relevance: LegalReferenceResult


def recorded_technical_context(row: CaseAnalysisResult) -> CaseRagContextPayload | None:
    stored = row.retrieval_context_json
    if not isinstance(stored, dict) or not isinstance(row.external_context_json, dict):
        return None
    try:
        recorded = RecordedRetrieval.model_validate(
            {**row.external_context_json, "context": stored.get("context")}
        )
    except ValidationError:
        return None
    augmentation = recorded.technical_augmentation
    if not augmentation.retrieval_context_id:
        return None
    return CaseRagContextPayload(
        retrieval_context_id=augmentation.retrieval_context_id,
        context=recorded.context,
        mitre_table=tuple(augmentation.mitre_table),
        legal_relevance=recorded.legal_relevance,
    )


async def get_latest_case_analysis(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> tuple[Case, CaseAnalysisResult | None]:
    case = await owned_case(
        db, case_id, user_id, options=(selectinload(Case.latest_analysis_result),)
    )
    result = case.latest_analysis_result
    return case, result if result is None or result.status == "validated" else None


def analysis_freshness(case: Case, result: CaseAnalysisResult | None) -> str:
    if result is None:
        return "missing"
    return "current" if result.source_revision == case.source_revision else "stale"


__all__ = [
    "RecordedRetrieval",
    "analysis_freshness",
    "get_latest_case_analysis",
    "recorded_technical_context",
]
