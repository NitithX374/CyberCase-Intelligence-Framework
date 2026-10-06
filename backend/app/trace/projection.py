from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import TypeVar

from app.trace import nli_model
from app.trace.claims import CaseAnalysisClaim
from app.trace.meaning import MIN_ENTAILMENT, Scorer
from app.trace.nli_model import NliUnavailable
from app.trace.support import item_support
from app.trace.trace import (
    CaseImpactItem,
    CaseInvolvedParty,
    CaseProjectionGrounding,
    CaseTimelineItem,
)

Projection = TypeVar("Projection", CaseInvolvedParty, CaseTimelineItem, CaseImpactItem)
THAI = re.compile(r"[ก-๛]")


def projection_statement(item: CaseInvolvedParty | CaseTimelineItem | CaseImpactItem) -> str:
    if isinstance(item, CaseInvolvedParty):
        if THAI.search(item.name + item.role):
            return f"{item.name} มีบทบาทเป็น{item.role}"
        return f"{item.name} is {item.role}."
    if isinstance(item, CaseTimelineItem):
        if THAI.search(item.time + item.event):
            return f"{item.time}: {item.event}"
        return f"At {item.time}, {item.event}"
    return item.description


class ProjectionValidator:
    def __init__(
        self, claims: Sequence[CaseAnalysisClaim], provider: Callable[[], Scorer] | None = None
    ) -> None:
        self.claims = {claim.claim_id: claim for claim in claims}
        self.provider = provider or nli_model.load_nli
        self.scorer: Scorer | None = None
        self.unavailable: str | None = None
        self.verdicts: dict[tuple[str, str], CaseProjectionGrounding] = {}

    def check(self, item: Projection) -> Projection:
        verdict = self.verdict(item)
        known = [claim_id for claim_id in item.claim_ids if claim_id in self.claims]
        return item.model_copy(
            update={
                "claim_ids": known,
                "support": item_support(known, self.claims),
                "projection_grounding": verdict,
            }
        )

    def verdict(self, item: Projection) -> CaseProjectionGrounding:
        if not item.claim_ids:
            return unassessed("no_claim")
        if any(claim_id not in self.claims for claim_id in item.claim_ids):
            return unassessed("unknown_claim")
        claims = [self.claims[claim_id] for claim_id in item.claim_ids]
        if any(not claim.supporting_citations for claim in claims):
            return unassessed("unbound_claim")
        if any(claim.epistemic_status != "reported" for claim in claims):
            return unassessed("qualified_claim")
        premise = "\n".join(claim.text for claim in claims)
        hypothesis = projection_statement(item)
        key = (premise, hypothesis)
        if key not in self.verdicts:
            self.verdicts[key] = self.judge(premise, hypothesis)
        return self.verdicts[key]

    def judge(self, premise: str, hypothesis: str) -> CaseProjectionGrounding:
        if self.scorer is None and self.unavailable is None:
            try:
                self.scorer = self.provider()
            except NliUnavailable as error:
                self.unavailable = error.reason
        if self.unavailable is not None:
            return unassessed(f"model_unavailable:{self.unavailable}")
        scorer = self.scorer
        assert scorer is not None
        if not scorer.fits(premise, hypothesis):
            return unassessed("context_limit", scorer.name)
        judgement = scorer.judge(premise, hypothesis)
        supported = judgement.label == "entailment" and judgement.entailment >= MIN_ENTAILMENT
        return CaseProjectionGrounding(
            verdict="supported" if supported else "not_supported",
            reason=judgement.label
            if supported or judgement.label != "entailment"
            else "low_entailment",
            model=scorer.name,
            entailment=judgement.entailment,
        )


def unassessed(reason: str, model: str | None = None) -> CaseProjectionGrounding:
    return CaseProjectionGrounding(verdict="unassessed", reason=reason, model=model)


def supported_projection(item: Projection) -> bool:
    return (
        item.projection_grounding is not None and item.projection_grounding.verdict == "supported"
    )


def projection_payload(items: Sequence[Projection]) -> list[dict[str, object]]:
    return [
        item.model_dump(mode="json", exclude={"support", "projection_grounding"})
        for item in items
        if supported_projection(item)
    ]


__all__ = [
    "ProjectionValidator",
    "projection_payload",
    "projection_statement",
    "supported_projection",
]
