from __future__ import annotations

import re
from collections.abc import Sequence
from types import MappingProxyType

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EvidenceIndex
from app.trace.bind import confirmed_status, deduplicated_claims, role_source_ids, unique_unverified
from app.trace.citations import MAX_EVIDENCE_ID_CHARS
from app.trace.claims import CaseAnalysisClaim, CaseReadingClaim
from app.trace.evidence_binding import bind_citations
from app.trace.trace import CaseProviderReadingReply

LOCAL_UNIT_PATTERN = re.compile(r"U(?P<number>[0-9]{3,})")


def provider_source_payload(source: CaseSourceItem) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_id": source.source_id,
        "source_kind": source.source_kind,
        "text": source.text,
    }
    if source.source_kind == "document" or source.document_id or source.filename:
        document: dict[str, object] = {
            "document_id": source.document_id,
            "filename": source.filename,
        }
        for quality_key in ("extraction_method", "verification_status", "warnings"):
            if quality_key in source.provenance:
                document[quality_key] = source.provenance[quality_key]
        payload["document"] = document
    return payload


class ReadingSources:
    def __init__(self, sources: Sequence[CaseSourceItem]) -> None:
        self.evidence = EvidenceIndex(sources)
        self.revisions = MappingProxyType(self.evidence.revisions)
        self.payloads = tuple(self.source_payload(source) for source in sources)

    def source_payload(self, source: CaseSourceItem) -> dict[str, object]:
        payload = provider_source_payload(source)
        del payload["text"]
        units = self.evidence.units_of(source.source_id).values()
        return {
            **payload,
            "evidence_units": [
                {"unit_id": f"U{number:03d}", "text": unit.text}
                for number, unit in enumerate(units, 1)
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

    def bound_claims(self, reply: CaseProviderReadingReply) -> list[CaseAnalysisClaim]:
        return [self.bound_claim(claim) for claim in deduplicated_claims(reply.claims)]

    def bound_claim(self, claim: CaseReadingClaim) -> CaseAnalysisClaim:
        seen: set[str] = set()
        supporting, supporting_invalid, supporting_unverified = bind_citations(
            claim.supporting_citations, "supporting", self.evidence, seen, self.canonical_id
        )
        contradicting, contradicting_invalid, contradicting_unverified = bind_citations(
            claim.contradicting_citations, "contradicting", self.evidence, seen, self.canonical_id
        )
        return CaseAnalysisClaim(
            claim_id=claim.claim_id,
            claim_type=claim.claim_type,
            text=claim.text,
            epistemic_status=confirmed_status(claim.epistemic_status, supporting),
            supporting_source_ids=role_source_ids(
                [citation.source_id for citation in claim.supporting_citations],
                supporting,
                self.evidence.sources,
            ),
            contradicting_source_ids=role_source_ids(
                [citation.source_id for citation in claim.contradicting_citations],
                contradicting,
                self.evidence.sources,
            ),
            supporting_citations=supporting,
            contradicting_citations=contradicting,
            unverified_citations=unique_unverified(
                [*supporting_unverified, *contradicting_unverified]
            ),
            invalid_evidence=[*supporting_invalid, *contradicting_invalid],
        )
