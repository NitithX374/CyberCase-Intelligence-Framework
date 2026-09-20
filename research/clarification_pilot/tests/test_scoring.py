"""Deterministic grading, on the four answer shapes AskMind actually contains."""

from __future__ import annotations

import asyncio
import dataclasses

from clarification_pilot.arms import ArmConfig, run_direct
from clarification_pilot.scoring import (
    candidate_answer,
    exact_match,
    extract_boxed,
    score_result,
)
from clarification_pilot.simulator import SilentSimulator

from .conftest import make_provider


# -- MedQA: "The answer is B." -----------------------------------------------


def test_a_multiple_choice_letter_matches_through_surrounding_prose():
    gold = "The answer is B."
    assert exact_match("Given the oedema and the age, this is kwashiorkor.\nThe answer is B.", gold)
    assert exact_match("The answer is B", gold)


def test_the_wrong_letter_does_not_match():
    assert not exact_match("The answer is C.", "The answer is B.")


# -- BBH: a bare token --------------------------------------------------------


def test_a_bare_token_answer_matches():
    assert exact_match("Working through the negations:\nFalse", "False")
    assert exact_match("Yes", "Yes")


def test_a_parenthesised_option_matches_the_bare_letter():
    assert exact_match("The best option is\n(E)", "E")


def test_a_different_token_does_not_match():
    assert not exact_match("True", "False")


# -- Math500: boxed LaTeX -----------------------------------------------------


def test_a_boxed_answer_matches():
    assert exact_match(r"The correct answer is \boxed{12}", "12")


def test_boxed_latex_matches_through_spacing_and_frac_spelling():
    assert exact_match(r"\boxed{\dfrac{\sqrt{3}}{3}}", r"\frac{\sqrt{3}}{3}")
    assert exact_match(r"\boxed{\sqrt{51}}", r"\sqrt{51}")
    assert exact_match(r"answer: \boxed{ \frac{1}{2} }", r"\frac{1}{2}")


def test_nested_braces_are_read_whole():
    assert extract_boxed(r"\boxed{\frac{1}{2}}") == r"\frac{1}{2}"
    assert extract_boxed(r"first \boxed{1} then \boxed{2}") == "2"
    assert extract_boxed("no box here") is None


def test_a_different_value_does_not_match():
    assert not exact_match(r"\boxed{13}", "12")
    assert not exact_match(r"\boxed{\sqrt{52}}", r"\sqrt{51}")


# -- things that must not count as correct ------------------------------------


def test_an_empty_or_refused_answer_is_wrong():
    assert not exact_match("", "12")
    assert not exact_match("   ", "12")


def test_a_number_buried_mid_sentence_is_not_taken_as_the_answer():
    """The extractor reads the last line, not any digit it can find."""

    assert not exact_match("I considered 12 and 13 but cannot decide.", "12")


def test_the_fallback_reads_the_last_line():
    assert candidate_answer("thinking...\nmore thinking\n42") == "42"


# -- routing ------------------------------------------------------------------


def test_a_gpqa_sample_is_graded_by_the_judge_and_says_so(sample):
    provider = make_provider(judge='{"correct": true, "reason": "equivalent"}')
    result = asyncio.run(
        run_direct(sample.candidate, provider, SilentSimulator(), ArmConfig(budget=0))
    )
    hidden = dataclasses.replace(sample.hidden, scoring="judge")
    scored = asyncio.run(score_result(result, hidden, provider, measure_coverage=False))
    assert scored.scored_by == "judge"
    assert scored.correct is True
    assert scored.judge_reason == "equivalent"


def test_judge_calls_are_billed_to_the_judge_not_the_candidate(sample):
    provider = make_provider()
    result = asyncio.run(
        run_direct(sample.candidate, provider, SilentSimulator(), ArmConfig(budget=0))
    )
    scored = asyncio.run(score_result(result, sample.hidden, provider, measure_coverage=True))
    assert scored.candidate_calls == 1, "grading must not inflate the candidate's cost"


def test_exact_match_falls_back_to_the_judge_only_when_asked(sample):
    provider = make_provider(judge='{"correct": true, "reason": "same thing"}')
    result = asyncio.run(
        run_direct(sample.candidate, provider, SilentSimulator(), ArmConfig(budget=0))
    )
    strict = asyncio.run(score_result(result, sample.hidden, provider, measure_coverage=False))
    assert strict.scored_by == "exact_match"
    assert strict.correct is False

    relaxed = asyncio.run(
        score_result(result, sample.hidden, provider, judge_fallback=True, measure_coverage=False)
    )
    assert relaxed.scored_by == "judge"
    assert relaxed.correct is True
