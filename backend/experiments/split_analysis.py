from __future__ import annotations

from collections.abc import Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from pydantic import ValidationError

from app.services.analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisMode,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    CaseProviderJudgement,
    CaseProviderReading,
    followup_payload,
    resolve_response_language,
)
from app.services.analysis.prompts import (
    case_judgement_prompt,
    case_reading_prompt,
    validate_analysis_request,
)
from app.services.analysis.settings import AnalysisPipelineConfig, read_pipeline
from app.services.analysis.steps.write import (
    provider_source_payload,
    request_analysis_stage,
    usable_technical_context,
    validate_source_bundle,
)
from app.services.sources.case_source_bundle import CaseSourceBundle


@dataclass(frozen=True)
class CaseReadingOutput:
    reading: CaseProviderReading
    execution_receipt: dict[str, object]


@asynccontextmanager
async def http_client(client: httpx.AsyncClient | None):
    if client is not None:
        yield client
        return
    async with httpx.AsyncClient() as owned:
        yield owned


def stage_receipt(config: AnalysisPipelineConfig) -> dict[str, object]:
    return {
        "configuration": config.model_dump(mode="json"),
        "calls": [],
        "source_reference_type": "case_source",
    }


async def request_case_reading(
    *,
    source_bundle: CaseSourceBundle,
    pipeline_config: dict[str, object],
    question: str | None,
    user_message: object,
    mode: CaseAnalysisMode = "case_overview",
    client: httpx.AsyncClient | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> CaseReadingOutput:
    validated_mode, validated_question = validate_analysis_request(mode, question)
    config = read_pipeline(pipeline_config)
    receipt = stage_receipt(config)
    try:
        validate_source_bundle(source_bundle)
        language = resolve_response_language(user_message)
        content = {
            "response_language": language,
            "analysis_mode": validated_mode,
            "case_sources": [provider_source_payload(source) for source in source_bundle.sources],
            "followup_history": followup_payload(followup_history),
            "question": validated_question,
        }
        async with http_client(client) as http:
            parsed = await request_analysis_stage(
                http,
                config,
                "reading",
                case_reading_prompt(),
                content,
                CaseProviderReading,
                receipt,
            )
        return CaseReadingOutput(reading=parsed, execution_receipt=receipt)
    except CaseAnalysisFailure as error:
        receipt["failure_code"] = error.code
        raise
    except (ValidationError, ValueError) as error:
        receipt["failure_code"] = "case_analysis_invalid"
        raise CaseAnalysisFailure(
            "case_analysis_invalid",
            "Case analysis validation failed",
        ) from error


async def request_case_judgement(
    *,
    source_bundle: CaseSourceBundle,
    pipeline_config: dict[str, object],
    question: str | None,
    user_message: object,
    reading: CaseProviderReading,
    mode: CaseAnalysisMode = "case_overview",
    technical_context: dict[str, object] | None = None,
    retrieval_context_id: str | None = None,
    client: httpx.AsyncClient | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> CaseAnalysisOutput:
    validated_mode, validated_question = validate_analysis_request(mode, question)
    config = read_pipeline(pipeline_config)
    receipt = stage_receipt(config)
    try:
        validate_source_bundle(source_bundle)
        language = resolve_response_language(user_message)
        cleaned_technical_context = usable_technical_context(technical_context)
        content = {
            "response_language": language,
            "analysis_mode": validated_mode,
            "case_sources": [provider_source_payload(source) for source in source_bundle.sources],
            "followup_history": followup_payload(followup_history),
            "reading": reading_payload(reading),
            "technical_context": cleaned_technical_context,
            "question": validated_question,
        }
        async with http_client(client) as http:
            parsed = await request_analysis_stage(
                http,
                config,
                "judgement",
                case_judgement_prompt(),
                content,
                CaseProviderJudgement,
                receipt,
            )
        trace = split_trace(
            reading,
            parsed,
            mode=validated_mode,
            retrieval_context_id=(retrieval_context_id if cleaned_technical_context else None),
        )
        return CaseAnalysisOutput(
            answer=trace.summary,
            trace=trace,
            execution_receipt=receipt,
        )
    except CaseAnalysisFailure as error:
        receipt["failure_code"] = error.code
        raise
    except (ValidationError, ValueError) as error:
        receipt["failure_code"] = "case_analysis_invalid"
        raise CaseAnalysisFailure(
            "case_analysis_invalid",
            "Case analysis validation failed",
        ) from error


def reading_payload(reading: CaseProviderReading) -> dict[str, object]:
    return {
        "claims": [claim.model_dump(mode="json") for claim in reading.claims],
        "involved_parties": [party.model_dump(mode="json") for party in reading.involved_parties],
        "timeline": [item.model_dump(mode="json") for item in reading.timeline],
        "impacts": [impact.model_dump(mode="json") for impact in reading.impacts],
    }


def split_trace(
    reading: CaseProviderReading,
    judgement: CaseProviderJudgement,
    *,
    mode: str,
    retrieval_context_id: str | None = None,
) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode=mode,
        summary=judgement.summary,
        involved_parties=reading.involved_parties,
        timeline=reading.timeline,
        claims=reading.claims,
        impacts=reading.impacts,
        gaps=judgement.gaps,
        mitre_associations=judgement.mitre_associations,
        retrieval_context_id=retrieval_context_id,
    )


__all__ = [
    "CaseReadingOutput",
    "http_client",
    "reading_payload",
    "request_case_judgement",
    "request_case_reading",
    "split_trace",
    "stage_receipt",
]
