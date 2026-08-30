from app.services.document_ingestion.contracts import (
    RecognitionMethod,
    VerificationStatus,
)
from app.services.document_ingestion.recognition.base import (
    RecognitionResult,
    RenderedRegion,
)


class ReviewRequiredHTRRecognizer:
    async def recognize(self, region: RenderedRegion) -> RecognitionResult:
        return RecognitionResult(
            text="",
            recognition_method=RecognitionMethod.HTR,
            recognizer="review_required",
            verification_status=VerificationStatus.NEEDS_REVIEW,
            warning=(
                f"Page {region.page_number} region {region.region_id}: no verified "
                "Thai HTR provider is configured; manual transcription is required."
            ),
        )
