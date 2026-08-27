import asyncio
from io import BytesIO

from PIL import Image

from app.services.document_ingestion.contracts import (
    BoundingBox,
    ContentRole,
    IngestionMode,
    RecognitionMethod,
    RegionType,
    VerificationStatus,
)
from app.services.document_ingestion.errors import RecognitionProviderError
from app.services.document_ingestion.recognition import (
    RecognizedPage,
    RecognitionResult,
    RenderedPage,
)
from app.services.document_ingestion.recognition.content_filter import (
    separate_generated_visual_descriptions,
)
from app.services.document_ingestion.recognition.htr import (
    ReviewRequiredHTRRecognizer,
)
from app.services.document_ingestion.region_pipeline import RegionRecognitionPipeline
from app.services.document_ingestion.routing import RegionRouter
from app.services.document_ingestion.segmentation.base import (
    SegmentedPage,
    SegmentedRegion,
)
from app.services.document_ingestion.service import (
    DocumentIngestionLimits,
    DocumentIngestionService,
)


def _png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (400, 300), "white").save(output, format="PNG")
    return output.getvalue()


def _region(
    region_id: str,
    region_type: RegionType,
    bbox: tuple[int, int, int, int],
    contains_handwriting: bool | None = None,
    page_number: int = 3,
) -> SegmentedRegion:
    return SegmentedRegion(
        region_id=region_id,
        page_number=page_number,
        bbox=BoundingBox(x0=bbox[0], y0=bbox[1], x1=bbox[2], y1=bbox[3]),
        region_type=region_type,
        confidence=0.91,
        contains_handwriting=contains_handwriting,
    )


class StaticSegmenter:
    def __init__(self, regions: list[SegmentedRegion]) -> None:
        self.regions = regions

    async def segment_page(self, page: RenderedPage) -> SegmentedPage:
        return SegmentedPage(self.regions)


class RecordingOCR:
    def __init__(self, generated: bool = False) -> None:
        self.region_ids = []
        self.generated = generated

    async def recognize(self, region) -> RecognitionResult:
        self.region_ids.append(region.region_id)
        return RecognitionResult(
            text=f"ocr:{region.region_id}",
            recognition_method=RecognitionMethod.OCR,
            recognizer="typhoon-ocr",
            verification_status=VerificationStatus.MACHINE_READ,
            generated_visual_descriptions=["generated QR description"]
            if self.generated
            else [],
        )


class RecordingHTR:
    def __init__(self) -> None:
        self.region_ids = []

    async def recognize(self, region) -> RecognitionResult:
        self.region_ids.append(region.region_id)
        return RecognitionResult(
            text=f"htr:{region.region_id}",
            recognition_method=RecognitionMethod.HTR,
            recognizer="test-htr",
            verification_status=VerificationStatus.NEEDS_REVIEW,
        )


class FailingRecognizer:
    async def recognize(self, region) -> RecognitionResult:
        raise RecognitionProviderError("provider unavailable")


class UnifiedRecognizer:
    def __init__(self) -> None:
        self.pages = []

    async def recognize_page(self, page: RenderedPage) -> RecognizedPage:
        self.pages.append(page.page_number)
        return RecognizedPage(text="whole-page text")


def _pipeline(
    regions: list[SegmentedRegion],
    ocr=None,
    htr=None,
    mixed_policy: str = "unified",
    htr_enabled: bool = False,
) -> RegionRecognitionPipeline:
    return RegionRecognitionPipeline(
        segmenter=StaticSegmenter(regions),
        router=RegionRouter(mixed_policy, "unified", htr_enabled=htr_enabled),
        ocr_recognizer=ocr or RecordingOCR(),
        htr_recognizer=htr or RecordingHTR(),
    )


def test_router_selects_ocr_htr_and_mixed_fallback() -> None:
    router = RegionRouter("unified", "review", htr_enabled=True)
    printed = router.route(_region("P", RegionType.PRINTED_TEXT, (0, 0, 10, 10)))
    handwritten = router.route(_region("H", RegionType.HANDWRITING, (0, 0, 10, 10)))
    mixed = router.route(_region("M", RegionType.MIXED_TEXT, (0, 0, 10, 10)))

    assert printed.recognition_method == RecognitionMethod.OCR
    assert handwritten.recognition_method == RecognitionMethod.HTR
    assert mixed.recognition_method == RecognitionMethod.UNIFIED
    assert mixed.verification_status == VerificationStatus.NEEDS_REVIEW

    printed_table = router.route(_region("T1", RegionType.TABLE, (0, 0, 10, 10), False))
    handwritten_table = router.route(
        _region("T2", RegionType.TABLE, (0, 0, 10, 10), True)
    )
    assert printed_table.recognition_method == RecognitionMethod.OCR
    assert handwritten_table.recognition_method == RecognitionMethod.UNIFIED


def test_router_does_not_transcribe_figures_or_signatures() -> None:
    router = RegionRouter("unified", "unified")
    for region_type in (RegionType.FIGURE, RegionType.SIGNATURE):
        route = router.route(_region("N", region_type, (0, 0, 10, 10)))
        assert route.recognition_method == RecognitionMethod.NONE
        assert route.content_role == ContentRole.NON_TEXT_REGION
        assert route.verification_status == VerificationStatus.NON_AUTHORITATIVE


def test_figure_region_stays_non_authoritative_without_recognizer_call() -> None:
    figure = _region("DOC-P003-R001", RegionType.FIGURE, (0, 0, 100, 100))
    ocr = RecordingOCR()
    htr = RecordingHTR()
    page, warnings = asyncio.run(
        _pipeline([figure], ocr, htr).process(RenderedPage("DOC", 3, _png_bytes()))
    )

    assert warnings == []
    assert ocr.region_ids == []
    assert htr.region_ids == []
    assert page.regions[0].content_role == ContentRole.NON_TEXT_REGION
    assert page.regions[0].verification_status == VerificationStatus.NON_AUTHORITATIVE
    assert page.merged_text == ""


def test_routed_pipeline_preserves_reading_order_bbox_and_page_number() -> None:
    document_id = "DOC-TEST"
    bottom = _region(
        f"{document_id}-P003-R002", RegionType.HANDWRITING, (20, 90, 200, 120)
    )
    top = _region(
        f"{document_id}-P003-R001", RegionType.PRINTED_TEXT, (10, 10, 210, 40)
    )
    ocr = RecordingOCR(generated=True)
    htr = RecordingHTR()
    page, warnings = asyncio.run(
        _pipeline([bottom, top], ocr, htr, htr_enabled=True).process(
            RenderedPage(document_id, 3, _png_bytes())
        )
    )

    assert warnings == []
    assert page.page_number == 3
    assert [item.region_id for item in page.regions] == [
        top.region_id,
        bottom.region_id,
    ]
    assert page.regions[0].bbox == top.bbox
    assert page.regions[0].recognizer == "typhoon-ocr"
    assert page.regions[0].selected_candidate_index == 0
    assert page.merged_text == f"ocr:{top.region_id}\nhtr:{bottom.region_id}"
    generated = page.regions[0].generated_contents[0]
    assert generated.content_role == ContentRole.GENERATED_VISUAL_DESCRIPTION
    assert generated.verification_status == VerificationStatus.NON_AUTHORITATIVE
    assert "generated QR description" not in page.merged_text


def test_ocr_and_htr_failures_are_controlled_per_region() -> None:
    printed = _region("DOC-P003-R001", RegionType.PRINTED_TEXT, (0, 0, 100, 40))
    handwriting = _region("DOC-P003-R002", RegionType.HANDWRITING, (0, 50, 100, 90))
    page, warnings = asyncio.run(
        _pipeline(
            [printed, handwriting],
            FailingRecognizer(),
            FailingRecognizer(),
            htr_enabled=True,
        ).process(RenderedPage("DOC", 3, _png_bytes()))
    )

    assert page.merged_text == ""
    assert len(warnings) == 2
    assert all("document_recognition_provider_error" in warning for warning in warnings)
    assert page.regions[1].verification_status == VerificationStatus.NEEDS_REVIEW


def test_disabled_htr_preserves_handwriting_without_calling_provider() -> None:
    printed = _region("DOC-P003-R001", RegionType.PRINTED_TEXT, (0, 0, 100, 40))
    handwriting = _region("DOC-P003-R002", RegionType.HANDWRITING, (0, 50, 100, 90))
    htr = RecordingHTR()
    page, warnings = asyncio.run(
        _pipeline([printed, handwriting], RecordingOCR(), htr).process(
            RenderedPage("DOC", 3, _png_bytes())
        )
    )

    assert htr.region_ids == []
    assert page.routing_summary.htr == 0
    assert page.regions[0].text == "ocr:DOC-P003-R001"
    assert page.regions[1].recognition_method == RecognitionMethod.NONE
    assert page.regions[1].recognizer == "none"
    assert page.regions[1].verification_status == VerificationStatus.NEEDS_REVIEW
    assert warnings == ["HTR is disabled; manual transcription is required."]


def test_unavailable_enabled_htr_does_not_interrupt_printed_region() -> None:
    printed = _region("DOC-P003-R001", RegionType.PRINTED_TEXT, (0, 0, 100, 40))
    handwriting = _region("DOC-P003-R002", RegionType.HANDWRITING, (0, 50, 100, 90))
    page, warnings = asyncio.run(
        _pipeline(
            [printed, handwriting],
            RecordingOCR(),
            ReviewRequiredHTRRecognizer(),
            htr_enabled=True,
        ).process(RenderedPage("DOC", 3, _png_bytes()))
    )

    assert len(warnings) == 1
    assert "manual transcription is required" in warnings[0]
    assert page.regions[0].text == "ocr:DOC-P003-R001"
    assert page.regions[1].text == ""
    assert page.regions[1].recognizer == "review_required"
    assert page.regions[1].verification_status == VerificationStatus.NEEDS_REVIEW


def test_unified_and_routed_modes_share_the_ingestion_service() -> None:
    recognizer = UnifiedRecognizer()
    printed = _region(
        "DOC-P001-R001", RegionType.PRINTED_TEXT, (0, 0, 100, 40), page_number=1
    )
    service = DocumentIngestionService(
        recognizer,
        DocumentIngestionLimits(1_000_000, 5, 1_000_000, 500),
        region_pipeline=_pipeline([printed]),
    )
    unified = asyncio.run(
        service.ingest(_png_bytes(), "page.png", IngestionMode.UNIFIED)
    )
    routed = asyncio.run(service.ingest(_png_bytes(), "page.png", IngestionMode.ROUTED))

    assert unified.mode == IngestionMode.UNIFIED
    assert unified.pages[0].regions[0].recognition_method == RecognitionMethod.UNIFIED
    assert routed.mode == IngestionMode.ROUTED
    assert routed.pages[0].regions[0].recognition_method == RecognitionMethod.OCR


def test_figure_tags_are_separated_from_literal_transcription() -> None:
    text, descriptions = separate_generated_visual_descriptions(
        "literal Thai text\n<figure>This QR appears to contain a URL</figure>"
    )

    assert text == "literal Thai text"
    assert descriptions == ["This QR appears to contain a URL"]
