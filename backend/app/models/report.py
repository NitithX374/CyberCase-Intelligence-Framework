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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.analysis import CaseAnalysisResult
    from app.models.case import Case


class CaseReport(Base):
    __tablename__ = "case_reports"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_case_reports"),
        UniqueConstraint(
            "case_id", "version_number", name="uq_case_reports_case_id_version_number"
        ),
        UniqueConstraint("analysis_result_id", name="uq_case_reports_analysis_result_id"),
        CheckConstraint("version_number > 0", name="ck_case_reports_version_number_positive"),
        Index("ix_case_reports_case_id_created_at", "case_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", name="fk_case_reports_case_id_cases", ondelete="CASCADE"),
        nullable=False,
    )
    analysis_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_analysis_results.id",
            name="fk_case_reports_analysis_result_id_case_analysis_results",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    structured_report: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    case: Mapped[Case] = relationship("Case", back_populates="reports")
    analysis_result: Mapped[CaseAnalysisResult] = relationship("CaseAnalysisResult")


__all__ = ["CaseReport"]
