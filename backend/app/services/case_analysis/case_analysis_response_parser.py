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
from app.services.case_analysis.source_citations import bind_analysis_claim_citations


import re

logger = logging.getLogger("app.case_analysis")

_CLAIM_ID_REGEX = re.compile(r"^A-\d{2,}$")
_ASSOC_ID_REGEX = re.compile(r"^MA-\d{2,}$")
_GAP_ID_REGEX = re.compile(r"^G-\d{2,}$")


def _normalize_raw_analysis_ids(
    raw_analysis: dict[str, object],
    *,
    source_message_ids: set[str] | None = None,
    ordered_source_ids: list[str] | None = None,
) -> None:
    raw_claims = raw_analysis.get("claims")
    if not isinstance(raw_claims, list):
        return

    claim_id_map: dict[str, str] = {}
    sources = [
        str(s).strip() for s in (ordered_source_ids or []) if str(s).strip()
    ]
    if not sources and source_message_ids:
        sources = [str(s).strip() for s in sorted(source_message_ids) if str(s).strip()]

    source_id_map: dict[str, str] = {}
    for idx, sid in enumerate(sources):
        k = idx + 1
        source_id_map[sid] = sid
        source_id_map[sid.lower()] = sid
        source_id_map[sid.upper()] = sid
        source_id_map[f"S{k}"] = sid
        source_id_map[f"s{k}"] = sid
        source_id_map[f"S-{k}"] = sid
        source_id_map[f"s-{k}"] = sid
        source_id_map[f"S_{k}"] = sid
        source_id_map[f"s_{k}"] = sid
        source_id_map[f"S{k:02d}"] = sid
        source_id_map[f"s{k:02d}"] = sid
        source_id_map[f"source-{k}"] = sid
        source_id_map[f"source_{k}"] = sid
        source_id_map[f"source{k}"] = sid
        source_id_map[f"message-{k}"] = sid
        source_id_map[f"message_{k}"] = sid
        source_id_map[f"message{k}"] = sid
        source_id_map[str(k)] = sid
        source_id_map[str(idx)] = sid
    if len(sources) == 1:
        single_sid = sources[0]
        source_id_map["source"] = single_sid
        source_id_map["evidence"] = single_sid
        source_id_map["document"] = single_sid
        source_id_map["case"] = single_sid

    for index, claim in enumerate(raw_claims):
        if not isinstance(claim, dict):
            continue
        canonical_id = f"A-{index + 1:02d}" if index < 64 else f"A-{index + 1}"
        orig_id = claim.get("claim_id")
        if orig_id is not None:
            str_orig = str(orig_id).strip()
            claim_id_map[str_orig] = canonical_id
            claim_id_map[str_orig.lower()] = canonical_id
            claim_id_map[str_orig.upper()] = canonical_id
            if str_orig.isdigit():
                claim_id_map[f"claim-{str_orig}"] = canonical_id
                claim_id_map[f"claim_{str_orig}"] = canonical_id
                claim_id_map[f"c{str_orig}"] = canonical_id
                claim_id_map[f"A-{str_orig}"] = canonical_id
            elif str_orig.lower().startswith(("claim-", "claim_")):
                suffix = str_orig.split("-", 1)[-1].split("_", 1)[-1]
                claim_id_map[suffix] = canonical_id
        claim["claim_id"] = canonical_id

        # Normalize supporting_source_message_ids
        raw_supp = claim.get("supporting_source_message_ids")
        if isinstance(raw_supp, list):
            mapped_supp = []
            for sid in raw_supp:
                if sid is not None:
                    str_sid = str(sid).strip()
                    mapped_supp.append(
                        source_id_map.get(str_sid, source_id_map.get(str_sid.lower(), str_sid))
                    )
            claim["supporting_source_message_ids"] = mapped_supp
        elif raw_supp is None and len(sources) == 1 and claim.get("claim_type") in {"reported", "analytical_inference"}:
            claim["supporting_source_message_ids"] = [sources[0]]

        # Normalize contradicting_source_message_ids
        raw_contra = claim.get("contradicting_source_message_ids")
        if isinstance(raw_contra, list):
            mapped_contra = []
            for sid in raw_contra:
                if sid is not None:
                    str_sid = str(sid).strip()
                    mapped_contra.append(
                        source_id_map.get(str_sid, source_id_map.get(str_sid.lower(), str_sid))
                    )
            claim["contradicting_source_message_ids"] = mapped_contra

        # Normalize citations source_message_id
        for cit_key in ("supporting_citations", "contradicting_citations"):
            citations = claim.get(cit_key)
            if isinstance(citations, list):
                for cit in citations:
                    if isinstance(cit, dict) and cit.get("source_message_id") is not None:
                        cit_sid = str(cit["source_message_id"]).strip()
                        cit["source_message_id"] = source_id_map.get(
                            cit_sid, source_id_map.get(cit_sid.lower(), cit_sid)
                        )
                        if not cit["source_message_id"] and len(sources) == 1:
                            cit["source_message_id"] = sources[0]

    raw_associations = raw_analysis.get("mitre_associations")
    if isinstance(raw_associations, list):
        for assoc_index, assoc in enumerate(raw_associations):
            if not isinstance(assoc, dict):
                continue
            orig_assoc_id = assoc.get("association_id")
            if not isinstance(orig_assoc_id, str) or not _ASSOC_ID_REGEX.match(orig_assoc_id):
                assoc["association_id"] = (
                    f"MA-{assoc_index + 1:02d}" if assoc_index < 64 else f"MA-{assoc_index + 1}"
                )
            cited_ids = assoc.get("claim_ids")
            if isinstance(cited_ids, list):
                assoc["claim_ids"] = [
                    claim_id_map.get(
                        str(cid).strip(),
                        claim_id_map.get(str(cid).strip().lower(), str(cid).strip()),
                    )
                    for cid in cited_ids
                    if cid is not None
                ]

    raw_gaps = raw_analysis.get("gaps")
    if isinstance(raw_gaps, list):
        for gap_index, gap in enumerate(raw_gaps):
            if not isinstance(gap, dict):
                continue
            orig_gap_id = gap.get("gap_id")
            if not isinstance(orig_gap_id, str) or not _GAP_ID_REGEX.match(orig_gap_id):
                gap["gap_id"] = (
                    f"G-{gap_index + 1:02d}" if gap_index < 64 else f"G-{gap_index + 1}"
                )
            affected = gap.get("affected_claim_ids")
            if isinstance(affected, list):
                gap["affected_claim_ids"] = [
                    claim_id_map.get(
                        str(cid).strip(),
                        claim_id_map.get(str(cid).strip().lower(), str(cid).strip()),
                    )
                    for cid in affected
                    if cid is not None
                ]


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
    raw_answer = _strip_trailing_ocr_boilerplate(raw_answer)
    raw_analysis["answer"] = raw_answer
    raw_summary = raw_analysis.get("summary")
    if isinstance(raw_summary, str):
        raw_analysis["summary"] = _strip_trailing_ocr_boilerplate(raw_summary)
    try:
        detect_forbidden_provenance(raw_analysis)
    except AnalysisTraceProvenanceError as error:
        raise CaseAnalysisFailure(error.code, str(error)) from error

    raw_source_ids = analysis_context.get("source_message_ids", [])
    ordered_source_ids = [
        str(v).strip()
        for v in raw_source_ids
        if isinstance(v, str) and str(v).strip()
    ] if isinstance(raw_source_ids, list) else sorted(
        str(v).strip() for v in source_message_ids if str(v).strip()
    )

    _normalize_raw_analysis_ids(
        raw_analysis,
        source_message_ids=source_message_ids,
        ordered_source_ids=ordered_source_ids,
    )
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
