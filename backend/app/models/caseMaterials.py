"""Case documents, extraction revisions, admitted evidence, and snapshots."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
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
        UUID(as_uuid=True), ForeignKey("cases.id", name="fk_case_documents_case_id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(160), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    content_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    content_bytes: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="documents")
    extractions: Mapped[list[DocumentExtraction]] = relationship(
        back_populates="document", cascade="all, delete-orphan", passive_deletes=True
    )
    evidence_sources: Mapped[list[EvidenceSource]] = relationship(
        back_populates="document", passive_deletes=True
    )


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_document_extractions"),
        UniqueConstraint("document_id", "revision", name="uq_document_extractions_document_revision"),
        CheckConstraint("revision > 0", name="ck_document_extractions_revision_positive"),
        Index("ix_document_extractions_document_id_created_at", "document_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_documents.id", name="fk_document_extractions_document_id", ondelete="CASCADE"), nullable=False
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    config_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    provenance_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    warnings_json: Mapped[list[object]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document: Mapped[CaseDocument] = relationship(back_populates="extractions")
    evidence_revisions: Mapped[list[EvidenceRevision]] = relationship(back_populates="extraction")


class EvidenceSource(Base):
    __tablename__ = "case_evidence_sources"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_evidence_sources"),
        CheckConstraint(
            "source_kind IN ('reviewed_document', 'narrative', 'clarification_answer', 'explicit_chat_addition', 'legacy_unbound')",
            name="ck_case_evidence_sources_kind",
        ),
        Index("ix_case_evidence_sources_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", name="fk_case_evidence_sources_case_id", ondelete="CASCADE"), nullable=False
    )
    source_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_documents.id", name="fk_case_evidence_sources_document_id", ondelete="SET NULL"), nullable=True
    )
    origin_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_messages.id", name="fk_case_evidence_sources_origin_message_id", ondelete="SET NULL"), nullable=True
    )
    source_metadata_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="evidence_sources")
    document: Mapped[CaseDocument | None] = relationship(back_populates="evidence_sources")
    origin_message: Mapped["ChatMessage | None"] = relationship()
    revisions: Mapped[list[EvidenceRevision]] = relationship(
        back_populates="source", cascade="all, delete-orphan", passive_deletes=True
    )


class EvidenceRevision(Base):
    __tablename__ = "case_evidence_revisions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_evidence_revisions"),
        UniqueConstraint("source_id", "revision", name="uq_case_evidence_revisions_source_revision"),
        CheckConstraint("revision > 0", name="ck_case_evidence_revisions_revision_positive"),
        Index("ix_case_evidence_revisions_source_id_revision", "source_id", "revision"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_evidence_sources.id", name="fk_case_evidence_revisions_source_id", ondelete="CASCADE"), nullable=False
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    exact_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    provenance_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    extraction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_extractions.id", name="fk_case_evidence_revisions_extraction_id", ondelete="SET NULL"), nullable=True
    )
    admitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source: Mapped[EvidenceSource] = relationship(back_populates="revisions")
    extraction: Mapped[DocumentExtraction | None] = relationship(back_populates="evidence_revisions")


class CaseEvidenceSnapshot(Base):
    __tablename__ = "case_evidence_snapshots"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_evidence_snapshots"),
        UniqueConstraint("case_id", "evidence_revision", "manifest_sha256", name="uq_case_evidence_snapshots_identity"),
        CheckConstraint("evidence_revision >= 0", name="ck_case_evidence_snapshots_revision_nonnegative"),
        Index("ix_case_evidence_snapshots_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", name="fk_case_evidence_snapshots_case_id", ondelete="CASCADE"), nullable=False
    )
    evidence_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    format_version: Mapped[str] = mapped_column(String(40), nullable=False)
    manifest_json: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="evidence_snapshots")


__all__ = [
    "CaseDocument",
    "CaseEvidenceSnapshot",
    "DocumentExtraction",
    "EvidenceRevision",
    "EvidenceSource",
]
