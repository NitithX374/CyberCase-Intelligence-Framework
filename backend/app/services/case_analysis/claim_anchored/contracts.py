import hashlib
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.case_analysis.contracts import (
    AnalysisClaimV3,
    AnalysisEvidenceCitation,
    CaseAnalysisFailure,
    ClaimType,
    EpistemicStatus,
    ProviderClaimId,
)


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



class ClaimAnchoredFailure(CaseAnalysisFailure):
    def __init__(
        self, code: str, message: str, receipt: dict[str, object] | None = None
    ):
        super().__init__(code, message)
        self.receipt = deepcopy(receipt or {})


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class QuoteCandidate(StrictRecord):
    source_message_id: str = Field(min_length=1, max_length=160)
    exact_quote: str = Field(min_length=1, max_length=2_000)
    role: Literal["supporting", "contradicting"]

    @field_validator("exact_quote")
    @classmethod
    def require_literal_quote(cls, value: str) -> str:
        if not value.strip() or value != value.strip():
            raise ValueError("Quote must be nonempty with no surrounding whitespace")
        return value


class ClaimCandidate(StrictRecord):
    text: str = Field(min_length=1, max_length=4_000)
    claim_type: ClaimType
    epistemic_status: EpistemicStatus
    evidence: tuple[QuoteCandidate, ...] = Field(min_length=1, max_length=64)
    reasoning_summary: str | None = Field(default=None, min_length=1, max_length=1_000)


class ExtractedClaims(StrictRecord):
    claims: tuple[ClaimCandidate, ...] = Field(min_length=1, max_length=256)


class BoundSpan(StrictRecord):
    citation: AnalysisEvidenceCitation
    source_text_sha256: str
    start_offset: int
    end_offset: int
    role: Literal["supporting", "contradicting"]
    locator_status: Literal["document_page", "narrative_only"]


class BoundClaim(StrictRecord):
    candidate_id: str
    claim: AnalysisClaimV3
    spans: tuple[BoundSpan, ...]


class GeneratedUnit(StrictRecord):
    text: str = Field(min_length=1, max_length=4_000)
    claim_ids: tuple[ProviderClaimId, ...] = Field(min_length=1, max_length=64)

    @field_validator("text")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Generated text must be nonempty")
        return value.strip()


class GeneratedSummary(StrictRecord):
    units: tuple[GeneratedUnit, ...] = Field(min_length=1, max_length=64)


@dataclass(frozen=True)
class Selection:
    claims: tuple[BoundClaim, ...]
    omissions: tuple[dict[str, str], ...]


class SemanticVerifier(Protocol):
    async def check_claims(self, claims: tuple[BoundClaim, ...]) -> None: ...

    async def check_summary(
        self, summary: GeneratedSummary, claims: tuple[BoundClaim, ...]
    ) -> None: ...
