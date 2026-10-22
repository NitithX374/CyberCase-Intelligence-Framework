from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EvidenceIndex, EvidenceUnit
from app.trace.citations import (
    CaseEvidenceReference,
    CaseInvalidEvidence,
    CaseSourceCitation,
    CaseUnverifiedCitation,
)
from app.trace.quotes import find_document_locator
from app.trace.sentences import SentenceIndex, quote_context


def direct_citation(
    unit: EvidenceUnit, source: CaseSourceItem, sentences: SentenceIndex | None = None
) -> CaseSourceCitation:
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
        context=None
        if "<tr" in quote.lower()
        else quote_context(sentences or SentenceIndex(source.text), quote),
    )


def bind_citations(
    citations: Sequence[CaseEvidenceReference] | Sequence[CaseSourceCitation],
    role: Literal["supporting", "contradicting"],
    index: EvidenceIndex,
    seen: set[str],
    canonical_id: Callable[[str, str], str] | None = None,
) -> tuple[list[CaseSourceCitation], list[CaseInvalidEvidence], list[CaseUnverifiedCitation]]:
    bound: list[CaseSourceCitation] = []
    invalid: list[CaseInvalidEvidence] = []
    for citation in citations:
        if not citation.evidence_unit_ids:
            invalid.append(
                CaseInvalidEvidence(
                    source_id=citation.source_id,
                    evidence_unit_id="",
                    role=role,
                    reason="malformed_id",
                )
            )
        for selected_id in citation.evidence_unit_ids:
            unit_id = canonical_id(citation.source_id, selected_id) if canonical_id else selected_id
            unit, reason = index.resolve(citation.source_id, unit_id)
            if unit_id in seen:
                unit, reason = None, "duplicate_id"
            seen.add(unit_id)
            if unit is not None:
                source_id = citation.source_id
                bound.append(
                    direct_citation(unit, index.sources[source_id], index.sentences[source_id])
                )
            else:
                invalid.append(
                    CaseInvalidEvidence(
                        source_id=citation.source_id,
                        evidence_unit_id=unit_id,
                        role=role,
                        reason=reason,
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


__all__ = ["bind_citations", "direct_citation"]
