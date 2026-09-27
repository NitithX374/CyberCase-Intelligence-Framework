from __future__ import annotations

from dataclasses import dataclass

from app.trace.messages import ChatAnswerUnit, ChatSuggestion
from app.trace.trace import CaseAnalysisTrace


@dataclass(frozen=True)
class CaseAnalysisOutput:
    answer: str
    trace: CaseAnalysisTrace | None
    units: tuple[ChatAnswerUnit, ...] = ()
    suggestion: ChatSuggestion = "none"


__all__ = [
    "CaseAnalysisOutput",
]
