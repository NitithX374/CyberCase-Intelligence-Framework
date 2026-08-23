from __future__ import annotations

from collections.abc import Mapping

from app.services.case_analysis.contracts import (
    AnalysisMode,
    AnalysisTraceDraft,
    ProviderCaseAnalysis,
)


class AnalysisTraceStructureError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class AnalysisTraceProvenanceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def validate_analysis_trace(
    analysis: ProviderCaseAnalysis,
    *,
    source_message_ids: set[str],
    mitre_table: object,
    analysis_mode: AnalysisMode,
) -> AnalysisTraceDraft:
    claim_ids = [claim.claim_id for claim in analysis.claims]
    if len(set(claim_ids)) != len(claim_ids):
        raise AnalysisTraceStructureError(
            "analysis_trace_duplicate_claim_id",
            "Analysis claims must have unique identifiers",
        )
    for claim in analysis.claims:
        if claim.claim_type == "reported" and not claim.source_message_ids:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_reported_claim_unbound",
                "Reported claims must cite a user-authored source message",
            )
        if not set(claim.source_message_ids).issubset(source_message_ids):
            raise AnalysisTraceProvenanceError(
                "analysis_trace_source_outside_evidence",
                "A claim cites a message outside accumulated raw evidence",
            )
    admitted_techniques = _admitted_technique_ids(mitre_table)
    for association in analysis.mitre_associations:
        if not set(association.claim_ids).issubset(set(claim_ids)):
            raise AnalysisTraceStructureError(
                "analysis_trace_unknown_claim",
                "A MITRE association cites an unknown analytical claim",
            )
        if association.technique_id not in admitted_techniques:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_mitre_outside_context",
                "A MITRE association is outside the bound retrieval context",
            )
    return AnalysisTraceDraft(
        analysis_mode=analysis_mode,
        claims=analysis.claims,
        mitre_associations=analysis.mitre_associations,
    )


def detect_forbidden_provenance(raw_payload: object) -> None:
    forbidden = {
        "case_state_version_id",
        "entity_ids",
        "relationship_ids",
        "evidence_ids",
        "timeline_event_ids",
    }
    if _contains_key(raw_payload, forbidden):
        raise AnalysisTraceProvenanceError(
            "analysis_trace_obsolete_reference",
            "Analysis Trace contains obsolete Case State references",
        )


def _admitted_technique_ids(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    identifiers: set[str] = set()
    for row in value:
        if not isinstance(row, Mapping):
            continue
        for key in ("technique_id", "id", "external_id"):
            candidate = row.get(key)
            if isinstance(candidate, str) and candidate.startswith("T"):
                identifiers.add(candidate)
    return identifiers


def _contains_key(value: object, forbidden: set[str]) -> bool:
    if isinstance(value, Mapping):
        return any(key in forbidden or _contains_key(item, forbidden) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_key(item, forbidden) for item in value)
    return False


__all__ = [
    "AnalysisTraceProvenanceError",
    "AnalysisTraceStructureError",
    "detect_forbidden_provenance",
    "validate_analysis_trace",
]
