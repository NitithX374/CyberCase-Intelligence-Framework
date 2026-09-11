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
    from app.models.caseMaterials import CaseEvidenceSnapshot, EvidenceSource
    from app.models.caseRun import CaseAnalysisResult, CaseRun
    from app.models.chat import ChatMessage


class CaseClarification(Base):
    __tablename__ = "case_clarifications"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_clarifications"),
        UniqueConstraint(
            "origin_analysis_result_id",
            "gap_key",
            name="uq_case_clarifications_origin_gap_key",
        ),
        CheckConstraint(
            "state IN ('pending', 'answered', 'superseded')",
            name="ck_case_clarifications_state",
        ),
        Index("ix_case_clarifications_case_id_state", "case_id", "state"),
        Index("ix_case_clarifications_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", name="fk_case_clarifications_case_id", ondelete="CASCADE"), nullable=False
    )
    origin_analysis_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_analysis_results.id", name="fk_case_clarifications_origin_result_id", ondelete="CASCADE"), nullable=False
    )
    origin_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_evidence_snapshots.id", name="fk_case_clarifications_origin_snapshot_id", ondelete="RESTRICT"), nullable=False
    )
    gap_key: Mapped[str] = mapped_column(String(255), nullable=False)
    gap_id: Mapped[str] = mapped_column(String(80), nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    state: Mapped[str] = mapped_column(String(16), nullable=False, default="pending", server_default=text("'pending'"))
    answer_evidence_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("case_evidence_sources.id", name="fk_case_clarifications_answer_source_id", ondelete="SET NULL"), nullable=True
    )
    question_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_messages.id", name="fk_case_clarifications_question_message_id", ondelete="SET NULL"), nullable=True
    )
    answer_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_messages.id", name="fk_case_clarifications_answer_message_id", ondelete="SET NULL"), nullable=True
    )
    answer_fingerprint: Mapped[str | None] = mapped_column(CHAR(64), nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="clarifications")
    origin_analysis_result: Mapped["CaseAnalysisResult"] = relationship("CaseAnalysisResult")
    origin_snapshot: Mapped["CaseEvidenceSnapshot"] = relationship("CaseEvidenceSnapshot")
    answer_evidence_source: Mapped["EvidenceSource | None"] = relationship("EvidenceSource")
    question_message: Mapped["ChatMessage | None"] = relationship("ChatMessage", foreign_keys=[question_message_id])
    answer_message: Mapped["ChatMessage | None"] = relationship("ChatMessage", foreign_keys=[answer_message_id])
    runs: Mapped[list["CaseRun"]] = relationship("CaseRun", back_populates="clarification")


__all__ = ["CaseClarification"]
