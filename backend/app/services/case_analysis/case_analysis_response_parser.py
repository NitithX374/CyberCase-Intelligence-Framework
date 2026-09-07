from __future__ import annotations

import json
import logging
from collections.abc import Mapping

import httpx
from pydantic import ValidationError

from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.case_analysis.case_analysis_response_utils import (
    _extract_visible_text,
    _strip_trailing_ocr_boilerplate,
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
from app.services.case_analysis.response_decoder import validated_response_payload
from app.services.case_analysis.response_identifiers import (
    normalize_analysis_identifiers,
)
from app.services.case_analysis.source_citations import bind_analysis_claim_citations


logger = logging.getLogger("app.case_analysis")


def parse_case_analysis_response(
    response: httpx.Response,
    *,
    source_message_ids: set[str],
    analysis_context: Mapping[str, object],
    analysis_mode: AnalysisMode,
    evidence_sha256: str,
) -> CaseAnalysisResult:
    response_payload = validated_response_payload(response)
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
    raw_answer = _strip_trailing_ocr_boilerplate(raw_answer)
    raw_analysis["answer"] = raw_answer
    raw_summary = raw_analysis.get("summary")
    if isinstance(raw_summary, str):
        raw_analysis["summary"] = _strip_trailing_ocr_boilerplate(raw_summary)
    try:
        detect_forbidden_provenance(raw_analysis)
    except AnalysisTraceProvenanceError as error:
        raise CaseAnalysisFailure(error.code, str(error)) from error

    try:
        parsed = ProviderCaseAnalysisV3.model_validate(
            normalize_analysis_identifiers(raw_analysis)
        )
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
    retrieval_context_id = _retrieval_context_id(analysis_context)
    candidate_trace = AnalysisTraceV3(
        analysis_mode=analysis_mode,
        summary=parsed.summary,
        claims=bind_analysis_claim_citations(parsed.claims, analysis_context),
        gaps=[],
        mitre_associations=(
            parsed.mitre_associations if retrieval_context_id is not None else []
        ),
        evidence_sha256=evidence_sha256,
        retrieval_context_id=retrieval_context_id,
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
