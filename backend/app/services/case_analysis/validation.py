"""Deterministic Analysis Trace membership and epistemic validation."""

from __future__ import annotations

from collections.abc import Mapping

from app.services.case_analysis.contracts import (
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
    response: ProviderCaseAnalysis,
    *,
    case_state_json: Mapping[str, object],
    mitre_table: object,
    analysis_mode: str,
) -> AnalysisTraceDraft:
    claims = response.claims
    claim_ids = [claim.claim_id for claim in claims]
    if len(set(claim_ids)) != len(claim_ids):
        raise AnalysisTraceStructureError(
            "analysis_trace_duplicate_claim_id",
            "Analysis Trace claim IDs must be unique",
        )

    entities = _indexed_collection(case_state_json, "entities", "entity_id")
    relationships = _indexed_collection(
        case_state_json,
        "relationships",
        "relationship_id",
    )
    evidence = _indexed_collection(case_state_json, "evidence", "evidence_id")
    timeline = _indexed_collection(case_state_json, "timeline", "event_id")
    _validate_relationship_endpoints(relationships, entities)

    for claim in claims:
        _require_membership(
            claim.entity_ids,
            entities,
            "analysis_trace_entity_reference_invalid",
        )
        _require_membership(
            claim.relationship_ids,
            relationships,
            "analysis_trace_relationship_reference_invalid",
        )
        _require_membership(
            claim.evidence_ids,
            evidence,
            "analysis_trace_evidence_reference_invalid",
        )
        _require_membership(
            claim.timeline_event_ids,
            timeline,
            "analysis_trace_timeline_reference_invalid",
        )
        _validate_relationship_status(claim, relationships)

    associations = response.mitre_associations
    association_ids = [association.association_id for association in associations]
    if len(set(association_ids)) != len(association_ids):
        raise AnalysisTraceStructureError(
            "analysis_trace_duplicate_association_id",
            "MITRE association IDs must be unique",
        )
    admitted_technique_ids = _admitted_mitre_technique_ids(mitre_table)
    claim_id_set = set(claim_ids)
    for association in associations:
        if association.technique_id not in admitted_technique_ids:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_mitre_technique_not_admitted",
                "MITRE association references a technique outside the bound RagContext",
            )
        if not set(association.claim_ids) <= claim_id_set:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_mitre_claim_reference_invalid",
                "MITRE association references a claim outside the Analysis Trace",
            )

    return AnalysisTraceDraft(
        analysis_mode=analysis_mode,
        claims=claims,
        mitre_associations=associations,
    )


def detect_forbidden_provenance(raw_payload: object) -> None:
    for key, value in _walk_mapping_values(raw_payload):
        if key == "mitre_technique_ids":
            raise AnalysisTraceProvenanceError(
                "analysis_trace_claim_mitre_reference_forbidden",
                "MITRE technique IDs cannot be attached to incident claims",
            )
        if key == "evidence_ids" and isinstance(value, list):
            if any(_looks_like_mitre_id(item) for item in value):
                raise AnalysisTraceProvenanceError(
                    "analysis_trace_mitre_used_as_incident_evidence",
                    "MITRE context cannot be used as incident evidence",
                )

    if not isinstance(raw_payload, Mapping):
        return
    raw_associations = raw_payload.get("mitre_associations", [])
    if not isinstance(raw_associations, list):
        return
    for association in raw_associations:
        if not isinstance(association, Mapping):
            continue
        technique_id = association.get("technique_id")
        if not _looks_like_mitre_id(technique_id):
            raise AnalysisTraceProvenanceError(
                "analysis_trace_mitre_technique_invalid",
                "MITRE association technique ID is invalid",
            )
        if association.get("status") != "candidate_only":
            raise AnalysisTraceProvenanceError(
                "analysis_trace_mitre_status_invalid",
                "MITRE associations must remain candidate-only",
            )
        if association.get("support_role") != "external_technical_context":
            raise AnalysisTraceProvenanceError(
                "analysis_trace_mitre_support_role_invalid",
                "MITRE associations must remain external technical context",
            )


def _indexed_collection(
    case_state: Mapping[str, object],
    collection_name: str,
    id_key: str,
) -> dict[str, Mapping[str, object]]:
    raw_collection = case_state.get(collection_name, [])
    if not isinstance(raw_collection, list):
        raise AnalysisTraceProvenanceError(
            "analysis_trace_bound_state_invalid",
            f"Bound Case State {collection_name} is invalid",
        )
    indexed: dict[str, Mapping[str, object]] = {}
    for item in raw_collection:
        if not isinstance(item, Mapping):
            raise AnalysisTraceProvenanceError(
                "analysis_trace_bound_state_invalid",
                f"Bound Case State {collection_name} is invalid",
            )
        item_id = item.get(id_key)
        if not isinstance(item_id, str) or not item_id or item_id in indexed:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_bound_state_invalid",
                f"Bound Case State {collection_name} identifiers are invalid",
            )
        indexed[item_id] = item
    return indexed


def _validate_relationship_endpoints(
    relationships: Mapping[str, Mapping[str, object]],
    entities: Mapping[str, Mapping[str, object]],
) -> None:
    for relationship in relationships.values():
        subject_id = relationship.get("subject_entity_id")
        object_id = relationship.get("object_entity_id")
        if subject_id not in entities or object_id not in entities:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_relationship_endpoint_invalid",
                "A bound relationship endpoint does not exist in Case State",
            )


def _require_membership(
    references: list[str],
    indexed: Mapping[str, Mapping[str, object]],
    failure_code: str,
) -> None:
    if any(reference not in indexed for reference in references):
        raise AnalysisTraceProvenanceError(
            failure_code,
            "Analysis Trace contains a reference outside the bound Case State",
        )


def _validate_relationship_status(
    claim: object,
    relationships: Mapping[str, Mapping[str, object]],
) -> None:
    relationship_ids = getattr(claim, "relationship_ids", [])
    epistemic_status = getattr(claim, "epistemic_status", None)
    for relationship_id in relationship_ids:
        relationship_status = relationships[relationship_id].get("status")
        if relationship_status != epistemic_status:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_relationship_status_changed",
                "A claim must preserve its referenced relationship status",
            )


def _admitted_mitre_technique_ids(mitre_table: object) -> set[str]:
    if not isinstance(mitre_table, list):
        raise AnalysisTraceProvenanceError(
            "analysis_trace_bound_mitre_context_invalid",
            "Bound RagContext MITRE table is invalid",
        )
    admitted: set[str] = set()
    for row in mitre_table:
        if not isinstance(row, Mapping):
            raise AnalysisTraceProvenanceError(
                "analysis_trace_bound_mitre_context_invalid",
                "Bound RagContext MITRE row is invalid",
            )
        technique_id = row.get("technique_id")
        entity_type = row.get("entity_type")
        if (
            _looks_like_mitre_id(technique_id)
            and isinstance(entity_type, str)
            and entity_type.strip().lower() in {"technique", "subtechnique"}
        ):
            admitted.add(str(technique_id).upper())
    return admitted


def _walk_mapping_values(value: object):
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key), child
            yield from _walk_mapping_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_mapping_values(child)


def _looks_like_mitre_id(value: object) -> bool:
    if not isinstance(value, str):
        return False
    prefix, separator, suffix = value.upper().partition(".")
    base = prefix if separator else value.upper()
    return base.startswith(("T", "G", "S")) and base[1:].isdigit() and len(base) == 5 and (
        not separator or (len(suffix) == 3 and suffix.isdigit())
    )


__all__ = [
    "AnalysisTraceProvenanceError",
    "AnalysisTraceStructureError",
    "detect_forbidden_provenance",
    "validate_analysis_trace",
]
