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


class DocumentIngestionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class UnsupportedDocumentError(DocumentIngestionError):
    def __init__(self, message: str) -> None:
        super().__init__("unsupported_document_type", message)


class DocumentLimitError(DocumentIngestionError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message)


class InvalidDocumentError(DocumentIngestionError):
    def __init__(self, message: str) -> None:
        super().__init__("invalid_document", message)


class DocumentRecognitionError(Exception):
    code = "document_recognition_failed"


class RecognitionConfigurationError(DocumentRecognitionError):
    code = "document_recognizer_not_configured"


class RecognitionTimeoutError(DocumentRecognitionError):
    code = "document_recognition_timeout"


class RecognitionProviderError(DocumentRecognitionError):
    code = "document_recognition_provider_error"


class RecognitionResponseError(DocumentRecognitionError):
    code = "document_recognition_invalid_response"
