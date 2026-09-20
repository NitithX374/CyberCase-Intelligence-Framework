"""Case documents, current extractions, and received Case sources."""

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
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.chat import ChatMessage


class CaseDocument(Base):
    __tablename__ = "case_documents"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_documents"),
        CheckConstraint("size_bytes >= 0", name="ck_case_documents_size_nonnegative"),
        Index("ix_case_documents_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", name="fk_case_documents_case_id", ondelete="CASCADE"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(160), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    # Deferred: every query that reaches a document through CaseSource wants its
    # filename, and loading the row dragged the whole upload along with it. The
    # download route is the only reader, and it undefers the column by name.
    content_bytes: Mapped[bytes] = mapped_column(LargeBinary, nullable=False, deferred=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    case: Mapped[Case] = relationship("Case", back_populates="documents")
    extractions: Mapped[list[DocumentExtraction]] = relationship(
        back_populates="document", cascade="all, delete-orphan", passive_deletes=True
    )
    sources: Mapped[list[CaseSource]] = relationship(
        back_populates="document", passive_deletes=True
    )


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_document_extractions"),
        Index("ix_document_extractions_document_id_created_at", "document_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_documents.id", name="fk_document_extractions_document_id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    config_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    warnings_json: Mapped[list[object]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    document: Mapped[CaseDocument] = relationship(back_populates="extractions")


class CaseSource(Base):
    __tablename__ = "case_sources"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_sources"),
        CheckConstraint(
            "source_kind IN ('document', 'narrative', 'followup_answer')",
            name="ck_case_sources_kind",
        ),
        Index("ix_case_sources_case_id_created_at", "case_id", "created_at"),
        Index("ix_case_sources_document_id", "document_id"),
        Index("ix_case_sources_origin_message_id", "origin_message_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", name="fk_case_sources_case_id", ondelete="CASCADE"),
        nullable=False,
    )
    source_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("case_documents.id", name="fk_case_sources_document_id", ondelete="SET NULL"),
        nullable=True,
    )
    origin_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chat_messages.id", name="fk_case_sources_origin_message_id", ondelete="SET NULL"
        ),
        nullable=True,
    )
    exact_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    source_metadata_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case: Mapped[Case] = relationship("Case", back_populates="sources")
    document: Mapped[CaseDocument | None] = relationship(back_populates="sources")
    origin_message: Mapped[ChatMessage | None] = relationship()


__all__ = [
    "CaseDocument",
    "DocumentExtraction",
    "CaseSource",
]
