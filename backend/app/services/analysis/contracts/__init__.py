from __future__ import annotations

from dataclasses import dataclass

from app.errors import AppError
from app.services.analysis.contracts.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisMode,
    CaseAssessmentTrace,
    CaseClaimType,
    CaseEpistemicStatus,
    CaseFollowupExchange,
    CaseProviderCitation,
    CaseProviderClaim,
    CaseSourceCitation,
    ChatAnswerUnit,
    ChatSuggestion,
    ChatUnitBasis,
    followup_history_of_snapshot,
    followup_payload,
    followup_qa_id,
    followup_snapshot,
)
from app.services.analysis.contracts.trace import (
    CaseAnalysisTrace,
    CaseGroundingReport,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseProviderAnalysis,
    CaseTimelineItem,
)


class CaseAnalysisFailure(AppError):
    pass


@dataclass(frozen=True)
class CaseAnalysisOutput:
    answer: str
    trace: CaseAnalysisTrace | None
    units: tuple[ChatAnswerUnit, ...] = ()
    suggestion: ChatSuggestion = "none"


__all__ = [
    "CaseAnalysisClaim",
    "CaseAnalysisFailure",
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
    "ChatAnswerUnit",
    "ChatSuggestion",
    "ChatUnitBasis",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseProviderCitation",
    "CaseProviderClaim",
    "CaseTimelineItem",
    "followup_history_of_snapshot",
    "followup_payload",
    "followup_qa_id",
    "followup_snapshot",
]
