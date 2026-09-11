from __future__ import annotations

from collections.abc import Mapping

from app.services.case_analysis.contracts import (
    AnalysisTraceV3,
    CaseAdmittedSource,
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_analysis.evidenceQuoteResolver import (
    find_aligned_quote,
    quote_occurrences,
    resolve_document_locator,
)


class AnalysisTraceStructureError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class AnalysisTraceProvenanceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def validate_case_trace(
    trace: CaseAnalysisTrace,
    sources: tuple[CaseAdmittedSource, ...],
    document_context: object,
    mitre_table: object = None,
) -> CaseAnalysisTrace:
    registry = {source.source_id: source for source in sources}
    claim_ids = [claim.claim_id for claim in trace.claims]
    if len(claim_ids) != len(set(claim_ids)):
        raise CaseAnalysisFailure(
            "case_trace_duplicate_claim_id",
            "Case analysis claims must have unique identifiers",
        )
    normalized_claims = [
        _validate_claim(claim, registry, document_context) for claim in trace.claims
    ]
    known_claim_ids = set(claim_ids)
    for party in trace.involved_parties:
        if not set(party.claim_ids).issubset(known_claim_ids):
            raise CaseAnalysisFailure(
                "case_trace_party_unknown_claim",
                "Case involved party references an unknown claim",
            )
    for item in trace.timeline:
        if not set(item.claim_ids).issubset(known_claim_ids):
            raise CaseAnalysisFailure(
                "case_trace_timeline_unknown_claim",
                "Case timeline item references an unknown claim",
            )
    for impact in trace.impacts:
        if not set(impact.claim_ids).issubset(known_claim_ids):
            raise CaseAnalysisFailure(
                "case_trace_impact_unknown_claim",
                "Case impact references an unknown claim",
            )
    for gap in trace.gaps:
        if not set(gap.affected_claim_ids).issubset(known_claim_ids):
            raise CaseAnalysisFailure(
                "case_trace_gap_unknown_claim",
                "Case analysis gap references an unknown claim",
            )
        if gap.status == "EXPLICITLY_UNKNOWN" and gap.askable:
            raise CaseAnalysisFailure(
                "case_trace_explicit_unknown_askable",
                "An explicitly unknown gap cannot be marked askable",
            )
    admitted_techniques = _admitted_technique_ids(mitre_table)
    if trace.mitre_associations and trace.retrieval_context_id is None:
        raise CaseAnalysisFailure(
            "case_trace_mitre_without_retrieval",
            "Case MITRE associations require a bound retrieval context",
        )
    for association in trace.mitre_associations:
        if not set(association.claim_ids).issubset(known_claim_ids):
            raise CaseAnalysisFailure(
                "case_trace_mitre_unknown_claim",
                "Case MITRE association references an unknown claim",
            )
        if association.technique_id not in admitted_techniques:
            raise CaseAnalysisFailure(
                "case_trace_mitre_outside_context",
                "Case MITRE association is outside the bound context",
            )
    return trace.model_copy(update={"claims": normalized_claims})


def _validate_claim(
    claim: CaseAnalysisClaim,
    registry: dict[str, CaseAdmittedSource],
    document_context: object,
) -> CaseAnalysisClaim:
    supporting = set(claim.supporting_source_ids)
    contradicting = set(claim.contradicting_source_ids)
    if not supporting.issubset(registry):
        raise CaseAnalysisFailure(
            "case_trace_support_outside_evidence",
            "Case claim cites supporting evidence outside the snapshot",
        )
    if not contradicting.issubset(registry):
        raise CaseAnalysisFailure(
            "case_trace_contradiction_outside_evidence",
            "Case claim cites contradicting evidence outside the snapshot",
        )
    if supporting & contradicting:
        raise CaseAnalysisFailure(
            "case_trace_conflicting_source_role",
            "A Case source cannot both support and contradict one claim",
        )
    if claim.claim_type in {"reported", "analytical_inference"} and not supporting:
        raise CaseAnalysisFailure(
            "case_trace_claim_unbound",
            "Reported and inferred claims need supporting Case evidence",
        )
    if claim.claim_type == "analytical_inference" and claim.reasoning_summary is None:
        raise CaseAnalysisFailure(
            "case_trace_inference_without_reasoning",
            "Case inferences need a concise reasoning summary",
        )
    supporting_citations = _normalize_citations(
        claim.supporting_citations,
        supporting,
        "supporting",
        registry,
        document_context,
    )
    contradicting_citations = _normalize_citations(
        claim.contradicting_citations,
        contradicting,
        "contradicting",
        registry,
        document_context,
    )
    _require_role_complete_citations(
        supporting,
        supporting_citations,
        "supporting",
    )
    _require_role_complete_citations(
        contradicting,
        contradicting_citations,
        "contradicting",
    )
    return claim.model_copy(
        update={
            "supporting_citations": supporting_citations,
            "contradicting_citations": contradicting_citations,
        }
    )


def _require_role_complete_citations(
    source_ids: set[str],
    citations: list[CaseEvidenceCitation],
    role: str,
) -> None:
    cited_ids = {citation.source_id for citation in citations}
    missing = source_ids - cited_ids
    if missing:
        raise CaseAnalysisFailure(
            "case_trace_role_citation_missing",
            f"Every {role} Case source must have an exact citation",
        )


def _normalize_citations(
    citations: list[CaseEvidenceCitation],
    allowed_ids: set[str],
    role: str,
    registry: dict[str, CaseAdmittedSource],
    document_context: object,
) -> list[CaseEvidenceCitation]:
    normalized: list[CaseEvidenceCitation] = []
    seen: set[tuple[str, int, str]] = set()
    for citation in citations:
        if citation.source_id not in allowed_ids:
            raise CaseAnalysisFailure(
                "case_trace_citation_role_invalid",
                f"A {role} citation is not bound to its claim role",
            )
        source = registry[citation.source_id]
        if citation.source_revision != source.revision:
            raise CaseAnalysisFailure(
                "case_trace_citation_revision_invalid",
                "Case citation revision does not match the pinned source revision",
            )
        exact_quote = citation.exact_quote
        positions = quote_occurrences(source.content, exact_quote)
        if len(positions) == 0:
            aligned = find_aligned_quote(source.content, exact_quote)
            if aligned is not None:
                exact_quote = aligned
                positions = quote_occurrences(source.content, exact_quote)
        locator = resolve_document_locator(
            source.source_id,
            exact_quote,
            source.content,
            document_context,
        )
        has_documents = any(
            isinstance(e, Mapping) and e.get("source_id") == source.source_id and e.get("documents")
            for e in (document_context if isinstance(document_context, list) else [])
        )
        if len(positions) == 0:
            raise CaseAnalysisFailure(
                "case_trace_citation_quote_invalid",
                "Case citation quote is absent or ambiguous in the pinned source",
            )
        if len(positions) > 1:
            if has_documents and not locator.get("page_numbers"):
                raise CaseAnalysisFailure(
                    "case_trace_citation_quote_invalid",
                    "Case citation quote is absent or ambiguous in the pinned source",
                )
        canonical = CaseEvidenceCitation(
            source_id=source.source_id,
            source_revision=source.revision,
            exact_quote=exact_quote,
            **locator,
        )
        key = (canonical.source_id, canonical.source_revision, canonical.exact_quote)
        if key not in seen:
            normalized.append(canonical)
            seen.add(key)
    return normalized


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
                "Analytical inferences must include an externally reviewable reasoning summary",
            )

        supporting_citations = _normalize_v3_citations(
            claim.supporting_citations,
            supporting_ids,
            "supporting",
        )
        contradicting_citations = _normalize_v3_citations(
            claim.contradicting_citations,
            contradicting_ids,
            "contradicting",
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
                "An investigation gap references an unknown claim ID",
            )
        if gap.status == "EXPLICITLY_UNKNOWN" and gap.askable:
            raise AnalysisTraceStructureError(
                "analysis_trace_v3_explicit_unknown_askable",
                "Explicitly unknown investigation gaps must not be marked askable",
            )

    admitted_techniques = _admitted_technique_ids(mitre_table)
    if analysis.mitre_associations and analysis.retrieval_context_id is None:
        raise AnalysisTraceStructureError(
            "analysis_trace_v3_mitre_without_retrieval",
            "MITRE associations require a bound retrieval context",
        )
    for association in analysis.mitre_associations:
        if not set(association.claim_ids).issubset(known_claim_ids):
            raise AnalysisTraceStructureError(
                "analysis_trace_v3_mitre_unknown_claim",
                "A MITRE association references an unknown claim ID",
            )
        if association.technique_id not in admitted_techniques:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_mitre_outside_context",
                "A MITRE association technique is absent from external context",
            )

    return analysis


def _require_v3_role_complete_citations(
    source_message_ids: set[str],
    citations: list[object],
    role: str,
) -> None:
    cited_ids = {citation.source_message_id for citation in citations}
    missing = source_message_ids - cited_ids
    if missing:
        raise AnalysisTraceProvenanceError(
            "analysis_trace_v3_role_citation_missing",
            f"Every {role} source must have at least one exact citation",
        )


def _normalize_v3_citations(
    citations: list[object],
    allowed_source_ids: set[str],
    role: str,
) -> list[object]:
    normalized: list[object] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        if citation.source_message_id not in allowed_source_ids:
            raise AnalysisTraceProvenanceError(
                "analysis_trace_v3_citation_role_invalid",
                f"A {role} citation source_message_id is not declared as a {role} source",
            )
        key = (citation.source_message_id, citation.exact_quote)
        if key not in seen:
            normalized.append(citation)
            seen.add(key)
    return normalized


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


validate_native_trace = validate_case_trace

__all__ = [
    "AnalysisTraceProvenanceError",
    "AnalysisTraceStructureError",
    "detect_forbidden_provenance",
    "validate_analysis_trace_v3",
    "validate_case_trace",
    "validate_native_trace",
]
