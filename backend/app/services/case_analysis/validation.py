from __future__ import annotations

from collections.abc import Mapping

from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.case_analysis.source_quote_resolver import (
    find_aligned_quote,
    quote_occurrences,
    resolve_document_locator,
)
from app.services.case_materials import CaseSourceBundle, CaseSourceItem, build_document_source_context


def validate_case_trace(
    trace: CaseAnalysisTrace,
    source_bundle: CaseSourceBundle,
    mitre_table: object = None,
) -> CaseAnalysisTrace:
    registry = {source.source_id: source for source in source_bundle.sources}
    document_context = build_document_source_context(source_bundle)
    claim_ids = [claim.claim_id for claim in trace.claims]
    if len(claim_ids) != len(set(claim_ids)):
        raise CaseAnalysisFailure(
            "case_trace_duplicate_claim_id",
            "Case analysis claims must have unique identifiers",
        )
    normalized_claims = [
        validate_claim(claim, registry, document_context) for claim in trace.claims
    ]
    known_claim_ids = set(claim_ids)
    normalized_parties = [
        party.model_copy(update={"claim_ids": [cid for cid in party.claim_ids if cid in known_claim_ids]})
        for party in trace.involved_parties
    ]
    normalized_timeline = [
        item.model_copy(update={"claim_ids": [cid for cid in item.claim_ids if cid in known_claim_ids]})
        for item in trace.timeline
    ]
    normalized_impacts = [
        impact.model_copy(update={"claim_ids": [cid for cid in impact.claim_ids if cid in known_claim_ids]})
        for impact in trace.impacts
    ]
    normalized_gaps = []
    for gap in trace.gaps:
        if gap.status == "EXPLICITLY_UNKNOWN" and gap.askable:
            raise CaseAnalysisFailure(
                "case_trace_explicit_unknown_askable",
                "An explicitly unknown gap cannot be marked askable",
            )
        valid_affected = [cid for cid in gap.affected_claim_ids if cid in known_claim_ids]
        normalized_gaps.append(gap.model_copy(update={"affected_claim_ids": valid_affected}))
    context_techniques = context_technique_ids(mitre_table)
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
        if association.technique_id not in context_techniques:
            raise CaseAnalysisFailure(
                "case_trace_mitre_outside_context",
                "Case MITRE association is outside the bound context",
            )
    return trace.model_copy(
        update={
            "claims": normalized_claims,
            "involved_parties": normalized_parties,
            "timeline": normalized_timeline,
            "impacts": normalized_impacts,
            "gaps": normalized_gaps,
        }
    )


def validate_claim(
    claim: CaseAnalysisClaim,
    registry: dict[str, CaseSourceItem],
    document_context: object,
) -> CaseAnalysisClaim:
    supporting = set(claim.supporting_source_ids)
    contradicting = set(claim.contradicting_source_ids)
    if not supporting.issubset(registry):
        raise CaseAnalysisFailure(
            "case_trace_support_outside_evidence",
            "Case claim cites supporting sources outside the Case source bundle",
        )
    if not contradicting.issubset(registry):
        raise CaseAnalysisFailure(
            "case_trace_contradiction_outside_evidence",
            "Case claim cites contradicting sources outside the Case source bundle",
        )
    if supporting & contradicting:
        raise CaseAnalysisFailure(
            "case_trace_conflicting_source_role",
            "A Case source cannot both support and contradict one claim",
        )
    if claim.claim_type in {"reported", "analytical_inference"} and not supporting:
        raise CaseAnalysisFailure(
            "case_trace_claim_unbound",
            "Reported and inferred claims need supporting Case sources",
        )
    supporting_citations = normalize_citations(
        claim.supporting_citations,
        supporting,
        "supporting",
        registry,
        document_context,
    )
    contradicting_citations = normalize_citations(
        claim.contradicting_citations,
        contradicting,
        "contradicting",
        registry,
        document_context,
    )
    return claim.model_copy(
        update={
            "supporting_citations": supporting_citations,
            "contradicting_citations": contradicting_citations,
        }
    )


def normalize_citations(
    citations: list[CaseSourceCitation],
    allowed_ids: set[str],
    role: str,
    registry: dict[str, CaseSourceItem],
    document_context: object,
) -> list[CaseSourceCitation]:
    normalized: list[CaseSourceCitation] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        if citation.source_id not in allowed_ids:
            continue
        source = registry.get(citation.source_id)
        if source is None:
            continue
        exact_quote = citation.exact_quote
        positions = quote_occurrences(source.text, exact_quote)
        if len(positions) == 0:
            aligned = find_aligned_quote(source.text, exact_quote)
            if aligned is not None:
                exact_quote = aligned
                positions = quote_occurrences(source.text, exact_quote)
        if len(positions) == 0:
            continue
        locator = resolve_document_locator(
            source.source_id,
            exact_quote,
            source.text,
            document_context,
        )
        has_documents = any(
            isinstance(entry, Mapping)
            and entry.get("source_id") == source.source_id
            and entry.get("documents")
            for entry in (document_context if isinstance(document_context, list) else [])
        )
        if len(positions) > 1 and has_documents and not locator.get("page_numbers"):
            locator["page_numbers"] = []
        canonical = CaseSourceCitation(
            source_id=source.source_id,
            exact_quote=exact_quote,
            **locator,
        )
        key = (canonical.source_id, canonical.exact_quote)
        if key not in seen:
            normalized.append(canonical)
            seen.add(key)
    return normalized


def context_technique_ids(value: object) -> set[str]:
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


__all__ = [
    "validate_case_trace",
]
