from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EvidenceIndex, EvidenceUnit
from app.trace.citations import CaseInvalidEvidence, CaseSourceCitation, CaseUnverifiedCitation
from app.trace.claims import CaseAnalysisClaim
from app.trace.quote_binding import QuoteSearch, resolved_citations, unverified_citations
from app.trace.quotes import find_document_locator


def direct_citation(unit: EvidenceUnit, source: CaseSourceItem) -> CaseSourceCitation:
    locator = find_document_locator(
        {
            "document_id": source.document_id,
            "filename": source.filename,
            "page_spans": source.provenance.get("pages"),
        },
        source.text,
        [unit.start],
        unit.end - unit.start,
    )
    return CaseSourceCitation(
        source_id=source.source_id,
        evidence_unit_ids=[unit.unit_id],
        pointer_state="direct",
        start=unit.start,
        end=unit.end,
        exact_quote=source.text[unit.start : unit.end],
        document_id=source.document_id,
        filename=source.filename,
        page_numbers=list(locator[2]) if locator else [],
    )


def bind_citations(
    citations: list[CaseSourceCitation],
    role: Literal["supporting", "contradicting"],
    index: EvidenceIndex,
    search: QuoteSearch,
    document_context: object,
    seen: set[str],
) -> tuple[list[CaseSourceCitation], list[CaseInvalidEvidence], list[CaseUnverifiedCitation]]:
    bound: list[CaseSourceCitation] = []
    invalid: list[CaseInvalidEvidence] = []
    legacy: list[CaseSourceCitation] = []
    for citation in citations:
        if not citation.evidence_unit_ids:
            legacy.append(citation)
            continue
        for unit_id in citation.evidence_unit_ids:
            unit, reason = index.resolve(citation.source_id, unit_id)
            if unit_id in seen:
                unit, reason = None, "duplicate_id"
            seen.add(unit_id)
            if unit is not None:
                bound.append(direct_citation(unit, index.sources[citation.source_id]))
            else:
                invalid.append(
                    CaseInvalidEvidence(
                        source_id=citation.source_id,
                        evidence_unit_id=unit_id,
                        role=role,
                        reason=reason,
                    )
                )
    bound.extend(resolved_citations(legacy, index.sources, document_context, search))
    unverified = unverified_citations(legacy, role, index.sources, search)
    unverified.extend(
        CaseUnverifiedCitation(
            source_id=item.source_id,
            role=role,
            evidence_unit_id=item.evidence_unit_id,
        )
        for item in invalid
        if item.reason != "duplicate_id"
    )
    return bound, invalid, unverified


def evidence_counts(
    written: Sequence[CaseAnalysisClaim],
    resolved: Sequence[CaseAnalysisClaim],
    index: EvidenceIndex,
) -> dict[str, int | float | None]:
    claimed = direct = 0
    for claim in written:
        seen: set[str] = set()
        for citation in claim.supporting_citations + claim.contradicting_citations:
            for unit_id in citation.evidence_unit_ids:
                claimed += 1
                unit, _ = index.resolve(citation.source_id, unit_id)
                direct += unit is not None and unit_id not in seen
                seen.add(unit_id)
    return {
        "evidence_ids_claimed": claimed,
        "evidence_ids_resolved": direct,
        "evidence_ids_invalid": claimed - direct,
        "evidence_id_resolution_rate": direct / claimed if claimed else None,
        "claims_with_direct_evidence": sum(
            any(c.pointer_state == "direct" for c in claim.supporting_citations)
            for claim in resolved
        ),
        "claims_with_recovered_evidence": sum(
            any(c.pointer_state == "recovered" for c in claim.supporting_citations)
            for claim in resolved
        ),
        "claims_without_resolved_evidence": sum(
            not claim.supporting_citations for claim in resolved
        ),
    }
