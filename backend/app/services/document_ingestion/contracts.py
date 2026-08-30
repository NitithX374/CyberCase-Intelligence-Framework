from enum import StrEnum

from pydantic import BaseModel, Field


class IngestionMode(StrEnum):
    UNIFIED = "unified"
    ROUTED = "routed"


class ExtractionMethod(StrEnum):
    NATIVE_PDF = "native_pdf"
    NATIVE_DOCX = "native_docx"
    DOCUMENT_RECOGNITION = "document_recognition"
    HYBRID = "hybrid"


class SourceType(StrEnum):
    NATIVE = "native"
    PRINTED = "printed"
    HANDWRITING = "handwriting"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class RegionType(StrEnum):
    PRINTED_TEXT = "printed_text"
    HANDWRITING = "handwriting"
    MIXED_TEXT = "mixed_text"
    TABLE = "table"
    FIGURE = "figure"
    SIGNATURE = "signature"
    UNKNOWN = "unknown"


class RecognitionMethod(StrEnum):
    NATIVE = "native"
    UNIFIED = "unified"
    OCR = "ocr"
    HTR = "htr"
    NONE = "none"


class VerificationStatus(StrEnum):
    NATIVE = "native"
    MACHINE_READ = "machine_read"
    NEEDS_REVIEW = "needs_review"
    HUMAN_VERIFIED = "human_verified"
    NON_AUTHORITATIVE = "non_authoritative"


class ContentRole(StrEnum):
    TRANSCRIBED_TEXT = "transcribed_text"
    GENERATED_VISUAL_DESCRIPTION = "generated_visual_description"
    NON_TEXT_REGION = "non_text_region"


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class DocumentBlock(BaseModel):
    block_id: str
    text: str
    source_type: SourceType
    bbox: BoundingBox | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class RecognizedContent(BaseModel):
    text: str
    content_role: ContentRole
    verification_status: VerificationStatus


class RecognitionCandidate(BaseModel):
    recognition_method: RecognitionMethod
    recognizer: str
    text: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    content_role: ContentRole
    verification_status: VerificationStatus


class DocumentRegion(BaseModel):
    region_id: str
    page_number: int = Field(ge=1)
    bbox: BoundingBox | None = None
    region_type: RegionType
    recognition_method: RecognitionMethod
    recognizer: str
    text: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    verification_status: VerificationStatus
    content_role: ContentRole
    contains_handwriting: bool | None = None
    candidates: list[RecognitionCandidate] = Field(default_factory=list)
    selected_candidate_index: int | None = Field(default=None, ge=0)
    generated_contents: list[RecognizedContent] = Field(default_factory=list)
    warning: str | None = None


class RoutingSummary(BaseModel):
    native: int = 0
    unified: int = 0
    ocr: int = 0
    htr: int = 0
    mixed: int = 0
    unknown: int = 0


class DocumentPage(BaseModel):
    page_number: int = Field(ge=1)
    regions: list[DocumentRegion] = Field(default_factory=list)
    merged_text: str = ""
    routing_summary: RoutingSummary = Field(default_factory=RoutingSummary)
    blocks: list[DocumentBlock] = Field(default_factory=list)
    full_text: str = ""
    layout_markdown: str | None = None


class IngestedDocument(BaseModel):
    document_id: str
    filename: str
    media_type: str
    extraction_method: ExtractionMethod
    mode: IngestionMode
    pages: list[DocumentPage]
    full_text: str
    warnings: list[str]
