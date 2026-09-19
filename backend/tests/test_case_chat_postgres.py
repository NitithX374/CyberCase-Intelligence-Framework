"""Sending a chat message, over HTTP, against a real database.

The ask path had no coverage, which is how a message that could never be stored
reached main: the service passed a column the model did not declare.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from isolated_database import isolated_database
from sqlalchemy import select

from app.main import app
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.models.sources import CaseSource
from app.models.user import User
from app.services.case_analysis.contracts import CaseAnalysisOutput
from app.services.case_workflow import answer_case_question

pytestmark = pytest.mark.asyncio

TRACE = {
    "version": "case_analysis_trace_v1",
    "analysis_mode": "case_overview",
    "validation_status": "validated",
    "summary": "Files on the shared drive were reported encrypted.",
    "claims": [],
    "gaps": [],
    "mitre_associations": [],
}


async def seeded_case(session_factory) -> tuple[uuid.UUID, uuid.UUID]:
    async with session_factory() as db, db.begin():
        user = User(
            email="chat@example.com",
            name="Analyst",
            password_hash="x",
            oauth_provider="password",
            oauth_subject_id="chat@example.com",
        )
        db.add(user)
        await db.flush()
        case = Case(user_id=user.id, title="Chat case", source_revision=1)
        db.add(case)
        await db.flush()
        db.add(
            CaseSource(
                case_id=case.id,
                source_kind="narrative",
                exact_text="Files on the shared drive were reported encrypted.",
            )
        )
        await db.flush()
        analysis = CaseAnalysisResult(
            case_id=case.id,
            source_revision=1,
            answer="Files were encrypted.",
            summary="Files were encrypted.",
            trace_json=TRACE,
            pipeline_config={"version": "case_analysis_v1"},
            external_context_json={},
        )
        db.add(analysis)
        await db.flush()
        case.latest_analysis_result_id = analysis.id
        return case.id, user.id


async def test_asking_a_question_stores_both_messages():
    """The question and the answer are written, and the request id is kept."""

    async with isolated_database() as session_factory:
        case_id, user_id = await seeded_case(session_factory)

        async def fake_answer(**_kwargs):
            return CaseAnalysisOutput(answer="Only the encryption is recorded.", trace=None)

        question, answer = await answer_case_question(
            case_id=case_id,
            user_id=user_id,
            content="What do we know so far?",
            response_language="english",
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


async def test_retrying_the_same_send_returns_the_first_exchange():
    """A client that timed out and retried gets its answer, not a second one."""

    async with isolated_database() as session_factory:
        case_id, user_id = await seeded_case(session_factory)
        calls: list[str] = []

        async def fake_answer(**kwargs):
            calls.append(str(kwargs.get("user_message")))
            return CaseAnalysisOutput(answer="Answered once.", trace=None)

        send = {
            "case_id": case_id,
            "user_id": user_id,
            "content": "What do we know so far?",
            "response_language": "english",
            "client_request_id": "send-1",
            "session_factory": session_factory,
            "answer_request": fake_answer,
        }
        first_question, first_answer = await answer_case_question(**send)
        again_question, again_answer = await answer_case_question(**send)

        assert again_question.id == first_question.id
        assert again_answer.id == first_answer.id
        assert len(calls) == 1, "the retry asked the model a second time"


async def test_chat_route_is_reachable():
    """The route exists and rejects an unauthenticated send."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        response = await client.post(
            f"/cases/{uuid.uuid4()}/chat/messages", json={"content": "hello"}
        )
    assert response.status_code in {401, 403}
