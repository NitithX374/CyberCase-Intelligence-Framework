from case_chat_support import GAP, SETTLED, TRACE, numbered_gaps

from app.config import settings
from app.services.analysis.clarification import Proceed, decide_followup
from app.trace.trace import CaseAnalysisTrace


def decide(trace: CaseAnalysisTrace, *, asked=(), this_round=0, rounds=1):
    return decide_followup(
        gaps=trace.gaps,
        asked_gap_keys=asked,
        asked_this_round=this_round,
        rounds_spent=rounds,
        max_rounds=settings.chat_followup_max_rounds,
        gaps_per_round=settings.chat_followup_gaps_per_round,
    )


def test_a_round_walks_the_gaps_one_at_a_time():
    trace = numbered_gaps(4)
    assert decide(trace).gap.gap_key == "topic:1"
    assert decide(trace, asked={"topic:1"}, this_round=1).gap.gap_key == "topic:2"
    assert decide(trace, asked={"topic:1", "topic:2"}, this_round=2).gap.gap_key == "topic:3"


def test_a_round_stops_at_three_even_with_more_gaps():
    spent = decide(numbered_gaps(4), asked={"topic:1", "topic:2", "topic:3"}, this_round=3)
    assert spent == Proceed("round_budget_spent")


def test_the_rounds_run_out():
    exhausted = decide(numbered_gaps(4), rounds=settings.chat_followup_max_rounds + 1)
    assert exhausted == Proceed("max_rounds_reached")


def test_a_gap_already_asked_is_not_asked_again_in_a_later_round():
    trace = CaseAnalysisTrace.model_validate(TRACE)
    assert decide(trace, asked={GAP["gap_key"]}, rounds=2) == Proceed("gaps_exhausted")


def test_a_gap_with_no_question_is_never_asked():
    trace = CaseAnalysisTrace.model_validate(
        {**TRACE, "gaps": [{**GAP, "clarification_question": None}]}
    )
    assert decide(trace) == Proceed("no_eligible_gap")


def test_nothing_to_ask_and_everything_asked_are_told_apart():
    assert decide(CaseAnalysisTrace.model_validate(SETTLED)) == Proceed("no_eligible_gap")
    assert decide(numbered_gaps(4), asked={f"topic:{n}" for n in (1, 2, 3, 4)}) == Proceed(
        "gaps_exhausted"
    )
