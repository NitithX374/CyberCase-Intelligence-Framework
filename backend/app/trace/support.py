from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypeVar

from app.trace.claims import CaseAnalysisClaim
from app.trace.trace import CaseImpactItem, CaseInvolvedParty, CaseTimelineItem, SupportStatus

Projection = TypeVar("Projection", CaseInvolvedParty, CaseTimelineItem, CaseImpactItem)


def item_support(
    claim_ids: Sequence[str], claims_by_id: Mapping[str, CaseAnalysisClaim]
) -> SupportStatus:
    named = [claims_by_id[claim_id] for claim_id in claim_ids if claim_id in claims_by_id]
    if not named:
        return "no_claim"
    bound = [bool(claim.supporting_citations) for claim in named]
    if all(bound):
        return "bound"
    return "mixed" if any(bound) else "unbound"


def with_support(item: Projection, claims_by_id: Mapping[str, CaseAnalysisClaim]) -> Projection:
    return item.model_copy(update={"support": item_support(item.claim_ids, claims_by_id)})
