from __future__ import annotations

import asyncio
import uuid
from functools import partial
from types import SimpleNamespace

import pytest
from case_chat_support import SETTLED, seeded_case
from httpx import ASGITransport, AsyncClient
from isolated_database import isolated_database
from sqlalchemy import select

import app.chat.reply as case_chat
import app.routers.chat as chat_router
from app.chat.answer import answer_case_question, answer_recorded_question
from app.chat.contracts import CaseAnalysisOutput
from app.errors import AppError, CaseAnalysisFailure
from app.main import app
from app.models.chat import ChatMessage
from app.models.sources import CaseSource
from app.schemas.chat import ChatMessageCreate
from app.services.auth.dependencies import get_current_user

pytestmark = pytest.mark.asyncio


async def settled_case(session_factory):
    case_id, user_id, _ = await seeded_case(session_factory, trace=SETTLED, asking=False)
    return case_id, user_id


async def test_asking_a_question_stores_both_messages():
    async with isolated_database() as session_factory:
        case_id, user_id = await settled_case(session_factory)

        async def fake_answer(**_kwargs):
            return CaseAnalysisOutput(answer="Only the encryption is recorded.", trace=None)

        question, answer = await answer_case_question(
            case_id=case_id,
            user_id=user_id,
            content="What do we know so far?",
            client_request_id="send-1",
            session_factory=session_factory,
            answer_request=fake_answer,
        )

        assert question.role == "user"
        assert question.client_request_id == "send-1"
        assert answer.role == "assistant"
        assert answer.content == "Only the encryption is recorded."
        assert answer.in_reply_to_message_id == question.id

        async with session_factory() as db:
            stored = list(
                (
                    await db.scalars(
                        select(ChatMessage)
                        .where(ChatMessage.case_id == case_id)
                        .order_by(ChatMessage.ordinal)
                    )
                ).all()
            )
        assert [message.role for message in stored] == ["user", "assistant"]


async def test_asking_question_without_analysis_stores_messages():
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory, trace=None, with_source=False)

        async def fake_answer(**kwargs):
            assert kwargs["result"] is None
            assert kwargs["sources"].sources == ()
            return CaseAnalysisOutput(
                answer="Here is general information about the case.", trace=None
            )

        question, answer = await answer_case_question(
            case_id=case_id,
            user_id=user_id,
            content="Can I ask before analyzing?",
            client_request_id="send-no-analysis",
            session_factory=session_factory,
            answer_request=fake_answer,
        )

        assert question.role == "user"
        assert question.analysis_result_id is None
        assert answer.role == "assistant"
        assert answer.content == "Here is general information about the case."
        assert answer.analysis_result_id is None
        assert answer.in_reply_to_message_id == question.id


def answering_with(monkeypatch, answer_request) -> None:
    monkeypatch.setattr(
        case_chat,
        "answer_case_question",
        partial(answer_case_question, answer_request=answer_request),
    )
    monkeypatch.setattr(
        case_chat,
        "answer_recorded_question",
        partial(answer_recorded_question, answer_request=answer_request),
    )


async def stored_roles(session_factory, case_id: uuid.UUID) -> list[str]:
    async with session_factory() as db:
        rows = await db.scalars(
            select(ChatMessage).where(ChatMessage.case_id == case_id).order_by(ChatMessage.ordinal)
        )
        return [message.role for message in rows]


async def test_retrying_the_same_send_returns_the_first_exchange(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id = await settled_case(session_factory)
        calls: list[str] = []

        async def fake_answer(**kwargs):
            calls.append(kwargs["question"])
            return CaseAnalysisOutput(answer="Answered once.", trace=None)

        answering_with(monkeypatch, fake_answer)
        send = ChatMessageCreate(content="What do we know so far?", client_request_id="send-1")
        first, _ = await case_chat.post_case_message(
            case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
        )
        again, _ = await case_chat.post_case_message(
            case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
        )

        assert [message.id for message in again] == [message.id for message in first]
        assert len(calls) == 1, "the retry asked the model a second time"


async def test_a_failed_answer_is_answered_when_the_send_is_retried(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id = await settled_case(session_factory)
        calls: list[str] = []

        async def flaky_answer(**kwargs):
            calls.append(kwargs["question"])
            if len(calls) == 1:
                raise CaseAnalysisFailure("chat_answer_timeout", "Analysis stage timed out")
            return CaseAnalysisOutput(answer="Answered on the retry.", trace=None)

        answering_with(monkeypatch, flaky_answer)
        send = ChatMessageCreate(content="What do we know so far?", client_request_id="send-1")
        with pytest.raises(AppError) as failure:
            await case_chat.post_case_message(
                case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
            )
        assert (failure.value.code, failure.value.status_code) == ("chat_answer_timeout", 502)
        assert await stored_roles(session_factory, case_id) == ["user"]

        retried, _ = await case_chat.post_case_message(
            case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
        )

        question, answer = retried
        assert question.client_request_id == "send-1"
        assert answer.content == "Answered on the retry."
        assert answer.in_reply_to_message_id == question.id
        assert calls == ["What do we know so far?", "What do we know so far?"]
        assert await stored_roles(session_factory, case_id) == ["user", "assistant"]


async def test_a_failed_answer_is_a_coded_bad_gateway_that_the_same_send_answers(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id = await settled_case(session_factory)
        calls: list[str] = []

        async def flaky_answer(**kwargs):
            calls.append(kwargs["question"])
            if len(calls) == 1:
                raise CaseAnalysisFailure("chat_answer_timeout", "Analysis stage timed out")
            return CaseAnalysisOutput(answer="Answered on the retry.", trace=None)

        answering_with(monkeypatch, flaky_answer)
        monkeypatch.setattr(
            chat_router,
            "send_case_message",
            partial(case_chat.send_case_message, session_factory=session_factory),
        )
        fastapi_app = app.app
        fastapi_app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user_id)
        send = {"content": "What do we know so far?", "client_request_id": "send-1"}
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/api/v1"
            ) as client:
                failed = await client.post(f"/cases/{case_id}/chat/messages", json=send)
                retried = await client.post(f"/cases/{case_id}/chat/messages", json=send)
        finally:
            fastapi_app.dependency_overrides.pop(get_current_user, None)

        assert failed.status_code == 502
        assert failed.json() == {
            "detail": {"code": "chat_answer_timeout", "message": "Analysis stage timed out"}
        }
        assert retried.status_code == 200
        body = retried.json()
        question, answer = body["messages"]
        assert question["content"] == "What do we know so far?"
        assert answer["content"] == "Answered on the retry."
        assert answer["in_reply_to_message_id"] == question["id"]
        assert (question["qa_id"], answer["qa_id"]) == (None, None)
        assert body["pending_question_id"] is None
        assert answer["metadata_json"] == {}
        assert len(calls) == 2
        assert await stored_roles(session_factory, case_id) == ["user", "assistant"]


async def test_a_retry_while_the_answer_is_pending_does_not_ask_twice(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id = await settled_case(session_factory)
        asked = asyncio.Event()
        release = asyncio.Event()
        calls: list[str] = []

        async def slow_answer(**kwargs):
            calls.append(kwargs["question"])
            asked.set()
            await release.wait()
            return CaseAnalysisOutput(answer="Answered once.", trace=None)

        answering_with(monkeypatch, slow_answer)
        send = ChatMessageCreate(content="What do we know so far?", client_request_id="send-1")
        first = asyncio.create_task(
            case_chat.post_case_message(
                case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
            )
        )
        await asked.wait()
        during, _ = await case_chat.post_case_message(
            case_id=case_id, user_id=user_id, request=send, session_factory=session_factory
        )
        release.set()
        answered, _ = await first

        assert [message.role for message in during] == ["user"]
        assert [message.role for message in answered] == ["user", "assistant"]
        assert len(calls) == 1
        assert await stored_roles(session_factory, case_id) == ["user", "assistant"]


async def test_a_reply_without_letters_is_answered_in_the_case_language():
    async with isolated_database() as session_factory:
        case_id, user_id = await settled_case(session_factory)
        async with session_factory() as db, db.begin():
            db.add(
                CaseSource(
                    case_id=case_id,
                    source_kind="narrative",
                    exact_text="ผู้เสียหายแจ้งว่าไฟล์ในไดรฟ์กลางถูกเข้ารหัส",
                )
            )
        languages: dict[str, str] = {}

        async def fake_answer(**kwargs):
            languages[kwargs["question"]] = kwargs["language"]
            return CaseAnalysisOutput(answer="Answered.", trace=None)

        for sent, content in enumerate(("02:00", "Who reported it?", "ใครเป็นผู้แจ้ง")):
            await answer_case_question(
                case_id=case_id,
                user_id=user_id,
                content=content,
                client_request_id=f"send-{sent}",
                session_factory=session_factory,
                answer_request=fake_answer,
            )

        assert languages == {
            "02:00": "thai",
            "Who reported it?": "english",
            "ใครเป็นผู้แจ้ง": "thai",
        }


async def test_chat_route_is_reachable():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        response = await client.post(
            f"/cases/{uuid.uuid4()}/chat/messages", json={"content": "hello"}
        )
    assert response.status_code in {401, 403}
