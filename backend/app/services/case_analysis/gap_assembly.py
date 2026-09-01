from __future__ import annotations

import re
import unicodedata

from pydantic import ValidationError

from app.services.case_analysis.contracts import (
    AnalysisClaimV3,
    AnalysisGapV3,
    AnalysisTraceV3,
    AnalysisTraceV3FailureMetadata,
    CaseAnalysisResult,
)
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    AnalysisTraceStructureError,
    validate_analysis_trace_v3,
)
from app.services.followup.schemas import GapAnalysis, GapItem


_CLAIM_ID_PATTERN = re.compile(r"(?<![A-Z0-9])A-\d{2,}(?![A-Z0-9])", re.IGNORECASE)
_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
_IGNORED_TOKENS = {
    "a",
    "an",
    "analysis",
    "analytical",
    "case",
    "claim",
    "conclusion",
    "current",
    "evidence",
    "it",
    "of",
    "or",
    "the",
    "this",
    "to",
    "whether",
}
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def assemble_claim_linked_gaps(
    trace: AnalysisTraceV3,
    gap_analysis: GapAnalysis,
    *,
    source_message_ids: set[str],
    mitre_table: object = None,
) -> AnalysisTraceV3:
    ordered_gaps = sorted(
        enumerate(gap_analysis.gaps),
        key=lambda entry: (_PRIORITY_RANK[entry[1].priority], entry[0]),
    )
    canonical_gaps = [
        AnalysisGapV3(
            gap_id=f"G-{index:02d}",
            topic=gap.topic,
            status=gap.status,
            description=gap.description,
            affected_claim_ids=_affected_claim_ids(gap, trace.claims),
            reason=gap.reason,
            priority=gap.priority,
            askable=gap.askable,
        )
        for index, (_, gap) in enumerate(ordered_gaps, start=1)
    ]
    enriched = trace.model_copy(update={"gaps": canonical_gaps})
    _validate_unchanged_trace_bindings(trace, enriched)
    return validate_analysis_trace_v3(
        enriched,
        source_message_ids=source_message_ids,
        mitre_table=mitre_table,
    )


def enrich_case_analysis_result(
    result: CaseAnalysisResult,
    gap_analysis: GapAnalysis | None,
    *,
    source_message_ids: set[str],
    mitre_table: object = None,
) -> CaseAnalysisResult:
    if not isinstance(result.trace, AnalysisTraceV3):
        return result
    if gap_analysis is None:
        return CaseAnalysisResult(
            answer=result.answer,
            trace=None,
            trace_failure=AnalysisTraceV3FailureMetadata(
                failure_code="analysis_trace_v3_gap_analysis_unavailable"
            ),
        )
    try:
        trace = assemble_claim_linked_gaps(
            result.trace,
            gap_analysis,
            source_message_ids=source_message_ids,
            mitre_table=mitre_table,
        )
    except (AnalysisTraceStructureError, ValidationError) as error:
        failure_code = getattr(error, "code", "analysis_trace_v3_gap_assembly_invalid")
        return CaseAnalysisResult(
            answer=result.answer,
            trace=None,
            trace_failure=AnalysisTraceV3FailureMetadata(failure_code=failure_code),
        )
    except AnalysisTraceProvenanceError:
        raise
    return CaseAnalysisResult(answer=result.answer, trace=trace)


def _affected_claim_ids(
    gap: GapItem,
    claims: list[AnalysisClaimV3],
) -> list[str]:
    known_claim_ids = {claim.claim_id for claim in claims}
    direct_ids = [value.upper() for value in _CLAIM_ID_PATTERN.findall(gap.affects)]
    if direct_ids:
        return list(dict.fromkeys(direct_ids))

    gap_text = _normalized_text(gap.affects)
    gap_tokens = _tokens(gap.affects)
    matches: list[str] = []
    for claim in claims:
        claim_text = _claim_linking_text(claim)
        if _text_matches(gap_text, gap_tokens, claim_text):
            matches.append(claim.claim_id)
    return [claim_id for claim_id in matches if claim_id in known_claim_ids]


def _claim_linking_text(claim: AnalysisClaimV3) -> str:
    values = [claim.text]
    if claim.reasoning_summary is not None:
        values.append(claim.reasoning_summary)
    return " ".join(values)


def _text_matches(gap_text: str, gap_tokens: set[str], claim_text: str) -> bool:
    normalized_claim = _normalized_text(claim_text)
    if len(gap_text) >= 8 and (
        gap_text in normalized_claim or normalized_claim in gap_text
    ):
        return True
    if len(gap_tokens) < 2:
        return False
    overlap = gap_tokens & _tokens(claim_text)
    return len(overlap) >= 2 and len(overlap) / len(gap_tokens) >= 0.6


def _normalized_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(_TOKEN_PATTERN.findall(normalized))


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in _TOKEN_PATTERN.findall(_normalized_text(value))
        if len(token) > 1 and token not in _IGNORED_TOKENS
    }


def _validate_unchanged_trace_bindings(
    original: AnalysisTraceV3,
    enriched: AnalysisTraceV3,
) -> None:
    preserved_fields = (
        "claims",
        "mitre_associations",
        "evidence_sha256",
        "retrieval_context_id",
    )
    if any(
        getattr(original, field) != getattr(enriched, field)
        for field in preserved_fields
    ):
        raise AnalysisTraceStructureError(
            "analysis_trace_v3_gap_assembly_mutation",
            "Gap assembly changed immutable analysis trace content",
        )


__all__ = ["assemble_claim_linked_gaps", "enrich_case_analysis_result"]
