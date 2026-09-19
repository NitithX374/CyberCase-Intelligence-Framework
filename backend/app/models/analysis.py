"""A stored analysis of the case sources.

``source_revision`` is the revision it was computed from; comparing it with
``cases.source_revision`` is the whole staleness rule. It belongs to no run:
the request that produced it has already returned.
"""

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
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class CaseAnalysisResult(Base):
    __tablename__ = "case_analysis_results"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_analysis_results"),
        CheckConstraint("status IN ('validated')", name="ck_case_analysis_results_status"),
        Index("ix_case_analysis_results_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", name="fk_case_analysis_results_case_id", ondelete="CASCADE"),
        nullable=False,
    )
    source_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_version: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        default="case_analysis_trace_v1",
        server_default=text("'case_analysis_trace_v1'"),
    )
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, default="validated", server_default=text("'validated'")
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    trace_json: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    retrieval_context_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    pipeline_config: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    external_context_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    case: Mapped[Case] = relationship(
        "Case", back_populates="analysis_results", foreign_keys=[case_id]
    )


__all__ = ["CaseAnalysisResult"]
