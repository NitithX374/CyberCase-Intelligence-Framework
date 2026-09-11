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
    CASE_TRACE_CORRECTION_PROMPT,
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
    document_quality_context = []
    for item in (context.get("document_source_context") or []):
        if not isinstance(item, dict):
            continue
        for doc in item.get("documents", []):
            if not isinstance(doc, dict):
                continue
            meta = {
                "source_id": item.get("source_id"),
                "document_id": doc.get("document_id"),
                "filename": doc.get("filename"),
            }
            for k in (
                "extraction_method",
                "provider",
                "verification_status",
                "confidence_status",
                "minimum_confidence",
                "warnings",
            ):
                if k in doc:
                    meta[k] = doc[k]
            document_quality_context.append(meta)

    request_content = {
        "response_language": language,
        "analysis_mode": mode,
        "raw_case_evidence": raw_evidence,
        "authoritative_case_source_ids": [source.source_id for source in sources],
        "question": question,
    }
    if document_quality_context:
        request_content["document_quality_context"] = document_quality_context

    parsed = await requestAnalysisStage(
        client,
        config,
        "direct",
        case_system_prompt(),
        request_content,
        CaseProviderAnalysis,
        receipt,
    )
    for correction_attempt in range(_DIRECT_TRACE_MAX_CORRECTIONS + 1):
        try:
            trace = _validate_direct_trace(
                parsed,
                mode=mode,
                digest=digest,
                sources=sources,
                document_context=context.get("document_source_context", []),
            )
            break
        except CaseAnalysisFailure as error:
            if (
                error.code not in _DIRECT_TRACE_CORRECTION_CODES
                or correction_attempt >= _DIRECT_TRACE_MAX_CORRECTIONS
            ):
                raise
            receipt.setdefault("validation_retries", []).append(
                {"attempt": correction_attempt + 1, "reason": error.code}
            )
            receipt.setdefault("validation_retry", {"reason": error.code})
            parsed = await requestAnalysisStage(
                client,
                config,
                "direct_correction",
                case_system_prompt() + "\n" + CASE_TRACE_CORRECTION_PROMPT,
                request_content,
                CaseProviderAnalysis,
                receipt,
            )
    return CaseAnalysisResult(
        answer=parsed.answer.strip(),
        trace=trace,
        execution_receipt=receipt,
    )


_DIRECT_TRACE_CORRECTION_CODES = frozenset(
    {
        "case_trace_support_outside_evidence",
        "case_trace_contradiction_outside_evidence",
        "case_trace_conflicting_source_role",
        "case_trace_claim_unbound",
        "case_trace_role_citation_missing",
        "case_trace_citation_role_invalid",
        "case_trace_citation_revision_invalid",
        "case_trace_citation_quote_invalid",
        "case_trace_party_without_claim",
        "case_trace_party_unknown_claim",
        "case_trace_timeline_without_claim",
        "case_trace_timeline_unknown_claim",
        "case_trace_impact_without_claim",
        "case_trace_impact_unknown_claim",
        "case_trace_gap_unknown_claim",
    }
)
_DIRECT_TRACE_MAX_CORRECTIONS = 2


def _validate_direct_trace(
    parsed: CaseProviderAnalysis,
    *,
    mode: str,
    digest: str,
    sources: tuple[CaseAdmittedSource, ...],
    document_context: object,
) -> CaseAnalysisTrace:
    return validate_case_trace(
        CaseAnalysisTrace(
            analysis_mode=mode,
            summary=parsed.summary,
            involved_parties=parsed.involved_parties,
            timeline=parsed.timeline,
            claims=parsed.claims,
            impacts=parsed.impacts,
            gaps=parsed.gaps,
            mitre_associations=[],
            evidence_sha256=digest,
        ),
        sources,
        document_context,
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
