from __future__ import annotations

from collections.abc import Mapping

from app.services.case_analysis.contracts import (
    AnalysisClaimV3,
    AnalysisEvidenceCitation,
)
from app.services.case_analysis.evidence_quote_resolver import resolve_document_locator


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
        if (
            source_id not in allowed_source_ids
            or content is None
            or quote not in content
        ):
            continue
        if key in seen:
            continue
        seen.add(key)
        locator = resolve_document_locator(
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


__all__ = ["bind_analysis_claim_citations"]
