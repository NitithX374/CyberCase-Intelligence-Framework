from dataclasses import dataclass, field
from typing import Protocol

from app.services.document_ingestion.contracts import BoundingBox, RegionType
from app.services.document_ingestion.recognition.base import RenderedPage


@dataclass(frozen=True)
class SegmentedRegion:
    region_id: str
    page_number: int
    bbox: BoundingBox
    region_type: RegionType
    confidence: float | None = None
    contains_handwriting: bool | None = None


@dataclass(frozen=True)
class SegmentedPage:
    regions: list[SegmentedRegion]
    warnings: list[str] = field(default_factory=list)


class DocumentRegionSegmenter(Protocol):
    async def segment_page(self, page: RenderedPage) -> SegmentedPage: ...
