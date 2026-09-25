from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field

from app.errors import AppError
from app.services.analysis.contracts import CaseAnalysisTrace, CaseFollowupExchange
from app.services.analysis.steps.technical_context import CaseTechnicalAugmentation
from app.services.sources.case_source_bundle import CaseSourceBundle


class CaseReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    case_id: UUID
    case_title: str = "CyberCase Investigation"
    analysis_result_id: UUID
    analysis_created_at: datetime | None = None
    source_bundle: CaseSourceBundle
    analysis_summary: str = Field(min_length=1)
    analysis_trace: CaseAnalysisTrace
    technical_augmentation: CaseTechnicalAugmentation | None = None
    followup_history: tuple[CaseFollowupExchange, ...] = ()


class ReportGenerationConflict(AppError):
    pass


class ReportNotFound(AppError):
    status_code = status.HTTP_404_NOT_FOUND


__all__ = [
    "CaseReportInput",
    "ReportGenerationConflict",
    "ReportNotFound",
]
