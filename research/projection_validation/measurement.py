from __future__ import annotations

import contextvars
from time import perf_counter

from app.trace.nli_model import Judgement, MdebertaNli

SCORER_STAGE = contextvars.ContextVar(
    "projection_evaluation_stage", default="binding_recovery"
)


class MeasuredScorer:
    def __init__(self, scorer: MdebertaNli) -> None:
        self.scorer = scorer
        self.name = scorer.name
        self.calls: list[dict] = []
        self.fit_checks: list[dict] = []

    def fits(self, premise: str, hypothesis: str) -> bool:
        started = perf_counter()
        result = self.scorer.fits(premise, hypothesis)
        self.fit_checks.append(
            {
                "fits": result,
                "seconds": perf_counter() - started,
                "stage": SCORER_STAGE.get(),
            }
        )
        return result

    def judge(self, premise: str, hypothesis: str) -> Judgement:
        started = perf_counter()
        result = self.scorer.judge(premise, hypothesis)
        self.calls.append(
            {
                "label": result.label,
                "entailment": result.entailment,
                "seconds": perf_counter() - started,
                "stage": SCORER_STAGE.get(),
            }
        )
        return result


def validate_reading(case: dict, provider) -> tuple[object, dict]:
    from unittest.mock import patch

    from app.analysis.write import reading_from
    from app.sources.bundle import CaseSourceBundle, CaseSourceItem
    from app.trace.bind import bound_claims
    from app.trace.projection import ProjectionValidator
    from app.trace.trace import CaseProviderReadingReply

    bundle = CaseSourceBundle(
        1, tuple(CaseSourceItem(**row) for row in case["sources"])
    )
    written = reading_from(CaseProviderReadingReply.model_validate(case["reading"]))
    checks = []
    original = ProjectionValidator.check

    def measured_check(validator, item):
        started = perf_counter()
        token = SCORER_STAGE.set("projection")
        try:
            checked = original(validator, item)
        finally:
            SCORER_STAGE.reset(token)
        checks.append(
            {
                "seconds": perf_counter() - started,
                "verdict": checked.projection_grounding.verdict,
            }
        )
        return checked

    started = perf_counter()
    with (
        patch("app.trace.nli_model.load_nli", provider),
        patch.object(ProjectionValidator, "check", measured_check),
    ):
        bound, grounding = bound_claims(written, bundle)
    return bound, {
        "binding_and_validation_seconds": perf_counter() - started,
        "projection_validation_seconds": sum(check["seconds"] for check in checks),
        "projection_checks": checks,
        "grounding": grounding.model_dump(mode="json"),
    }


def checked_items(reading) -> list[tuple[str, int, object]]:
    return [
        (kind, index, item)
        for kind in ("involved_parties", "timeline", "impacts")
        for index, item in enumerate(getattr(reading, kind))
    ]
