from __future__ import annotations

from collections.abc import Callable, Sequence

from app.trace.b1_verifier import ClaimVerification, supported_probability
from app.trace.nli_model import Judgement, NliProbabilities

NEUTRAL = Judgement(label="neutral", entailment=0.1)


class FakeNli:
    name = "fake-nli"

    def __init__(
        self,
        judge: Callable[[str, str], Judgement] | None = None,
        fits: Callable[[str, str], bool] | None = None,
    ) -> None:
        self.rule = judge or (lambda premise, hypothesis: NEUTRAL)
        self.room = fits or (lambda premise, hypothesis: True)
        self.judged: list[tuple[str, str]] = []

    def fits(self, premise: str, hypothesis: str) -> bool:
        return self.room(premise, hypothesis)

    def judge(self, premise: str, hypothesis: str) -> Judgement:
        self.judged.append((premise, hypothesis))
        return self.rule(premise, hypothesis)

    def verify(self, claim: str, units: Sequence[str]) -> ClaimVerification:
        premise = "\n".join(units)
        result = self.judge(premise, claim)
        neutral = 0 if result.label == "contradiction" else 1 - result.entailment
        contradiction = 1 - result.entailment if result.label == "contradiction" else 0
        nli = NliProbabilities(
            result.entailment, neutral, contradiction, 20, not self.fits(premise, claim)
        )
        return ClaimVerification(
            nli,
            supported_probability(nli.vector),
            tuple(range(len(units))),
            tuple(1.0 for _ in units),
            0,
        )


def entailing(*fragments: str, probability: float = 0.9) -> FakeNli:
    def rule(premise: str, hypothesis: str) -> Judgement:
        if any(fragment in premise for fragment in fragments):
            return Judgement(label="entailment", entailment=probability)
        return NEUTRAL

    return FakeNli(judge=rule)
