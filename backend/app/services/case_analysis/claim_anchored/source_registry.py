import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure


@dataclass(frozen=True)
class AdmittedSource:
    source_message_id: str
    content: str
    content_sha256: str


def build_source_registry(context: Mapping[str, object]) -> tuple[AdmittedSource, ...]:
    ids = context.get("source_message_ids")
    texts = context.get("_source_text_by_message_id")
    if (
        not isinstance(ids, list)
        or not ids
        or not all(isinstance(value, str) and value.strip() for value in ids)
        or len(ids) != len(set(ids))
        or not isinstance(texts, Mapping)
        or set(ids) != set(texts)
    ):
        raise ClaimAnchoredFailure(
            "claim_sources_invalid", "Admitted source registry is invalid"
        )
    sources = []
    for source_id in ids:
        content = texts[source_id]
        if not isinstance(content, str) or not content.strip():
            raise ClaimAnchoredFailure(
                "claim_source_empty", "Admitted source text is empty"
            )
        sources.append(
            AdmittedSource(
                source_id, content, hashlib.sha256(content.encode("utf-8")).hexdigest()
            )
        )
    return tuple(sources)
