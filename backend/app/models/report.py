"""Report history scoped to a Case and bound to a CaseAnalysisResult."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
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
    from app.models.caseRun import CaseAnalysisResult
    from app.models.ragContext import RagContext


class CaseReport(Base):
    __tablename__ = "case_reports"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_reports"),
        UniqueConstraint(
            "case_id",
            "version_number",
            name="uq_case_reports_case_id_version_number",
        ),
        UniqueConstraint(
            "case_id",
            "idempotency_key",
            name="uq_case_reports_case_id_idempotency_key",
        ),
        CheckConstraint(
            "version_number > 0",
            name="ck_case_reports_version_number_positive",
        ),
        CheckConstraint(
            "status IN ('completed', 'failed')",
            name="ck_case_reports_status",
        ),
        CheckConstraint(
            "validation_status IN ('validated', 'failed')",
            name="ck_case_reports_validation_status",
        ),
        Index("ix_case_reports_case_id_created_at", "case_id", "created_at"),
        Index("ix_case_reports_analysis_result_id", "analysis_result_id"),
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
            name="fk_case_reports_case_id_cases",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_analysis_results.id",
            name="fk_case_reports_analysis_result_id_case_analysis_results",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    retrieval_context_id: Mapped[str | None] = mapped_column(
        String(160),
        ForeignKey(
            "rag_contexts.retrieval_context_id",
            name="fk_case_reports_retrieval_context_id_rag_contexts",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    prompt_version: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    validation_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )
    validation_errors_json: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    structured_report: Mapped[dict[str, object] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    failure_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    failure_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="reports")
    analysis_result: Mapped["CaseAnalysisResult"] = relationship("CaseAnalysisResult")
    retrieval_context: Mapped["RagContext | None"] = relationship("RagContext")


__all__ = ["CaseReport"]
