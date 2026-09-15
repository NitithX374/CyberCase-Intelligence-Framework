from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from app.services.case_analysis.analysisEvidenceContracts import (
    CaseEvidenceSource,
    CaseAnalysisMode,
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseClaimType,
    CaseEvidenceCitation,
    CaseEpistemicStatus,
    CaseGeneratedUnit,
)
from app.services.case_analysis.analysisTraceContracts import (
    CaseAnalysisFailureMetadata,
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseProviderAnalysis,
    CaseProviderMitreMapping,
    CaseTimelineItem,
)


class CaseAnalysisFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def build_case_source_registry(
    context: Mapping[str, object],
) -> tuple[CaseEvidenceSource, ...]:
    ids = context.get("source_ids")
    texts = context.get("_source_text_by_source_id")
    if (
        not isinstance(ids, list)
        or not ids
        or not all(isinstance(value, str) and value.strip() for value in ids)
        or len(ids) != len(set(ids))
        or not isinstance(texts, Mapping)
        or set(ids) != set(texts)
    ):
        raise CaseAnalysisFailure("case_sources_invalid", "Case evidence source registry is invalid")
    sources: list[CaseEvidenceSource] = []
    for source_id in ids:
        content = texts[source_id]
        if not isinstance(content, str) or not content.strip():
            raise CaseAnalysisFailure("case_source_empty", "Case evidence source text is empty")
        sources.append(CaseEvidenceSource(source_id=source_id, content=content))
    return tuple(sources)


ResponseLanguage = Literal["thai", "english"]
def resolve_response_language(user_message: object) -> ResponseLanguage:
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("User message must be a non-empty string")
    if any("\u0e00" <= character <= "\u0e7f" for character in user_message):
        return "thai"
    if any(character.isascii() and character.isalpha() for character in user_message):
        return "english"
    raise ValueError("User message language must be Thai or English")


@dataclass(frozen=True)
class CaseAnalysisResult:
    answer: str
    trace: CaseAnalysisTrace | None
    trace_failure: CaseAnalysisFailureMetadata | None = None
    execution_receipt: dict[str, object] | None = None
    followup_question: str | None = None
    followup_metadata: dict[str, object] | None = None


__all__ = [
    "CaseEvidenceSource",
    "CaseAnalysisClaim",
    "CaseAnalysisFailure",
    "CaseAnalysisFailureMetadata",
    "CaseAnalysisGap",
    "CaseAnalysisMode",
    "CaseAnalysisResult",
    "CaseAnalysisTrace",
    "CaseClaimType",
    "CaseEpistemicStatus",
    "CaseEvidenceCitation",
    "CaseGeneratedUnit",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseProviderMitreMapping",
    "CaseTimelineItem",
    "ResponseLanguage",
    "build_case_source_registry",
    "resolve_response_language",
]
