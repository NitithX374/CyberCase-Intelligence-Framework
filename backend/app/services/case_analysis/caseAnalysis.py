from __future__ import annotations

import asyncio
import hashlib
from dataclasses import asdict

import httpx
from pydantic import ValidationError

from app.config import settings
from app.services.case_analysis.caseAnalysisResponseParser import (
    parse_case_analysis_response,
)
from app.services.case_analysis.caseBinding import (
    bind_case_claims,
    select_case_claims,
)
from app.services.case_analysis.claim_anchored import (
    input_budget,
    request_stage,
    resolve_target,
    token_count,
)
from app.services.case_analysis.claim_anchored.contracts import ClaimAnchoredFailure
from app.services.case_analysis.contracts import (
    AnalysisMode,
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisResult,
    CaseAnalysisTrace,
    CaseExtractedClaims,
    CaseGeneratedSummary,
    CaseProviderAnalysis,
    ProviderCaseAnalysisV3,
    build_case_source_registry,
    resolve_response_language,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_analysis.prompts import (
    CASE_EXTRACTION_PROMPT,
    CASE_GENERATION_PROMPT,
    _ANALYSIS_TRACE_OUTPUT_PROMPT,
    _CASE_ANALYSIS_TRUST_PROMPT,
    _PERSONALIZED_RESPONSE_PROMPT,
    _TASK_PROMPTS,
    _validate_analysis_request,
    build_case_analysis_prompt,
    case_generation_input,
    case_system_prompt,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.llm.coreLlm import resolve_core_llm_target
from app.services.llm.structuredOutput import (
    structured_output_request_options,
    structured_output_schema,
)


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
    except (CaseAnalysisFailure, ValidationError) as error:
        code = getattr(error, "code", "case_analysis_invalid")
        message = getattr(error, "message", "Case analysis validation failed")
        receipt["failure_code"] = code
        raise ClaimAnchoredFailure(code, message, receipt) from error


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
        return await executeClaimAnchoredPipeline(
            raw_evidence, context, language, config, sources, client, digest, receipt
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


async def executeClaimAnchoredPipeline(
    raw_evidence: str,
    context: dict[str, object],
    language: str,
    config: AnalysisPipelineConfig,
    sources: tuple[CaseAdmittedSource, ...],
    client: httpx.AsyncClient,
    digest: str,
    receipt: dict[str, object],
) -> CaseAnalysisResult:
    extracted = await requestAnalysisStage(
        client,
        config,
        "extraction",
        CASE_EXTRACTION_PROMPT,
        {
            "response_language": language,
            "sources": [asdict(source) for source in sources],
        },
        CaseExtractedClaims,
        receipt,
    )
    bound = bind_case_claims(extracted, sources, context.get("document_source_context", []))
    selection = await asyncio.to_thread(
        select_case_claims,
        bound,
        source_ids=tuple(source.source_id for source in sources),
        max_claims=config.max_claims,
        fits=lambda values: token_count(
            {
                "system": CASE_GENERATION_PROMPT,
                "content": case_generation_input(values, language),
            }
        )
        <= min(input_budget(config), config.selection_tokens),
    )
    receipt["selection_policy"] = "stable_case_source_coverage_v1"
    receipt["omissions"] = list(selection.omissions)
    generated = await requestAnalysisStage(
        client,
        config,
        "generation",
        CASE_GENERATION_PROMPT,
        case_generation_input(selection.claims, language),
        CaseGeneratedSummary,
        receipt,
    )
    known = {claim.claim.claim_id for claim in selection.claims}
    referenced = {claim_id for unit in generated.units for claim_id in unit.claim_ids}
    if referenced != known:
        raise CaseAnalysisFailure(
            "case_generation_mapping_loss",
            "Case generation omitted or changed selected claims",
        )
    trace = validate_case_trace(
        CaseAnalysisTrace(
            analysis_mode="case_overview",
            summary="\n\n".join(unit.text for unit in generated.units),
            claims=[bound.claim for bound in selection.claims],
            evidence_sha256=digest,
        ),
        sources,
        context.get("document_source_context", []),
    )
    return CaseAnalysisResult(
        answer=trace.summary,
        trace=trace,
        execution_receipt=receipt,
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
        """Analyze defensive snapshots of Case Narrative and retrieval context."""

        validated_mode, validated_question = _validate_analysis_request(
            mode,
            question,
        )
        from app.services.case_analysis.pipelineConfig import read_pipeline

        config = read_pipeline((analysis_context or {}).get("_analysis_pipeline"))
        if (analysis_context or {}).get("source_reference_type") == "case_evidence_source":
            return await analyze_case(
                raw_evidence=raw_evidence,
                analysis_context=analysis_context or {},
                user_message=user_message,
                config=config,
                mode=validated_mode,
                question=validated_question,
                client=self._client,
            )
        if validated_mode == "case_overview" and config.pipeline == "claim_anchored":
            from app.services.case_analysis.claim_anchored.service import (
                analyze_claim_anchored,
            )

            return await analyze_claim_anchored(
                raw_evidence=raw_evidence,
                analysis_context=analysis_context or {},
                user_message=user_message,
                config=config,
                client=self._client,
            )
        try:
            response_language = resolve_response_language(user_message)
        except ValueError as error:
            raise CaseAnalysisFailure(
                "analysis_response_language_unsupported",
                str(error),
            ) from error
        prompt = build_case_analysis_prompt(
            mode=validated_mode,
            raw_evidence=raw_evidence,
            analysis_context=analysis_context,
            question=validated_question,
            response_language=response_language,
        )
        target = resolve_core_llm_target(settings.chat_ask_model)
        request_payload = {
            "model": target.model,
            **structured_output_request_options(
                provider=target.provider,
                feature="case_analysis",
                configured_max_tokens=max(1, settings.chat_ask_max_output_tokens),
            ),
            "system": (
                _CASE_ANALYSIS_TRUST_PROMPT
                + "\n"
                + _TASK_PROMPTS[validated_mode]
                + "\n"
                + _PERSONALIZED_RESPONSE_PROMPT
                + "\n"
                + _ANALYSIS_TRACE_OUTPUT_PROMPT
            ),
            "messages": [{"role": "user", "content": prompt}],
            "output_config": {
                "format": {
                    "type": "json_schema",
                    "schema": structured_output_schema(
                        ProviderCaseAnalysisV3,
                        provider=target.provider,
                    ),
                }
            },
        }

        if self._client is not None:
            response = await self._post(
                self._client,
                target.messages_url,
                target.headers,
                request_payload,
            )
        else:
            async with httpx.AsyncClient(
                timeout=max(0.01, settings.chat_ask_timeout_seconds),
            ) as owned_client:
                response = await self._post(
                    owned_client,
                    target.messages_url,
                    target.headers,
                    request_payload,
                )

        trusted_context = analysis_context or {}
        raw_source_ids = trusted_context.get("source_message_ids", [])
        source_message_ids = (
            {value.strip() for value in raw_source_ids if isinstance(value, str)}
            if isinstance(raw_source_ids, list)
            else set()
        )
        return parse_case_analysis_response(
            response,
            source_message_ids=source_message_ids,
            analysis_context=trusted_context,
            analysis_mode=validated_mode,
            evidence_sha256=hashlib.sha256(
                raw_evidence.strip().encode("utf-8")
            ).hexdigest(),
        )

    @staticmethod
    async def _post(
        client: httpx.AsyncClient,
        messages_url: str,
        headers: dict[str, str],
        request_payload: dict[str, object],
    ) -> httpx.Response:
        try:
            return await client.post(
                messages_url,
                headers=headers,
                json=request_payload,
            )
        except httpx.TimeoutException as exc:
            raise CaseAnalysisFailure(
                "analysis_timeout",
                "The post-answer analysis request timed out",
            ) from exc
        except httpx.RequestError as exc:
            raise CaseAnalysisFailure(
                "analysis_transport_error",
                "The post-answer analysis request failed",
            ) from exc


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
    "executeClaimAnchoredPipeline",
    "executeNativeAnalysisPipeline",
    "executeRawDirectPipeline",
    "requestAnalysisStage",
    "request_case_analysis",
    "resolve_core_llm_target",
]
