from __future__ import annotations

from copy import deepcopy

from app.analysis.write import judgement_request
from app.trace.projection import projection_statement
from app.trace.trace import CaseProviderReading

from research.projection_validation.measurement import validate_reading
from research.projection_validation.runtime import digest

KINDS = ("involved_parties", "timeline", "impacts")


def replay_input(case: dict, plan: dict, grounded: dict, provider=None) -> dict:
    frozen = deepcopy(case)
    frozen["reading"] = {
        **case["reading"],
        **{
            kind: [
                case["reading"][kind][
                    plan["target_index"]
                    if kind == plan["type"] and plan["target_index"] is not None
                    else 0
                ]
            ]
            for kind in KINDS
        },
    }
    if "claim_override" in plan:
        for claim in frozen["reading"]["claims"]:
            if claim["claim_id"] in plan["claim_override"]:
                claim["text"] = plan["claim_override"][claim["claim_id"]]
        assert provider is not None
        checked, receipt = validate_reading(frozen, provider)
    else:
        full = CaseProviderReading.model_validate(grounded["reading"])
        checked = full.model_copy(
            update={
                kind: [
                    getattr(full, kind)[
                        plan["target_index"] if kind == plan["type"] else 0
                    ]
                ]
                for kind in KINDS
            }
        )
        receipt = {
            "validation": "Reused identical production verdicts for the exact same premise/hypothesis; no additional verifier invocation."
        }
    proposed = judgement_request(checked, case["language"], ())
    baseline = deepcopy(proposed)
    for kind in KINDS:
        baseline["reading"][kind] = [
            item.model_dump(mode="json", exclude={"support", "projection_grounding"})
            for item in getattr(checked, kind)
        ]
    assert digest(baseline["reading"]["claims"]) == digest(
        proposed["reading"]["claims"]
    )
    assert all(
        baseline[key] == proposed[key]
        for key in ("response_language", "followup_history")
    )
    target = getattr(checked, plan["type"])[0]
    if plan["error_scope"] == "claim_level":
        from app.trace.trace import CaseInvolvedParty

        target_statement = projection_statement(
            CaseInvolvedParty.model_validate(plan["target"])
        )
    else:
        target_statement = projection_statement(target)
    return {
        **plan,
        "language": case["language"],
        "frozen_reading": frozen["reading"],
        "frozen_reading_sha256": digest(frozen["reading"]),
        "checked_reading": checked.model_dump(mode="json"),
        "claims_sha256": digest(proposed["reading"]["claims"]),
        "target_statement": target_statement,
        "target_grounding": target.projection_grounding.model_dump(mode="json"),
        "target_admitted": {
            "no_validation": plan["error_scope"] != "claim_level",
            "semantic": plan["error_scope"] != "claim_level"
            and bool(proposed["reading"][plan["type"]]),
        },
        "projection_counts": {
            "total": 3,
            "supported": sum(
                item.projection_grounding.verdict == "supported"
                for kind in KINDS
                for item in getattr(checked, kind)
            ),
            "not_supported": sum(
                item.projection_grounding.verdict == "not_supported"
                for kind in KINDS
                for item in getattr(checked, kind)
            ),
            "unassessed": sum(
                item.projection_grounding.verdict == "unassessed"
                for kind in KINDS
                for item in getattr(checked, kind)
            ),
            "admitted": sum(len(proposed["reading"][kind]) for kind in KINDS),
            "withheld": 3 - sum(len(proposed["reading"][kind]) for kind in KINDS),
        },
        "validation_receipt": receipt,
        "conditions": {"no_validation": baseline, "semantic": proposed},
    }
