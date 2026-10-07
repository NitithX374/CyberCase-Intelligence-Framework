from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EvidenceIndex, EvidenceUnit
from app.trace.citations import CaseInvalidEvidence, CaseSourceCitation, CaseUnverifiedCitation
from app.trace.claims import CaseAnalysisClaim
from app.trace.quotes import find_document_locator
from app.trace.sentences import SentenceIndex, quote_context


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
    quote = source.text[unit.start : unit.end]
    return CaseSourceCitation(
        source_id=source.source_id,
        evidence_unit_ids=[unit.unit_id],
        pointer_state="direct",
        start=unit.start,
        end=unit.end,
        exact_quote=quote,
        document_id=source.document_id,
        filename=source.filename,
        page_numbers=list(locator[2]) if locator else [],
        context=quote_context(SentenceIndex(source.text), quote),
    )


def bind_citations(
    citations: list[CaseSourceCitation],
    role: Literal["supporting", "contradicting"],
    index: EvidenceIndex,
    seen: set[str],
    *args,
    **kwargs,
) -> tuple[list[CaseSourceCitation], list[CaseInvalidEvidence], list[CaseUnverifiedCitation]]:
    bound: list[CaseSourceCitation] = []
    invalid: list[CaseInvalidEvidence] = []
    for citation in citations:
        if citation.evidence_unit_ids:
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
            continue

        source = index.sources.get(citation.source_id)
        if source is None:
            invalid.append(
                CaseInvalidEvidence(
                    source_id=citation.source_id,
                    evidence_unit_id="",
                    role=role,
                    reason="unknown_source",
                )
            )
            continue

        quote = citation.exact_quote.strip()
        if not quote:
            invalid.append(
                CaseInvalidEvidence(
                    source_id=citation.source_id,
                    evidence_unit_id="",
                    role=role,
                    reason="empty_unit",
                )
            )
            continue

        start = source.text.find(quote)
        if start < 0:
            invalid.append(
                CaseInvalidEvidence(
                    source_id=citation.source_id,
                    evidence_unit_id="",
                    role=role,
                    reason="unknown_unit",
                )
            )
            continue

        end = start + len(quote)
        unit_ids = [
            u.unit_id for u in index.units_for(source.source_id)
            if u.start < end and u.end > start
        ]
        locator = find_document_locator(
            {
                "document_id": source.document_id,
                "filename": source.filename,
                "page_spans": source.provenance.get("pages"),
            },
            source.text,
            [start],
            end - start,
        )
        bound.append(
            CaseSourceCitation(
                source_id=source.source_id,
                evidence_unit_ids=unit_ids,
                pointer_state="recovered",
                start=start,
                end=end,
                exact_quote=quote,
                document_id=source.document_id,
                filename=source.filename,
                page_numbers=list(locator[2]) if locator else [],
                context=quote_context(SentenceIndex(source.text), quote),
            )
        )

    unverified = [
        CaseUnverifiedCitation(
            source_id=item.source_id,
            role=role,
            evidence_unit_id=item.evidence_unit_id or None,
        )
        for item in invalid
        if item.reason != "duplicate_id"
    ]
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


__all__ = ["bind_citations", "direct_citation", "evidence_counts"]
