from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from app.sources.bundle import CaseSourceItem
from app.trace.claims import (
    CaseNearPassage,
    CaseQuoteContext,
    CaseQuoteDifference,
    CaseReviewFlag,
    CaseSourceCitation,
    CaseUnverifiedCitation,
)
from app.trace.quotes import (
    MAX_QUOTE_CHARS,
    MAX_TOLERATED_DIFFERENCES,
    IndexedText,
    edge_marks,
    find_aligned_quote,
    ignored_marks,
    indexed,
    locate_quote,
    nearest_passage,
    quote_occurrences,
    resolve_document_locator,
    tolerated_differences,
    without_edge_ellipses,
)
from app.trace.sentences import SentenceIndex, quote_context


def unverified_citations(
    citations: list[CaseSourceCitation],
    role: Literal["supporting", "contradicting"],
    registry: dict[str, CaseSourceItem],
    search: QuoteSearch,
) -> list[CaseUnverifiedCitation]:
    kept: list[CaseUnverifiedCitation] = []
    for citation in citations:
        if not citation.exact_quote:
            continue
        source = registry.get(citation.source_id)
        if source is not None and search.located(source.source_id, citation.exact_quote):
            continue
        kept.append(
            CaseUnverifiedCitation(
                source_id=citation.source_id,
                role=role,
                written_quote=citation.exact_quote,
                near_passage=(
                    search.near(source.source_id, citation.exact_quote)
                    if source is not None
                    else None
                ),
            )
        )
    return kept


def located_quote(source: str | IndexedText, quote: str) -> tuple[str, ...] | None:
    source = indexed(source)
    quote = without_edge_ellipses(quote)
    if quote_occurrences(source.text, quote):
        return (quote,) if len(quote) <= MAX_QUOTE_CHARS else None
    spans = find_aligned_quote(source, quote)
    if spans is None or spans[-1][1] - spans[0][0] > MAX_QUOTE_CHARS:
        return None
    pieces = tuple(source.text[start:end] for start, end in spans)
    if any(len(quote_occurrences(source.text, piece)) > 1 for piece in pieces):
        return (source.text[spans[0][0] : spans[-1][1]],)
    return pieces


def tolerated_in(source: str | IndexedText, quote: str) -> list[CaseQuoteDifference]:
    source = indexed(source)
    quote = without_edge_ellipses(quote)
    located = None if quote_occurrences(source.text, quote) else locate_quote(source, quote)
    if located is None or located.tier not in ("folded", "relaxed", "format"):
        return []
    start, end = located.spans[0]
    if end - start > MAX_QUOTE_CHARS:
        return []
    return [
        CaseQuoteDifference(written=written, source=found)
        for written, found in tolerated_differences(quote, source.text[start:end])
    ]


class QuoteSearch:
    def __init__(self, registry: Mapping[str, CaseSourceItem]) -> None:
        self.texts = {source_id: IndexedText(source.text) for source_id, source in registry.items()}
        self.found: dict[tuple[str, str], tuple[str, ...] | None] = {}
        self.tolerances: dict[tuple[str, str], list[CaseQuoteDifference]] = {}
        self.sentences: dict[str, SentenceIndex] = {}
        self.contexts: dict[tuple[str, str], CaseQuoteContext | None] = {}
        self.nearest: dict[tuple[str, str], CaseNearPassage | None] = {}

    def located(self, source_id: str, quote: str) -> tuple[str, ...] | None:
        key = (source_id, quote)
        if key not in self.found:
            self.found[key] = located_quote(self.texts[source_id], quote)
        return self.found[key]

    def tolerated(self, source_id: str, quote: str) -> list[CaseQuoteDifference]:
        key = (source_id, quote)
        if key not in self.tolerances:
            self.tolerances[key] = tolerated_in(self.texts[source_id], quote)
        return self.tolerances[key]

    def context(self, source_id: str, quote: str) -> CaseQuoteContext | None:
        key = (source_id, quote)
        if key not in self.contexts:
            if source_id not in self.sentences:
                self.sentences[source_id] = SentenceIndex(self.texts[source_id].text)
            self.contexts[key] = quote_context(self.sentences[source_id], quote)
        return self.contexts[key]

    def near(self, source_id: str, quote: str) -> CaseNearPassage | None:
        key = (source_id, quote)
        if key not in self.nearest:
            passage = nearest_passage(self.texts[source_id], quote)
            self.nearest[key] = (
                None
                if passage is None
                else CaseNearPassage(
                    source_text=passage.source_text,
                    differences=[
                        CaseQuoteDifference(written=written, source=source)
                        for written, source in passage.differences
                    ],
                    occurrences=passage.occurrences,
                )
            )
        return self.nearest[key]


def added_citations(
    citations: list[CaseSourceCitation],
    registry: dict[str, CaseSourceItem],
    search: QuoteSearch,
    document_context: object = None,
    *,
    tolerance: bool = False,
) -> list[list[CaseSourceCitation]]:
    added: list[list[CaseSourceCitation]] = []
    kept: dict[tuple[str, str], CaseSourceCitation] = {}
    for citation in citations:
        fresh: list[CaseSourceCitation] = []
        added.append(fresh)
        source = registry.get(citation.source_id)
        if source is None:
            continue
        found = [
            *(search.tolerated(source.source_id, citation.exact_quote) if tolerance else []),
            *citation.tolerated_differences,
        ]
        for exact_quote in search.located(source.source_id, citation.exact_quote) or ():
            canonical = CaseSourceCitation(
                source_id=source.source_id,
                exact_quote=exact_quote,
                context=search.context(source.source_id, exact_quote),
                tolerated_differences=merged_differences([], found),
                **resolve_document_locator(
                    source.source_id, exact_quote, source.text, document_context
                ),
            )
            key = (canonical.source_id, canonical.exact_quote)
            if key in kept:
                kept[key].tolerated_differences = merged_differences(
                    kept[key].tolerated_differences, found
                )
            else:
                fresh.append(canonical)
                kept[key] = canonical
    if tolerance:
        for citation in kept.values():
            citation.review_flags = review_flags(search.texts[citation.source_id], citation)
    return added


def review_flags(source: IndexedText, citation: CaseSourceCitation) -> list[CaseReviewFlag]:
    flags: list[CaseReviewFlag] = []
    ignored = ignored_marks((item.written, item.source) for item in citation.tolerated_differences)
    if ignored:
        flags.append(mark_flag(ignored, "ignored"))
    places = quote_occurrences(source.text, citation.exact_quote)
    if places:
        at_edge = edge_marks(source, places[0], places[0] + len(citation.exact_quote))
        if at_edge:
            flags.append(mark_flag(at_edge, "edge"))
    return flags


def mark_flag(marks: list[str], place: Literal["ignored", "edge"]) -> CaseReviewFlag:
    return CaseReviewFlag(
        kind="meaning_mark", verdict="rule_warning", detail=f"{' '.join(marks)} {place}"
    )


def merged_differences(
    existing: list[CaseQuoteDifference], found: list[CaseQuoteDifference]
) -> list[CaseQuoteDifference]:
    merged = list(existing)
    for difference in found:
        if difference not in merged and len(merged) < MAX_TOLERATED_DIFFERENCES:
            merged.append(difference)
    return merged


def resolved_citations(
    citations: list[CaseSourceCitation],
    registry: dict[str, CaseSourceItem],
    document_context: object,
    search: QuoteSearch | None = None,
) -> list[CaseSourceCitation]:
    search = search or QuoteSearch(registry)
    return [
        citation
        for fresh in added_citations(citations, registry, search, document_context, tolerance=True)
        for citation in fresh
    ]
