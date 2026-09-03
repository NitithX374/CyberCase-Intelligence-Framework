from __future__ import annotations

import hashlib

from app.schemas.chat import CaseNarrativeDocumentSource


def validated_document_source_payloads(
    content: str,
    sources: list[CaseNarrativeDocumentSource],
) -> list[dict[str, object]]:
    return [_validated_source_payload(content, source) for source in sources]


def _validated_source_payload(
    content: str,
    source: CaseNarrativeDocumentSource,
) -> dict[str, object]:
    payload = source.model_dump(mode="json")
    valid_spans: list[dict[str, object]] = []
    for span in source.page_spans:
        if not _span_matches(content, span.start_offset, span.end_offset, span.text_sha256):
            break
        valid_spans.append(span.model_dump(mode="json"))
    payload["page_spans"] = valid_spans
    return payload


def _span_matches(content: str, start: int, end: int, expected_hash: str) -> bool:
    if start < 0 or end > len(content) or start >= end:
        return False
    actual_hash = hashlib.sha256(content[start:end].encode("utf-8")).hexdigest()
    return actual_hash == expected_hash


__all__ = ["validated_document_source_payloads"]
