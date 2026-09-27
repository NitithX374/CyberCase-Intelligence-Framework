from __future__ import annotations

from collections.abc import Sequence

from app.services.analysis.contracts import (
    CaseAssessmentTrace,
    CaseFollowupExchange,
    followup_payload,
)
from app.services.analysis.prompts import case_assessment_prompt
from app.services.analysis.provider import request_stage
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.analysis.steps.write import provider_source_payload
from app.services.sources.case_source_bundle import CaseSourceBundle


async def assess_case(
    *,
    source_bundle: CaseSourceBundle,
    followup_history: Sequence[CaseFollowupExchange],
    response_language: str,
    config: AnalysisPipelineConfig,
) -> CaseAssessmentTrace:
    return await request_stage(
        config=config,
        stage="assess",
        system=case_assessment_prompt(),
        content={
            "response_language": response_language,
            "case_sources": [provider_source_payload(source) for source in source_bundle.sources],
            "followup_history": followup_payload(followup_history),
        },
        schema=CaseAssessmentTrace,
    )


__all__ = ["assess_case"]
