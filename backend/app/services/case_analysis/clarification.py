"""Whether to ask the reader another question, or analyse with what is here.

The model finds the gaps and writes the questions. This decides which of them
is actually put to the reader, and when to stop asking — deterministically, so
that the clarification policy is something you can read rather than something
you have to infer from a transcript.

Nothing here touches the database, calls a model, or reads settings. The bounds
arrive as arguments so an experiment can vary them without a second
implementation of the policy.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Literal

from app.services.case_analysis.contracts import CaseAnalysisGap

# Why the loop stopped asking. Never "sufficient": a spent budget and a
# complete case are different things, and a reader deserves to know which one
# produced the analysis they are reading.
ProceedReason = Literal[
    # Nothing in this analysis was worth asking about.
    "no_eligible_gap",
    # Everything worth asking about has already been asked on this case.
    "gaps_exhausted",
    # The case has had as many rounds of questions as it is allowed.
    "max_rounds_reached",
    # This round has asked its share. Not terminal: the caller analyses again
    # with the answers it now has, and that analysis decides afresh.
    "round_budget_spent",
]

TERMINAL_REASONS: frozenset[str] = frozenset(
    {"no_eligible_gap", "gaps_exhausted", "max_rounds_reached"}
)


@dataclass(frozen=True)
class Ask:
    """Put this gap to the reader."""

    gap: CaseAnalysisGap


@dataclass(frozen=True)
class Proceed:
    """Do not ask. ``reason`` says why, and terminal reasons become stop_reason."""

    reason: ProceedReason

    @property
    def is_terminal(self) -> bool:
        return self.reason in TERMINAL_REASONS


FollowupDecision = Ask | Proceed


def eligible_gaps(
    gaps: Sequence[CaseAnalysisGap], asked_gap_keys: Collection[str]
) -> list[CaseAnalysisGap]:
    """The gaps that could be put to a reader, in the order the analysis wrote them.

    A gap qualifies when the analysis called it high priority, marked it
    askable, and wrote a question for it. Validation has already cleared
    ``askable`` on anything the sources say is unknowable.

    ``asked_gap_keys`` is every key asked on this case, not just this round.
    The keys come from different analyses, so they can drift, but a key that
    does recur names the same gap — and asking it twice wastes a round on
    something the reader has already addressed.
    """

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
    """Ask the next question, or say why there will not be one.

    The order of the checks is the policy. Budget is spent before eligibility
    is considered, so a case that has used its rounds stops for that reason
    rather than for whatever the analysis happened to write last.
    """

    if rounds_spent > max_rounds:
        return Proceed("max_rounds_reached")
    if asked_this_round >= gaps_per_round:
        return Proceed("round_budget_spent")

    candidates = eligible_gaps(gaps, asked_gap_keys)
    if candidates:
        return Ask(candidates[0])

    # Nothing left to ask. Whether that is because the analysis never found
    # anything worth asking, or because the case has been asked it all, is the
    # difference between a complete case and an exhausted one.
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
