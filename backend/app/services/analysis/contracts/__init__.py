from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.services.analysis.contracts.assessment import CaseAssessmentTrace
from app.services.analysis.contracts.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisMode,
    CaseClaimType,
    CaseEpistemicStatus,
    CaseGeneratedUnit,
    CaseSourceCitation,
)
from app.services.analysis.contracts.exchange import (
    CaseFollowupExchange,
    followup_payload,
    followup_qa_id,
)
from app.services.analysis.contracts.trace import (
    CaseAnalysisFailureMetadata,
    CaseAnalysisTrace,
    CaseGroundingReport,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseProviderAnalysis,
    CaseProviderJudgement,
    CaseProviderReading,
    CaseTimelineItem,
)


class CaseAnalysisFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


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
class CaseAnalysisOutput:
    answer: str
    trace: CaseAnalysisTrace | None
    trace_failure: CaseAnalysisFailureMetadata | None = None
    execution_receipt: dict[str, object] | None = None


__all__ = [
    "CaseAnalysisClaim",
    "CaseAnalysisFailure",
    "CaseAnalysisFailureMetadata",
    "CaseAnalysisGap",
    "CaseAnalysisMode",
    "CaseAnalysisOutput",
    "CaseAnalysisTrace",
    "CaseAssessmentTrace",
    "CaseFollowupExchange",
    "CaseGroundingReport",
    "CaseClaimType",
    "CaseEpistemicStatus",
    "CaseSourceCitation",
    "CaseGeneratedUnit",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseProviderJudgement",
    "CaseProviderReading",
    "CaseTimelineItem",
    "ResponseLanguage",
    "followup_payload",
    "followup_qa_id",
    "resolve_response_language",
]
