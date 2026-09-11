import asyncio
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import BackgroundTasks, HTTPException

from app.routers.chat import create_chat_message
from app.schemas.chat import ChatMessageCreate


def test_unlinked_chat_message_is_read_only_after_execution_retirement():
    async def exercise():
        thread_id = uuid4()
        request = ChatMessageCreate(
            content="Historical request",
            idempotency_key="historical-request",
        )
        thread = SimpleNamespace(id=thread_id, case=None)
        with (
            patch(
                "app.routers.chat.ChatService.get_thread",
                new=AsyncMock(return_value=thread),
            ),
        ):
            with pytest.raises(HTTPException) as error:
                await create_chat_message(
                    thread_id,
                    request,
                    BackgroundTasks(),
                    db=AsyncMock(),
                    user=SimpleNamespace(id=uuid4()),
                )

        assert error.value.status_code == 410
        assert error.value.detail["code"] == "legacy_chat_execution_retired"

    asyncio.run(exercise())
