from __future__ import annotations

from collections.abc import Mapping

from app.services.case_analysis.contracts import (
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
        if not party.claim_ids:
            raise CaseAnalysisFailure(
                "case_trace_party_without_claim",
                "Case involved party requires at least one claim ID",
            )
        if not set(party.claim_ids).issubset(known_claim_ids):
            raise CaseAnalysisFailure(
                "case_trace_party_unknown_claim",
                "Case involved party references an unknown claim",
            )
    for item in trace.timeline:
        if not item.claim_ids:
            raise CaseAnalysisFailure(
                "case_trace_timeline_without_claim",
                "Case timeline item requires at least one claim ID",
            )
        if not set(item.claim_ids).issubset(known_claim_ids):
            raise CaseAnalysisFailure(
                "case_trace_timeline_unknown_claim",
                "Case timeline item references an unknown claim",
            )
    for impact in trace.impacts:
        if not impact.claim_ids:
            raise CaseAnalysisFailure(
                "case_trace_impact_without_claim",
                "Case impact requires at least one claim ID",
            )
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


__all__ = [
    "AnalysisTraceProvenanceError",
    "AnalysisTraceStructureError",
    "validate_case_trace",
]
