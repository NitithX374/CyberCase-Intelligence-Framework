"""Aggregation and the paired comparison, on hand-built rows.

The numbers these produce are the thesis's numbers, so they are checked against
arithmetic done by hand rather than against whatever the code happens to emit.
"""

from __future__ import annotations

from clarification_pilot.contracts import ArmResult, ScoredResult, TurnRecord
from clarification_pilot.metrics import ask_decision, compare, failure_counts, summarise
from clarification_pilot.stats import exact_binomial, mcnemar


def row(
    sample_id: str,
    arm: str,
    correct: bool,
    *,
    budget: int = 0,
    gold_should_ask: bool = True,
    predicted_ask: bool | None = None,
    asked: bool = False,
    followups: int = 0,
    covered: int = 0,
    total: int = 0,
    stop: str = "sufficient",
) -> ScoredResult:
    return ScoredResult(
        sample_id=sample_id,
        arm=arm,
        budget=budget,
        source_task="ask_mind_bbhde",
        correct=correct,
        scored_by="exact_match",
        checkpoint_coverage=(covered / total) if total else None,
        checkpoints_total=total,
        checkpoints_covered=covered,
        gold_should_ask=gold_should_ask,
        predicted_ask=predicted_ask,
        asked=asked,
        num_followups=followups,
        stop_reason=stop,
        candidate_calls=1,
    )


def test_ask_decision_scores_against_the_undegraded_items():
    """Two true asks, one false alarm, one miss."""

    rows = [
        row("a", "gap_aware", True, gold_should_ask=True, predicted_ask=True),
        row("b", "gap_aware", True, gold_should_ask=True, predicted_ask=True),
        row("c", "gap_aware", True, gold_should_ask=False, predicted_ask=True),
        row("d", "gap_aware", True, gold_should_ask=True, predicted_ask=False),
    ]
    decision = ask_decision(rows)
    assert decision.n == 4
    assert decision.precision == 2 / 3
    assert decision.recall == 2 / 3
    assert decision.f1 == 2 / 3
    assert decision.accuracy == 0.5


def test_arms_without_an_ask_decision_report_nothing_rather_than_zero():
    """Direct never decides. Scoring it as "never asks" would be a made-up number."""

    decision = ask_decision([row("a", "direct", True, predicted_ask=None)])
    assert decision.n == 0
    assert decision.f1 is None


def test_recovery_gain_is_paired_on_sample_id():
    scored = [
        row("a", "multi_stage", False),
        row("b", "multi_stage", False),
        row("c", "multi_stage", True),
        row("a", "followup", True, budget=2, asked=True, followups=1),
        row("b", "followup", False, budget=2, asked=True, followups=1),
        row("c", "followup", True, budget=2, asked=True, followups=1),
    ]
    result = compare(scored, treatment="followup", baseline="multi_stage", budget=2)
    assert result is not None
    assert result.n == 3
    assert result.baseline_accuracy == 1 / 3
    assert result.treatment_accuracy == 2 / 3
    assert abs(result.recovery_gain - 1 / 3) < 1e-9
    assert result.mcnemar.only_b == 1
    assert result.mcnemar.only_a == 0


def test_a_comparison_without_shared_samples_is_none():
    scored = [row("a", "multi_stage", True), row("z", "followup", True, budget=1)]
    assert compare(scored, treatment="followup", baseline="multi_stage", budget=1) is None


def test_mcnemar_uses_only_the_discordant_pairs():
    a = [True, True, False, False, True]
    b = [True, False, True, True, True]
    result = mcnemar(a, b)
    assert result.only_a == 1
    assert result.only_b == 2
    assert result.both_right == 2
    assert result.discordant == 3
    assert 0 < result.p_value <= 1


def test_no_discordant_pairs_means_no_evidence_of_a_difference():
    assert mcnemar([True, False], [True, False]).p_value == 1.0


def test_the_exact_binomial_is_two_sided():
    assert exact_binomial(0, 0) == 1.0
    assert abs(exact_binomial(0, 5) - 2 / 32) < 1e-12
    assert exact_binomial(5, 10) == 1.0


def test_failures_only_blame_an_arm_that_was_allowed_to_ask():
    """Gap-aware not asking is its design; follow-up not asking is a miss."""

    gap_aware = [row("a", "gap_aware", False, budget=0, gold_should_ask=True, asked=False)]
    followup = [row("a", "followup", False, budget=2, gold_should_ask=True, asked=False)]
    assert failure_counts(gap_aware, {}, None)["failed_to_ask"] == 0
    assert failure_counts(followup, {}, None)["failed_to_ask"] == 1


def test_an_unnecessary_question_is_counted_against_the_undegraded_items():
    rows = [row("a", "followup", True, budget=2, gold_should_ask=False, asked=True, followups=1)]
    assert failure_counts(rows, {}, None)["asked_unnecessarily"] == 1


def test_asking_off_target_is_counted_when_coverage_is_zero():
    rows = [
        row("a", "followup", False, budget=2, asked=True, followups=1, covered=0, total=3),
        row("b", "followup", False, budget=2, asked=True, followups=1, covered=1, total=3),
    ]
    assert failure_counts(rows, {}, None)["asked_irrelevant"] == 1


def test_information_that_arrived_and_did_not_help_is_counted():
    runs = {
        "a": ArmResult(
            sample_id="a",
            arm="followup",
            budget=2,
            turns=[TurnRecord(index=0, question="q", simulator_knew=True)],
        )
    }
    rows = [row("a", "followup", False, budget=2, asked=True, followups=1)]
    assert failure_counts(rows, runs, None)["informed_but_still_wrong"] == 1


def test_no_gain_is_measured_against_the_named_baseline():
    baseline = {"a": row("a", "multi_stage", False)}
    rows = [row("a", "followup", False, budget=2, asked=True, followups=1)]
    assert failure_counts(rows, {}, baseline)["no_gain_over_baseline"] == 1

    improved = [row("a", "followup", True, budget=2, asked=True, followups=1)]
    assert failure_counts(improved, {}, baseline)["no_gain_over_baseline"] == 0


def test_summaries_separate_deterministic_accuracy_from_the_judged_kind():
    scored = [
        row("a", "direct", True),
        ScoredResult(
            sample_id="b",
            arm="direct",
            budget=0,
            source_task="ask_mind_gpqade",
            correct=True,
            scored_by="judge",
        ),
    ]
    summary = summarise(scored, [])[0]
    assert summary.n == 2
    assert summary.accuracy == 1.0
    assert summary.deterministic_n == 1
    assert summary.judged_n == 1
    assert summary.deterministic_accuracy == 1.0


def test_summaries_read_in_arm_order_not_alphabetically():
    scored = [
        row("a", "followup", True, budget=1),
        row("a", "direct", True),
        row("a", "gap_aware", True),
        row("a", "multi_stage", True),
    ]
    assert [item.arm for item in summarise(scored, [])] == [
        "direct",
        "multi_stage",
        "gap_aware",
        "followup",
    ]
