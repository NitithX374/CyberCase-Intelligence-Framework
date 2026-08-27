from dataclasses import dataclass, field
from typing import Any, Protocol

from app.services.document_ingestion.contracts import (
    BoundingBox,
    ContentRole,
    RecognitionMethod,
    SourceType,
    VerificationStatus,
)


@dataclass(frozen=True)
class RenderedPage:
    document_id: str
    page_number: int
    image_bytes: bytes
    media_type: str = "image/png"


@dataclass(frozen=True)
class RecognizedPage:
    text: str
    recognizer: str = "unknown"
    source_type: SourceType = SourceType.UNKNOWN
    bbox: BoundingBox | None = None
    confidence: float | None = None
    layout_markdown: str | None = None
    generated_visual_descriptions: list[str] = field(default_factory=list)
    raw_provider_output: Any | None = None


@dataclass(frozen=True)
class RenderedRegion:
    document_id: str
    page_number: int
    region_id: str
    image_bytes: bytes
    media_type: str = "image/png"


@dataclass(frozen=True)
class RecognitionResult:
    text: str
    recognition_method: RecognitionMethod
    recognizer: str
    verification_status: VerificationStatus
    content_role: ContentRole = ContentRole.TRANSCRIBED_TEXT
    confidence: float | None = None
    generated_visual_descriptions: list[str] = field(default_factory=list)
    raw_provider_output: Any | None = None
    warning: str | None = None


class DocumentRecognizer(Protocol):
    async def recognize_page(self, page: RenderedPage) -> RecognizedPage: ...


class OCRRecognizer(Protocol):
    async def recognize(self, region: RenderedRegion) -> RecognitionResult: ...


class HTRRecognizer(Protocol):
    async def recognize(self, region: RenderedRegion) -> RecognitionResult: ...
