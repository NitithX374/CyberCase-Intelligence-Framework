from __future__ import annotations

import json
import logging
from collections.abc import Mapping

import httpx
from pydantic import ValidationError

from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.case_analysis.case_analysis_response_utils import (
    _extract_visible_text,
    _log_response_shape,
)
from app.services.case_analysis.contracts import (
    AnalysisMode,
    AnalysisTraceV3,
    AnalysisTraceV3FailureMetadata,
    CaseAnalysisResult,
    ProviderCaseAnalysisV3,
)
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    AnalysisTraceStructureError,
    detect_forbidden_provenance,
    validate_analysis_trace_v3,
)


logger = logging.getLogger("app.case_analysis")


def parse_case_analysis_response(
    response: httpx.Response,
    *,
    source_message_ids: set[str],
    analysis_context: Mapping[str, object],
    analysis_mode: AnalysisMode,
    evidence_sha256: str,
) -> CaseAnalysisResult:
    response_payload = _validated_response_payload(response)
    raw_text = _extract_visible_text(response_payload).strip()
    if not raw_text:
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider returned no answer",
        )
    try:
        raw_analysis = json.loads(raw_text)
    except (TypeError, ValueError) as error:
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider did not return structured JSON",
        ) from error
    if not isinstance(raw_analysis, dict):
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer structured analysis must be an object",
        )
    raw_answer = raw_analysis.get("answer")
    if not isinstance(raw_answer, str) or not raw_answer.strip():
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer structured analysis returned no safe prose",
        )
    try:
        detect_forbidden_provenance(raw_analysis)
    except AnalysisTraceProvenanceError as error:
        raise CaseAnalysisFailure(error.code, str(error)) from error
    try:
        parsed = ProviderCaseAnalysisV3.model_validate(raw_analysis)
    except ValidationError as error:
        logger.warning(
            "Case analysis trace validation failed: %s | keys: %s",
            error,
            list(raw_analysis.keys()),
        )
        failure_code = (
            "analysis_trace_version_unsupported"
            if raw_analysis.get("version") != "analysis_trace_v3"
            else "analysis_trace_structure_invalid"
        )
        return CaseAnalysisResult(
            answer=raw_answer.strip(),
            trace=None,
            trace_failure=AnalysisTraceV3FailureMetadata(failure_code=failure_code),
        )
    candidate_trace = AnalysisTraceV3(
        analysis_mode=analysis_mode,
        summary=parsed.summary,
        claims=parsed.claims,
        gaps=[],
        mitre_associations=parsed.mitre_associations,
        evidence_sha256=evidence_sha256,
        retrieval_context_id=_retrieval_context_id(analysis_context),
    )
    try:
        trace = validate_analysis_trace_v3(
            candidate_trace,
            source_message_ids=source_message_ids,
            mitre_table=analysis_context.get("mitre_table", []),
        )
    except AnalysisTraceStructureError as error:
        logger.warning(
            "Case analysis trace structure error: %s (code=%s)",
            error,
            error.code,
        )
        return CaseAnalysisResult(
            answer=parsed.answer,
            trace=None,
            trace_failure=AnalysisTraceV3FailureMetadata(failure_code=error.code),
        )
    except AnalysisTraceProvenanceError as error:
        logger.warning(
            "Case analysis trace provenance error: %s (code=%s)",
            error,
            error.code,
        )
        raise CaseAnalysisFailure(error.code, str(error)) from error
    return CaseAnalysisResult(answer=parsed.answer.strip(), trace=trace)


def _validated_response_payload(response: httpx.Response) -> dict[str, object]:
    if not 200 <= response.status_code < 300:
        raise CaseAnalysisFailure(
            "analysis_provider_error",
            "The post-answer analysis provider returned an error",
        )
    try:
        response_payload = response.json()
    except (TypeError, ValueError) as error:
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider response was invalid",
        ) from error
    if not isinstance(response_payload, dict):
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider response was invalid",
        )
    _log_response_shape(response.status_code, response_payload)
    if isinstance(response_payload.get("error"), dict):
        raise CaseAnalysisFailure(
            "analysis_provider_error",
            "The post-answer analysis provider returned an error",
        )
    if response_payload.get("stop_reason") in {
        "refusal",
        "max_tokens",
        "length",
        "pause_turn",
    }:
        raise CaseAnalysisFailure(
            "analysis_incomplete",
            "The post-answer analysis provider did not complete",
        )
    content = response_payload.get("content")
    if content is not None and not isinstance(content, (list, str)):
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider response was invalid",
        )
    return response_payload


def _retrieval_context_id(analysis_context: Mapping[str, object]) -> str | None:
    value = analysis_context.get("retrieval_context_id")
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise CaseAnalysisFailure(
        "analysis_context_invalid",
        "Retrieval context identifier must be a non-empty string or null",
    )


__all__ = ["parse_case_analysis_response"]
