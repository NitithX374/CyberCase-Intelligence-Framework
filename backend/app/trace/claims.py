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
    ValidationError,
    field_validator,
    model_validator,
)

from app.trace.quotes import (
    MAX_PAGE_SPANS_PER_QUOTE,
    MAX_POINTER_PLACES,
    MAX_QUOTE_CHARS,
    MAX_SUPPORTED_DOCUMENT_PAGES,
    MAX_TOLERATED_DIFFERENCES,
)

MAX_CLARIFICATION_QUESTION_CHARS = 300
MAX_CONTEXT_CHARS = 400
MAX_REVIEW_FLAGS = 8


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


class CaseQuoteContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    before: str = Field(default="", max_length=MAX_CONTEXT_CHARS)
    after: str = Field(default="", max_length=MAX_CONTEXT_CHARS)
    cut_before: bool = False
    cut_after: bool = False


class CaseQuoteDifference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    written: str = Field(default="", max_length=MAX_QUOTE_CHARS)
    source: str = Field(default="", max_length=2 * MAX_QUOTE_CHARS)


class CaseReviewFlag(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["meaning_mark"]
    verdict: Literal["rule_warning"]
    detail: str = Field(min_length=1, max_length=80)


class CaseSourceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    exact_quote: str = Field(default="", max_length=MAX_QUOTE_CHARS)
    document_id: str | None = Field(default=None, min_length=1, max_length=160)
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    page_numbers: list[int] = Field(default_factory=list, max_length=MAX_PAGE_SPANS_PER_QUOTE)
    context: CaseQuoteContext | None = None
    tolerated_differences: list[CaseQuoteDifference] = Field(
        default_factory=list, max_length=MAX_TOLERATED_DIFFERENCES
    )
    review_flags: list[CaseReviewFlag] = Field(default_factory=list, max_length=MAX_REVIEW_FLAGS)

    @field_validator("source_id", "exact_quote", "document_id", "filename")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("page_numbers", mode="before")
    @classmethod
    def sanitize_page_numbers(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            return value
        pages: list[int] = []
        for item in value:
            page = int(item.strip()) if isinstance(item, str) and item.strip().isdigit() else item
            if (
                isinstance(page, int)
                and 1 <= page <= MAX_SUPPORTED_DOCUMENT_PAGES
                and page not in pages
            ):
                pages.append(page)
        return pages

    @model_validator(mode="after")
    def drop_incomplete_locator(self) -> CaseSourceCitation:
        if not (self.document_id and self.filename and self.page_numbers):
            self.document_id = None
            self.filename = None
            self.page_numbers = []
        return self


class CaseProviderCitation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_id: str = Field(min_length=1, max_length=160)
    exact_quote: str = Field(min_length=1, max_length=MAX_QUOTE_CHARS)


class CaseNearPassage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_text: str = Field(min_length=1, max_length=2 * MAX_QUOTE_CHARS)
    differences: list[CaseQuoteDifference] = Field(
        default_factory=list, max_length=MAX_POINTER_PLACES
    )
    occurrences: int = Field(default=1, ge=1)


class CaseUnverifiedCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    role: Literal["supporting", "contradicting"]
    written_quote: str = Field(min_length=1, max_length=MAX_QUOTE_CHARS)
    near_passage: CaseNearPassage | None = None


class CaseClaimFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$", max_length=80)
    claim_type: CaseClaimType
    text: str = Field(min_length=1, max_length=4_000)
    epistemic_status: CaseEpistemicStatus
    supporting_source_ids: list[str] = Field(default_factory=list, max_length=64)
    contradicting_source_ids: list[str] = Field(default_factory=list, max_length=64)

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
            data[field_name] = cleaned[:64]
        return data

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


class CaseProviderClaim(CaseClaimFields):
    supporting_citations: list[CaseProviderCitation] = Field(default_factory=list, max_length=64)
    contradicting_citations: list[CaseProviderCitation] = Field(default_factory=list, max_length=64)
    reasoning_summary: ReasoningSummary = Field(default=None, max_length=1_000)


class CaseAnalysisClaim(CaseClaimFields):
    supporting_citations: list[CaseSourceCitation] = Field(default_factory=list, max_length=64)
    contradicting_citations: list[CaseSourceCitation] = Field(default_factory=list, max_length=64)
    unverified_citations: list[CaseUnverifiedCitation] = Field(default_factory=list, max_length=128)
    reasoning_summary: ReasoningSummary = Field(default=None, max_length=1_000)


CLAIM_FIELDS_HIDDEN_FROM_MODELS = {
    "unverified_citations": True,
    "supporting_citations": {"__all__": {"tolerated_differences", "review_flags"}},
    "contradicting_citations": {"__all__": {"tolerated_differences", "review_flags"}},
}

CLAIM_FIELDS_HIDDEN_FROM_JUDGEMENT = {
    "unverified_citations": True,
    "supporting_citations": {"__all__": {"tolerated_differences", "context", "review_flags"}},
    "contradicting_citations": {"__all__": {"tolerated_differences", "context", "review_flags"}},
}


def normalized_citation(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    source_id = data.get("source_id")
    quote = data.get("exact_quote")
    if not isinstance(source_id, str) or not isinstance(quote, str):
        return None
    source_id = source_id.strip()
    quote = quote.strip()
    if not source_id or not quote or len(source_id) > 160 or len(quote) > MAX_QUOTE_CHARS:
        return None
    return {
        "source_id": source_id,
        "exact_quote": quote,
        "document_id": bounded_locator(data.get("document_id"), 160),
        "filename": bounded_locator(data.get("filename"), 255),
        "page_numbers": data.get("page_numbers")
        if isinstance(data.get("page_numbers"), (list, tuple))
        else [],
        "context": stored_context(data.get("context")),
        "tolerated_differences": stored_differences(data.get("tolerated_differences")),
        "review_flags": stored_review_flags(data.get("review_flags")),
    }


def stored_context(value: object) -> CaseQuoteContext | None:
    if not isinstance(value, dict):
        return None
    try:
        return CaseQuoteContext.model_validate(value)
    except ValidationError:
        return None


def stored_differences(value: object) -> list[CaseQuoteDifference]:
    if not isinstance(value, list):
        return []
    kept: list[CaseQuoteDifference] = []
    for item in value[:MAX_TOLERATED_DIFFERENCES]:
        try:
            kept.append(CaseQuoteDifference.model_validate(item))
        except ValidationError:
            continue
    return kept


def stored_review_flags(value: object) -> list[CaseReviewFlag]:
    if not isinstance(value, list):
        return []
    kept: list[CaseReviewFlag] = []
    for item in value[:MAX_REVIEW_FLAGS]:
        try:
            kept.append(CaseReviewFlag.model_validate(item))
        except ValidationError:
            continue
    return kept


def bounded_locator(value: object, limit: int) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if normalized and len(normalized) <= limit else None


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
