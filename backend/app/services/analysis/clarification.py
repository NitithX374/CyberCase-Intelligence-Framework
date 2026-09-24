from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Literal

from app.services.analysis.contracts import CaseAnalysisGap

ProceedReason = Literal[
    "no_eligible_gap",
    "gaps_exhausted",
    "max_rounds_reached",
    "round_budget_spent",
]

TERMINAL_REASONS: frozenset[str] = frozenset(
    {"no_eligible_gap", "gaps_exhausted", "max_rounds_reached"}
)


@dataclass(frozen=True)
class Ask:
    gap: CaseAnalysisGap


@dataclass(frozen=True)
class Proceed:
    reason: ProceedReason

    @property
    def is_terminal(self) -> bool:
        return self.reason in TERMINAL_REASONS


FollowupDecision = Ask | Proceed


def eligible_gaps(
    gaps: Sequence[CaseAnalysisGap], asked_gap_keys: Collection[str]
) -> list[CaseAnalysisGap]:
    already = set(asked_gap_keys)
    return [
        gap
        for gap in gaps
        if gap.priority == "high"
        and gap.askable
        and gap.clarification_question
        and gap.gap_key not in already
    ]


def decide_followup(
    *,
    gaps: Sequence[CaseAnalysisGap],
    asked_gap_keys: Collection[str],
    asked_this_round: int,
    rounds_spent: int,
    max_rounds: int,
    gaps_per_round: int,
) -> FollowupDecision:
    if rounds_spent > max_rounds:
        return Proceed("max_rounds_reached")
    if asked_this_round >= gaps_per_round:
        return Proceed("round_budget_spent")

    candidates = eligible_gaps(gaps, asked_gap_keys)
    if candidates:
        return Ask(candidates[0])

    ever_eligible = any(
        gap.priority == "high" and gap.askable and gap.clarification_question for gap in gaps
    )
    return Proceed("gaps_exhausted" if ever_eligible else "no_eligible_gap")


__all__ = [
    "Ask",
    "FollowupDecision",
    "Proceed",
    "ProceedReason",
    "TERMINAL_REASONS",
    "decide_followup",
    "eligible_gaps",
]
