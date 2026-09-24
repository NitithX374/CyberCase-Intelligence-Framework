from __future__ import annotations

from collections.abc import Sequence

import httpx
from pydantic import ValidationError

from app.services.analysis.contracts import (
    CaseAnalysisFailure,
    CaseAssessmentTrace,
    CaseFollowupExchange,
    followup_payload,
)
from app.services.analysis.prompts import case_assessment_prompt
from app.services.analysis.provider import request_stage, resolve_target
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.analysis.steps.write import provider_source_payload, validate_source_bundle
from app.services.sources.case_source_bundle import CaseSourceBundle


async def assess_case(
    *,
    source_bundle: CaseSourceBundle,
    followup_history: Sequence[CaseFollowupExchange],
    response_language: str,
    config: AnalysisPipelineConfig,
    client: httpx.AsyncClient | None = None,
) -> CaseAssessmentTrace:
    calls: list[dict[str, object]] = []
    content = {
        "response_language": response_language,
        "case_sources": [provider_source_payload(source) for source in source_bundle.sources],
        "followup_history": followup_payload(followup_history),
    }
    try:
        validate_source_bundle(source_bundle)
        if client is not None:
            return await request_assessment(client, config, content, calls)
        async with httpx.AsyncClient() as owned_client:
            return await request_assessment(owned_client, config, content, calls)
    except CaseAnalysisFailure:
        raise
    except (ValidationError, ValueError) as error:
        raise CaseAnalysisFailure(
            "case_assessment_invalid", "Case assessment validation failed"
        ) from error


async def request_assessment(
    client: httpx.AsyncClient,
    config: AnalysisPipelineConfig,
    content: dict[str, object],
    calls: list[dict[str, object]],
) -> CaseAssessmentTrace:
    result = await request_stage(
        client=client,
        target=resolve_target(config),
        config=config,
        stage="assess",
        system=case_assessment_prompt(),
        content=content,
        schema=CaseAssessmentTrace,
        calls=calls,
    )
    if not isinstance(result, CaseAssessmentTrace):
        raise CaseAnalysisFailure(
            "case_assessment_invalid", "Case assessment did not produce validated gaps"
        )
    return result


__all__ = ["assess_case", "request_assessment"]
