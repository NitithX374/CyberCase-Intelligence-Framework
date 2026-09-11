from dataclasses import dataclass, field
from typing import Protocol

from app.services.document_ingestion.contracts import BoundingBox, RegionType
from app.services.document_ingestion.recognition.base import RenderedPage


from app.services.document_ingestion.provenance import build_region_id
from app.services.document_ingestion.rendering import image_dimensions


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


class WholePageRegionSegmenter:
    async def segment_page(self, page: RenderedPage) -> SegmentedPage:
        width, height = image_dimensions(page.image_bytes)
        return SegmentedPage(
            regions=[
                SegmentedRegion(
                    region_id=build_region_id(page.document_id, page.page_number, 1),
                    page_number=page.page_number,
                    bbox=BoundingBox(x0=0, y0=0, x1=width, y1=height),
                    region_type=RegionType.UNKNOWN,
                )
            ],
            warnings=[
                f"Page {page.page_number}: region classification is disabled; "
                "the page was preserved as one unknown region."
            ],
        )


__all__ = [
    "DocumentRegionSegmenter",
    "SegmentedPage",
    "SegmentedRegion",
    "WholePageRegionSegmenter",
]
