from __future__ import annotations

from collections.abc import Sequence

import httpx
from pydantic import ValidationError

from app.services.analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisMode,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    CaseProviderAnalysis,
    followup_payload,
    resolve_response_language,
)
from app.services.analysis.prompts import (
    case_system_prompt,
    validate_analysis_request,
)
from app.services.analysis.provider import request_stage, resolve_target
from app.services.analysis.settings import AnalysisPipelineConfig, read_pipeline
from app.services.analysis.steps.bind import resolve_case_trace
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem


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
    revision: str | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
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
                revision=revision,
                followup_history=followup_history,
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
                revision=revision,
                followup_history=followup_history,
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
    revision: str | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> CaseAnalysisOutput:
    validate_source_bundle(source_bundle)
    cleaned_technical_context = usable_technical_context(technical_context)

    request_content = {
        "response_language": language,
        "analysis_mode": mode,
        "case_sources": [provider_source_payload(source) for source in source_bundle.sources],
        "followup_history": followup_payload(followup_history),
        "technical_context": cleaned_technical_context,
        "question": question,
    }

    parsed = await request_analysis_stage(
        client,
        config,
        "direct" if revision is None else "direct_revision",
        case_system_prompt() if revision is None else f"{case_system_prompt()}\n\n{revision}",
        request_content,
        CaseProviderAnalysis,
        receipt,
    )
    bound_retrieval_id = retrieval_context_id if cleaned_technical_context else None
    trace = direct_trace(parsed, mode=mode, retrieval_context_id=bound_retrieval_id)
    return CaseAnalysisOutput(
        answer=trace.summary,
        trace=trace,
        execution_receipt=receipt,
    )


def usable_technical_context(value: object) -> dict[str, object] | None:
    if (
        isinstance(value, dict)
        and isinstance(value.get("context"), str)
        and isinstance(value.get("mitre_table"), (list, tuple))
        and value.get("mitre_table")
    ):
        return {
            "context": value["context"],
            "mitre_table": list(value["mitre_table"]),
        }
    return None


def provider_source_payload(source: CaseSourceItem) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_id": source.source_id,
        "source_kind": source.source_kind,
        "text": source.text,
    }
    question = source.provenance.get("question")
    if source.source_kind == "followup_answer" and isinstance(question, str) and question.strip():
        payload["answers_question"] = question.strip()
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
    if any(
        not isinstance(source_id, str) or not source_id.strip() for source_id in source_ids
    ) or len(source_ids) != len(set(source_ids)):
        raise CaseAnalysisFailure("case_sources_invalid", "Case source bundle is invalid")
    if any(
        not isinstance(source.text, str) or not source.text.strip()
        for source in source_bundle.sources
    ):
        raise CaseAnalysisFailure("case_source_empty", "Case source text is empty")


def direct_trace(
    parsed: CaseProviderAnalysis,
    *,
    mode: str,
    retrieval_context_id: str | None = None,
) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode=mode,
        summary=parsed.summary,
        involved_parties=parsed.involved_parties,
        timeline=parsed.timeline,
        claims=parsed.claims,
        impacts=parsed.impacts,
        gaps=parsed.gaps,
        mitre_associations=parsed.mitre_associations,
        retrieval_context_id=retrieval_context_id,
    )


def validate_direct_trace(
    parsed: CaseProviderAnalysis,
    *,
    mode: str,
    source_bundle: CaseSourceBundle,
    retrieval_context_id: str | None = None,
    mitre_table: list[dict[str, object]] | tuple[dict[str, object], ...] | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> CaseAnalysisTrace:
    return resolve_case_trace(
        direct_trace(parsed, mode=mode, retrieval_context_id=retrieval_context_id),
        source_bundle,
        mitre_table=list(mitre_table) if mitre_table else [],
        followup_history=followup_history,
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
    revision: str | None = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
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
        revision=revision,
        followup_history=followup_history,
    )


__all__ = [
    "analyze_case",
    "provider_source_payload",
    "usable_technical_context",
    "validate_source_bundle",
    "execute_analysis_pipeline",
    "request_analysis_stage",
    "direct_trace",
    "request_case_analysis",
]
