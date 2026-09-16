from __future__ import annotations

import httpx
from pydantic import ValidationError

from app.services.case_analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisMode,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseProviderAnalysis,
    resolve_response_language,
)
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig, read_pipeline
from app.services.case_analysis.prompts import (
    CASE_TRACE_CORRECTION_PROMPT,
    case_system_prompt,
    validate_analysis_request,
)
from app.services.case_analysis.provider_stage import request_stage, resolve_target
from app.services.case_analysis.validation import validate_case_trace
from app.services.case_materials import CaseSourceBundle, CaseSourceItem


async def analyze_case(
    *,
    source_bundle: CaseSourceBundle,
    user_message: object,
    config: AnalysisPipelineConfig,
    mode: str = "case_overview",
    question: str | None = None,
    client: httpx.AsyncClient | None = None,
    technical_context: dict[str, object] | None = None,
    retrieval_context_id: str | None = None,
) -> CaseAnalysisOutput:
    receipt: dict[str, object] = {
        "configuration": config.model_dump(mode="json"),
        "calls": [],
        "source_reference_type": "case_source",
    }
    try:
        validate_source_bundle(source_bundle)
        language = resolve_response_language(user_message)
        if client is not None:
            return await execute_analysis_pipeline(
                source_bundle,
                language,
                config,
                client,
                receipt=receipt,
                mode=mode,
                question=question,
                technical_context=technical_context,
                retrieval_context_id=retrieval_context_id,
            )
        async with httpx.AsyncClient() as owned_client:
            return await execute_analysis_pipeline(
                source_bundle,
                language,
                config,
                owned_client,
                receipt=receipt,
                mode=mode,
                question=question,
                technical_context=technical_context,
                retrieval_context_id=retrieval_context_id,
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


async def execute_analysis_pipeline(
    source_bundle: CaseSourceBundle,
    language: str,
    config: AnalysisPipelineConfig,
    client: httpx.AsyncClient | None,
    *,
    receipt: dict[str, object],
    mode: str = "case_overview",
    question: str | None = None,
    technical_context: dict[str, object] | None = None,
    retrieval_context_id: str | None = None,
) -> CaseAnalysisOutput:
    validate_source_bundle(source_bundle)
    cleaned_technical_context = None
    if (
        isinstance(technical_context, dict)
        and isinstance(technical_context.get("context"), str)
        and isinstance(technical_context.get("mitre_table"), (list, tuple))
        and technical_context.get("mitre_table")
    ):
        cleaned_technical_context = {
            "context": technical_context["context"],
            "mitre_table": list(technical_context["mitre_table"]),
        }

    request_content = {
        "response_language": language,
        "analysis_mode": mode,
        "case_sources": [
            provider_source_payload(source)
            for source in source_bundle.sources
        ],
        "technical_context": cleaned_technical_context,
        "question": question,
    }

    parsed = await request_analysis_stage(
        client,
        config,
        "direct",
        case_system_prompt(),
        request_content,
        CaseProviderAnalysis,
        receipt,
    )
    mitre_table = (
        cleaned_technical_context["mitre_table"]
        if cleaned_technical_context
        else None
    )
    bound_retrieval_id = retrieval_context_id if cleaned_technical_context else None
    for correction_attempt in range(_DIRECT_TRACE_MAX_CORRECTIONS + 1):
        try:
            trace = validate_direct_trace(
                parsed,
                mode=mode,
                source_bundle=source_bundle,
                retrieval_context_id=bound_retrieval_id,
                mitre_table=mitre_table,
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
            parsed = await request_analysis_stage(
                client,
                config,
                "direct_correction",
                case_system_prompt() + "\n" + CASE_TRACE_CORRECTION_PROMPT,
                request_content,
                CaseProviderAnalysis,
                receipt,
            )
    return CaseAnalysisOutput(
        answer=parsed.answer.strip(),
        trace=trace,
        execution_receipt=receipt,
    )


def provider_source_payload(source: CaseSourceItem) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_id": source.source_id,
        "source_kind": source.source_kind,
        "text": source.text,
    }
    if source.source_kind == "document" or source.document_id or source.filename:
        document: dict[str, object] = {
            "document_id": source.document_id,
            "filename": source.filename,
        }
        for quality_key in (
            "extraction_method",
            "provider",
            "verification_status",
            "confidence_status",
            "minimum_confidence",
            "warnings",
        ):
            if quality_key in source.provenance:
                document[quality_key] = source.provenance[quality_key]
        payload["document"] = document
    return payload


def validate_source_bundle(source_bundle: CaseSourceBundle) -> None:
    if not isinstance(source_bundle, CaseSourceBundle) or not source_bundle.sources:
        raise CaseAnalysisFailure("case_sources_invalid", "Case source bundle is invalid")
    source_ids = [source.source_id for source in source_bundle.sources]
    if (
        any(not isinstance(source_id, str) or not source_id.strip() for source_id in source_ids)
        or len(source_ids) != len(set(source_ids))
    ):
        raise CaseAnalysisFailure("case_sources_invalid", "Case source bundle is invalid")
    if any(not isinstance(source.text, str) or not source.text.strip() for source in source_bundle.sources):
        raise CaseAnalysisFailure("case_source_empty", "Case source text is empty")


_DIRECT_TRACE_CORRECTION_CODES = frozenset(
    {
        "case_trace_support_outside_evidence",
        "case_trace_contradiction_outside_evidence",
        "case_trace_conflicting_source_role",
        "case_trace_claim_unbound",
        "case_trace_role_citation_missing",
        "case_trace_citation_role_invalid",
        "case_trace_citation_quote_invalid",
        "case_trace_party_without_claim",
        "case_trace_party_unknown_claim",
        "case_trace_timeline_without_claim",
        "case_trace_timeline_unknown_claim",
        "case_trace_impact_without_claim",
        "case_trace_impact_unknown_claim",
        "case_trace_gap_unknown_claim",
        "case_trace_mitre_without_retrieval",
        "case_trace_mitre_unknown_claim",
        "case_trace_mitre_outside_context",
    }
)
_DIRECT_TRACE_MAX_CORRECTIONS = 2


def validate_direct_trace(
    parsed: CaseProviderAnalysis,
    *,
    mode: str,
    source_bundle: CaseSourceBundle,
    retrieval_context_id: str | None = None,
    mitre_table: list[dict[str, object]] | tuple[dict[str, object], ...] | None = None,
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
            mitre_associations=parsed.mitre_associations,
            retrieval_context_id=retrieval_context_id,
        ),
        source_bundle,
        mitre_table=list(mitre_table) if mitre_table else [],
    )


async def request_analysis_stage(
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


async def request_case_analysis(
    *,
    mode: CaseAnalysisMode,
    source_bundle: CaseSourceBundle,
    pipeline_config: dict[str, object],
    question: str | None,
    user_message: object,
    client: httpx.AsyncClient | None = None,
    technical_context: dict[str, object] | None = None,
    retrieval_context_id: str | None = None,
) -> CaseAnalysisOutput:
    validated_mode, validated_question = validate_analysis_request(mode, question)
    return await analyze_case(
        source_bundle=source_bundle,
        user_message=user_message,
        config=read_pipeline(pipeline_config),
        question=validated_question,
        mode=validated_mode,
        client=client,
        technical_context=technical_context,
        retrieval_context_id=retrieval_context_id,
    )


__all__ = [
    "analyze_case",
    "execute_analysis_pipeline",
    "request_analysis_stage",
    "request_case_analysis",
]
