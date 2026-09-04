from fastapi import APIRouter, File, Header, HTTPException, Query, UploadFile, status

from app.config import settings
from app.services.document_ingestion import (
    DocumentIngestionError,
    DocumentIngestionLimits,
    DocumentIngestionService,
    IngestedDocument,
)
from app.services.document_ingestion.contracts import IngestionMode
from app.services.document_ingestion.recognition import DocumentRecognizer
from app.services.document_ingestion.recognition.htr import ReviewRequiredHTRRecognizer
from app.services.document_ingestion.recognition.typhoon import (
    TyphoonDocumentRecognizer,
    TyphoonRecognizerConfig,
)
from app.services.document_ingestion.region_pipeline import RegionRecognitionPipeline
from app.services.document_ingestion.routing import RegionRouter
from app.services.document_ingestion.segmentation import WholePageRegionSegmenter

router = APIRouter(prefix="/document-ingestion", tags=["document-ingestion"])


def _build_recognizer() -> DocumentRecognizer:
    if settings.document_recognizer == "google_vision":
        from app.services.document_ingestion.recognition.google_vision import (
            GoogleVisionDocumentRecognizer,
        )

        return GoogleVisionDocumentRecognizer(
            timeout_seconds=settings.document_recognition_timeout_seconds
        )
    if settings.document_recognizer == "typhoon":
        return TyphoonDocumentRecognizer(
            TyphoonRecognizerConfig(
                api_key=settings.typhoon_ocr_api_key,
                base_url=settings.typhoon_ocr_base_url,
                model=settings.typhoon_ocr_model,
                timeout_seconds=settings.document_recognition_timeout_seconds,
                target_image_dimension=settings.document_ingestion_render_longest_edge,
            )
        )
    raise RuntimeError(
        f"Unsupported document recognizer: {settings.document_recognizer}"
    )


def _build_region_pipeline(recognizer) -> RegionRecognitionPipeline:
    return RegionRecognitionPipeline(
        segmenter=WholePageRegionSegmenter(),
        router=RegionRouter(
            mixed_policy=settings.document_mixed_region_policy,
            unknown_policy=settings.document_unknown_region_policy,
            htr_enabled=False,
        ),
        ocr_recognizer=recognizer,
        htr_recognizer=ReviewRequiredHTRRecognizer(),
    )


def _build_service() -> DocumentIngestionService:
    limits = DocumentIngestionLimits(
        max_bytes=settings.document_ingestion_max_bytes,
        max_pages=settings.document_ingestion_max_pages,
        max_image_pixels=settings.document_ingestion_max_image_pixels,
        render_longest_edge=settings.document_ingestion_render_longest_edge,
    )
    recognizer = _build_recognizer()
    return DocumentIngestionService(
        recognizer,
        limits,
        region_pipeline=_build_region_pipeline(recognizer),
    )


async def _read_limited(upload: UploadFile, max_bytes: int) -> bytes:
    chunks = []
    total_bytes = 0
    while chunk := await upload.read(1024 * 1024):
        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail={
                    "code": "document_size_limit_exceeded",
                    "message": f"The document exceeds the {max_bytes}-byte ingestion limit.",
                },
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post(
    "/preview",
    response_model=IngestedDocument,
    status_code=status.HTTP_200_OK,
)
async def preview_document_ingestion(
    file: UploadFile = File(...),
    mode: IngestionMode = Query(default=IngestionMode.UNIFIED),
    segmentation: bool | None = Query(default=None),
    case_key: str | None = Query(default=None),
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
    x_case_key: str | None = Header(default=None, alias="X-Case-Key"),
) -> IngestedDocument:
    content = await _read_limited(file, settings.document_ingestion_max_bytes)
    selected_mode = mode
    if segmentation is not None:
        selected_mode = IngestionMode.ROUTED if segmentation else IngestionMode.UNIFIED
    try:
        return await _build_service().ingest(
            content,
            file.filename or "document",
            selected_mode,
        )
    except DocumentIngestionError as error:
        status_code = (
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            if error.code == "unsupported_document_type"
            else status.HTTP_413_CONTENT_TOO_LARGE
            if error.code.endswith("limit_exceeded")
            else status.HTTP_422_UNPROCESSABLE_CONTENT
        )
        raise HTTPException(
            status_code=status_code,
            detail={"code": error.code, "message": error.message},
        ) from error
