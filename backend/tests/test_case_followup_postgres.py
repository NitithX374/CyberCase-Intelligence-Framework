"""The follow-up loop, against a real database.

The analysis asks about one gap at a time. Each reply stays a chat message the
next analysis reads as follow-up history — it is not case material and does not
revise ``source_revision`` — and only the last reply of a round costs another
analysis, which is what makes asking three things affordable.
"""

from __future__ import annotations

import uuid

import pytest
from isolated_database import isolated_database
from sqlalchemy import select

from app.config import settings
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.models.sources import CaseSource
from app.models.user import User
from app.schemas.chat import ChatMessageCreate
from app.services.case_analysis.clarification import Proceed, decide_followup
from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.chat.case_chat import post_case_message

GAP = {
    "gap_id": "G-01",
    "gap_key": "topic:incident-time",
    "topic": "Incident time",
    "status": "NOT_PROVIDED",
    "description": "The incident time is missing.",
    "reason": "Timing fixes the chronology.",
    "priority": "high",
    "askable": True,
    "clarification_question": "When did the incident happen?",
}
TRACE = {
    "version": "case_analysis_trace_v1",
    "analysis_mode": "case_overview",
    "validation_status": "validated",
    "summary": "Files on the shared drive were reported encrypted.",
    "claims": [],
    "gaps": [GAP],
    "mitre_associations": [],
}


async def case_with_a_question(
    session_factory, trace: dict | None = None
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID]:
    """A case whose analysis has already asked about the first gap it found."""

    trace = trace or TRACE

    async with session_factory() as db, db.begin():
        user = User(
            email="followup@example.com",
            name="Analyst",
            password_hash="x",
            oauth_provider="password",
            oauth_subject_id="followup@example.com",
        )
        db.add(user)
        await db.flush()
        case = Case(user_id=user.id, title="Follow-up case", source_revision=1)
        db.add(case)
        await db.flush()
        db.add(
            CaseSource(
                case_id=case.id,
                source_kind="narrative",
                exact_text="Files on the shared drive were reported encrypted.",
            )
        )
        analysis = CaseAnalysisResult(
            case_id=case.id,
            source_revision=1,
            answer="Files were encrypted.",
            summary="Files were encrypted.",
            trace_json=trace,
            pipeline_config={"version": "case_analysis_v1"},
            external_context_json={},
        )
        db.add(analysis)
        await db.flush()
        case.latest_analysis_result_id = analysis.id
        question = ChatMessage(
            case_id=case.id,
            ordinal=1,
            role="assistant",
            content=trace["gaps"][0]["clarification_question"],
            gap_key=trace["gaps"][0]["gap_key"],
            analysis_result_id=analysis.id,
        )
        db.add(question)
        await db.flush()
        return case.id, user.id, question.id


def three_gaps() -> CaseAnalysisTrace:
    return CaseAnalysisTrace.model_validate(
        {
            **TRACE,
            "gaps": [
                {
                    **GAP,
                    "gap_id": f"G-0{n}",
                    "gap_key": f"topic:{n}",
                    "clarification_question": f"Question {n}?",
                }
                for n in (1, 2, 3, 4)
            ],
        }
    )


def decide(trace: CaseAnalysisTrace, *, asked=(), this_round=0, rounds=1):
    """The policy at the settings the product ships, so the defaults are tested."""

    return decide_followup(
        gaps=trace.gaps,
        asked_gap_keys=asked,
        asked_this_round=this_round,
        rounds_spent=rounds,
        max_rounds=settings.chat_followup_max_rounds,
        gaps_per_round=settings.chat_followup_gaps_per_round,
    )


def test_a_round_walks_the_gaps_one_at_a_time():
    trace = three_gaps()
    assert decide(trace).gap.gap_key == "topic:1"
    assert decide(trace, asked={"topic:1"}, this_round=1).gap.gap_key == "topic:2"
    assert decide(trace, asked={"topic:1", "topic:2"}, this_round=2).gap.gap_key == "topic:3"


def test_a_round_stops_at_three_even_with_more_gaps():
    spent = decide(three_gaps(), asked={"topic:1", "topic:2", "topic:3"}, this_round=3)
    assert spent == Proceed("round_budget_spent")
    # Not terminal: the caller analyses again rather than finishing here.
    assert not spent.is_terminal


def test_the_rounds_run_out():
    exhausted = decide(three_gaps(), rounds=settings.chat_followup_max_rounds + 1)
    assert exhausted == Proceed("max_rounds_reached")
    assert exhausted.is_terminal


def test_a_gap_already_asked_is_not_asked_again_in_a_later_round():
    """The keys come from the whole case, so a new analysis cannot re-ask one."""

    trace = CaseAnalysisTrace.model_validate({**TRACE, "gaps": [GAP]})
    assert decide(trace, asked={GAP["gap_key"]}, rounds=2) == Proceed("gaps_exhausted")


def test_a_gap_with_no_question_is_never_asked():
    trace = CaseAnalysisTrace.model_validate(
        {**TRACE, "gaps": [{**GAP, "clarification_question": None}]}
    )
    assert decide(trace) == Proceed("no_eligible_gap")


def test_nothing_to_ask_and_everything_asked_are_told_apart():
    """A settled case and an exhausted one stop for different reasons."""

    settled = CaseAnalysisTrace.model_validate({**TRACE, "gaps": []})
    assert decide(settled) == Proceed("no_eligible_gap")
    assert decide(three_gaps(), asked={f"topic:{n}" for n in (1, 2, 3, 4)}) == Proceed(
        "gaps_exhausted"
    )


@pytest.mark.asyncio
async def test_replying_to_the_question_stays_conversation():
    """The reply is admitted and the case analysed again, without being marked.

    It does not become a case source, and it does not move source_revision:
    answering a question is not a revision of the material the case was filed
    with, and treating it as one would invalidate any analysis already running.
    """

    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await case_with_a_question(session_factory)
        analyses: list[str] = []

        async def fake_analysis(**kwargs):
            analyses.append(str(kwargs.get("case_id")))
            raise RuntimeError("stop after admission")

        import app.services.chat.case_chat as module

        original = module.run_case_analysis
        module.run_case_analysis = fake_analysis
        try:
            with pytest.raises(RuntimeError):
                await post_case_message(
                    case_id=case_id,
                    user_id=user_id,
                    request=ChatMessageCreate(content="Around two in the morning."),
                    session_factory=session_factory,
                )
        finally:
            module.run_case_analysis = original

        assert analyses == [str(case_id)]
        async with session_factory() as db:
            answer = await db.scalar(
                select(ChatMessage).where(ChatMessage.in_reply_to_message_id == question_id)
            )
            source = await db.scalar(
                select(CaseSource).where(CaseSource.source_kind == "followup_answer")
            )
            case = await db.get(Case, case_id)
        assert answer.role == "user"
        assert answer.content == "Around two in the morning."
        assert answer.message_kind == "followup_answer"
        assert source is None, "a reply is conversation, not case material"
        assert case.source_revision == 1, "answering does not revise the case"


@pytest.mark.asyncio
async def test_a_question_that_was_answered_is_no_longer_pending():
    """A second send is an ordinary question, not another answer."""

    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await case_with_a_question(session_factory)
        async with session_factory() as db, db.begin():
            db.add(
                ChatMessage(
                    case_id=case_id,
                    ordinal=2,
                    role="user",
                    content="Around two in the morning.",
                    in_reply_to_message_id=question_id,
                )
            )

        from app.services.chat.followup import pending_question

        async with session_factory() as db:
            assert await pending_question(db, case_id) is None


@pytest.mark.asyncio
async def test_the_round_asks_the_next_gap_before_spending_an_analysis():
    """Three questions, one analysis: the reply moves the round along."""

    async with isolated_database() as session_factory:
        trace = three_gaps().model_dump(mode="json")
        case_id, user_id, first_id = await case_with_a_question(session_factory, trace)
        analyses: list[str] = []

        async def fake_analysis(**kwargs):
            analyses.append(str(kwargs.get("case_id")))
            raise RuntimeError("the round was not finished")

        import app.services.chat.case_chat as module

        original = module.run_case_analysis
        module.run_case_analysis = fake_analysis
        try:
            produced, analysis = await post_case_message(
                case_id=case_id,
                user_id=user_id,
                request=ChatMessageCreate(content="Around two in the morning."),
                session_factory=session_factory,
            )
        finally:
            module.run_case_analysis = original

        assert analyses == [], "the second question should come before another analysis"
        assert analysis is None
        assert [message.role for message in produced] == ["user", "assistant"]
        assert produced[0].in_reply_to_message_id == first_id
        assert produced[1].content == "Question 2?"
        assert produced[1].gap_key == "topic:2"


@pytest.mark.asyncio
async def test_a_retried_send_gets_what_it_already_produced():
    """The analysis is slow enough that a client can give up and try again."""

    async with isolated_database() as session_factory:
        trace = three_gaps().model_dump(mode="json")
        case_id, user_id, _ = await case_with_a_question(session_factory, trace)
        send = ChatMessageCreate(content="Around two.", client_request_id="send-1")

        first, _ = await post_case_message(
            case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
        )
        again, _ = await post_case_message(
            case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
        )

        assert [message.id for message in again] == [message.id for message in first]
        async with session_factory() as db:
            stored = await db.scalars(select(ChatMessage).where(ChatMessage.case_id == case_id))
            case = await db.get(Case, case_id)
        assert len(list(stored)) == 3, "the retry must not add a second answer"
        assert case.source_revision == 1, "and no reply revises the case"


@pytest.mark.asyncio
async def test_a_spent_budget_does_not_silence_the_case_for_good():
    """The budget spent. A reply gets nothing more; the reader's own analysis asks.

    The budget bounds the chain a reply keeps going, not the case. Counted over
    the case's whole life it would turn the questions off permanently, however
    much new material arrived afterwards.
    """

    from app.services.case_analysis.contracts import CaseAnalysisTrace
    from app.services.case_analysis.pipeline import AnalysisArtifacts
    from app.services.case_workflow import CaseUnderAnalysis, store_analysis
    from app.services.sources import load_case_source_bundle

    async with isolated_database() as session_factory:
        trace_json = three_gaps().model_dump(mode="json")
        case_id, user_id, _ = await case_with_a_question(session_factory, trace_json)
        async with session_factory() as db, db.begin():
            # Enough further asking analyses to spend the whole budget. The
            # fixture already contributed one.
            for extra in range(settings.chat_followup_max_rounds):
                other = CaseAnalysisResult(
                    case_id=case_id,
                    source_revision=1,
                    answer="Earlier.",
                    summary="Earlier.",
                    trace_json=trace_json,
                    pipeline_config={},
                    external_context_json={},
                )
                db.add(other)
                await db.flush()
                db.add(
                    ChatMessage(
                        case_id=case_id,
                        ordinal=9 + extra,
                        role="assistant",
                        content="An earlier question.",
                        gap_key=f"topic:spent-{extra}",
                        analysis_result_id=other.id,
                    )
                )

        async def questions() -> int:
            async with session_factory() as db:
                rows = await db.scalars(
                    select(ChatMessage.id).where(
                        ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None)
                    )
                )
                return len(list(rows))

        async def store(*, continuing: bool):
            async with session_factory() as db:
                bundle = await load_case_source_bundle(db, case_id=case_id, user_id=user_id)
            before = await questions()
            step = await store_analysis(
                session_factory,
                CaseUnderAnalysis(case_id=case_id, source_bundle=bundle),
                AnalysisArtifacts(
                    answer="Analysed.", trace=CaseAnalysisTrace.model_validate(trace_json)
                ),
                continuing_followup=continuing,
            )
            return await questions() - before, step

        asked, step = await store(continuing=True)
        assert asked == 0, "a reply must respect the spent budget"
        assert step.stop_reason == "max_rounds_reached"
        assert step.result.trace_json["stop_reason"] == "max_rounds_reached", (
            "the stored analysis has to say why it stopped asking"
        )

        asked, step = await store(continuing=False)
        assert asked == 1, "the reader's own analysis may ask again"
        assert step.stop_reason is None
        assert step.question is not None
