from __future__ import annotations

import httpx
from pydantic import ValidationError

from app.services.case_analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisMode,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseProviderAnalysis,
    CaseQuestionAnswerOutput,
    CaseQuestionAnswerResponse,
    ResponseLanguage,
    resolve_response_language,
)
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig, read_pipeline
from app.services.case_analysis.prompts import (
    CASE_TRACE_CORRECTION_PROMPT,
    CASE_REASONING_PROMPT_VERSION,
    case_system_prompt,
    validate_analysis_request,
)
from app.services.case_analysis.provider_stage import request_stage, resolve_target
from app.services.case_analysis.validation import validate_case_trace
from app.services.case_materials import CaseSourceBundle
from app.services.case_materials.case_source_bundle import build_case_reasoning_payload


async def request_case_reasoning(
    *,
    source_bundle: CaseSourceBundle,
    user_message: object,
    pipeline_config: dict[str, object],
    mode: CaseAnalysisMode,
    question: str | None = None,
    client: httpx.AsyncClient | None = None,
    technical_context: dict[str, object] | None = None,
    retrieval_context_id: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    analysis_context: dict[str, object] | None = None,
    active_clarification: dict[str, object] | None = None,
    current_evidence_revision: int | None = None,
    analysis_evidence_revision: int | None = None,
) -> CaseAnalysisOutput | CaseQuestionAnswerOutput:
    mode, question = validate_analysis_request(mode, question)
    config = read_pipeline(pipeline_config)
    receipt: dict[str, object] = {
        "configuration": config.model_dump(mode="json"),
        "prompt_version": CASE_REASONING_PROMPT_VERSION,
        "calls": [],
        "source_reference_type": "case_source",
    }
    try:
        validate_source_bundle(source_bundle, require_sources=mode == "case_overview")
        language = resolve_response_language(user_message)
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
            conversation_history=conversation_history,
            analysis_context=analysis_context,
            active_clarification=active_clarification,
            current_evidence_revision=current_evidence_revision,
            analysis_evidence_revision=analysis_evidence_revision,
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
    language: ResponseLanguage,
    config: AnalysisPipelineConfig,
    client: httpx.AsyncClient | None,
    *,
    receipt: dict[str, object],
    mode: CaseAnalysisMode = "case_overview",
    question: str | None = None,
    technical_context: dict[str, object] | None = None,
    retrieval_context_id: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    analysis_context: dict[str, object] | None = None,
    active_clarification: dict[str, object] | None = None,
    current_evidence_revision: int | None = None,
    analysis_evidence_revision: int | None = None,
) -> CaseAnalysisOutput | CaseQuestionAnswerOutput:
    mode, question = validate_analysis_request(mode, question)
    validate_source_bundle(source_bundle, require_sources=mode == "case_overview")
    request_content = build_case_reasoning_payload(
        source_bundle=source_bundle,
        response_language=language,
        mode=mode,
        question=question,
        technical_context=technical_context,
        conversation_history=conversation_history,
        analysis_context=analysis_context,
        active_clarification=active_clarification,
        current_evidence_revision=current_evidence_revision,
        analysis_evidence_revision=analysis_evidence_revision,
    )
    if mode == "question_answer":
        parsed = await request_analysis_stage(
            client, config, "question_answer", case_system_prompt(mode),
            request_content, CaseQuestionAnswerResponse, receipt,
        )
        source_ids = {source.source_id for source in source_bundle.sources}
        if any(source_id not in source_ids for source_id in parsed.cited_source_ids):
            raise CaseAnalysisFailure(
                "case_question_answer_unknown_source", "Answer cites an unknown Case source",
            )
        return CaseQuestionAnswerOutput(
            answer=parsed.answer,
            cited_source_ids=tuple(parsed.cited_source_ids),
            clarification_question=parsed.clarification_question,
            execution_receipt=receipt,
        )

    parsed = await request_analysis_stage(
        client,
        config,
        "direct",
        case_system_prompt(),
        request_content,
        CaseProviderAnalysis,
        receipt,
    )
    cleaned_technical_context = request_content["technical_context"]
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


def validate_source_bundle(
    source_bundle: CaseSourceBundle,
    *,
    require_sources: bool = True,
) -> None:
    if not isinstance(source_bundle, CaseSourceBundle) or (require_sources and not source_bundle.sources):
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
    client: httpx.AsyncClient | None,
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
    if mode != "case_overview":
        raise CaseAnalysisFailure("analysis_invalid_request", "Main Analysis requires case_overview mode")
    output = await request_case_reasoning(
        source_bundle=source_bundle,
        user_message=user_message,
        pipeline_config=pipeline_config,
        question=question,
        mode=mode,
        client=client,
        technical_context=technical_context,
        retrieval_context_id=retrieval_context_id,
    )
    if not isinstance(output, CaseAnalysisOutput):
        raise CaseAnalysisFailure("case_analysis_invalid", "Main Analysis returned an invalid result")
    return output

__all__ = [
    "request_case_reasoning",
    "execute_analysis_pipeline",
    "request_analysis_stage",
    "request_case_analysis",
]
