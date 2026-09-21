"""Concurrent chat sends cannot answer one standing question twice."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from isolated_database import isolated_database
from sqlalchemy import select

from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatMessageCreate
from app.services.chat.case_chat import post_case_message

pytestmark = pytest.mark.asyncio


TRACE = {
    "version": "case_analysis_trace_v1",
    "analysis_mode": "case_overview",
    "validation_status": "validated",
    "summary": "The incident time is not established.",
    "claims": [],
    "gaps": [
        {
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
    ],
    "mitre_associations": [],
}


async def seeded_case(session_factory) -> tuple[uuid.UUID, uuid.UUID]:
    async with session_factory() as db, db.begin():
        user = User(
            email="chat-race@example.com",
            name="Analyst",
            password_hash="x",
            oauth_provider="password",
            oauth_subject_id="chat-race@example.com",
        )
        db.add(user)
        await db.flush()
        case = Case(user_id=user.id, title="Concurrent chat case", source_revision=1)
        db.add(case)
        await db.flush()
        analysis = CaseAnalysisResult(
            case_id=case.id,
            source_revision=1,
            answer="The incident time is not established.",
            summary="The incident time is not established.",
            trace_json=TRACE,
            pipeline_config={},
            external_context_json={},
        )
        db.add(analysis)
        await db.flush()
        db.add(
            ChatMessage(
                case_id=case.id,
                ordinal=1,
                role="assistant",
                content="When did the incident happen?",
                message_kind="followup_question",
                gap_key="topic:incident-time",
                analysis_result_id=analysis.id,
            )
        )
        return case.id, user.id


async def test_concurrent_sends_record_one_followup_answer(monkeypatch):
    async with isolated_database() as session_factory:
        case_id, user_id = await seeded_case(session_factory)
        dispatches = asyncio.Barrier(2)
        ordinary_replies = 0

        import app.services.chat.case_chat as module

        original_standing_question = module.standing_question

        async def synchronized_dispatch(*args, **kwargs):
            question = await original_standing_question(*args, **kwargs)
            await dispatches.wait()
            return question

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

        monkeypatch.setattr(module, "standing_question", synchronized_dispatch)
        monkeypatch.setattr(module, "answer_case_question", ordinary_reply)
        monkeypatch.setattr(module, "run_case_analysis", no_analysis)

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
