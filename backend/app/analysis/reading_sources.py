from __future__ import annotations

import re
from collections.abc import Sequence
from types import MappingProxyType

from app.analysis.source_payload import provider_source_payload
from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EVIDENCE_VERSION, EvidenceIndex, evidence_units
from app.trace.citations import MAX_EVIDENCE_ID_CHARS, CaseEvidenceReference
from app.trace.trace import CaseProviderReadingReply

LOCAL_UNIT_PATTERN = re.compile(r"U(?P<number>[0-9]{3,})")


class ReadingSources:
    def __init__(self, sources: Sequence[CaseSourceItem]) -> None:
        index = EvidenceIndex(sources)
        self.revisions = MappingProxyType(index.revisions)
        self.payloads = tuple(self.source_payload(source) for source in sources)

    @staticmethod
    def source_payload(source: CaseSourceItem) -> dict[str, object]:
        payload = provider_source_payload(source)
        del payload["text"]
        return {
            **payload,
            "evidence_version": EVIDENCE_VERSION,
            "evidence_units": [
                {"unit_id": f"U{number:03d}", "text": unit.text}
                for number, unit in enumerate(evidence_units(source), 1)
            ],
        }

    def canonical_id(self, source_id: str, selected_id: str) -> str:
        match = LOCAL_UNIT_PATTERN.fullmatch(selected_id)
        if match is None or source_id not in self.revisions:
            return selected_id
        number = int(match["number"])
        if number < 1 or match["number"] != f"{number:03d}":
            return selected_id
        canonical_id = f"{source_id}:U{number:03d}-{self.revisions[source_id]}"
        return canonical_id if len(canonical_id) <= MAX_EVIDENCE_ID_CHARS else selected_id

    def canonical_citations(
        self, citations: list[CaseEvidenceReference]
    ) -> list[CaseEvidenceReference]:
        return [
            citation.model_copy(
                update={
                    "evidence_unit_ids": [
                        self.canonical_id(citation.source_id, selected_id)
                        for selected_id in citation.evidence_unit_ids
                    ]
                }
            )
            for citation in citations
        ]

    def canonical_reply(self, reply: CaseProviderReadingReply) -> CaseProviderReadingReply:
        return reply.model_copy(
            update={
                "claims": [
                    claim.model_copy(
                        update={
                            "supporting_citations": self.canonical_citations(
                                claim.supporting_citations
                            ),
                            "contradicting_citations": self.canonical_citations(
                                claim.contradicting_citations
                            ),
                        }
                    )
                    for claim in reply.claims
                ]
            }
        )
