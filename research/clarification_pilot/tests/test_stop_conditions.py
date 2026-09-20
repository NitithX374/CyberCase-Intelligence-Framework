"""The loop is bounded, and it records why it stopped.

Every branch here is a way the loop can end. A stop condition that is never
tested is a stop condition that quietly does not exist, and the failure mode --
an agent that keeps asking -- is exactly what the design forbids.
"""

from __future__ import annotations

import asyncio
import itertools
import json

from clarification_pilot.arms import ArmConfig, run_followup, run_gap_aware
from clarification_pilot.contracts import STOP_REASONS
from clarification_pilot.simulator import SilentSimulator, UserSimulator

from .conftest import make_provider


def run(sample, provider, budget=3, tolerance=2):
    simulator = UserSimulator(provider=provider, hidden=sample.hidden)
    return asyncio.run(
        run_followup(
            sample.candidate,
            provider,
            simulator,
            ArmConfig(budget=budget, unknown_tolerance=tolerance),
        )
    )


def test_sufficient_stops_before_asking_anything(sample):
    provider = make_provider(
        sufficiency=json.dumps({"status": "SUFFICIENT", "reason": "all there", "gaps": []})
    )
    result = run(sample, provider)
    assert result.stop_reason == "sufficient"
    assert result.num_followups == 0
    assert result.asked is False


def test_the_budget_is_never_exceeded(sample):
    """A fresh gap every turn, so only the budget can stop it."""

    counter = itertools.count(1)

    def fresh_gap(_messages):
        index = next(counter)
        return json.dumps(
            {
                "status": "NEED_CLARIFICATION",
                "reason": "more needed",
                "gaps": [{"id": f"gap_{index}", "description": "x", "priority": 0.5}],
            }
        )

    def fresh_question(_messages):
        return json.dumps(
            {"selected_gap_id": f"gap_{next(counter)}", "question": f"question {next(counter)}?"}
        )

    for budget in (1, 2, 3):
        provider = make_provider(sufficiency=fresh_gap, gap_selection=fresh_question)
        result = run(sample, provider, budget=budget)
        assert result.num_followups <= budget
        assert result.stop_reason == "budget_exhausted"
        assert len(result.turns) <= budget + 1


def test_the_same_gap_twice_stops_the_loop(sample):
    """The default script always returns gap_1, which is the repeat case."""

    result = run(sample, make_provider(), budget=3)
    assert result.stop_reason == "repeat_gap"
    assert result.num_followups == 1


def test_the_same_question_under_a_new_gap_id_also_stops(sample):
    ids = itertools.count(1)

    def new_id_same_question(_messages):
        return json.dumps(
            {"selected_gap_id": f"gap_{next(ids)}", "question": "What is the radius?"}
        )

    def always_more(_messages):
        return json.dumps(
            {
                "status": "NEED_CLARIFICATION",
                "reason": "more",
                "gaps": [{"id": "gap_x", "description": "x", "priority": 0.5}],
            }
        )

    result = run(
        sample,
        make_provider(sufficiency=always_more, gap_selection=new_id_same_question),
        budget=3,
    )
    assert result.stop_reason == "repeat_question"


def test_a_simulator_that_keeps_saying_it_does_not_know_stops_the_loop(sample):
    ids = itertools.count(1)

    def always_more(_messages):
        return json.dumps(
            {
                "status": "NEED_CLARIFICATION",
                "reason": "more",
                "gaps": [{"id": "gap_x", "description": "x", "priority": 0.5}],
            }
        )

    def fresh(_messages):
        index = next(ids)
        return json.dumps({"selected_gap_id": f"gap_{index}", "question": f"question {index}?"})

    provider = make_provider(
        sufficiency=always_more,
        gap_selection=fresh,
        simulator=json.dumps({"answer": "I do not know.", "knew": False}),
    )
    result = run(sample, provider, budget=5, tolerance=2)
    assert result.stop_reason == "unknown_information"
    assert result.num_followups == 2


def test_one_unknown_does_not_stop_it(sample):
    """Tolerance is consecutive unknowns, so a single miss is survivable."""

    replies = itertools.cycle(
        [
            json.dumps({"answer": "I do not know.", "knew": False}),
            json.dumps({"answer": "It is 30 meters.", "knew": True}),
        ]
    )
    ids = itertools.count(1)

    provider = make_provider(
        sufficiency=lambda _m: json.dumps(
            {
                "status": "NEED_CLARIFICATION",
                "reason": "more",
                "gaps": [{"id": "gap_x", "description": "x", "priority": 0.5}],
            }
        ),
        gap_selection=lambda _m: json.dumps(
            {"selected_gap_id": f"gap_{next(ids)}", "question": f"question {next(ids)}?"}
        ),
        simulator=lambda _m: next(replies),
    )
    result = run(sample, provider, budget=3, tolerance=2)
    assert result.stop_reason == "budget_exhausted"


def test_unparseable_sufficiency_is_an_error_stop_not_a_crash(sample):
    result = run(sample, make_provider(sufficiency="not json at all"), budget=3)
    assert result.stop_reason == "error"
    assert result.error is not None


def test_an_arm_always_answers_however_it_stopped(sample):
    for provider in (
        make_provider(),
        make_provider(sufficiency="not json"),
        make_provider(simulator=json.dumps({"answer": "no idea", "knew": False})),
    ):
        result = run(sample, provider, budget=2)
        assert result.final_answer, f"stopped at {result.stop_reason} without answering"


def test_gap_aware_reasons_about_gaps_and_still_asks_nothing(sample):
    provider = make_provider()
    result = asyncio.run(
        run_gap_aware(sample.candidate, provider, SilentSimulator(), ArmConfig(budget=3))
    )
    assert result.asked is False
    assert result.num_followups == 0
    assert result.turns[0].decision.status == "NEED_CLARIFICATION"
    assert result.turns[0].decision.gaps, "it should still have found the gap"
    assert result.stop_reason == "budget_exhausted"


def test_every_recorded_stop_reason_is_one_of_the_declared_ones(sample):
    seen = set()
    for provider, budget in (
        (make_provider(sufficiency=json.dumps({"status": "SUFFICIENT", "gaps": []})), 3),
        (make_provider(), 3),
        (make_provider(sufficiency="not json"), 3),
        (make_provider(simulator=json.dumps({"answer": "no", "knew": False})), 2),
    ):
        seen.add(run(sample, provider, budget=budget).stop_reason)
    assert seen <= set(STOP_REASONS)
