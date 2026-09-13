"""Chat Thread and Message Domain Services."""

from app.services.chat.chatService import (
    ChatService,
)
from app.services.chat.clarification_chain import (
    ClarificationChain,
    reconstruct_clarification_chain,
)

__all__ = [
    "CaseChatError",
    "ChatService",
    "createCaseChatMessageAndRun",
    "ClarificationChain",
    "reconstruct_clarification_chain",
]


def __getattr__(name: str):
    if name in {"CaseChatError", "createCaseChatMessageAndRun"}:
        from app.services.chat.caseChat import (
            CaseChatError,
            createCaseChatMessageAndRun,
        )

        return {
            "CaseChatError": CaseChatError,
            "createCaseChatMessageAndRun": createCaseChatMessageAndRun,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
