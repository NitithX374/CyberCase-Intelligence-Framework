from __future__ import annotations

import hashlib

import httpx
from pydantic import ValidationError

from app.services.case_analysis.contracts import (
    AnalysisMode,
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisResult,
    CaseAnalysisTrace,
    CaseProviderAnalysis,
    build_case_source_registry,
    resolve_response_language,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_analysis.providerStage import request_stage, resolve_target
from app.services.case_analysis.prompts import (
    _validate_analysis_request,
    case_system_prompt,
)
from app.services.case_analysis.validation import validate_case_trace


async def analyze_case(
    *,
    raw_evidence: str,
    analysis_context: dict[str, object],
    user_message: object,
    config: AnalysisPipelineConfig,
    mode: str = "case_overview",
    question: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> CaseAnalysisResult:
    receipt: dict[str, object] = {
        "configuration": config.model_dump(mode="json"),
        "calls": [],
        "source_reference_type": "case_evidence_source",
    }
    try:
        sources = build_case_source_registry(analysis_context)
        if client is not None:
            return await executeCaseAnalysisPipeline(
                raw_evidence,
                analysis_context,
                user_message,
                config,
                sources,
                client,
                receipt,
                mode,
                question,
            )
        async with httpx.AsyncClient() as owned_client:
            return await executeCaseAnalysisPipeline(
                raw_evidence,
                analysis_context,
                user_message,
                config,
                sources,
                owned_client,
                receipt,
                mode,
                question,
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


async def executeCaseAnalysisPipeline(
    raw_evidence: str,
    context: dict[str, object],
    user_message: object,
    config: AnalysisPipelineConfig,
    sources: tuple[CaseAdmittedSource, ...],
    client: httpx.AsyncClient,
    receipt: dict[str, object],
    mode: str,
    question: str | None,
) -> CaseAnalysisResult:
    digest = hashlib.sha256(raw_evidence.encode("utf-8")).hexdigest()
    if context.get("_evidence_sha256", digest) != digest:
        raise CaseAnalysisFailure("case_evidence_stale", "Case snapshot hash changed")
    language = resolve_response_language(user_message)
    if mode == "case_overview" and config.pipeline == "claim_anchored":
        from app.services.case_analysis.claim_anchored.nativeAdapter import (
            execute_claim_anchored_case_pipeline,
        )

        return await execute_claim_anchored_case_pipeline(
            raw_evidence=raw_evidence,
            context=context,
            language=language,
            config=config,
            sources=sources,
            client=client,
            evidence_sha256=digest,
            receipt=receipt,
        )
    return await executeRawDirectPipeline(
        raw_evidence,
        context,
        language,
        config,
        sources,
        client,
        digest,
        receipt,
        mode,
        question,
    )


async def executeRawDirectPipeline(
    raw_evidence: str,
    context: dict[str, object],
    language: str,
    config: AnalysisPipelineConfig,
    sources: tuple[CaseAdmittedSource, ...],
    client: httpx.AsyncClient,
    digest: str,
    receipt: dict[str, object],
    mode: str,
    question: str | None,
) -> CaseAnalysisResult:
    parsed = await requestAnalysisStage(
        client,
        config,
        "direct",
        case_system_prompt(),
        {
            "response_language": language,
            "analysis_mode": mode,
            "raw_case_evidence": raw_evidence,
            "authoritative_case_source_ids": [source.source_id for source in sources],
            "question": question,
        },
        CaseProviderAnalysis,
        receipt,
    )
    trace = validate_case_trace(
        CaseAnalysisTrace(
            analysis_mode=mode,
            summary=parsed.summary,
            claims=parsed.claims,
            gaps=parsed.gaps,
            mitre_associations=[],
            evidence_sha256=digest,
        ),
        sources,
        context.get("document_source_context", []),
    )
    return CaseAnalysisResult(
        answer=parsed.answer.strip(),
        trace=trace,
        execution_receipt=receipt,
    )


async def requestAnalysisStage(
    client: httpx.AsyncClient,
    config: AnalysisPipelineConfig,
    stage: str,
    system: str,
    content: dict[str, object],
    schema: type,
    receipt: dict[str, object],
):
    calls = receipt["calls"]
    if not isinstance(calls, list):
        raise CaseAnalysisFailure("case_receipt_invalid", "Case analysis receipt is invalid")
    return await request_stage(
        client=client,
        target=resolve_target(config),
        config=config,
        stage=f"case_{stage}",
        system=system,
        content=content,
        schema=schema,
        calls=calls,
    )


class MainCaseAnalysisService:
    """Run internal analysis without retrieval, persistence, or state mutation."""

    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def analyze(
        self,
        *,
        mode: AnalysisMode,
        raw_evidence: str,
        analysis_context: dict[str, object] | None,
        question: str | None,
        user_message: object,
    ) -> CaseAnalysisResult:
        validated_mode, validated_question = _validate_analysis_request(
            mode,
            question,
        )
        from app.services.case_analysis.pipelineConfig import read_pipeline

        context = analysis_context or {}
        if context.get("source_reference_type") != "case_evidence_source":
            raise CaseAnalysisFailure(
                "case_sources_invalid",
                "Main Case Analysis requires admitted Case evidence",
            )
        return await analyze_case(
            raw_evidence=raw_evidence,
            analysis_context=context,
            user_message=user_message,
            config=read_pipeline(context.get("_analysis_pipeline")),
            mode=validated_mode,
            question=validated_question,
            client=self._client,
        )


async def request_case_analysis(
    *,
    mode: AnalysisMode,
    raw_evidence: str,
    analysis_context: dict[str, object] | None,
    question: str | None,
    user_message: object,
    client: httpx.AsyncClient | None = None,
) -> CaseAnalysisResult:
    validated_mode, validated_question = _validate_analysis_request(mode, question)
    return await MainCaseAnalysisService(client=client).analyze(
        mode=validated_mode,
        raw_evidence=raw_evidence,
        analysis_context=analysis_context,
        question=validated_question,
        user_message=user_message,
    )


# Backward-compatibility aliases
analyze_case_native = analyze_case
executeNativeAnalysisPipeline = executeCaseAnalysisPipeline

__all__ = [
    "MainCaseAnalysisService",
    "analyze_case",
    "analyze_case_native",
    "executeCaseAnalysisPipeline",
    "executeNativeAnalysisPipeline",
    "executeRawDirectPipeline",
    "requestAnalysisStage",
    "request_case_analysis",
]
