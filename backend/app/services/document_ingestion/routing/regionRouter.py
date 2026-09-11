from dataclasses import dataclass

from app.services.document_ingestion.contracts import (
    ContentRole,
    RecognitionMethod,
    RegionType,
    VerificationStatus,
)
from app.services.document_ingestion.segmentation.base import SegmentedRegion


@dataclass(frozen=True)
class RegionRoute:
    recognition_method: RecognitionMethod
    verification_status: VerificationStatus
    content_role: ContentRole
    warning: str | None = None


class RegionRouter:
    def __init__(
        self,
        mixed_policy: str,
        unknown_policy: str,
        htr_enabled: bool = False,
    ) -> None:
        self._mixed_policy = mixed_policy
        self._unknown_policy = unknown_policy
        self._htr_enabled = htr_enabled

    def route(self, region: SegmentedRegion) -> RegionRoute:
        if region.region_type == RegionType.PRINTED_TEXT:
            return self._machine_route(RecognitionMethod.OCR)
        if region.region_type == RegionType.HANDWRITING:
            if self._htr_enabled:
                return self._review_route(RecognitionMethod.HTR)
            return self._disabled_htr_route()
        if region.region_type == RegionType.MIXED_TEXT:
            return self._fallback(self._mixed_policy)
        if region.region_type == RegionType.TABLE:
            if region.contains_handwriting:
                return self._fallback(self._mixed_policy)
            return self._machine_route(RecognitionMethod.OCR)
        if region.region_type in {RegionType.FIGURE, RegionType.SIGNATURE}:
            return RegionRoute(
                recognition_method=RecognitionMethod.NONE,
                verification_status=VerificationStatus.NON_AUTHORITATIVE,
                content_role=ContentRole.NON_TEXT_REGION,
            )
        return self._fallback(self._unknown_policy)

    @staticmethod
    def _machine_route(method: RecognitionMethod) -> RegionRoute:
        return RegionRoute(
            recognition_method=method,
            verification_status=VerificationStatus.MACHINE_READ,
            content_role=ContentRole.TRANSCRIBED_TEXT,
        )

    @staticmethod
    def _review_route(method: RecognitionMethod) -> RegionRoute:
        return RegionRoute(
            recognition_method=method,
            verification_status=VerificationStatus.NEEDS_REVIEW,
            content_role=ContentRole.TRANSCRIBED_TEXT,
        )

    @staticmethod
    def _fallback(policy: str) -> RegionRoute:
        if policy == "unified":
            return RegionRouter._review_route(RecognitionMethod.UNIFIED)
        return RegionRouter._review_route(RecognitionMethod.NONE)

    @staticmethod
    def _disabled_htr_route() -> RegionRoute:
        return RegionRoute(
            recognition_method=RecognitionMethod.NONE,
            verification_status=VerificationStatus.NEEDS_REVIEW,
            content_role=ContentRole.TRANSCRIBED_TEXT,
            warning="HTR is disabled; manual transcription is required.",
        )
