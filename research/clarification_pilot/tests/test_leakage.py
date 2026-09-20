"""The boundary the whole experiment rests on.

If the candidate can see the rubric, the full question or the gold answer, every
number the harness produces is meaningless -- and the failure is silent, because
a leaking run looks like a very good one. These tests are the only thing
standing between that and a published table.
"""

from __future__ import annotations

import asyncio
import dataclasses

import pytest

from clarification_pilot import prompts
from clarification_pilot.arms import ARMS, ArmConfig
from clarification_pilot.contracts import CandidateView, HiddenContext
from clarification_pilot.simulator import SilentSimulator, UserSimulator

from .conftest import FULL_TASK, GOLD_ANSWER, HIDDEN_SUMMARY, REQUIRED_POINT, make_provider

SECRETS = (GOLD_ANSWER, FULL_TASK, HIDDEN_SUMMARY, REQUIRED_POINT)


def test_candidate_view_carries_nothing_hidden():
    """The type the arms are given has two fields, and neither is a secret."""

    fields = {field.name for field in dataclasses.fields(CandidateView)}
    assert fields == {"sample_id", "initial_input"}

    hidden_fields = {field.name for field in dataclasses.fields(HiddenContext)}
    assert {"gold_answer", "required_points", "full_input", "hidden_summary"} <= hidden_fields
    assert not (fields & hidden_fields - {"sample_id"})


def test_candidate_prompt_builders_cannot_see_hidden_context(sample):
    """Every candidate-facing builder takes a CandidateView, so it has nothing to leak."""

    view = sample.candidate
    built = [
        prompts.direct_answer_messages(view),
        prompts.understanding_messages(view),
        prompts.sufficiency_messages(view, "notes"),
        prompts.gap_selection_messages(view, "notes", [], []),
        prompts.state_update_messages("notes", "q", "a"),
        prompts.final_answer_messages(view, "notes", []),
    ]
    for messages in built:
        text = " ".join(message["content"] for message in messages)
        for secret in SECRETS:
            assert secret not in text


def test_simulator_prompt_is_the_only_one_that_holds_the_reference(sample):
    text = " ".join(
        message["content"] for message in prompts.simulator_messages(sample.hidden, "What radius?")
    )
    assert FULL_TASK in text
    assert REQUIRED_POINT in text
    # Even the simulator is not shown the gold answer; it is told not to solve
    # the task, and it cannot reveal what it was never given.
    assert GOLD_ANSWER not in text


@pytest.mark.parametrize("arm", ["direct", "multi_stage", "gap_aware", "followup"])
def test_no_arm_puts_hidden_context_in_a_candidate_prompt(sample, arm):
    """Run each arm for real and read back every prompt the candidate was sent."""

    provider = make_provider()
    simulator = (
        UserSimulator(provider=provider, hidden=sample.hidden)
        if arm == "followup"
        else SilentSimulator()
    )
    result = asyncio.run(ARMS[arm](sample.candidate, provider, simulator, ArmConfig(budget=2)))

    candidate_prompts = [
        call.prompt for call in result.calls if call.role == "candidate" and call.prompt
    ]
    assert candidate_prompts, "the arm made no candidate calls"
    for prompt in candidate_prompts:
        for secret in SECRETS:
            assert secret not in prompt, f"{arm} leaked {secret!r} into a candidate prompt"


def test_only_the_simulator_and_judge_roles_may_hold_secrets(sample):
    provider = make_provider()
    simulator = UserSimulator(provider=provider, hidden=sample.hidden)
    result = asyncio.run(
        ARMS["followup"](sample.candidate, provider, simulator, ArmConfig(budget=1))
    )

    holders = {
        call.role
        for call in result.calls
        if call.prompt and any(secret in call.prompt for secret in SECRETS)
    }
    assert holders <= {"simulator", "judge"}


def test_revealed_information_reaches_the_candidate_only_through_a_reply(sample):
    """What the simulator chooses to say is allowed through. Nothing else is.

    The reply below carries a value the candidate could not otherwise know, and
    it must appear in the later candidate prompts -- otherwise the loop is not
    actually feeding answers back and any gain would be the extra calls.
    """

    provider = make_provider(simulator='{"answer": "The radius is 30 meters.", "knew": true}')
    simulator = UserSimulator(provider=provider, hidden=sample.hidden)
    result = asyncio.run(
        ARMS["followup"](sample.candidate, provider, simulator, ArmConfig(budget=1))
    )

    final = [call for call in result.calls if call.stage == "final_answer"]
    assert final, "the arm never answered"
    assert "30 meters" in final[-1].prompt
    for secret in SECRETS:
        assert secret not in final[-1].prompt


def test_non_interactive_arms_cannot_ask(sample):
    """A silent simulator makes "does not ask" a fact about the run, not a promise."""

    provider = make_provider()
    for arm in ("direct", "multi_stage", "gap_aware"):
        result = asyncio.run(
            ARMS[arm](sample.candidate, provider, SilentSimulator(), ArmConfig(budget=3))
        )
        assert result.asked is False
        assert result.num_followups == 0
        assert not [call for call in result.calls if call.role == "simulator"]


def test_silent_simulator_raises_rather_than_answering():
    with pytest.raises(AssertionError):
        asyncio.run(SilentSimulator().answer("anything", []))
