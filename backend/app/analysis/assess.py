from __future__ import annotations

from collections.abc import Sequence

from app.analysis.prompts import case_assessment_prompt
from app.analysis.write import provider_source_payload
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig
from app.services.sources.case_source_bundle import CaseSourceBundle
from app.trace.claims import CaseAssessmentTrace, CaseFollowupExchange, followup_payload


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
