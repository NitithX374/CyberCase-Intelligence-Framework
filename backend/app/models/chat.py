"""Persistent chat threads and messages."""

from __future__ import annotations

import uuid
from datetime import datetime
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


class ChatThread(Base):
    __tablename__ = "chat_threads"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_chat_threads"),
        UniqueConstraint("case_id", name="uq_chat_threads_case_id"),
        CheckConstraint(
            "status IN ('idle', 'processing', 'awaiting_followup', 'answered', 'failed')",
            name="ck_chat_threads_status",
        ),
        CheckConstraint(
            "next_message_ordinal > 0",
            name="ck_chat_threads_next_message_ordinal_positive",
        ),
        Index("ix_chat_threads_case_id", "case_id"),
        Index("ix_chat_threads_updated_at", "updated_at"),
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
            name="fk_chat_threads_case_id_cases",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="idle",
        server_default=text("'idle'"),
    )
    next_message_ordinal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __init__(self, **kwargs: Any) -> None:
        title = kwargs.pop("title", None)
        user_id = kwargs.pop("user_id", None)
        if "case_id" not in kwargs and "id" in kwargs:
            kwargs["case_id"] = kwargs["id"]
        elif "id" not in kwargs and "case_id" in kwargs:
            kwargs["id"] = kwargs["case_id"]
        super().__init__(**kwargs)
        self._title = title or "New case"
        self._user_id = user_id

    @property
    def user_id(self) -> uuid.UUID | None:
        case = self.__dict__.get("case")
        if case is not None and getattr(case, "user_id", None) is not None:
            return case.user_id
        return getattr(self, "_user_id", None)

    @user_id.setter
    def user_id(self, val: uuid.UUID | None) -> None:
        self._user_id = val
        case = self.__dict__.get("case")
        if case is not None:
            case.user_id = val

    @property
    def title(self) -> str:
        case = self.__dict__.get("case")
        if case is not None and getattr(case, "title", None) is not None:
            return case.title
        return getattr(self, "_title", "New case")

    @title.setter
    def title(self, val: str) -> None:
        self._title = val
        case = self.__dict__.get("case")
        if case is not None:
            case.title = val

    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatMessage.ordinal",
    )
    case: Mapped["Case | None"] = relationship(
        "Case",
        back_populates="chat_thread",
        foreign_keys=[case_id],
        uselist=False,
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_chat_messages"),
        UniqueConstraint(
            "thread_id",
            "ordinal",
            name="uq_chat_messages_thread_id_ordinal",
        ),
        UniqueConstraint(
            "thread_id",
            "id",
            name="uq_chat_messages_thread_id_id",
        ),
        CheckConstraint(
            "ordinal > 0",
            name="ck_chat_messages_ordinal_positive",
        ),
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_chat_messages_role",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chat_threads.id",
            name="fk_chat_messages_thread_id_chat_threads",
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

    thread: Mapped[ChatThread] = relationship(back_populates="messages")


__all__ = ["ChatMessage", "ChatThread"]
