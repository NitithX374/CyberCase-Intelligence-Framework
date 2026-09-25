from __future__ import annotations

import uuid
from dataclasses import replace

import pytest
from case_chat_support import GAP, TRACE, numbered_gaps, seeded_case
from isolated_database import isolated_database
from sqlalchemy import select

import app.services.analysis.pipeline as pipeline_module
import app.services.chat.case_chat as case_chat
from app.config import settings
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.models.sources import CaseSource
from app.schemas.chat import ChatMessageCreate, ChatMessageRead
from app.schemas.message_metadata import MessageAnalysisTrace
from app.services.analysis.clarification import Ask
from app.services.analysis.contracts import CaseAnalysisGap, CaseAnalysisTrace, CaseAssessmentTrace
from app.services.analysis.pipeline import AnalysisAdvance, AnalysisArtifacts
from app.services.chat.case_chat import get_case_chat, post_case_message, send_case_message
from app.services.chat.followup import pending_question
from app.services.reports.content import clarification_limitation
from app.services.workflow.run_analysis import (
    analysing,
    get_latest_case_analysis,
    run_case_analysis,
)
from app.services.workflow.shared import CaseWorkflowError

pytestmark = pytest.mark.asyncio


async def answer_the_question(
    session_factory, case_id: uuid.UUID, question_id: uuid.UUID, *, sent: str | None = None
) -> None:
    async with session_factory() as db, db.begin():
        question = await db.get(ChatMessage, question_id)
        db.add(
            ChatMessage(
                case_id=case_id,
                ordinal=2,
                role="user",
                content="Around two in the morning.",
                message_kind="followup_answer",
                analysis_result_id=question.analysis_result_id,
                in_reply_to_message_id=question_id,
                client_request_id=sent,
            )
        )


async def analysed_after_the_round(session_factory, case_id: uuid.UUID) -> None:
    async with session_factory() as db, db.begin():
        db.add(
            CaseAnalysisResult(
                case_id=case_id,
                source_revision=1,
                summary="Analysed after the round.",
                trace_json=TRACE,
                pipeline_config={},
                external_context_json={},
            )
        )


async def gap_questions(session_factory, case_id: uuid.UUID) -> list[ChatMessage]:
    async with session_factory() as db:
        rows = await db.scalars(
            select(ChatMessage)
            .where(ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None))
            .order_by(ChatMessage.ordinal)
        )
        return list(rows)


def production_pipeline(monkeypatch, gaps: list[CaseAnalysisGap], seen: list | None = None):
    async def assess(data):
        if seen is not None:
            seen.append((data.asked_gap_keys, data.rounds_spent))
        return CaseAssessmentTrace(gaps=gaps)

    async def unchanged(_data, so_far):
        return so_far

    async def write(_data, so_far):
        return replace(so_far, trace=CaseAnalysisTrace.model_validate(TRACE))

    monkeypatch.setattr(pipeline_module, "assess_gaps", assess)
    monkeypatch.setattr(pipeline_module, "retrieve_technical_context", unchanged)
    monkeypatch.setattr(pipeline_module, "write_analysis", write)
    monkeypatch.setattr(pipeline_module, "bind_to_case", unchanged)


async def bare_analysis(_data):
    return AnalysisArtifacts(trace=CaseAnalysisTrace.model_validate(TRACE))


async def test_replying_to_the_question_stays_conversation(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        analyses: list[str] = []

        async def fake_analysis(**kwargs):
            analyses.append(str(kwargs.get("case_id")))
            raise RuntimeError("stop after admission")

        monkeypatch.setattr(case_chat, "run_case_analysis", fake_analysis)
        with pytest.raises(RuntimeError):
            await post_case_message(
                case_id=case_id,
                user_id=user_id,
                request=ChatMessageCreate(content="Around two in the morning."),
                session_factory=session_factory,
            )

        assert analyses == [str(case_id)]
        async with session_factory() as db:
            answer = await db.scalar(
                select(ChatMessage).where(ChatMessage.in_reply_to_message_id == question_id)
            )
            sources = list(
                await db.scalars(select(CaseSource).where(CaseSource.case_id == case_id))
            )
            case = await db.get(Case, case_id)
        assert answer.role == "user"
        assert answer.content == "Around two in the morning."
        assert answer.message_kind == "followup_answer"
        assert [source.source_kind for source in sources] == ["narrative"], (
            "a reply is conversation, not case material"
        )
        assert case.source_revision == 1, "answering does not revise the case"


async def test_a_question_that_was_answered_is_no_longer_pending():
    async with isolated_database() as session_factory:
        case_id, _, question_id = await seeded_case(session_factory)
        async with session_factory() as db:
            assert (await pending_question(db, case_id)).id == question_id
        await answer_the_question(session_factory, case_id, question_id)

        async with session_factory() as db:
            assert await pending_question(db, case_id) is None


async def test_the_round_asks_the_next_gap_before_spending_an_analysis(monkeypatch):
    async with isolated_database() as session_factory:
        trace = numbered_gaps(4).model_dump(mode="json")
        case_id, user_id, first_id = await seeded_case(session_factory, trace=trace)
        analyses: list[str] = []

        async def fake_analysis(**kwargs):
            analyses.append(str(kwargs.get("case_id")))
            raise RuntimeError("the round was not finished")

        monkeypatch.setattr(case_chat, "run_case_analysis", fake_analysis)
        produced, analysis = await post_case_message(
            case_id=case_id,
            user_id=user_id,
            request=ChatMessageCreate(content="Around two in the morning."),
            session_factory=session_factory,
        )

        assert analyses == [], "the second question should come before another analysis"
        assert analysis is None
        assert [message.role for message in produced] == ["user", "assistant"]
        assert produced[0].in_reply_to_message_id == first_id
        assert produced[1].content == "Question 2?"
        assert produced[1].gap_key == "topic:2"


async def test_the_chat_names_each_follow_up_by_its_qa_id_and_the_question_still_open():
    async with isolated_database() as session_factory:
        trace = numbered_gaps(4).model_dump(mode="json")
        case_id, user_id, first_id = await seeded_case(session_factory, trace=trace)

        sent = await send_case_message(
            case_id=case_id,
            user_id=user_id,
            request=ChatMessageCreate(content="Around two in the morning."),
            session_factory=session_factory,
        )
        answer, second = sent.messages
        async with session_factory() as db:
            chat = await get_case_chat(db, case_id=case_id, user_id=user_id)

        assert (answer.qa_id, second.qa_id) == ("QA-01", "QA-02")
        assert sent.pending_question_id == second.id
        assert [(message.id, message.qa_id) for message in chat.messages] == [
            (first_id, "QA-01"),
            (answer.id, "QA-01"),
            (second.id, "QA-02"),
        ]
        assert chat.pending_question_id == second.id


async def test_a_retried_send_gets_what_it_already_produced():
    async with isolated_database() as session_factory:
        trace = numbered_gaps(4).model_dump(mode="json")
        case_id, user_id, _ = await seeded_case(session_factory, trace=trace)
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


async def test_a_retried_answer_runs_the_analysis_its_first_attempt_lost(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        send = ChatMessageCreate(content="Around two in the morning.", client_request_id="send-1")
        continuing: list[bool] = []
        finished = object()

        async def lost(**kwargs):
            continuing.append(kwargs["continuing_followup"])
            raise CaseWorkflowError("case_assessment_transport", "Analysis stage transport failed")

        async def analysed(**kwargs):
            continuing.append(kwargs["continuing_followup"])
            return finished

        monkeypatch.setattr(case_chat, "run_case_analysis", lost)
        with pytest.raises(CaseWorkflowError) as failure:
            await post_case_message(
                case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
            )
        assert failure.value.code == "case_assessment_transport"

        monkeypatch.setattr(case_chat, "run_case_analysis", analysed)
        produced, step = await post_case_message(
            case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
        )

        assert step is finished
        assert continuing == [True, True]
        assert [message.in_reply_to_message_id for message in produced] == [question_id]
        async with session_factory() as db:
            answers = list(
                await db.scalars(
                    select(ChatMessage).where(ChatMessage.in_reply_to_message_id == question_id)
                )
            )
        assert len(answers) == 1, "the retry must not record the answer twice"


async def test_a_retried_answer_whose_analysis_ran_is_not_analysed_again(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        await answer_the_question(session_factory, case_id, question_id, sent="send-1")
        await analysed_after_the_round(session_factory, case_id)
        analyses: list[uuid.UUID] = []

        async def analysed(**kwargs):
            analyses.append(kwargs["case_id"])

        monkeypatch.setattr(case_chat, "run_case_analysis", analysed)
        produced, step = await post_case_message(
            case_id=case_id,
            user_id=user_id,
            request=ChatMessageCreate(
                content="Around two in the morning.", client_request_id="send-1"
            ),
            session_factory=session_factory,
        )

        assert analyses == []
        assert step is None
        assert produced[0].in_reply_to_message_id == question_id


async def test_a_retry_while_the_round_is_being_analysed_does_not_start_another(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        await answer_the_question(session_factory, case_id, question_id, sent="send-1")
        analyses: list[uuid.UUID] = []

        async def analysed(**kwargs):
            analyses.append(kwargs["case_id"])

        monkeypatch.setattr(case_chat, "run_case_analysis", analysed)
        with analysing(case_id):
            produced, step = await post_case_message(
                case_id=case_id,
                user_id=user_id,
                request=ChatMessageCreate(
                    content="Around two in the morning.", client_request_id="send-1"
                ),
                session_factory=session_factory,
            )

        assert analyses == [], "the first attempt is still analysing the round"
        assert step is None
        assert produced[0].in_reply_to_message_id == question_id


async def test_analysing_again_continues_a_round_whose_analysis_never_ran(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        await answer_the_question(session_factory, case_id, question_id)
        seen: list = []
        production_pipeline(monkeypatch, [CaseAnalysisGap.model_validate(GAP)], seen)

        step = await run_case_analysis(
            case_id=case_id, user_id=user_id, session_factory=session_factory
        )

        assert seen == [(frozenset({GAP["gap_key"]}), 2)]
        assert not step.needs_followup, "the gap that was answered is not asked again"
        assert step.result.trace_json["stop_reason"] == "gaps_exhausted"
        assert len(await gap_questions(session_factory, case_id)) == 1


async def test_analysing_again_after_the_round_was_analysed_starts_afresh():
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        await answer_the_question(session_factory, case_id, question_id)
        await analysed_after_the_round(session_factory, case_id)
        seen = []

        async def pipeline(data):
            seen.append((data.asked_gap_keys, data.rounds_spent))
            return AnalysisArtifacts(trace=CaseAnalysisTrace.model_validate(TRACE))

        await run_case_analysis(
            case_id=case_id,
            user_id=user_id,
            session_factory=session_factory,
            pipeline=pipeline,
        )

        assert seen == [(frozenset(), 1)]


async def test_a_pipeline_that_returns_only_an_analysis_stores_it_and_asks_nothing():
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory, asking=False)

        step = await run_case_analysis(
            case_id=case_id,
            user_id=user_id,
            session_factory=session_factory,
            pipeline=bare_analysis,
        )

        assert not step.needs_followup
        assert step.result.status == "validated"
        assert step.result.trace_json["stop_reason"] is None, (
            "the clarification policy never ran, so the analysis cannot say why it stopped asking"
        )
        assert (
            clarification_limitation(CaseAnalysisTrace.model_validate(step.result.trace_json))
            is None
        ), "a report would otherwise claim that no outstanding gap was worth asking about"
        assert await gap_questions(session_factory, case_id) == []
        async with session_factory() as db:
            summary = await db.scalar(
                select(ChatMessage).where(ChatMessage.analysis_result_id == step.result.id)
            )
        assert summary.content == TRACE["summary"]
        assert set(summary.metadata_json) == {"analysis_trace"}
        stored_trace = ChatMessageRead.model_validate(summary).metadata_json["analysis_trace"]
        assert isinstance(stored_trace, MessageAnalysisTrace)
        assert stored_trace.summary == TRACE["summary"]


async def test_an_analysis_records_the_answers_it_read_and_not_later_ones():
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        await answer_the_question(session_factory, case_id, question_id)

        async def pipeline(data):
            async with session_factory() as db, db.begin():
                asked_by = (await db.get(ChatMessage, question_id)).analysis_result_id
                later = ChatMessage(
                    case_id=case_id,
                    ordinal=3,
                    role="assistant",
                    content="Who reported it?",
                    gap_key="topic:reporter",
                    analysis_result_id=asked_by,
                )
                db.add(later)
                await db.flush()
                db.add(
                    ChatMessage(
                        case_id=case_id,
                        ordinal=4,
                        role="user",
                        content="The payroll manager.",
                        message_kind="followup_answer",
                        analysis_result_id=asked_by,
                        in_reply_to_message_id=later.id,
                    )
                )
            return AnalysisArtifacts(trace=CaseAnalysisTrace.model_validate(TRACE))

        step = await run_case_analysis(
            case_id=case_id,
            user_id=user_id,
            session_factory=session_factory,
            pipeline=pipeline,
        )

        async with session_factory() as db:
            stored = await db.get(CaseAnalysisResult, step.result.id)
        assert stored.external_context_json["followup_history"] == {
            "version": "followup_snapshot_v1",
            "items": [
                {
                    "qa_id": "QA-01",
                    "gap_key": GAP["gap_key"],
                    "question": GAP["clarification_question"],
                    "answer": "Around two in the morning.",
                }
            ],
        }, "the answer given while the model was thinking was never read"


async def test_an_analysis_records_the_sources_it_read_and_not_later_ones():
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory)
        async with session_factory() as db:
            read = await db.scalar(select(CaseSource.id).where(CaseSource.case_id == case_id))

        async def pipeline(data):
            async with session_factory() as db, db.begin():
                db.add(
                    CaseSource(
                        case_id=case_id,
                        source_kind="narrative",
                        exact_text="Added while the model was thinking.",
                    )
                )
            return AnalysisArtifacts(trace=CaseAnalysisTrace.model_validate(TRACE))

        step = await run_case_analysis(
            case_id=case_id,
            user_id=user_id,
            session_factory=session_factory,
            pipeline=pipeline,
        )

        async with session_factory() as db:
            stored = await db.get(CaseAnalysisResult, step.result.id)
        assert stored.external_context_json["sources_read"] == {
            "version": "sources_read_v1",
            "source_ids": [str(read)],
        }, "the source added while the model was thinking was never read"


async def test_a_spent_budget_does_not_silence_the_case_for_good(monkeypatch):
    async with isolated_database() as session_factory:
        gaps = numbered_gaps(4)
        case_id, user_id, _ = await seeded_case(session_factory, trace=gaps.model_dump(mode="json"))
        async with session_factory() as db, db.begin():
            for extra in range(settings.chat_followup_max_rounds):
                other = CaseAnalysisResult(
                    case_id=case_id,
                    source_revision=1,
                    summary="Earlier.",
                    status="assessment",
                    trace_json=CaseAssessmentTrace(gaps=gaps.gaps).model_dump(mode="json"),
                    pipeline_config={},
                )
                db.add(other)
                await db.flush()
                db.add(
                    ChatMessage(
                        case_id=case_id,
                        ordinal=9 + extra,
                        role="assistant",
                        content="An earlier question.",
                        message_kind="followup_question",
                        gap_key=f"topic:spent-{extra}",
                        analysis_result_id=other.id,
                    )
                )
        standing = (await gap_questions(session_factory, case_id))[-1]
        production_pipeline(monkeypatch, gaps.gaps)

        replied = await run_case_analysis(
            case_id=case_id,
            user_id=user_id,
            session_factory=session_factory,
            continuing_followup=True,
        )

        assert not replied.needs_followup, "a reply must respect the spent budget"
        assert replied.result.trace_json["stop_reason"] == "max_rounds_reached", (
            "the stored analysis has to say why it stopped asking"
        )
        assert (await gap_questions(session_factory, case_id))[-1].id == standing.id

        asked_again = await run_case_analysis(
            case_id=case_id, user_id=user_id, session_factory=session_factory
        )

        assert asked_again.needs_followup, "the reader's own analysis may ask again"
        assert asked_again.question.id == standing.id, (
            "and it re-offers the standing question rather than adding one"
        )
        assert (await gap_questions(session_factory, case_id))[-1].id == standing.id


async def test_a_second_analysis_does_not_strand_the_standing_question(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, question_id = await seeded_case(session_factory)
        production_pipeline(monkeypatch, [CaseAnalysisGap.model_validate(GAP)])

        step = await run_case_analysis(
            case_id=case_id, user_id=user_id, session_factory=session_factory
        )

        assert step.needs_followup
        assert step.result.status == "assessment"
        assert step.question.id == question_id, "asked a new question over the standing one"
        asked = await gap_questions(session_factory, case_id)
        assert len(asked) == 1, f"{len(asked)} questions outstanding, expected 1"


async def test_assessment_row_asks_without_becoming_the_latest_analysis():
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory, trace=None)
        assessment = CaseAssessmentTrace.model_validate({"gaps": [GAP]})

        async def pipeline(_data):
            return AnalysisAdvance(
                assessment=assessment,
                decision=Ask(assessment.gaps[0]),
            )

        step = await run_case_analysis(
            case_id=case_id,
            user_id=user_id,
            session_factory=session_factory,
            pipeline=pipeline,
        )

        assert step.needs_followup
        assert step.result.status == "assessment"
        assert step.question.analysis_result_id == step.result.id
        async with session_factory() as db:
            case, latest = await get_latest_case_analysis(db, case_id=case_id, user_id=user_id)
            stored = await db.get(CaseAnalysisResult, step.result.id)
        assert stored is not None
        assert case.latest_analysis_result_id is None
        assert latest is None


async def test_assessment_round_keeps_serving_its_remaining_gaps():
    async with isolated_database() as session_factory:
        trace = CaseAssessmentTrace(gaps=numbered_gaps(4).gaps).model_dump(mode="json")
        case_id, user_id, first_id = await seeded_case(session_factory, trace=trace)
        async with session_factory() as db, db.begin():
            result = await db.scalar(
                select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
            )
            result.status = "assessment"
            case = await db.get(Case, case_id)
            case.latest_analysis_result_id = None

        produced, analysis = await post_case_message(
            case_id=case_id,
            user_id=user_id,
            request=ChatMessageCreate(content="Around two in the morning."),
            session_factory=session_factory,
        )

        assert analysis is None
        assert produced[0].in_reply_to_message_id == first_id
        assert produced[1].gap_key == "topic:2"
