from dataclasses import dataclass, field
from typing import Any, Protocol

from app.services.document_ingestion.contracts import (
    BoundingBox,
    ContentRole,
    OCRWord,
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
    words: list[OCRWord] = field(default_factory=list)


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
    words: list[OCRWord] = field(default_factory=list)


import re

_FIGURE_PATTERN = re.compile(
    r"<figure\b[^>]*>(.*?)</figure>", re.DOTALL | re.IGNORECASE
)


def separate_generated_visual_descriptions(text: str) -> tuple[str, list[str]]:
    descriptions = [
        " ".join(match.split())
        for match in _FIGURE_PATTERN.findall(text)
        if match.strip()
    ]
    transcription = _FIGURE_PATTERN.sub("", text)
    transcription = re.sub(r"\n{3,}", "\n\n", transcription).strip()
    return transcription, descriptions


class DocumentRecognizer(Protocol):
    async def recognize_page(self, page: RenderedPage) -> RecognizedPage: ...


class OCRRecognizer(Protocol):
    async def recognize(self, region: RenderedRegion) -> RecognitionResult: ...


class HTRRecognizer(Protocol):
    async def recognize(self, region: RenderedRegion) -> RecognitionResult: ...


class ReviewRequiredHTRRecognizer:
    async def recognize(self, region: RenderedRegion) -> RecognitionResult:
        return RecognitionResult(
            text="",
            recognition_method=RecognitionMethod.HTR,
            recognizer="review_required",
            verification_status=VerificationStatus.NEEDS_REVIEW,
            warning=(
                f"Page {region.page_number} region {region.region_id}: no verified "
                "Thai HTR provider is configured; manual transcription is required."
            ),
        )


__all__ = [
    "DocumentRecognizer",
    "HTRRecognizer",
    "OCRRecognizer",
    "RecognitionResult",
    "RecognizedPage",
    "RenderedPage",
    "RenderedRegion",
    "ReviewRequiredHTRRecognizer",
    "separate_generated_visual_descriptions",
]
