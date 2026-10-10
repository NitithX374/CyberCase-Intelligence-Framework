"""What a case conversation holds, and where conversations are kept.

One conversation is one case: the case file, the analysis the served pipeline
made of it, and the turns about it. They live in this process's memory —
nothing is written to disk, and a restart forgets them all.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from ...config import CONVERSATION_CAPACITY, CONVERSATION_TTL_SECONDS

# Who said a turn, and what kind of turn it is. A user turn is the case file,
# facts added to it later, or a question. An assistant turn is an analysis
# (the pipeline ran) or an answer (it did not).
USER, ASSISTANT = "user", "assistant"
CASE, FACTS, QUESTION = "case", "facts", "question"
ANALYSIS, ANSWER = "analysis", "answer"


@dataclass
class Analysis:
    """What one run of the served pipeline left behind for a case."""

    # The text that was analysed: the case file, plus any facts added since.
    # The table's evidence offsets index into this string and no other.
    case_text: str
    answer: str
    context: str
    mitre_table: list = field(default_factory=list)  # list[MitreTableRow]
    legal_reference: Any = None  # LegalReferenceResult, when the caller fetched one


@dataclass
class Turn:
    role: str
    kind: str
    text: str
    created_at: float = field(default_factory=time.time)
    # Assistant turns only: how long the reply took, and what it rests on
    # beyond the case's own analysis.
    seconds: float = 0.0
    lookup_queries: list[str] = field(default_factory=list)  # asked of the ATT&CK knowledge base
    lookup_ids: list[str] = field(default_factory=list)  # ATT&CK entities fetched by their ID
    # An analysis that replaced an earlier one: technique rows that came and went.
    rows_added: list[str] = field(default_factory=list)
    rows_removed: list[str] = field(default_factory=list)


@dataclass
class Conversation:
    case_file: str  # as first submitted, without later facts
    analysis: Analysis
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    facts: list[str] = field(default_factory=list)
    turns: list[Turn] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    # Held for the length of one message. Two messages to the same
    # conversation would read and write the same turns and analysis.
    busy: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)


class ConversationStore:
    """Conversations by id, forgetting the idle and, past capacity, the oldest."""

    def __init__(
        self,
        ttl_seconds: float = CONVERSATION_TTL_SECONDS,
        capacity: int = CONVERSATION_CAPACITY,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._ttl = ttl_seconds
        self._capacity = capacity
        self._clock = clock
        self._lock = threading.Lock()
        self._conversations: dict[str, Conversation] = {}

    def __len__(self) -> int:
        with self._lock:
            return len(self._conversations)

    def add(self, conversation: Conversation) -> None:
        with self._lock:
            self._forget_idle()
            conversation.last_used_at = self._clock()
            self._conversations[conversation.id] = conversation
            # A conversation in the middle of a message is never the one to go.
            spare = sorted(
                (c for c in self._conversations.values()
                 if c is not conversation and not c.busy.locked()),
                key=lambda c: c.last_used_at,
            )
            for oldest in spare[: max(0, len(self._conversations) - self._capacity)]:
                del self._conversations[oldest.id]

    def get(self, conversation_id: str) -> Optional[Conversation]:
        """The conversation, counted as used now; None when unknown or forgotten."""
        with self._lock:
            self._forget_idle()
            conversation = self._conversations.get(conversation_id)
            if conversation is not None:
                conversation.last_used_at = self._clock()
            return conversation

    def delete(self, conversation_id: str) -> bool:
        with self._lock:
            return self._conversations.pop(conversation_id, None) is not None

    def _forget_idle(self) -> None:
        cutoff = self._clock() - self._ttl
        for conversation in list(self._conversations.values()):
            if conversation.last_used_at < cutoff and not conversation.busy.locked():
                del self._conversations[conversation.id]
