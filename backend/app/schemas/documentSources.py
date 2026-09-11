from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DocumentExtractionMethod = Literal[
    "native_pdf",
    "native_docx",
    "document_recognition",
    "hybrid",
]
DocumentVerificationStatus = Literal["native", "machine_read", "needs_review"]
DocumentConfidenceStatus = Literal["reported", "not_reported", "not_applicable"]


class CaseNarrativeDocumentPageSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_number: int = Field(ge=1, le=500)
    start_offset: int = Field(ge=0, le=2_000_000)
    end_offset: int = Field(ge=1, le=2_000_000)
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_offsets(self) -> "CaseNarrativeDocumentPageSpan":
        if self.end_offset <= self.start_offset:
            raise ValueError("document page span must have positive length")
        return self


class CaseNarrativeDocumentSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1, max_length=160)
    filename: str = Field(min_length=1, max_length=255)
    extraction_method: DocumentExtractionMethod
    page_count: int = Field(ge=1, le=500)
    verification_status: DocumentVerificationStatus
    confidence_status: DocumentConfidenceStatus
    minimum_confidence: float | None = Field(default=None, ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=32)
    page_spans: list[CaseNarrativeDocumentPageSpan] = Field(
        default_factory=list,
        max_length=500,
    )

    @field_validator("document_id", "filename")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("warnings")
    @classmethod
    def normalize_warnings(cls, value: list[str]) -> list[str]:
        normalized = [warning.strip() for warning in value]
        if any(not warning or len(warning) > 500 for warning in normalized):
            raise ValueError("document warnings must be non-empty and bounded")
        if len(set(normalized)) != len(normalized):
            raise ValueError("document warnings must be unique")
        return normalized

    @model_validator(mode="after")
    def validate_confidence(self) -> "CaseNarrativeDocumentSource":
        if self.confidence_status == "reported" and self.minimum_confidence is None:
            raise ValueError("reported confidence requires a value")
        if self.confidence_status != "reported" and self.minimum_confidence is not None:
            raise ValueError("unreported confidence cannot include a value")
        page_numbers = [span.page_number for span in self.page_spans]
        if len(page_numbers) != len(set(page_numbers)):
            raise ValueError("document page spans must use unique page numbers")
        if any(page_number > self.page_count for page_number in page_numbers):
            raise ValueError("document page span exceeds the document page count")
        return self
