from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from app.trace.quotes import MAX_PAGE_SPANS_PER_QUOTE, MAX_QUOTE_CHARS, MAX_SUPPORTED_DOCUMENT_PAGES

MAX_CONTEXT_CHARS = 400
MAX_EVIDENCE_ID_CHARS = 240

EvidencePointerState = Literal["direct", "recovered", "unresolved"]
EvidenceUnitId = Annotated[str, Field(max_length=MAX_EVIDENCE_ID_CHARS)]


def legacy_pointer_schema(schema: dict[str, object]) -> None:
    schema.pop("default", None)


class CaseEvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    evidence_unit_ids: list[EvidenceUnitId] = Field(min_length=1, max_length=64)

    @field_validator("source_id", mode="before")
    @classmethod
    def normalize_source_id(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class CaseInvalidEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    evidence_unit_id: str = Field(max_length=MAX_EVIDENCE_ID_CHARS)
    role: Literal["supporting", "contradicting"]
    pointer_state: Literal["unresolved"] = "unresolved"
    reason: Literal[
        "unknown_source",
        "malformed_id",
        "cross_source",
        "stale_id",
        "unknown_unit",
        "empty_unit",
        "duplicate_id",
    ]


class CaseQuoteContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    before: str = Field(default="", max_length=MAX_CONTEXT_CHARS)
    after: str = Field(default="", max_length=MAX_CONTEXT_CHARS)
    cut_before: bool = False
    cut_after: bool = False


class CaseSourceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    exact_quote: str = Field(default="", max_length=MAX_QUOTE_CHARS)
    evidence_unit_ids: list[EvidenceUnitId] = Field(default_factory=list, max_length=64)
    pointer_state: EvidencePointerState = Field(
        default="recovered", json_schema_extra=legacy_pointer_schema
    )
    start: int | None = Field(default=None, ge=0)
    end: int | None = Field(default=None, gt=0)
    document_id: str | None = Field(default=None, min_length=1, max_length=160)
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    page_numbers: list[int] = Field(default_factory=list, max_length=MAX_PAGE_SPANS_PER_QUOTE)
    context: CaseQuoteContext | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_quote(cls, data: object) -> object:
        if isinstance(data, dict) and not data.get("evidence_unit_ids"):
            data = dict(data)
            if isinstance(data.get("exact_quote"), str):
                data["exact_quote"] = data["exact_quote"].strip()
        return data

    @field_validator("source_id", "document_id", "filename")
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
        if self.pointer_state == "direct":
            if self.start is None or self.end is None or self.end <= self.start:
                raise ValueError("A direct evidence citation requires valid source offsets")
            if not self.evidence_unit_ids or len(self.exact_quote) != self.end - self.start:
                raise ValueError(
                    "A direct evidence citation requires its unit IDs and original text"
                )
        elif not (self.document_id and self.filename and self.page_numbers):
            self.document_id = None
            self.filename = None
            self.page_numbers = []
        return self


class CaseUnverifiedCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    role: Literal["supporting", "contradicting"]
    evidence_unit_id: str | None = Field(default=None, max_length=MAX_EVIDENCE_ID_CHARS)


def normalized_citation(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    source_id = data.get("source_id")
    quote = data.get("exact_quote", "")
    unit_ids = data.get("evidence_unit_ids", [])
    if not isinstance(source_id, str) or not isinstance(quote, str):
        return None
    source_id = source_id.strip()
    if not unit_ids:
        quote = quote.strip()
    if (
        not source_id
        or not (quote or unit_ids)
        or len(source_id) > 160
        or len(quote) > MAX_QUOTE_CHARS
    ):
        return None
    return {
        "source_id": source_id,
        "exact_quote": quote,
        "evidence_unit_ids": unit_ids,
        "pointer_state": data.get("pointer_state", "unresolved" if unit_ids else "recovered"),
        "start": data.get("start"),
        "end": data.get("end"),
        "document_id": bounded_locator(data.get("document_id"), 160),
        "filename": bounded_locator(data.get("filename"), 255),
        "page_numbers": data.get("page_numbers")
        if isinstance(data.get("page_numbers"), (list, tuple))
        else [],
        "context": stored_context(data.get("context")),
    }


def stored_context(value: object) -> CaseQuoteContext | None:
    if not isinstance(value, dict):
        return None
    try:
        return CaseQuoteContext.model_validate(value)
    except ValidationError:
        return None


def bounded_locator(value: object, limit: int) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if normalized and len(normalized) <= limit else None
