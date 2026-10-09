from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.trace.citations import (
    CaseEvidenceReference,
    CaseInvalidEvidence,
    CaseProviderCitation,
    CaseUnverifiedCitation,
    normalized_citation,
)
from app.trace.citations import (
    CaseSourceCitation as CaseSourceCitation,
)

MAX_CLARIFICATION_QUESTION_CHARS = 300
MAX_RESOLVED_EVIDENCE_REFERENCES = 64 * 64


CaseClaimType = Literal["reported", "analytical_inference", "unknown"]


CaseEpistemicStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
    "unknown",
    "not_confirmed",
]


CaseAnalysisMode = Literal["case_overview", "question_answer"]


def normalize_identifier(value: object, prefix: str, aliases: str) -> object:
    if not isinstance(value, str):
        return value
    match = re.fullmatch(rf"(?:{aliases})[-_]?([0-9]+)", value.strip(), re.I)
    return f"{prefix}-{int(match[1]):02d}" if match else value


def unique_claim_ids(value: object) -> object:
    if not isinstance(value, (list, tuple)):
        return value
    claim_ids: list[str] = []
    for item in value:
        claim_id = normalize_identifier(item, "A", "A|claim|c")
        if not isinstance(claim_id, str) or not claim_id.strip():
            continue
        if claim_id.strip() not in claim_ids:
            claim_ids.append(claim_id.strip())
    return claim_ids[:64]


def one_line(value: object) -> object:
    return " ".join(value.split()) if isinstance(value, str) else value


def empty_as_none(value: object) -> object:
    if isinstance(value, str):
        return value.strip() or None
    return value


def clipped(limit: int) -> BeforeValidator:
    return BeforeValidator(lambda value: value.strip()[:limit] if isinstance(value, str) else value)


ClaimIds = Annotated[list[str], BeforeValidator(unique_claim_ids)]
ReasoningSummary = Annotated[str | None, BeforeValidator(empty_as_none), clipped(1_000)]


class CaseClaimContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$", max_length=80)
    claim_type: CaseClaimType
    text: str = Field(min_length=1, max_length=4_000)
    epistemic_status: CaseEpistemicStatus

    @field_validator("claim_id", mode="before")
    @classmethod
    def normalize_claim_id(cls, value: object) -> object:
        return normalize_identifier(value, "A", "A|claim|c")

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("claim text values must be non-empty")
        return normalized


class CaseClaimFields(CaseClaimContent):
    supporting_source_ids: list[str] = Field(default_factory=list, max_length=64)
    contradicting_source_ids: list[str] = Field(default_factory=list, max_length=64)

    @field_validator("supporting_source_ids", "contradicting_source_ids", mode="before")
    @classmethod
    def unique_source_ids(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            return value
        normalized: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            source_id = item.strip()
            if source_id and source_id not in normalized:
                normalized.append(source_id)
        return normalized[:64]


class CaseReadingClaim(CaseClaimContent):
    claim_type: Literal["reported", "unknown"]
    epistemic_status: Literal["reported", "suspected", "contradicted", "not_established", "unknown"]
    supporting_citations: list[CaseEvidenceReference] = Field(min_length=1, max_length=64)
    contradicting_citations: list[CaseEvidenceReference] = Field(
        default_factory=list, max_length=64
    )


class CaseProviderClaim(CaseClaimFields):
    supporting_citations: list[CaseEvidenceReference | CaseProviderCitation] = Field(
        default_factory=list, max_length=64
    )
    contradicting_citations: list[CaseEvidenceReference | CaseProviderCitation] = Field(
        default_factory=list, max_length=64
    )
    reasoning_summary: ReasoningSummary = Field(default=None, max_length=1_000)

    @model_validator(mode="before")
    @classmethod
    def select_evidence_references(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        data = dict(data)
        for field_name in ("supporting_citations", "contradicting_citations"):
            citations = data.get(field_name)
            if not isinstance(citations, (list, tuple)):
                continue
            data[field_name] = [
                {"source_id": item.get("source_id"), "evidence_unit_ids": item["evidence_unit_ids"]}
                if isinstance(item, dict) and item.get("evidence_unit_ids")
                else item
                for item in citations
            ]
        return data


class CaseClaimGrounding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: Literal["supported", "not_supported", "unassessed"]
    reason: Literal[
        "entailed",
        "neutral",
        "contradiction",
        "low_entailment",
        "no_resolved_source",
        "unresolved_source_reference",
        "conflicting_source",
        "claim_uncertain",
        "input_too_long",
        "lr_supported",
        "lr_not_supported",
        "verifier_unavailable",
    ]
    model: str | None = Field(default=None, max_length=200)
    label: Literal["entailment", "neutral", "contradiction"] | None = None
    entailment: float | None = Field(default=None, ge=0, le=1)
    threshold: float = Field(default=0.8, ge=0.5, le=1)
    method: str | None = None
    artifact_sha256: str | None = None
    neutral: float | None = Field(default=None, ge=0, le=1)
    contradiction: float | None = Field(default=None, ge=0, le=1)
    p_supported: float | None = Field(default=None, ge=0, le=1)
    selected_citation_indices: list[int] = Field(default_factory=list)
    considered_citation_indices: list[int] = Field(default_factory=list)
    selected_evidence_unit_ids: list[str] = Field(default_factory=list)
    source_similarities: list[float] = Field(default_factory=list)
    selector_threshold: float | None = None
    selection_ms: float = Field(default=0, ge=0)
    raw_tokens: int | None = Field(default=None, ge=0)
    truncated: bool | None = None
    duration_ms: float = Field(default=0, ge=0)


class CaseAnalysisClaim(CaseClaimFields):
    supporting_citations: list[CaseSourceCitation] = Field(
        default_factory=list, max_length=MAX_RESOLVED_EVIDENCE_REFERENCES
    )
    contradicting_citations: list[CaseSourceCitation] = Field(
        default_factory=list, max_length=MAX_RESOLVED_EVIDENCE_REFERENCES
    )
    unverified_citations: list[CaseUnverifiedCitation] = Field(
        default_factory=list, max_length=2 * MAX_RESOLVED_EVIDENCE_REFERENCES
    )
    invalid_evidence: list[CaseInvalidEvidence] = Field(default_factory=list)
    semantic_grounding: CaseClaimGrounding | None = None
    reasoning_summary: ReasoningSummary = Field(default=None, max_length=1_000)

    @model_validator(mode="before")
    @classmethod
    def sanitize_raw_citations(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        data = dict(data)
        for field_name in ("supporting_citations", "contradicting_citations"):
            raw = data.get(field_name)
            if not isinstance(raw, (list, tuple)):
                continue
            cleaned = []
            for item in raw:
                citation = normalized_citation(
                    item.model_dump() if isinstance(item, BaseModel) else item
                )
                if citation is not None:
                    cleaned.append(citation)
            data[field_name] = cleaned
        return data


CLAIM_FIELDS_HIDDEN_FROM_MODELS = {
    "semantic_grounding": True,
    "reasoning_summary": True,
    "supporting_source_ids": True,
    "contradicting_source_ids": True,
    "invalid_evidence": True,
    "unverified_citations": True,
    "supporting_citations": {"__all__": {"tolerated_differences", "review_flags"}},
    "contradicting_citations": {"__all__": {"tolerated_differences", "review_flags"}},
}

CLAIM_FIELDS_FOR_JUDGEMENT = {
    "claim_id": True,
    "claim_type": True,
    "text": True,
    "epistemic_status": True,
    "supporting_citations": {"__all__": {"exact_quote"}},
    "contradicting_citations": {"__all__": {"exact_quote"}},
}


class CaseAnalysisGap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gap_id: str = Field(pattern=r"^G-\d{2,}$", max_length=80)
    gap_key: str = Field(min_length=1, max_length=160)
    topic: str = Field(min_length=1, max_length=500)
    status: Literal["NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"]
    description: str = Field(min_length=1, max_length=4_000)
    affected_claim_ids: ClaimIds = Field(default_factory=list)
    reason: str = Field(min_length=1, max_length=4_000)
    priority: Literal["high", "medium", "low"]
    askable: bool
    clarification_question: str | None = Field(
        default=None, max_length=MAX_CLARIFICATION_QUESTION_CHARS
    )

    @field_validator("gap_id", mode="before")
    @classmethod
    def normalize_gap_id(cls, value: object) -> object:
        return normalize_identifier(value, "G", "G|gap")

    @field_validator("gap_key", "topic", mode="before")
    @classmethod
    def normalize_gap_text(cls, value: object) -> object:
        return one_line(value)

    @field_validator("clarification_question", mode="before")
    @classmethod
    def askable_question(cls, value: object) -> object:
        question = one_line(value)
        if not isinstance(question, str):
            return question
        return question if 0 < len(question) <= MAX_CLARIFICATION_QUESTION_CHARS else None


class CaseAssessmentTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_assessment_v1"] = "case_assessment_v1"
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)


@dataclass(frozen=True)
class CaseFollowupExchange:
    qa_id: str
    gap_key: str
    question: str
    answer: str | None = None

    @property
    def is_answered(self) -> bool:
        return bool(self.answer and self.answer.strip())


def followup_qa_id(index: int) -> str:
    return f"QA-{index:02d}"


def followup_payload(history: Sequence[CaseFollowupExchange]) -> list[dict[str, str]]:
    return [
        {
            "qa_id": item.qa_id,
            "gap_key": item.gap_key,
            "question": item.question,
            "answer": item.answer or "",
        }
        for item in history
        if item.is_answered
    ]


class FollowupSnapshotItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qa_id: str = Field(min_length=1)
    gap_key: str
    question: str
    answer: str = Field(min_length=1)


class FollowupSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["followup_snapshot_v1"] = "followup_snapshot_v1"
    items: list[FollowupSnapshotItem]


def followup_snapshot(history: Sequence[CaseFollowupExchange]) -> dict[str, object]:
    return FollowupSnapshot(
        items=[
            FollowupSnapshotItem(
                qa_id=item.qa_id,
                gap_key=item.gap_key,
                question=item.question,
                answer=item.answer or "",
            )
            for item in history
            if item.is_answered
        ]
    ).model_dump(mode="json")


def followup_history_of_snapshot(value: object) -> tuple[CaseFollowupExchange, ...]:
    snapshot = FollowupSnapshot.model_validate(value)
    return tuple(
        CaseFollowupExchange(
            qa_id=item.qa_id, gap_key=item.gap_key, question=item.question, answer=item.answer
        )
        for item in snapshot.items
    )
