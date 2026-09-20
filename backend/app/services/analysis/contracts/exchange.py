"""What the reader was asked, and what they said back.

A follow-up answer is conversation, not a document the case was filed with, so
it is not a case source and nothing about it is versioned. It still has to be
citable: an analysis that cannot quote what the reader told it would report
the answer as an unsupported claim.

So each exchange carries a stable id for the length of one analysis, and is
handed to the citation registry as if it were a source. That costs no rows and
no ``source_revision`` churn — the ids are derived from the same chat messages
the prompt is built from.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class CaseFollowupExchange:
    """One question the analysis asked and, once given, its answer."""

    qa_id: str
    gap_key: str
    question: str
    answer: str | None = None

    @property
    def is_answered(self) -> bool:
        return bool(self.answer and self.answer.strip())


def followup_qa_id(index: int) -> str:
    """``QA-01`` for the first exchange. Matches the A-01/G-01 ids elsewhere."""

    return f"QA-{index:02d}"


def followup_payload(history: Sequence[CaseFollowupExchange]) -> list[dict[str, str]]:
    """The exchanges as the model is shown them. Unanswered ones are left out.

    An outstanding question tells the model nothing it does not already know
    from the gap it came from, and showing it invites an answer to be invented
    for it.
    """

    return [
        {"qa_id": item.qa_id, "question": item.question, "answer": item.answer or ""}
        for item in history
        if item.is_answered
    ]


__all__ = [
    "CaseFollowupExchange",
    "followup_payload",
    "followup_qa_id",
]
