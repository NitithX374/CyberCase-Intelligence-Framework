import asyncio
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.case import Case
from app.models.chat import ChatThread
from app.services.chat.chatService import ChatService


def _service_for(thread: ChatThread) -> ChatService:
    result = Mock()
    result.scalar_one_or_none.return_value = thread
    database = Mock()
    database.execute = AsyncMock(return_value=result)
    return ChatService(database)


def test_case_link_uses_proven_relation_even_when_ids_differ():
    async def exercise():
        thread = ChatThread(id=uuid4(), user_id=None)
        case = Case(id=uuid4(), user_id=None, title="Owned Case")
        thread.case = case

        link = await _service_for(thread).get_case_link(thread.id, user_id=None)

        assert link.status == "linked"
        assert link.case_id == case.id
        assert link.case_id != thread.id

    asyncio.run(exercise())


def test_case_link_reports_historical_unavailable_without_relation():
    async def exercise():
        thread = ChatThread(id=uuid4(), user_id=None)

        link = await _service_for(thread).get_case_link(thread.id, user_id=None)

        assert link.status == "historical_unavailable"
        assert link.case_id is None

    asyncio.run(exercise())


def test_case_link_hides_missing_thread():
    async def exercise():
        service = _service_for(None)

        with pytest.raises(HTTPException) as error:
            await service.get_case_link(uuid4(), user_id=None)

        assert error.value.status_code == 404

    asyncio.run(exercise())


def test_case_link_hides_thread_owned_by_another_user():
    async def exercise():
        thread = ChatThread(id=uuid4(), user_id=uuid4())
        service = _service_for(thread)

        with pytest.raises(HTTPException) as error:
            await service.get_case_link(thread.id, user_id=uuid4())

        assert error.value.status_code == 404

    asyncio.run(exercise())
