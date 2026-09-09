import json
from collections import defaultdict, deque
from collections.abc import Callable

from app.services.case_analysis.claim_anchored.contracts import BoundClaim, Selection
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure


def assign_ids(claims: tuple[BoundClaim, ...]) -> tuple[BoundClaim, ...]:
    return tuple(
        bound.model_copy(
            update={
                "claim": bound.claim.model_copy(update={"claim_id": f"A-{index:02d}"})
            }
        )
        for index, bound in enumerate(claims, 1)
    )


def select_claims(
    claims: tuple[BoundClaim, ...],
    *,
    source_ids: tuple[str, ...],
    max_claims: int,
    fits: Callable[[tuple[BoundClaim, ...]], bool],
) -> Selection:
    unique = []
    seen = set()
    omissions = []
    source_rank = {value: index for index, value in enumerate(source_ids)}
    for bound in claims:
        signature = json.dumps(
            {
                "claim": bound.claim.model_dump(exclude={"claim_id"}),
                "spans": [span.model_dump() for span in bound.spans],
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        if signature in seen:
            omissions.append(
                {"candidate_id": bound.candidate_id, "reason": "exact_duplicate"}
            )
        else:
            seen.add(signature)
            unique.append(bound)
    unique.sort(
        key=lambda bound: min(
            (source_rank[span.citation.source_message_id], span.start_offset)
            for span in bound.spans
        )
    )
    if len(unique) <= max_claims and fits(assign_ids(tuple(unique))):
        return Selection(assign_ids(tuple(unique)), tuple(omissions))
    required = [
        bound
        for bound in unique
        if (
            bound.claim.claim_type == "unknown"
            or bound.claim.epistemic_status != "reported"
            or bound.claim.contradicting_citations
        )
    ]
    if len(required) > max_claims or not fits(assign_ids(tuple(required))):
        raise ClaimAnchoredFailure(
            "claim_required_budget_exceeded", "Uncertainty claims cannot fit together"
        )
    selected = list(required)
    groups: dict[str, deque[BoundClaim]] = defaultdict(deque)
    required_ids = {bound.candidate_id for bound in required}
    for bound in unique:
        if bound.candidate_id not in required_ids:
            source_id = min(
                (span.citation.source_message_id for span in bound.spans),
                key=source_rank.get,
            )
            groups[source_id].append(bound)
    while any(groups.values()):
        for source_id in source_ids:
            if not groups[source_id]:
                continue
            bound = groups[source_id].popleft()
            if len(selected) < max_claims and fits(
                assign_ids(tuple([*selected, bound]))
            ):
                selected.append(bound)
            else:
                omissions.append(
                    {"candidate_id": bound.candidate_id, "reason": "selection_budget"}
                )
    if not selected:
        raise ClaimAnchoredFailure(
            "claim_selection_empty", "No admitted claim fits generation budget"
        )
    return Selection(assign_ids(tuple(selected)), tuple(omissions))
