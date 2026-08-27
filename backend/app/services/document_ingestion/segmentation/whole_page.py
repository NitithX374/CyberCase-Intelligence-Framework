from app.services.document_ingestion.contracts import BoundingBox, RegionType
from app.services.document_ingestion.provenance import build_region_id
from app.services.document_ingestion.recognition.base import RenderedPage
from app.services.document_ingestion.rendering import image_dimensions
from app.services.document_ingestion.segmentation.base import (
    SegmentedPage,
    SegmentedRegion,
)


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
