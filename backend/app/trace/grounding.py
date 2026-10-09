from __future__ import annotations

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EvidenceIndex
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.evidence_binding import evidence_counts
from app.trace.trace import CaseGroundingReport


def grounding_report(
    written: list[CaseAnalysisClaim],
    kept: list[CaseAnalysisClaim],
    registry: dict[str, CaseSourceItem],
    *,
    evidence: EvidenceIndex | None = None,
    claims_dropped: int = 0,
) -> CaseGroundingReport:
    evidence = evidence or EvidenceIndex(tuple(registry.values()))
    counts = evidence_counts(written, kept, evidence)

    def all_citations(claims: list[CaseAnalysisClaim]) -> list[CaseSourceCitation]:
        return [
            c
            for claim in claims
            for c in claim.supporting_citations + claim.contradicting_citations
        ]

    legacy_claimed = [c for c in all_citations(written) if not c.evidence_unit_ids]
    legacy_verified = 0
    legacy_unfound = 0
    for citation in legacy_claimed:
        source = registry.get(citation.source_id)
        quote = citation.exact_quote.strip()
        if source and quote and quote in source.text:
            legacy_verified += 1
        else:
            legacy_unfound += 1

    duplicated_ids = sum(
        item.reason == "duplicate_id" for claim in kept for item in claim.invalid_evidence
    )
    return CaseGroundingReport(
        claims=len(kept),
        citations_claimed=len(legacy_claimed) + counts["evidence_ids_claimed"],
        citations_verified=legacy_verified + counts["evidence_ids_resolved"],
        citations_pointed=0,
        citations_unfound=legacy_unfound + counts["evidence_ids_invalid"] - duplicated_ids,
        claims_without_citation=sum(1 for c in kept if not c.supporting_citations),
        claims_duplicated=claims_dropped,
        citations_duplicated=duplicated_ids,
        citations_marked=sum(1 for c in all_citations(kept) if c.review_flags),
        sources_cited=len({c.source_id for c in all_citations(kept)}),
        sources_total=len(registry),
        **counts,
    )


__all__ = ["grounding_report"]
