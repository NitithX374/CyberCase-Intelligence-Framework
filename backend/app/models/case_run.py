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
    from app.models.chat import ChatMessage
    from app.models.rag_context import RagContext


class CaseRun(Base):
    __tablename__ = "case_runs"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_runs"),
        UniqueConstraint("case_id", "idempotency_key", name="uq_case_runs_case_id_idempotency_key"),
        CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="ck_case_runs_status"),
        CheckConstraint("attempt_count >= 0", name="ck_case_runs_attempt_count_nonnegative"),
        Index("ix_case_runs_active_per_case", "case_id", postgresql_where=text("status IN ('queued', 'running')")),
        Index("ix_case_runs_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", name="fk_case_runs_case_id", ondelete="CASCADE"), nullable=False
    )
    evidence_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    pipeline_config: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="queued", server_default=text("'queued'"))
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="case_runs")
    analysis_result: Mapped["CaseAnalysisResult | None"] = relationship(
        "CaseAnalysisResult",
        back_populates="run",
        foreign_keys="CaseAnalysisResult.run_id",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    rag_context: Mapped["RagContext | None"] = relationship(
        "RagContext",
        back_populates="run",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class CaseAnalysisResult(Base):
    __tablename__ = "case_analysis_results"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_analysis_results"),
        UniqueConstraint("run_id", name="uq_case_analysis_results_run_id"),
        CheckConstraint("status IN ('validated')", name="ck_case_analysis_results_status"),
        Index("ix_case_analysis_results_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", name="fk_case_analysis_results_case_id", ondelete="CASCADE"), nullable=False
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_runs.id", name="fk_case_analysis_results_run_id", ondelete="CASCADE"), nullable=False
    )
    evidence_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_version: Mapped[str] = mapped_column(
        String(80), nullable=False, default="case_analysis_trace_v1", server_default=text("'case_analysis_trace_v1'")
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="validated", server_default=text("'validated'"))
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    trace_json: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    execution_receipt_json: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    retrieval_context_id: Mapped[str | None] = mapped_column(
        String(160),
        ForeignKey("rag_contexts.retrieval_context_id", name="fk_case_analysis_results_retrieval_context_id", ondelete="RESTRICT"),
        nullable=True,
    )
    pipeline_config: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    external_context_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    case: Mapped["Case"] = relationship(
        "Case",
        back_populates="analysis_results",
        foreign_keys=[case_id],
    )
    run: Mapped[CaseRun] = relationship(
        "CaseRun", back_populates="analysis_result", foreign_keys=[run_id], uselist=False
    )

__all__ = ["CaseAnalysisResult", "CaseRun"]
