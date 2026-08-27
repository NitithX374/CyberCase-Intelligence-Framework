import asyncio
from io import BytesIO

from PIL import Image

from app.services.document_ingestion.contracts import RegionType
from app.services.document_ingestion.recognition import RenderedPage
from app.services.document_ingestion.segmentation.whole_page import (
    WholePageRegionSegmenter,
)


def _png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (400, 300), "white").save(output, format="PNG")
    return output.getvalue()


def test_whole_page_segmentation_assigns_deterministic_region_ids() -> None:
    page = RenderedPage("DOC-ABC", 3, _png_bytes())
    first = asyncio.run(WholePageRegionSegmenter().segment_page(page))
    second = asyncio.run(WholePageRegionSegmenter().segment_page(page))

    assert [region.region_id for region in first.regions] == ["DOC-ABC-P003-R001"]
    assert [region.region_id for region in second.regions] == ["DOC-ABC-P003-R001"]
    assert first.regions[0].region_type == RegionType.UNKNOWN
    assert first.regions[0].confidence is None
    assert first.warnings == [
        "Page 3: region classification is disabled; "
        "the page was preserved as one unknown region."
    ]
