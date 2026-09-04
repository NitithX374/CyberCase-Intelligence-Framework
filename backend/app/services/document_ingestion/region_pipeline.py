from app.services.document_ingestion.contracts import (
    ContentRole,
    DocumentBlock,
    DocumentPage,
    DocumentRegion,
    RecognitionCandidate,
    RecognitionMethod,
    RecognizedContent,
    RegionType,
    RoutingSummary,
    SourceType,
    VerificationStatus,
)
from app.services.document_ingestion.errors import (
    DocumentRecognitionError,
    DocumentSegmentationError,
)
from app.services.document_ingestion.merge import merge_region_text, order_regions
from app.services.document_ingestion.provenance import build_block_id
from app.services.document_ingestion.recognition.base import (
    HTRRecognizer,
    OCRRecognizer,
    RecognitionResult,
    RenderedPage,
    RenderedRegion,
)
from app.services.document_ingestion.rendering import crop_image_region
from app.services.document_ingestion.routing import RegionRoute, RegionRouter
from app.services.document_ingestion.segmentation import DocumentRegionSegmenter
from app.services.document_ingestion.segmentation.base import SegmentedRegion


class RegionRecognitionPipeline:
    def __init__(
        self,
        segmenter: DocumentRegionSegmenter,
        router: RegionRouter,
        ocr_recognizer: OCRRecognizer,
        htr_recognizer: HTRRecognizer,
    ) -> None:
        self._segmenter = segmenter
        self._router = router
        self._ocr_recognizer = ocr_recognizer
        self._htr_recognizer = htr_recognizer

    async def process(self, page: RenderedPage) -> tuple[DocumentPage, list[str]]:
        try:
            segmented = await self._segmenter.segment_page(page)
        except DocumentSegmentationError as error:
            warning = f"Page {page.page_number} [{error.code}]: {error}"
            return DocumentPage(page_number=page.page_number), [warning]

        regions = []
        warnings = list(segmented.warnings)
        summary = RoutingSummary()
        for segmented_region in segmented.regions:
            route = self._router.route(segmented_region)
            self._count_route(summary, segmented_region, route)
            region = await self._recognize_region(page, segmented_region, route)
            regions.append(region)
            if region.warning:
                warnings.append(region.warning)

        ordered = order_regions(regions)
        merged_text = merge_region_text(ordered)
        return DocumentPage(
            page_number=page.page_number,
            regions=ordered,
            merged_text=merged_text,
            routing_summary=summary,
            blocks=self._build_blocks(page, ordered),
            full_text=merged_text,
        ), warnings

    async def _recognize_region(
        self,
        page: RenderedPage,
        segmented_region: SegmentedRegion,
        route: RegionRoute,
    ) -> DocumentRegion:
        if route.recognition_method == RecognitionMethod.NONE:
            return self._empty_region(segmented_region, route)

        rendered_region = RenderedRegion(
            document_id=page.document_id,
            page_number=page.page_number,
            region_id=segmented_region.region_id,
            image_bytes=crop_image_region(page.image_bytes, segmented_region.bbox),
        )
        try:
            if route.recognition_method == RecognitionMethod.HTR:
                result = await self._htr_recognizer.recognize(rendered_region)
            else:
                result = await self._ocr_recognizer.recognize(rendered_region)
                if route.recognition_method == RecognitionMethod.UNIFIED:
                    result = RecognitionResult(
                        text=result.text,
                        recognition_method=RecognitionMethod.UNIFIED,
                        recognizer=result.recognizer,
                        verification_status=VerificationStatus.NEEDS_REVIEW,
                        confidence=result.confidence,
                        words=result.words,
                        generated_visual_descriptions=result.generated_visual_descriptions,
                        raw_provider_output=result.raw_provider_output,
                        warning=result.warning,
                    )
        except DocumentRecognitionError as error:
            warning = (
                f"Page {page.page_number} region {segmented_region.region_id} "
                f"[{error.code}]: {error}"
            )
            return self._empty_region(segmented_region, route, warning)
        return self._result_region(segmented_region, result)

    @staticmethod
    def _result_region(
        segmented_region: SegmentedRegion,
        result: RecognitionResult,
    ) -> DocumentRegion:
        candidate = RecognitionCandidate(
            recognition_method=result.recognition_method,
            recognizer=result.recognizer,
            text=result.text,
            confidence=result.confidence,
            words=result.words,
            content_role=result.content_role,
            verification_status=result.verification_status,
        )
        generated = [
            RecognizedContent(
                text=description,
                content_role=ContentRole.GENERATED_VISUAL_DESCRIPTION,
                verification_status=VerificationStatus.NON_AUTHORITATIVE,
            )
            for description in result.generated_visual_descriptions
        ]
        return DocumentRegion(
            region_id=segmented_region.region_id,
            page_number=segmented_region.page_number,
            bbox=segmented_region.bbox,
            region_type=segmented_region.region_type,
            recognition_method=result.recognition_method,
            recognizer=result.recognizer,
            text=result.text,
            segmentation_confidence=segmented_region.confidence,
            recognition_confidence=result.confidence,
            words=result.words,
            verification_status=result.verification_status,
            content_role=result.content_role,
            contains_handwriting=segmented_region.contains_handwriting,
            candidates=[candidate],
            selected_candidate_index=0,
            generated_contents=generated,
            warning=result.warning,
        )

    @staticmethod
    def _empty_region(
        segmented_region: SegmentedRegion,
        route: RegionRoute,
        warning: str | None = None,
    ) -> DocumentRegion:
        return DocumentRegion(
            region_id=segmented_region.region_id,
            page_number=segmented_region.page_number,
            bbox=segmented_region.bbox,
            region_type=segmented_region.region_type,
            recognition_method=route.recognition_method,
            recognizer="none",
            text="",
            segmentation_confidence=segmented_region.confidence,
            verification_status=route.verification_status,
            content_role=route.content_role,
            contains_handwriting=segmented_region.contains_handwriting,
            warning=warning or route.warning,
        )

    @staticmethod
    def _count_route(
        summary: RoutingSummary,
        region: SegmentedRegion,
        route: RegionRoute,
    ) -> None:
        field = route.recognition_method.value
        if hasattr(summary, field):
            setattr(summary, field, getattr(summary, field) + 1)
        if region.region_type == RegionType.MIXED_TEXT:
            summary.mixed += 1
        if region.region_type == RegionType.UNKNOWN:
            summary.unknown += 1

    @staticmethod
    def _build_blocks(
        page: RenderedPage,
        regions: list[DocumentRegion],
    ) -> list[DocumentBlock]:
        blocks = []
        for index, region in enumerate(
            (item for item in regions if item.text), start=1
        ):
            source_type = {
                RegionType.PRINTED_TEXT: SourceType.PRINTED,
                RegionType.HANDWRITING: SourceType.HANDWRITING,
                RegionType.MIXED_TEXT: SourceType.MIXED,
            }.get(region.region_type, SourceType.UNKNOWN)
            blocks.append(
                DocumentBlock(
                    block_id=build_block_id(page.document_id, page.page_number, index),
                    text=region.text,
                    source_type=source_type,
                    bbox=region.bbox,
                    confidence=region.recognition_confidence,
                )
            )
        return blocks
