from __future__ import annotations

from .models import ClassificationRecord, EntityRecord, Span
from .normalization import normalize_text, normalize_with_mapping


class SpanMappingError(ValueError):
    pass


def _token_ranges(entity: EntityRecord) -> tuple[str, tuple[tuple[int, int], ...]]:
    cursor = 0
    ranges: list[tuple[int, int]] = []
    token_texts: list[str] = []
    for token in entity.tokens:
        if token_texts:
            cursor += 1
        start = cursor
        cursor += len(token.text)
        ranges.append((start, cursor))
        token_texts.append(token.text)
    return " ".join(token_texts), tuple(ranges)


def _normalized_indices_for_range(
    source_ranges: tuple[tuple[int, int], ...], start: int, end: int
) -> tuple[int, ...]:
    return tuple(
        index
        for index, (source_start, source_end) in enumerate(source_ranges)
        if source_start < end and source_end > start
    )


def _map_span(
    classification: ClassificationRecord,
    entity_text: str,
    canonical_mapping,
    token_start: int,
    token_end: int,
) -> Span:
    normalized_indices = _normalized_indices_for_range(
        canonical_mapping.source_ranges, token_start, token_end
    )
    if not normalized_indices:
        raise SpanMappingError("ATK token run disappeared during normalization")
    normalized_start = min(normalized_indices)
    normalized_end = max(normalized_indices) + 1
    classification_mapping = normalize_with_mapping(classification.original_text)
    original_ranges = classification_mapping.source_ranges[normalized_start:normalized_end]
    if not original_ranges:
        raise SpanMappingError("Normalized ATK run has no original character range")
    start = min(item[0] for item in original_ranges)
    end = max(item[1] for item in original_ranges)
    if start < 0 or end > len(classification.original_text) or start >= end:
        raise SpanMappingError("Derived span is outside original text bounds")
    text = classification.original_text[start:end]
    expected = entity_text[token_start:token_end]
    if normalize_text(text) != normalize_text(expected):
        raise SpanMappingError("Derived span text does not reproduce the ATK token run")
    return Span(start, end, text)


def derive_spans(classification: ClassificationRecord, entity: EntityRecord) -> tuple[Span, ...]:
    entity_text, token_ranges = _token_ranges(entity)
    classification_mapping = normalize_with_mapping(classification.original_text)
    entity_mapping = normalize_with_mapping(entity_text)
    if classification_mapping.text != entity_mapping.text:
        raise SpanMappingError("Classification and entity text are not exactly aligned")
    spans: list[Span] = []
    run_start: int | None = None
    for index, token in enumerate(entity.tokens + (None,)):
        if token is not None and token.label == "ATK":
            if run_start is None:
                run_start = index
            continue
        if run_start is None:
            continue
        token_start = token_ranges[run_start][0]
        token_end = token_ranges[index - 1][1]
        spans.append(_map_span(classification, entity_text, entity_mapping, token_start, token_end))
        run_start = None
    return tuple(spans)


def span_signature(spans: tuple[Span, ...]) -> tuple[tuple[int, int, str], ...]:
    return tuple((span.start, span.end, span.text) for span in spans)
