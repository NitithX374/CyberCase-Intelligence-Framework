"""Persistent chat messages and thread compatibility view."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_chat_messages"),
        UniqueConstraint(
            "case_id",
            "ordinal",
            name="uq_chat_messages_case_id_ordinal",
        ),
        CheckConstraint(
            "ordinal > 0",
            name="ck_chat_messages_ordinal_positive",
        ),
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_chat_messages_role",
        ),
        CheckConstraint(
            "message_kind IN ('conversation', 'followup_question', 'followup_answer')",
            name="ck_chat_messages_message_kind",
        ),
        Index("ix_chat_messages_case_id_ordinal", "case_id", "ordinal"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "cases.id",
            name="fk_chat_messages_case_id_cases",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_context_id: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
    )
    message_kind: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="conversation",
        server_default=text("'conversation'"),
    )
    analysis_result_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("case_analysis_results.id", name="fk_chat_messages_analysis_result_id", ondelete="SET NULL"),
        nullable=True,
    )
    in_reply_to_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_messages.id", name="fk_chat_messages_in_reply_to_message_id", ondelete="SET NULL"),
        nullable=True,
    )
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    case: Mapped["Case"] = relationship(
        "Case",
        back_populates="chat_messages",
        foreign_keys=[case_id],
    )
    in_reply_to_message: Mapped["ChatMessage | None"] = relationship(
        "ChatMessage", remote_side=[id], foreign_keys=[in_reply_to_message_id]
    )

    def __init__(self, **kwargs: Any) -> None:
        if "case_id" not in kwargs and "thread_id" in kwargs:
            kwargs["case_id"] = kwargs.pop("thread_id")
        super().__init__(**kwargs)

    @property
    def thread_id(self) -> uuid.UUID:
        return self.case_id

    @thread_id.setter
    def thread_id(self, val: uuid.UUID) -> None:
        self.case_id = val


class ChatThread:
    """In-memory compatibility view of a Case's chat state."""

    def __init__(
        self,
        id: uuid.UUID | None = None,
        case_id: uuid.UUID | None = None,
        title: str = "New case",
        user_id: uuid.UUID | None = None,
        next_message_ordinal: int = 1,
        case: Case | None = None,
        messages: list[ChatMessage] | None = None,
        status: str = "idle",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        **kwargs: Any,
    ) -> None:
        self.id = id or case_id or uuid.uuid4()
        self.case_id = case_id or self.id
        self.title = title
        self.user_id = user_id
        self.next_message_ordinal = next_message_ordinal
        self.case = case
        self.messages = messages if messages is not None else []
        self._status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @property
    def status(self) -> str:
        if self._status and self._status != "idle":
            return self._status
        if self.messages:
            answered_ids = {
                m.in_reply_to_message_id
                for m in self.messages
                if getattr(m, "in_reply_to_message_id", None) is not None
            }
            has_pending = any(
                getattr(m, "message_kind", None) == "followup_question" and m.id not in answered_ids
                for m in self.messages
            )
            if has_pending:
                return "awaiting_followup"
        if self.case is not None and getattr(self.case, "latest_analysis_result_id", None) is not None:
            return "answered"
        return self._status or "idle"

    @status.setter
    def status(self, val: Any) -> None:
        self._status = str(val) if val is not None else "idle"


__all__ = ["ChatMessage", "ChatThread"]
