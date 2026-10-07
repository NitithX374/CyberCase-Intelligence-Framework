from __future__ import annotations

from collections import Counter

from app.trace.nli_model import NliUnavailable
from app.trace.projection import ProjectionValidator, projection_statement
from app.trace.trace import CaseInvolvedParty

from research.projection_validation.measurement import checked_items, validate_reading
from research.projection_validation.metrics import percentile, ratio


def evaluate_cases(
    cases: list[dict], provider, measured=None
) -> tuple[list[dict], list[dict], list[dict]]:
    rows, receipts, readings = [], [], []
    for case in cases:
        before_calls = len(measured.calls) if measured else 0
        before_fits = len(measured.fit_checks) if measured else 0
        bound, receipt = validate_reading(case, provider)
        items = checked_items(bound)
        assert len(items) == len(case["annotations"])
        claims = {claim.claim_id: claim for claim in bound.claims}
        for (kind, index, item), annotation, timing in zip(
            items, case["annotations"], receipt["projection_checks"], strict=True
        ):
            assert (kind, index) == (annotation["type"], annotation["index"])
            written = case["reading"][kind][index]
            known_links = bool(written["claim_ids"]) and all(
                claim_id in claims for claim_id in written["claim_ids"]
            )
            rows.append(
                {
                    **annotation,
                    "case_id": case["case_id"],
                    "family_id": case["family_id"],
                    "origin": case["origin"],
                    "language": case["language"],
                    "projection": written,
                    "hypothesis": projection_statement(item),
                    "premise": "\n".join(
                        claims[claim_id].text for claim_id in item.claim_ids
                    ),
                    "linked_epistemic_status": [
                        claims[claim_id].epistemic_status for claim_id in item.claim_ids
                    ],
                    "binding_support": item.support,
                    "grounding": item.projection_grounding.model_dump(mode="json"),
                    "predictions": {
                        "no_validation": "supported",
                        "claim_link": "supported" if known_links else "not_supported",
                        "semantic": item.projection_grounding.verdict,
                    },
                    "validation_seconds": timing["seconds"],
                }
            )
        receipts.append(
            {
                "case_id": case["case_id"],
                "projections": len(items),
                **receipt,
                "verifier_calls": sum(
                    call["stage"] == "projection"
                    for call in measured.calls[before_calls:]
                )
                if measured
                else 0,
                "binding_recovery_verifier_calls": sum(
                    call["stage"] != "projection"
                    for call in measured.calls[before_calls:]
                )
                if measured
                else 0,
                "fit_checks": sum(
                    call["stage"] == "projection"
                    for call in measured.fit_checks[before_fits:]
                )
                if measured
                else 0,
            }
        )
        readings.append(
            {
                "case_id": case["case_id"],
                "reading": bound.model_dump(mode="json"),
                "receipt": receipts[-1],
            }
        )
        print(
            case["case_id"],
            dict(Counter(item.projection_grounding.verdict for _, _, item in items)),
            flush=True,
        )
    return rows, receipts, readings


def cost_metrics(rows: list[dict], receipts: list[dict], measured) -> dict:
    cases = [row["projection_validation_seconds"] for row in receipts]
    projections = [row["validation_seconds"] for row in rows]
    return {
        "cases": len(receipts),
        "projections": len(rows),
        "verifier_calls": sum(row["verifier_calls"] for row in receipts),
        "verifier_calls_per_case": sum(row["verifier_calls"] for row in receipts)
        / len(receipts),
        "mean_validation_seconds_per_case": sum(cases) / len(cases),
        "p95_validation_seconds_per_case": percentile(cases, 0.95),
        "mean_validation_seconds_per_projection": sum(projections) / len(projections),
        "p95_validation_seconds_per_projection": percentile(projections, 0.95),
        "mean_inference_seconds": ratio(
            sum(
                call["seconds"]
                for call in measured.calls
                if call["stage"] == "projection"
            ),
            sum(call["stage"] == "projection" for call in measured.calls),
        )
        if measured
        else None,
        "fit_checks": sum(row["fit_checks"] for row in receipts),
        "unassessed_reasons": dict(
            Counter(
                row["grounding"]["reason"]
                for row in rows
                if row["grounding"]["verdict"] == "unassessed"
            )
        ),
        "unassessed_rate_all_rows": sum(
            row["grounding"]["verdict"] == "unassessed" for row in rows
        )
        / len(rows),
        "model_load_excluded": True,
    }


def eligibility_diagnostics(claim, scorer) -> list[dict]:
    party = CaseInvolvedParty(name="John", role="a witness", claim_ids=[claim.claim_id])

    def unavailable():
        raise NliUnavailable("evaluation_injected_unavailable")

    tests = (
        (
            "no_claim",
            [claim],
            party.model_copy(update={"claim_ids": []}),
            lambda: scorer,
        ),
        (
            "unknown_claim",
            [claim],
            party.model_copy(update={"claim_ids": ["A-99"]}),
            lambda: scorer,
        ),
        (
            "unbound_claim",
            [claim.model_copy(update={"supporting_citations": []})],
            party,
            lambda: scorer,
        ),
        (
            "qualified_claim",
            [claim.model_copy(update={"epistemic_status": "suspected"})],
            party,
            lambda: scorer,
        ),
        (
            "context_limit",
            [
                claim.model_copy(
                    update={
                        "text": "John is a witness and reported the incident. " * 80
                    }
                )
            ],
            party,
            lambda: scorer,
        ),
        (
            "model_unavailable:evaluation_injected_unavailable",
            [claim],
            party,
            unavailable,
        ),
    )
    output = []
    for reason, claims, projection, provider in tests:
        verdict = (
            ProjectionValidator(claims, provider).check(projection).projection_grounding
        )
        assert verdict.verdict == "unassessed" and verdict.reason == reason, verdict
        output.append(
            {"expected": reason, "grounding": verdict.model_dump(mode="json")}
        )
    validator = ProjectionValidator([claim], lambda: scorer)
    validator.check(party)
    calls = len(scorer.calls)
    validator.check(party)
    assert len(scorer.calls) == calls
    output.append({"cache_repeat": "same premise/hypothesis judged once"})
    return output
