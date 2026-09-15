"""Case-owned chat domain services."""
from app.services.chat.clarification_chain import (
    ClarificationChain,
    reconstruct_clarification_chain,
)

__all__ = [
    "CaseChatError",
    "createCaseChatMessageAndRun",
    "getCaseChat",
    "ClarificationChain",
    "reconstruct_clarification_chain",
]


def __getattr__(name: str):
    if name in {"CaseChatError", "createCaseChatMessageAndRun", "getCaseChat"}:
        from app.services.chat.caseChat import (
            CaseChatError,
            createCaseChatMessageAndRun,
            getCaseChat,
        )

        return {
            "CaseChatError": CaseChatError,
            "createCaseChatMessageAndRun": createCaseChatMessageAndRun,
            "getCaseChat": getCaseChat,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
