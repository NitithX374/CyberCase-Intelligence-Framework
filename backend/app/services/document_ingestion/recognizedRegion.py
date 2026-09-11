from app.services.document_ingestion.contracts import (
    BoundingBox,
    ContentRole,
    DocumentRegion,
    RecognitionCandidate,
    RecognitionMethod,
    RecognizedContent,
    RegionType,
    VerificationStatus,
)
from app.services.document_ingestion.provenance import build_region_id
from app.services.document_ingestion.recognition.base import (
    RecognizedPage,
    RenderedPage,
)
from app.services.document_ingestion.rendering import image_dimensions


def build_unified_region(
    page: RenderedPage, recognized: RecognizedPage
) -> DocumentRegion:
    width, height = image_dimensions(page.image_bytes)
    generated = [
        RecognizedContent(
            text=description,
            content_role=ContentRole.GENERATED_VISUAL_DESCRIPTION,
            verification_status=VerificationStatus.NON_AUTHORITATIVE,
        )
        for description in recognized.generated_visual_descriptions
    ]
    candidate = RecognitionCandidate(
        recognition_method=RecognitionMethod.UNIFIED,
        recognizer=recognized.recognizer,
        text=recognized.text,
        confidence=recognized.confidence,
        words=recognized.words,
        content_role=ContentRole.TRANSCRIBED_TEXT,
        verification_status=VerificationStatus.MACHINE_READ,
    )
    return DocumentRegion(
        region_id=build_region_id(page.document_id, page.page_number, 1),
        page_number=page.page_number,
        bbox=BoundingBox(x0=0, y0=0, x1=width, y1=height),
        region_type=RegionType.UNKNOWN,
        recognition_method=RecognitionMethod.UNIFIED,
        recognizer=recognized.recognizer,
        text=recognized.text,
        recognition_confidence=recognized.confidence,
        words=recognized.words,
        verification_status=VerificationStatus.MACHINE_READ,
        content_role=ContentRole.TRANSCRIBED_TEXT,
        candidates=[candidate],
        selected_candidate_index=0,
        generated_contents=generated,
    )
