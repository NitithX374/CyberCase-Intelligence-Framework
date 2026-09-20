"""Shared fixtures. Nothing here reaches the network or needs an API key."""

from __future__ import annotations

import json

import pytest

from clarification_pilot.contracts import (
    CandidateView,
    ClarificationBenchmarkSample,
    HiddenContext,
)
from clarification_pilot.provider import Provider

# Strings that must never reach the candidate except through a simulator reply.
GOLD_ANSWER = "ZZTOPSECRETANSWER"
FULL_TASK = "The detector radius is QQHIDDENRADIUS meters."
HIDDEN_SUMMARY = "WWREMOVEDFACT was taken out of the question."
REQUIRED_POINT = "VVEXACTRADIUS of the detector"


@pytest.fixture
def sample() -> ClarificationBenchmarkSample:
    return ClarificationBenchmarkSample(
        candidate=CandidateView(
            sample_id="sample-1",
            initial_input="The detector radius is a few tens of meters. What is the answer?",
        ),
        hidden=HiddenContext(
            sample_id="sample-1",
            full_input=FULL_TASK,
            required_points=(REQUIRED_POINT,),
            hidden_summary=HIDDEN_SUMMARY,
            gold_answer=GOLD_ANSWER,
            should_ask=True,
            scoring="exact_match",
            source_task="ask_mind_gpqade",
        ),
    )


def scripted(**overrides):
    """A dry-run responder, with per-stage overrides for a specific test."""

    def respond(prompt_version: str, messages):
        for prefix, value in overrides.items():
            if prompt_version.startswith(prefix):
                return value(messages) if callable(value) else value
        if prompt_version.startswith("sufficiency"):
            return json.dumps(
                {
                    "status": "NEED_CLARIFICATION",
                    "reason": "a value is missing",
                    "gaps": [{"id": "gap_1", "description": "the radius", "priority": 0.9}],
                }
            )
        if prompt_version.startswith("gap_selection"):
            return json.dumps({"selected_gap_id": "gap_1", "question": "What is the radius?"})
        if prompt_version.startswith("question_generation"):
            return json.dumps({"question": "What is the radius?"})
        if prompt_version.startswith("simulator"):
            return json.dumps({"answer": "It is 30 meters.", "knew": True})
        if prompt_version.startswith("judge"):
            return json.dumps({"correct": False, "reason": "no"})
        if prompt_version.startswith("coverage"):
            return json.dumps({"covered": []})
        if prompt_version.startswith(("understanding", "state_update")):
            return "Notes about the task."
        return "The answer is A."

    return respond


@pytest.fixture
def provider() -> Provider:
    return Provider(dry_run=True, log_prompts=True, script=scripted())


def make_provider(**overrides) -> Provider:
    return Provider(dry_run=True, log_prompts=True, script=scripted(**overrides))
