from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
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
    from app.models.document import CaseDocument


class CaseSource(Base):
    __tablename__ = "case_sources"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_sources"),
        CheckConstraint(
            "source_kind IN ('document', 'narrative')",
            name="ck_case_sources_kind",
        ),
        Index("ix_case_sources_case_id_created_at", "case_id", "created_at"),
        Index("ix_case_sources_document_id", "document_id"),
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

    case: Mapped[Case] = relationship("Case", back_populates="sources")
    document: Mapped[CaseDocument | None] = relationship(back_populates="sources")

    @property
    def filename(self) -> str | None:
        return self.document.filename if self.document is not None else None

    @property
    def mime_type(self) -> str | None:
        return self.document.mime_type if self.document is not None else None

    @property
    def size_bytes(self) -> int | None:
        return self.document.size_bytes if self.document is not None else None


__all__ = [
    "CaseSource",
]
