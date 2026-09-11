from __future__ import annotations

import json
import logging
import re
import unicodedata
from collections.abc import Mapping
from copy import deepcopy

import httpx
from pydantic import ValidationError

from app.services.case_analysis.contracts import (
    AnalysisClaimV3,
    AnalysisEvidenceCitation,
    AnalysisMode,
    AnalysisTraceV3,
    AnalysisTraceV3FailureMetadata,
    CaseAnalysisFailure,
    CaseAnalysisResult,
    ProviderCaseAnalysisV3,
)

_VISIBLE_TEXT_BLOCK_TYPES = frozenset({"text", "output_text"})
from app.services.case_analysis.evidenceQuoteResolver import resolve_document_locator
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    AnalysisTraceStructureError,
    detect_forbidden_provenance,
    validate_analysis_trace_v3,
)

logger = logging.getLogger("app.case_analysis")


def formatIdentifier(value: object, prefix: str, aliases: str) -> object:
    """Format claim or association identifier into normalized prefix-number string."""
    if not isinstance(value, str):
        return value
    match = re.fullmatch(rf"(?:{aliases})[-_]?([0-9]+)", value.strip(), re.I)
    return f"{prefix}-{int(match[1]):02d}" if match else value


def normalizeAnalysisIdentifiers(payload: dict[str, object]) -> dict[str, object]:
    """Normalize claim IDs and association IDs across parsed analysis payload."""
    normalized = deepcopy(payload)
    for collection, field, prefix, aliases in (
        ("claims", "claim_id", "A", "A|claim|c"),
        ("mitre_associations", "association_id", "MA", "MA|assoc|association"),
    ):
        rows = normalized.get(collection)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            if field in row:
                row[field] = formatIdentifier(row[field], prefix, aliases)
            references = row.get("claim_ids")
            if isinstance(references, list):
                row["claim_ids"] = [
                    formatIdentifier(value, "A", "A|claim|c") for value in references
                ]
    return normalized


def extractTextValue(value: object) -> str:
    """Recursively extract raw text values from provider block payload."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(extractTextValue(item) for item in value)
    if not isinstance(value, Mapping):
        return ""

    block_type = value.get("type")
    if block_type in {"thinking", "redacted_thinking", "reasoning"}:
        return ""
    if block_type in _VISIBLE_TEXT_BLOCK_TYPES:
        text = value.get("text")
        if isinstance(text, str):
            return text

    text = value.get("text")
    if isinstance(text, str) and block_type in {None, "message", "output_text"}:
        return text

    nested_content = value.get("content")
    nested = extractTextValue(nested_content)
    if nested:
        return nested

    message = value.get("message")
    return extractTextValue(message)


def extractVisibleText(payload: Mapping[str, object]) -> str:
    """Extract visible assistant text across supported provider response shapes."""
    direct_output = payload.get("output_text")
    if isinstance(direct_output, str):
        return direct_output

    content = payload.get("content")
    answer = extractTextValue(content)
    if answer:
        return answer

    choices = payload.get("choices")
    if isinstance(choices, list):
        return extractTextValue(choices)

    output = payload.get("output")
    return extractTextValue(output)


def logResponseShape(status_code: int, payload: Mapping[str, object]) -> None:
    """Log provider shape metadata without logging prompts or answer text."""
    content = payload.get("content")
    block_types = []
    if isinstance(content, list):
        block_types = [
            str(block.get("type"))
            for block in content
            if isinstance(block, Mapping) and block.get("type") is not None
        ]
    usage = payload.get("usage")
    usage_keys = sorted(usage.keys()) if isinstance(usage, Mapping) else []
    logger.info(
        "Main Case Analysis provider response status=%s keys=%s "
        "content_type=%s block_types=%s stop_reason=%s usage_keys=%s",
        status_code,
        sorted(str(key) for key in payload.keys()),
        type(content).__name__,
        block_types,
        payload.get("stop_reason"),
        usage_keys,
    )


def stripTrailingOcrBoilerplate(text: str) -> str:
    """Strip default trailing OCR metadata disclaimers emitted by provider."""
    if not text:
        return text
    lines = text.rstrip().split("\n")
    while lines:
        last_line = lines[-1].strip()
        if not last_line:
            lines.pop()
            continue
        cleaned = last_line.lstrip("*-# \t").rstrip(".*- \t")
        if (
            "เอกสารต้นทางใช้การรู้จำเอกสารจากภาพ" in cleaned
            or ("รู้จำเอกสารจากภาพ" in cleaned and "ความเชื่อมั่น" in cleaned)
            or ("OCR" in cleaned and "ไม่ได้รายงานค่าความเชื่อมั่น" in cleaned)
            or ("การรู้จำเอกสาร" in cleaned and "ไม่ได้รายงานค่าความเชื่อมั่น" in cleaned)
        ):
            lines.pop()
        else:
            break
    return "\n".join(lines).strip()


def validateResponsePayload(response: httpx.Response) -> dict[str, object]:
    """Validate HTTP response status, decode JSON, and ensure no provider-level error/stop."""
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

    logResponseShape(response.status_code, response_payload)

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


def parseCaseAnalysisResponse(
    response: httpx.Response,
    *,
    source_message_ids: set[str],
    analysis_context: Mapping[str, object],
    analysis_mode: AnalysisMode,
    evidence_sha256: str,
) -> CaseAnalysisResult:
    """Parse, normalize, and validate structured Case Analysis response from provider."""
    response_payload = validateResponsePayload(response)
    raw_text = extractVisibleText(response_payload).strip()
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

    raw_answer = stripTrailingOcrBoilerplate(raw_answer)
    raw_analysis["answer"] = raw_answer

    raw_summary = raw_analysis.get("summary")
    if isinstance(raw_summary, str):
        raw_analysis["summary"] = stripTrailingOcrBoilerplate(raw_summary)

    try:
        detect_forbidden_provenance(raw_analysis)
    except AnalysisTraceProvenanceError as error:
        raise CaseAnalysisFailure(error.code, str(error)) from error

    try:
        parsed = ProviderCaseAnalysisV3.model_validate(
            normalizeAnalysisIdentifiers(raw_analysis)
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


def bind_analysis_claim_citations(
    claims: list[AnalysisClaimV3],
    analysis_context: Mapping[str, object],
) -> list[AnalysisClaimV3]:
    source_texts = _source_texts(analysis_context)
    document_context = analysis_context.get("document_source_context", [])
    return [
        claim.model_copy(
            update={
                "supporting_citations": _bind_citations(
                    claim.supporting_citations,
                    set(claim.supporting_source_message_ids),
                    source_texts,
                    document_context,
                ),
                "contradicting_citations": _bind_citations(
                    claim.contradicting_citations,
                    set(claim.contradicting_source_message_ids),
                    source_texts,
                    document_context,
                ),
            }
        )
        for claim in claims
    ]


def _bind_citations(
    citations: list[AnalysisEvidenceCitation],
    allowed_source_ids: set[str],
    source_texts: dict[str, str],
    document_context: object,
) -> list[AnalysisEvidenceCitation]:
    bound: list[AnalysisEvidenceCitation] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        source_id = citation.source_message_id
        quote = citation.exact_quote
        key = (source_id, quote)
        content = source_texts.get(source_id)
        if (
            source_id not in allowed_source_ids
            or content is None
            or quote not in content
        ):
            continue
        if key in seen:
            continue
        seen.add(key)
        locator = resolve_document_locator(
            source_id,
            quote,
            content,
            document_context,
        )
        bound.append(
            AnalysisEvidenceCitation(
                source_message_id=source_id,
                exact_quote=quote,
                **locator,
            )
        )
    return bound


def _source_texts(analysis_context: Mapping[str, object]) -> dict[str, str]:
    raw = analysis_context.get("_source_text_by_message_id")
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(source_id): content
        for source_id, content in raw.items()
        if isinstance(source_id, str) and isinstance(content, str)
    }


# Backward-compatibility aliases
_format_identifier = formatIdentifier
normalize_analysis_identifiers = normalizeAnalysisIdentifiers
_extract_text_value = extractTextValue
_extract_visible_text = extractVisibleText
_log_response_shape = logResponseShape
_strip_trailing_ocr_boilerplate = stripTrailingOcrBoilerplate
validated_response_payload = validateResponsePayload
parse_case_analysis_response = parseCaseAnalysisResponse

__all__ = [
    "bind_analysis_claim_citations",
    "extractTextValue",
    "extractVisibleText",
    "formatIdentifier",
    "logResponseShape",
    "normalizeAnalysisIdentifiers",
    "normalize_analysis_identifiers",
    "parseCaseAnalysisResponse",
    "parse_case_analysis_response",
    "stripTrailingOcrBoilerplate",
    "validateResponsePayload",
    "validated_response_payload",
]
