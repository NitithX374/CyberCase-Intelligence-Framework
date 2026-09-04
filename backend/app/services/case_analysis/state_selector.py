from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import ValidationError

from app.models.chat import ChatMessage
from app.services.case_analysis.contracts import AnalysisTraceV3, read_analysis_trace
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    AnalysisTraceStructureError,
    validate_analysis_trace_v3,
)


@dataclass(frozen=True)
class CanonicalCaseAnalysisState:
    message: ChatMessage
    trace: AnalysisTraceV3


def validate_canonical_case_overview_trace(
    trace: AnalysisTraceV3,
    *,
    evidence_sha256: str,
    source_message_ids: set[str],
    mitre_table: object = None,
) -> AnalysisTraceV3 | None:
    if trace.analysis_mode != "case_overview":
        return None
    if trace.evidence_sha256 != evidence_sha256:
        return None
    try:
        return validate_analysis_trace_v3(
            trace,
            source_message_ids=source_message_ids,
            mitre_table=mitre_table,
        )
    except (AnalysisTraceProvenanceError, AnalysisTraceStructureError):
        return None


def select_latest_canonical_case_overview(
    messages: Sequence[ChatMessage],
    *,
    evidence_sha256: str,
    source_message_ids: set[str],
) -> CanonicalCaseAnalysisState | None:
    ordered = sorted(messages, key=lambda message: message.ordinal, reverse=True)
    for message in ordered:
        if message.role != "assistant":
            continue
        metadata = message.metadata_json
        if not isinstance(metadata, dict):
            continue
        try:
            trace = read_analysis_trace(metadata.get("analysis_trace"))
        except ValidationError:
            continue
        if not isinstance(trace, AnalysisTraceV3):
            continue
        mitre_table = metadata.get("mitre_table", [])
        validated = validate_canonical_case_overview_trace(
            trace,
            evidence_sha256=evidence_sha256,
            source_message_ids=source_message_ids,
            mitre_table=mitre_table,
        )
        if validated is None:
            continue
        return CanonicalCaseAnalysisState(message=message, trace=validated)
    return None


__all__ = [
    "CanonicalCaseAnalysisState",
    "select_latest_canonical_case_overview",
    "validate_canonical_case_overview_trace",
]
