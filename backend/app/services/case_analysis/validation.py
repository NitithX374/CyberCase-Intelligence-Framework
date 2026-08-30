from __future__ import annotations

from collections.abc import Mapping

from app.services.case_analysis.contracts import (
    AnalysisMode,
    AnalysisTraceDraft,
    AnalysisTraceV3,
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


def validate_analysis_trace_v3(
    analysis: AnalysisTraceV3,
    *,
    source_message_ids: set[str],
    mitre_table: object = None,
) -> AnalysisTraceV3:
    claim_ids = [claim.claim_id for claim in analysis.claims]
    known_claim_ids = set(claim_ids)
    if len(known_claim_ids) != len(claim_ids):
        raise AnalysisTraceStructureError(
            "analysis_trace_v3_duplicate_claim_id",
            "Analysis claims must have unique identifiers",
        )

    for claim in analysis.claims:
        supporting_ids = set(claim.supporting_source_message_ids)
        contradicting_ids = set(claim.contradicting_source_message_ids)
        if not supporting_ids.issubset(source_message_ids):
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_support_outside_evidence",
                "A claim cites supporting evidence outside the authoritative snapshot",
            )
        if not contradicting_ids.issubset(source_message_ids):
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_contradiction_outside_evidence",
                "A claim cites contradicting evidence outside the authoritative snapshot",
            )
        if supporting_ids & contradicting_ids:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_conflicting_source_role",
                "A source cannot both support and contradict the same claim",
            )
        if claim.claim_type == "reported" and not supporting_ids:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_reported_claim_unbound",
                "Reported claims must cite supporting authoritative evidence",
            )
        if claim.claim_type == "analytical_inference" and not supporting_ids:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_inference_unbound",
                "Analytical inferences must cite supporting authoritative evidence",
            )
        if claim.claim_type == "analytical_inference" and claim.reasoning_summary is None:
            raise AnalysisTraceStructureError(
                "analysis_trace_v3_inference_without_reasoning",
                "Analytical inferences must include a concise reasoning summary",
            )

    gap_ids = [gap.gap_id for gap in analysis.gaps]
    if len(set(gap_ids)) != len(gap_ids):
        raise AnalysisTraceStructureError(
            "analysis_trace_v3_duplicate_gap_id",
            "Analysis gaps must have unique identifiers",
        )
    for gap in analysis.gaps:
        if not set(gap.affected_claim_ids).issubset(known_claim_ids):
            raise AnalysisTraceStructureError(
                "analysis_trace_v3_gap_unknown_claim",
                "An analysis gap references an unknown claim",
            )
        if gap.status == "EXPLICITLY_UNKNOWN" and gap.askable:
            raise AnalysisTraceStructureError(
                "analysis_trace_v3_explicit_unknown_askable",
                "An explicitly unknown gap cannot be marked askable",
            )

    admitted_techniques = _admitted_technique_ids(mitre_table)
    if analysis.mitre_associations and analysis.retrieval_context_id is None:
        raise AnalysisTraceProvenanceError(
            "analysis_trace_v3_mitre_without_retrieval",
            "MITRE associations require a bound retrieval context",
        )
    for association in analysis.mitre_associations:
        if not set(association.claim_ids).issubset(known_claim_ids):
            raise AnalysisTraceStructureError(
                "analysis_trace_v3_mitre_unknown_claim",
                "A MITRE association references an unknown claim",
            )
        if association.technique_id not in admitted_techniques:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_mitre_outside_context",
                "A MITRE association is outside the bound retrieval context",
            )
    return analysis


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
        return any(
            key in forbidden or _contains_key(item, forbidden)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden) for item in value)
    return False


__all__ = [
    "AnalysisTraceProvenanceError",
    "AnalysisTraceStructureError",
    "detect_forbidden_provenance",
    "validate_analysis_trace",
    "validate_analysis_trace_v3",
]
