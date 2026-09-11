"""Durable retrieval context bound to the Case and CaseRun that produced it."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CHAR,
    DateTime,
    ForeignKey,
    Index,
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
    from app.models.caseMaterials import CaseEvidenceSnapshot
    from app.models.caseRun import CaseRun


class RagContext(Base):
    __tablename__ = "rag_contexts"
    __table_args__ = (
        PrimaryKeyConstraint(
            "retrieval_context_id",
            name="pk_rag_contexts",
        ),
        UniqueConstraint("case_run_id", name="uq_rag_contexts_case_run_id"),
        Index("ix_rag_contexts_case_id_created_at", "case_id", "created_at"),
        Index("ix_rag_contexts_query_sha256", "query_sha256"),
    )

    retrieval_context_id: Mapped[str] = mapped_column(
        String(160),
        primary_key=True,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "cases.id",
            name="fk_rag_contexts_case_id_cases",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    case_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_runs.id",
            name="fk_rag_contexts_case_run_id_case_runs",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    evidence_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_evidence_snapshots.id",
            name="fk_rag_contexts_evidence_snapshot_id_case_evidence_snapshots",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    query_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default=text("''"),
    )
    query_sha256: Mapped[str] = mapped_column(
        CHAR(64),
        nullable=False,
        default="",
        server_default=text("''"),
    )
    context_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default=text("''"),
    )
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

    @property
    def context(self) -> str:
        return self.context_text

    @context.setter
    def context(self, value: str) -> None:
        self.context_text = value

    case: Mapped["Case"] = relationship("Case", back_populates="rag_contexts")
    run: Mapped["CaseRun"] = relationship("CaseRun")
    snapshot: Mapped["CaseEvidenceSnapshot"] = relationship("CaseEvidenceSnapshot")


__all__ = ["RagContext"]
