import re
from dataclasses import dataclass

from app.services.document_ingestion.contracts import (
    DocumentBlock,
    DocumentPage,
    ExtractionMethod,
    IngestedDocument,
    IngestionMode,
    RoutingSummary,
    SourceType,
)
from app.services.document_ingestion.detection import DocumentKind, detect_document
from app.services.document_ingestion.errors import (
    DocumentLimitError,
    DocumentRecognitionError,
    InvalidDocumentError,
)
from app.services.document_ingestion.parsers import inspect_pdf, parse_docx
from app.services.document_ingestion.parsers.pdf_text_parser import (
    NativeTextPolicy,
    split_native_blocks,
)
from app.services.document_ingestion.provenance import (
    build_block_id,
    build_blocks,
    build_document_id,
    build_native_regions,
)
from app.services.document_ingestion.recognition import DocumentRecognizer, RenderedPage
from app.services.document_ingestion.recognized_region import build_unified_region
from app.services.document_ingestion.region_pipeline import RegionRecognitionPipeline
from app.services.document_ingestion.rendering import (
    normalize_image,
    render_pdf_page,
)


@dataclass(frozen=True)
class DocumentIngestionLimits:
    max_bytes: int
    max_pages: int
    max_image_pixels: int
    render_longest_edge: int


class DocumentIngestionService:
    def __init__(
        self,
        recognizer: DocumentRecognizer,
        limits: DocumentIngestionLimits,
        native_text_policy: NativeTextPolicy | None = None,
        region_pipeline: RegionRecognitionPipeline | None = None,
    ) -> None:
        self._recognizer = recognizer
        self._limits = limits
        self._native_text_policy = native_text_policy or NativeTextPolicy()
        self._region_pipeline = region_pipeline

    async def ingest(
        self,
        content: bytes,
        filename: str,
        mode: IngestionMode = IngestionMode.UNIFIED,
    ) -> IngestedDocument:
        self._validate_content(content)
        detected = detect_document(content)
        document_id = build_document_id(content)
        safe_filename = self._safe_filename(filename)

        if detected.kind == DocumentKind.DOCX:
            pages, warnings = parse_docx(content, document_id)
            method = ExtractionMethod.NATIVE_DOCX
        elif detected.kind == DocumentKind.PDF:
            pages, warnings, method = await self._ingest_pdf(content, document_id, mode)
        else:
            pages, warnings = await self._ingest_image(content, document_id, mode)
            method = ExtractionMethod.DOCUMENT_RECOGNITION

        full_text = "\n\n".join(page.merged_text for page in pages if page.merged_text)
        return IngestedDocument(
            document_id=document_id,
            filename=safe_filename,
            media_type=detected.media_type,
            extraction_method=method,
            mode=mode,
            pages=pages,
            full_text=full_text,
            warnings=warnings,
        )

    def _validate_content(self, content: bytes) -> None:
        if not content:
            raise InvalidDocumentError("The uploaded document is empty.")
        if len(content) > self._limits.max_bytes:
            raise DocumentLimitError(
                "document_size_limit_exceeded",
                f"The document exceeds the {self._limits.max_bytes}-byte ingestion limit.",
            )

    async def _ingest_pdf(
        self,
        content: bytes,
        document_id: str,
        mode: IngestionMode,
    ) -> tuple[list[DocumentPage], list[str], ExtractionMethod]:
        inspection = inspect_pdf(
            content,
            self._native_text_policy,
            self._limits.max_pages,
        )
        pages = []
        warnings = []
        native_page_count = 0

        for inspected_page in inspection.pages:
            if inspected_page.warning:
                warnings.append(inspected_page.warning)
            if inspected_page.usable_native_text:
                pages.append(
                    self._native_page(
                        document_id,
                        inspected_page.page_number,
                        split_native_blocks(inspected_page.text),
                    )
                )
                native_page_count += 1
                continue

            warnings.append(
                f"Page {inspected_page.page_number}: native text was not usable; document recognition was requested."
            )
            rendered = RenderedPage(
                document_id,
                inspected_page.page_number,
                render_pdf_page(
                    content,
                    inspected_page.page_number,
                    self._limits.render_longest_edge,
                ),
            )
            page, page_warnings = await self._process_rendered_page(rendered, mode)
            pages.append(page)
            warnings.extend(page_warnings)

        if native_page_count == inspection.page_count:
            method = ExtractionMethod.NATIVE_PDF
        elif native_page_count:
            method = ExtractionMethod.HYBRID
        else:
            method = ExtractionMethod.DOCUMENT_RECOGNITION
        return pages, warnings, method

    async def _ingest_image(
        self,
        content: bytes,
        document_id: str,
        mode: IngestionMode,
    ) -> tuple[list[DocumentPage], list[str]]:
        image_bytes = normalize_image(
            content,
            self._limits.render_longest_edge,
            self._limits.max_image_pixels,
        )
        page, warnings = await self._process_rendered_page(
            RenderedPage(document_id, 1, image_bytes), mode
        )
        return [page], warnings

    async def _process_rendered_page(
        self,
        rendered_page: RenderedPage,
        mode: IngestionMode,
    ) -> tuple[DocumentPage, list[str]]:
        if mode == IngestionMode.ROUTED:
            if self._region_pipeline is None:
                raise InvalidDocumentError(
                    "Region-aware ingestion is not configured for this service."
                )
            return await self._region_pipeline.process(rendered_page)
        page, warning = await self._recognize_page(rendered_page)
        return page, [warning] if warning else []

    async def _recognize_page(
        self,
        rendered_page: RenderedPage,
    ) -> tuple[DocumentPage, str | None]:
        try:
            recognized = await self._recognizer.recognize_page(rendered_page)
        except DocumentRecognitionError as error:
            warning = f"Page {rendered_page.page_number} [{error.code}]: {error}"
            return DocumentPage(page_number=rendered_page.page_number), warning

        region = build_unified_region(rendered_page, recognized)
        texts = [
            text.strip()
            for text in re.split(r"\n\s*\n", recognized.text.replace("\r\n", "\n"))
            if text.strip()
        ]
        blocks = build_blocks(
            rendered_page.document_id,
            rendered_page.page_number,
            texts,
            recognized.source_type,
        )
        if len(blocks) == 1:
            blocks[0] = DocumentBlock(
                block_id=build_block_id(
                    rendered_page.document_id, rendered_page.page_number, 1
                ),
                text=blocks[0].text,
                source_type=blocks[0].source_type,
                bbox=region.bbox,
                confidence=recognized.confidence,
            )
        return DocumentPage(
            page_number=rendered_page.page_number,
            regions=[region],
            merged_text=recognized.text,
            routing_summary=RoutingSummary(unified=1, unknown=1),
            blocks=blocks,
            full_text=recognized.text,
            layout_markdown=recognized.layout_markdown,
        ), None

    @staticmethod
    def _native_page(
        document_id: str,
        page_number: int,
        texts: list[str],
    ) -> DocumentPage:
        blocks = build_blocks(document_id, page_number, texts, SourceType.NATIVE)
        regions = build_native_regions(document_id, page_number, texts)
        full_text = "\n".join(block.text for block in blocks)
        return DocumentPage(
            page_number=page_number,
            regions=regions,
            merged_text=full_text,
            routing_summary=RoutingSummary(native=len(regions)),
            blocks=blocks,
            full_text=full_text,
        )

    @staticmethod
    def _safe_filename(filename: str) -> str:
        safe_filename = filename.replace("\\", "/").split("/")[-1].strip()
        return (safe_filename or "document")[:255]
