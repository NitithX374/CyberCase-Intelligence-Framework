from __future__ import annotations

import hashlib
from collections.abc import Mapping

from app.services.case_analysis.contracts import AnalysisClaimV3
from app.services.case_analysis.source_citation_contracts import (
    AnalysisEvidenceCitation,
)


def bind_analysis_claim_citations(
    claims: list[AnalysisClaimV3],
    analysis_context: Mapping[str, object],
) -> list[AnalysisClaimV3]:
    source_texts = _source_texts(analysis_context)
    document_context = analysis_context.get("document_source_context", [])
    return [
        claim.model_copy(
            update={
                "supporting_citations": _bind_citations(
                    claim.supporting_citations,
                    set(claim.supporting_source_message_ids),
                    source_texts,
                    document_context,
                ),
                "contradicting_citations": _bind_citations(
                    claim.contradicting_citations,
                    set(claim.contradicting_source_message_ids),
                    source_texts,
                    document_context,
                ),
            }
        )
        for claim in claims
    ]


def _bind_citations(
    citations: list[AnalysisEvidenceCitation],
    allowed_source_ids: set[str],
    source_texts: dict[str, str],
    document_context: object,
) -> list[AnalysisEvidenceCitation]:
    bound: list[AnalysisEvidenceCitation] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        source_id = citation.source_message_id
        quote = citation.exact_quote
        key = (source_id, quote)
        content = source_texts.get(source_id)
        if source_id not in allowed_source_ids or content is None or quote not in content:
            continue
        if key in seen:
            continue
        seen.add(key)
        locator = _resolve_document_locator(
            source_id,
            quote,
            content,
            document_context,
        )
        bound.append(
            AnalysisEvidenceCitation(
                source_message_id=source_id,
                exact_quote=quote,
                **locator,
            )
        )
    return bound


def _source_texts(analysis_context: Mapping[str, object]) -> dict[str, str]:
    raw = analysis_context.get("_source_text_by_message_id")
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(source_id): content
        for source_id, content in raw.items()
        if isinstance(source_id, str) and isinstance(content, str)
    }


def _resolve_document_locator(
    source_id: str,
    quote: str,
    content: str,
    document_context: object,
) -> dict[str, object]:
    occurrences = _quote_occurrences(content, quote)
    candidates: set[tuple[str, str, tuple[int, ...]]] = set()
    for document in _documents_for_source(source_id, document_context):
        locator = _locator_for_document(document, content, occurrences, len(quote))
        if locator is not None:
            candidates.add(locator)
    if len(candidates) != 1:
        return {"document_id": None, "filename": None, "page_numbers": []}
    document_id, filename, page_numbers = candidates.pop()
    return {
        "document_id": document_id,
        "filename": filename,
        "page_numbers": list(page_numbers),
    }


def _documents_for_source(source_id: str, context: object) -> list[Mapping[str, object]]:
    if not isinstance(context, list):
        return []
    documents: list[Mapping[str, object]] = []
    for entry in context:
        if not isinstance(entry, Mapping) or entry.get("source_message_id") != source_id:
            continue
        raw_documents = entry.get("documents")
        if isinstance(raw_documents, list):
            documents.extend(
                value for value in raw_documents if isinstance(value, Mapping)
            )
    return documents


def _locator_for_document(
    document: Mapping[str, object],
    content: str,
    occurrences: list[int],
    quote_length: int,
) -> tuple[str, str, tuple[int, ...]] | None:
    document_id = document.get("document_id")
    filename = document.get("filename")
    if not isinstance(document_id, str) or not isinstance(filename, str):
        return None
    spans = _valid_page_spans(document.get("page_spans"), content)
    occurrence_pages = [
        tuple(
            span[0]
            for span in spans
            if span[1] < start + quote_length and span[2] > start
        )
        for start in occurrences
    ]
    if not occurrence_pages or any(not pages for pages in occurrence_pages):
        return None
    unique_pages = set(occurrence_pages)
    if len(unique_pages) != 1:
        return None
    return document_id, filename, unique_pages.pop()


def _valid_page_spans(value: object, content: str) -> list[tuple[int, int, int]]:
    if not isinstance(value, list):
        return []
    spans: list[tuple[int, int, int]] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        page = item.get("page_number")
        start = item.get("start_offset")
        end = item.get("end_offset")
        expected_hash = item.get("text_sha256")
        if not all(isinstance(part, int) for part in (page, start, end)):
            continue
        if not isinstance(expected_hash, str) or start < 0 or end > len(content) or start >= end:
            continue
        actual_hash = hashlib.sha256(content[start:end].encode("utf-8")).hexdigest()
        if actual_hash == expected_hash:
            spans.append((page, start, end))
    return sorted(spans, key=lambda span: span[1])


def _quote_occurrences(content: str, quote: str) -> list[int]:
    occurrences: list[int] = []
    start = content.find(quote)
    while start >= 0 and len(occurrences) < 64:
        occurrences.append(start)
        start = content.find(quote, start + 1)
    return occurrences


__all__ = ["bind_analysis_claim_citations"]
