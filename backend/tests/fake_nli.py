from __future__ import annotations

from collections.abc import Callable

from app.trace.nli_model import Judgement

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


def entailing(*fragments: str, probability: float = 0.9) -> FakeNli:
    def rule(premise: str, hypothesis: str) -> Judgement:
        if any(fragment in premise for fragment in fragments):
            return Judgement(label="entailment", entailment=probability)
        return NEUTRAL

    return FakeNli(judge=rule)
