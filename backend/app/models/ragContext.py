"""Durable retrieval context bound one-to-one to the chat run that produced it."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
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


class RagContext(Base):
    __tablename__ = "rag_contexts"
    __table_args__ = (
        PrimaryKeyConstraint(
            "retrieval_context_id",
            name="pk_rag_contexts",
        ),
        UniqueConstraint("run_id", name="uq_rag_contexts_run_id"),
    )

    retrieval_context_id: Mapped[str] = mapped_column(
        String(160),
        primary_key=True,
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chat_threads.id",
            name="fk_rag_contexts_thread_id_chat_threads",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chat_runs.id",
            name="fk_rag_contexts_run_id_chat_runs",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    context: Mapped[str] = mapped_column(Text, nullable=False)
    mitre_table: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    run = relationship("ChatRun", back_populates="rag_context")


__all__ = ["RagContext"]
