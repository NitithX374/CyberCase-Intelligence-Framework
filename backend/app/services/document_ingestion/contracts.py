from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ExtractionMethod(StrEnum):
    NATIVE_PDF = "native_pdf"
    NATIVE_DOCX = "native_docx"
    DOCUMENT_RECOGNITION = "document_recognition"
    HYBRID = "hybrid"


class DocumentPage(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    text_method: Literal["native", "ocr"]
    verification_status: Literal["native", "machine_read", "needs_review"]


class IngestedDocument(BaseModel):
    document_id: str
    filename: str
    media_type: str
    extraction_method: ExtractionMethod
    pages: list[DocumentPage]
    full_text: str
    warnings: list[str] = Field(default_factory=list)


__all__ = [
    "DocumentPage",
    "ExtractionMethod",
    "IngestedDocument",
]
