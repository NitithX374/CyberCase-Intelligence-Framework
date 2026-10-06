from __future__ import annotations

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EvidenceIndex
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.evidence_binding import evidence_counts
from app.trace.quote_binding import QuoteSearch, added_citations
from app.trace.trace import CaseGroundingReport


def grounding_report(
    written: list[CaseAnalysisClaim],
    kept: list[CaseAnalysisClaim],
    registry: dict[str, CaseSourceItem],
    *,
    search: QuoteSearch | None = None,
    evidence: EvidenceIndex | None = None,
    associations_outside_context: int = 0,
    associations_without_claim: int = 0,
    claims_dropped: int = 0,
) -> CaseGroundingReport:
    search = search or QuoteSearch(registry)

    def all_citations(claims: list[CaseAnalysisClaim]) -> list[CaseSourceCitation]:
        return [
            c
            for claim in claims
            for c in claim.supporting_citations + claim.contradicting_citations
        ]

    claimed = [citation for citation in all_citations(written) if not citation.evidence_unit_ids]
    verified = sum(
        bool(fresh)
        for claim in written
        for citations in (claim.supporting_citations, claim.contradicting_citations)
        for fresh in added_citations(
            [citation for citation in citations if not citation.evidence_unit_ids], registry, search
        )
    )
    located = 0
    pointed = 0
    unfound = 0
    for citation in claimed:
        if citation.source_id not in registry:
            unfound += 1
        elif search.located(citation.source_id, citation.exact_quote) is not None:
            located += 1
        elif search.near(citation.source_id, citation.exact_quote) is not None:
            pointed += 1
        else:
            unfound += 1

    counts = evidence_counts(written, kept, evidence or EvidenceIndex(tuple(registry.values())))
    duplicated_ids = sum(
        item.reason == "duplicate_id" for claim in kept for item in claim.invalid_evidence
    )
    return CaseGroundingReport(
        claims=len(kept),
        citations_claimed=len(claimed) + counts["evidence_ids_claimed"],
        citations_verified=verified + counts["evidence_ids_resolved"],
        citations_pointed=pointed,
        citations_unfound=unfound + counts["evidence_ids_invalid"] - duplicated_ids,
        claims_without_citation=sum(1 for c in kept if not c.supporting_citations),
        claims_duplicated=claims_dropped,
        citations_duplicated=located - verified + duplicated_ids,
        citations_marked=sum(1 for c in all_citations(kept) if c.review_flags),
        associations_outside_context=associations_outside_context,
        associations_without_claim=associations_without_claim,
        sources_cited=len({c.source_id for c in all_citations(kept)}),
        sources_total=len(registry),
        **counts,
    )
