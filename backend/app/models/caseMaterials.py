"""Case documents, current extractions, and currently admitted evidence sources."""

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
        UUID(as_uuid=True), ForeignKey("cases.id", name="fk_case_documents_case_id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(160), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
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
        Index("ix_document_extractions_document_id_created_at", "document_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_documents.id", name="fk_document_extractions_document_id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    config_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    warnings_json: Mapped[list[object]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document: Mapped[CaseDocument] = relationship(back_populates="extractions")


class EvidenceSource(Base):
    __tablename__ = "case_evidence_sources"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_evidence_sources"),
        CheckConstraint(
            "source_kind IN ('reviewed_document', 'narrative', 'followup_answer')",
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
    exact_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    source_metadata_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="evidence_sources")
    document: Mapped[CaseDocument | None] = relationship(back_populates="evidence_sources")
    origin_message: Mapped["ChatMessage | None"] = relationship()

    @property
    def revisions(self) -> list[EvidenceRevision]:
        return [
            EvidenceRevision(
                id=self.id,
                source_id=self.id,
                extraction_id=uuid.UUID(self.provenance_json["extraction_id"]) if isinstance(self.provenance_json, dict) and self.provenance_json.get("extraction_id") else None,
                revision=1,
                exact_text=self.exact_text,
                provenance_json=self.provenance_json or {},
                admitted_at=self.created_at,
                archived_at=self.archived_at,
            )
        ]


from dataclasses import dataclass, field
from datetime import timezone


@dataclass
class EvidenceRevision:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    source_id: uuid.UUID | None = None
    extraction_id: uuid.UUID | None = None
    revision: int = 1
    exact_text: str = ""
    provenance_json: dict[str, object] = field(default_factory=dict)
    admitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: datetime | None = None


@dataclass
class CaseEvidenceSnapshot:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    case_id: uuid.UUID | None = None
    evidence_revision: int = 0
    format_version: str = "case_evidence_snapshot_v1"
    manifest_json: list[dict[str, object]] = field(default_factory=list)
    input_text: str = ""
    text_sha256: str = ""
    manifest_sha256: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    "CaseDocument",
    "DocumentExtraction",
    "EvidenceSource",
    "EvidenceRevision",
    "CaseEvidenceSnapshot",
]
