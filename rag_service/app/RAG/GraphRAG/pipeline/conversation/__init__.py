"""The case conversation: the RAG service used on its own.

``POST /query`` is stateless and stays so. This package is what sits on top of
it when there is no backend in front: one conversation per case, kept in
memory, served by ``routers/conversation.py`` when ``STANDALONE_CHAT`` is on.
"""

from .case_chat import CaseChat, ConversationBusy, case_with_facts
from .store import (
    ANALYSIS,
    ANSWER,
    ASSISTANT,
    CASE,
    FACTS,
    QUESTION,
    USER,
    Analysis,
    Conversation,
    ConversationStore,
    Turn,
)

__all__ = [
    "ANALYSIS",
    "ANSWER",
    "ASSISTANT",
    "CASE",
    "FACTS",
    "QUESTION",
    "USER",
    "Analysis",
    "CaseChat",
    "Conversation",
    "ConversationBusy",
    "ConversationStore",
    "Turn",
    "case_with_facts",
]
