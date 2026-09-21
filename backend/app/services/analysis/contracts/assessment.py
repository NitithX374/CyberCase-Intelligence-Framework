from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.services.analysis.contracts.claims import CaseAnalysisGap


class CaseAssessmentTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_assessment_v1"] = "case_assessment_v1"
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)


__all__ = ["CaseAssessmentTrace"]
