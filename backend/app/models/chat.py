"""Persistent chat messages and thread compatibility view."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

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
        Index(
            "ux_chat_messages_case_id_client_request_id",
            "case_id",
            "client_request_id",
            unique=True,
            postgresql_where=text("client_request_id IS NOT NULL"),
        ),
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
    # Set by the client so a retried send cannot create a second message.
    client_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
    # Set on an assistant message that asks about one analysis gap. Null on
    # every other message, which is what makes "already asked" a single query.
    gap_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    analysis_result_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_analysis_results.id",
            name="fk_chat_messages_analysis_result_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    in_reply_to_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chat_messages.id", name="fk_chat_messages_in_reply_to_message_id", ondelete="SET NULL"
        ),
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

    case: Mapped[Case] = relationship(
        "Case",
        back_populates="chat_messages",
        foreign_keys=[case_id],
    )
    in_reply_to_message: Mapped[ChatMessage | None] = relationship(
        "ChatMessage", remote_side=[id], foreign_keys=[in_reply_to_message_id]
    )


__all__ = ["ChatMessage"]
