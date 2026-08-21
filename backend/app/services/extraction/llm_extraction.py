import httpx

from app.services.llm.core_llm import resolve_core_llm_target

from app.services.extraction.extraction_config import *
from app.services.extraction.extraction_contracts import *
from app.services.extraction.extraction_results import ExtractionRunResult
from app.services.extraction.extraction_adapter import AnthropicExtractionAdapter
from app.services.extraction.extraction_input import build_extraction_input
from app.services.extraction.extraction_normalizer import normalize_case_state
from app.services.extraction.extraction_runner import run_baseline_extraction
from app.services.extraction.extraction_utils import (
    contains_secret_or_prompt_text,
    normalize_model_response,
    safe_retained_response,
)
from app.services.extraction.extraction_utils import (
    safe_retained_response as _safe_retained_response,
)
from app.services.extraction.extraction_validation import validate_baseline_extraction


__all__ = [
    "ACCEPTED_BASELINE_EXTRACTION_PROMPT_VERSIONS",
    "AnthropicExtractionAdapter",
    "EXTRACTION_METADATA_KEY",
    "LEGACY_BASELINE_EXTRACTION_VERSION",
    "BASELINE_EXTRACTION_MODE",
    "BASELINE_EXTRACTION_PROMPT_VERSION",
    "BASELINE_EXTRACTION_SYSTEM_PROMPT",
    "BASELINE_EXTRACTION_VERSION",
    "BaselineExtraction",
    "CaseState",
    "LegacyBaselineExtractionV1",
    "Confidence",
    "ExtractedEntity",
    "ExtractedEvidence",
    "ExtractedFact",
    "ExtractedImpact",
    "ExtractedMissingInformation",
    "ExtractedRelationship",
    "ExtractedTimelineEvent",
    "ExtractionFailure",
    "ExtractionInput",
    "ExtractionModelAdapter",
    "ExtractionModelResponse",
    "ExtractionRunResult",
    "ExtractionSourceMessage",
    "ExtractionValidationError",
    "FactCategory",
    "FactStatus",
    "ImpactStatus",
    "MissingImportance",
    "RelationshipStatus",
    "ReportedStatus",
    "build_extraction_input",
    "normalize_case_state",
    "run_baseline_extraction",
    "validate_baseline_extraction",
]
