from __future__ import annotations

import asyncio
from functools import partial

import pytest
from case_chat_support import SETTLED, seeded_case
from isolated_database import isolated_database
from sqlalchemy import select, text

import app.services.chat.case_chat as case_chat
from app.models.case import Case
from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageCreate
from app.services.analysis.contracts import CaseAnalysisOutput
from app.services.chat.case_chat import post_case_message
from app.services.workflow.answer_question import answer_case_question
from app.services.workflow.shared import next_ordinal

pytestmark = pytest.mark.asyncio


async def test_concurrent_sends_record_one_followup_answer(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory, with_source=False)
        both_arrived = asyncio.Barrier(2)
        ordinary_replies = 0
        original_owned_case = case_chat.owned_case

        async def owned_case_together(*args, lock=False, **kwargs):
            if lock:
                await both_arrived.wait()
            return await original_owned_case(*args, lock=lock, **kwargs)

        async def ordinary_reply(**kwargs):
            nonlocal ordinary_replies
            ordinary_replies += 1
            question = ChatMessage(
                case_id=kwargs["case_id"], ordinal=100, role="user", content="ordinary"
            )
            answer = ChatMessage(
                case_id=kwargs["case_id"],
                ordinal=101,
                role="assistant",
                content="ordinary answer",
            )
            return question, answer

        async def no_analysis(**_kwargs):
            return None

        monkeypatch.setattr(case_chat, "owned_case", owned_case_together)
        monkeypatch.setattr(case_chat, "answer_case_question", ordinary_reply)
        monkeypatch.setattr(case_chat, "run_case_analysis", no_analysis)

        await asyncio.gather(
            *(
                post_case_message(
                    case_id=case_id,
                    user_id=user_id,
                    request=ChatMessageCreate(
                        content=f"Answer {index}", client_request_id=f"send-{index}"
                    ),
                    session_factory=session_factory,
                )
                for index in (1, 2)
            )
        )

        async with session_factory() as db:
            answers = list(
                await db.scalars(
                    select(ChatMessage).where(
                        ChatMessage.case_id == case_id,
                        ChatMessage.message_kind == "followup_answer",
                    )
                )
            )

        assert len(answers) == 1
        assert ordinary_replies == 1


async def blocked_by(session_factory, blocker: int) -> None:
    for _ in range(400):
        async with session_factory() as observer:
            waiting = await observer.scalar(
                text(
                    "SELECT count(*) FROM pg_stat_activity WHERE :pid = ANY(pg_blocking_pids(pid))"
                ),
                {"pid": blocker},
            )
        if waiting:
            return
        await asyncio.sleep(0.025)
    raise AssertionError("the answer write never waited for the case")


async def test_an_answer_waits_for_a_case_write_in_flight_and_takes_the_next_ordinal():
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory, with_source=False)
        asked = asyncio.Event()
        release = asyncio.Event()

        async def slow_answer(**_kwargs):
            asked.set()
            await release.wait()
            return CaseAnalysisOutput(answer="Answered.", trace=None)

        answering = asyncio.create_task(
            answer_case_question(
                case_id=case_id,
                user_id=user_id,
                content="What happened?",
                session_factory=session_factory,
                answer_request=slow_answer,
            )
        )
        await asked.wait()
        async with session_factory() as db, db.begin():
            await db.scalar(select(Case).where(Case.id == case_id).with_for_update())
            db.add(
                ChatMessage(
                    case_id=case_id,
                    ordinal=await next_ordinal(db, case_id),
                    role="assistant",
                    content="Written by an analysis while the answer was pending.",
                )
            )
            await db.flush()
            release.set()
            await blocked_by(session_factory, await db.scalar(text("SELECT pg_backend_pid()")))
        question, answer = await answering

        assert (question.ordinal, answer.ordinal) == (2, 4)


async def sent_together(monkeypatch, session_factory, case_id, user_id):
    looked_up = asyncio.Barrier(2)
    lookups = 0
    sent_message = case_chat.sent_message

    async def looked_up_together(*args, **kwargs):
        nonlocal lookups
        found = await sent_message(*args, **kwargs)
        lookups += 1
        if lookups <= 2:
            await looked_up.wait()
        return found

    monkeypatch.setattr(case_chat, "sent_message", looked_up_together)
    send = ChatMessageCreate(content="Around two in the morning.", client_request_id="send-1")
    return await asyncio.gather(
        *(
            post_case_message(
                case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
            )
            for _ in range(2)
        )
    )


async def stored_kinds(session_factory, case_id) -> list[str]:
    async with session_factory() as db:
        rows = await db.scalars(
            select(ChatMessage).where(ChatMessage.case_id == case_id).order_by(ChatMessage.ordinal)
        )
        return [message.message_kind for message in rows]


async def test_one_question_sent_twice_at_once_is_asked_once(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(
            session_factory, trace=SETTLED, asking=False, with_source=False
        )
        asked: list[str] = []

        async def answer(**kwargs):
            asked.append(kwargs["question"])
            return CaseAnalysisOutput(answer="Answered once.", trace=None)

        monkeypatch.setattr(
            case_chat, "answer_case_question", partial(answer_case_question, answer_request=answer)
        )
        replies = await sent_together(monkeypatch, session_factory, case_id, user_id)

        assert [step for _, step in replies] == [None, None]
        assert asked == ["Around two in the morning."]
        assert await stored_kinds(session_factory, case_id) == ["conversation", "conversation"]


async def test_one_answer_sent_twice_at_once_is_recorded_and_analysed_once(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory, with_source=False)
        analyses: list[bool] = []

        async def analysed(**kwargs):
            analyses.append(kwargs["continuing_followup"])

        monkeypatch.setattr(case_chat, "run_case_analysis", analysed)
        replies = await sent_together(monkeypatch, session_factory, case_id, user_id)

        assert len(replies) == 2
        assert analyses == [True]
        assert await stored_kinds(session_factory, case_id) == [
            "followup_question",
            "followup_answer",
        ]
