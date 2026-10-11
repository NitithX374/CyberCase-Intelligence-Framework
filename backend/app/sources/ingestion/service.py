import asyncio
from dataclasses import dataclass

from fastapi import UploadFile, status

from app.config import settings
from app.sources.ingestion.contracts import (
    DocumentIngestionError,
    DocumentLimitError,
    DocumentPage,
    DocumentRecognitionError,
    ExtractionMethod,
    IngestedDocument,
    InvalidDocumentError,
    RecognitionConfigurationError,
    RecognitionProviderError,
    RecognitionTimeoutError,
    strip_unstorable,
)
from app.sources.ingestion.files import (
    DocumentKind,
    detect_document,
    normalize_image,
    pdf_page_count,
    render_pdf_page,
)
from app.sources.ingestion.parsers import parse_docx
from app.sources.ingestion.recognition import DocumentRecognizer, RenderedPage


@dataclass(frozen=True)
class DocumentIngestionLimits:
    max_bytes: int
    max_pages: int
    max_image_pixels: int
    render_longest_edge: int
    max_concurrent_ocr: int = 4


class DocumentIngestionService:
    def __init__(self, recognizer: DocumentRecognizer, limits: DocumentIngestionLimits) -> None:
        self._recognizer = recognizer
        self._limits = limits

    async def aclose(self) -> None:
        if hasattr(self._recognizer, "aclose"):
            await self._recognizer.aclose()

    async def ingest(
        self,
        content: bytes,
        filename: str,
    ) -> IngestedDocument:
        self.validate_content(content)
        detected = detect_document(content)
        safe_filename = self.safe_filename(filename)

        failures: list[DocumentRecognitionError] = []
        method = ExtractionMethod.DOCUMENT_RECOGNITION
        if detected.kind == DocumentKind.DOCX:
            pages, warnings = await asyncio.to_thread(parse_docx, content)
            method = ExtractionMethod.NATIVE_DOCX
        elif detected.kind == DocumentKind.PDF:
            pages, warnings, failures = await self.ingest_pdf(content)
        else:
            pages, warnings, failures = await self.ingest_image(content)

        full_text = "\n\n".join(page.text for page in pages if page.text)
        if not full_text and failures:
            raise unreadable_document(failures[0])
        return IngestedDocument(
            filename=safe_filename,
            media_type=detected.media_type,
            extraction_method=method,
            pages=pages,
            full_text=full_text,
            warnings=warnings,
        )

    def validate_content(self, content: bytes) -> None:
        if not content:
            raise InvalidDocumentError("The uploaded document is empty.")
        if len(content) > self._limits.max_bytes:
            raise DocumentLimitError(
                "document_size_limit_exceeded",
                f"The document exceeds the {self._limits.max_bytes}-byte ingestion limit.",
            )

    async def ingest_pdf(
        self,
        content: bytes,
    ) -> tuple[list[DocumentPage], list[str], list[DocumentRecognitionError]]:
        page_count = await asyncio.to_thread(pdf_page_count, content, self._limits.max_pages)
        semaphore = asyncio.Semaphore(self._limits.max_concurrent_ocr)

        async def process_page(
            page_number: int,
        ) -> tuple[DocumentPage, list[str], DocumentRecognitionError | None]:
            async with semaphore:
                image_bytes = await asyncio.to_thread(
                    render_pdf_page,
                    content,
                    page_number,
                    self._limits.render_longest_edge,
                )
                return await self.process_rendered_page(RenderedPage(page_number, image_bytes))

        results = await asyncio.gather(
            *(process_page(number) for number in range(1, page_count + 1))
        )

        pages = [page for page, _, _ in results]
        warnings = [warning for _, page_warnings, _ in results for warning in page_warnings]
        failures = [failure for _, _, failure in results if failure is not None]
        return pages, warnings, failures

    async def ingest_image(
        self,
        content: bytes,
    ) -> tuple[list[DocumentPage], list[str], list[DocumentRecognitionError]]:
        image_bytes = await asyncio.to_thread(
            normalize_image,
            content,
            self._limits.render_longest_edge,
            self._limits.max_image_pixels,
        )
        page, warnings, failure = await self.process_rendered_page(RenderedPage(1, image_bytes))
        return [page], warnings, [failure] if failure else []

    async def process_rendered_page(
        self,
        rendered_page: RenderedPage,
    ) -> tuple[DocumentPage, list[str], DocumentRecognitionError | None]:
        try:
            recognized = await self._recognizer.recognize_page(rendered_page)
            return (
                DocumentPage(
                    page_number=rendered_page.page_number,
                    text=recognized.text,
                    text_method="ocr",
                    verification_status="machine_read",
                ),
                [],
                None,
            )
        except DocumentRecognitionError as error:
            warning = f"Page {rendered_page.page_number} [{error.code}]: {error}"
            return (
                DocumentPage(
                    page_number=rendered_page.page_number,
                    text="",
                    text_method="ocr",
                    verification_status="needs_review",
                ),
                [warning],
                error,
            )

    @staticmethod
    def safe_filename(filename: str) -> str:
        safe_filename = strip_unstorable(filename).replace("\\", "/").split("/")[-1].strip()
        return (safe_filename or "document")[:255]


RECOGNITION_FAILURE_STATUS: dict[type[DocumentRecognitionError], int] = {
    RecognitionConfigurationError: status.HTTP_503_SERVICE_UNAVAILABLE,
    RecognitionProviderError: status.HTTP_502_BAD_GATEWAY,
    RecognitionTimeoutError: status.HTTP_504_GATEWAY_TIMEOUT,
}


def unreadable_document(failure: DocumentRecognitionError) -> DocumentIngestionError:
    return DocumentIngestionError(
        failure.code, str(failure), RECOGNITION_FAILURE_STATUS.get(type(failure))
    )


def build_document_recognizer() -> DocumentRecognizer:
    from app.sources.ingestion.recognition import TyphoonDocumentRecognizer, TyphoonRecognizerConfig

    return TyphoonDocumentRecognizer(
        TyphoonRecognizerConfig(
            api_key=settings.typhoon_api_key,
            base_url=settings.typhoon_ocr_base_url,
            model=settings.typhoon_ocr_model,
            timeout_seconds=settings.document_recognition_timeout_seconds,
            target_image_dimension=settings.document_ingestion_render_longest_edge,
            max_retries=settings.document_recognition_max_retries,
            retry_delay_seconds=settings.document_recognition_retry_delay_seconds,
        )
    )


def build_document_ingestion_service() -> DocumentIngestionService:
    return DocumentIngestionService(
        build_document_recognizer(),
        DocumentIngestionLimits(
            max_bytes=settings.document_ingestion_max_bytes,
            max_pages=settings.document_ingestion_max_pages,
            max_image_pixels=settings.document_ingestion_max_image_pixels,
            render_longest_edge=settings.document_ingestion_render_longest_edge,
            max_concurrent_ocr=settings.document_ingestion_max_concurrent_ocr,
        ),
    )


async def read_limited(upload: UploadFile) -> bytes:
    chunks = []
    total_bytes = 0
    while chunk := await upload.read(1024 * 1024):
        total_bytes += len(chunk)
        if total_bytes > settings.document_ingestion_max_bytes:
            raise DocumentLimitError(
                "document_size_limit_exceeded",
                f"The document exceeds the {settings.document_ingestion_max_bytes}-byte ingestion limit.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


__all__ = [
    "DocumentIngestionLimits",
    "DocumentIngestionService",
    "build_document_ingestion_service",
    "build_document_recognizer",
    "read_limited",
]
