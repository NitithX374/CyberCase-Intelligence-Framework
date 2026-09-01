from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AnalysisEvidenceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_message_id: str = Field(min_length=1, max_length=160)
    exact_quote: str = Field(min_length=1, max_length=2_000)
    document_id: str | None = Field(default=None, min_length=1, max_length=160)
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    page_numbers: list[int] = Field(default_factory=list, max_length=8)

    @field_validator("source_message_id", "exact_quote", "document_id", "filename")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("page_numbers")
    @classmethod
    def unique_page_numbers(cls, value: list[int]) -> list[int]:
        if any(page < 1 or page > 500 for page in value):
            raise ValueError("citation page numbers must be between 1 and 500")
        if len(value) != len(set(value)):
            raise ValueError("citation page numbers must be unique")
        return value

    @model_validator(mode="after")
    def validate_document_locator(self) -> "AnalysisEvidenceCitation":
        has_document_locator = bool(
            self.document_id or self.filename or self.page_numbers
        )
        if has_document_locator and not (
            self.document_id and self.filename and self.page_numbers
        ):
            raise ValueError("document citations require an identifier, filename, and pages")
        return self


__all__ = ["AnalysisEvidenceCitation"]
