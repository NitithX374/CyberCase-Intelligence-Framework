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
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.analysis import CaseAnalysisResult
    from app.models.chat import ChatMessage
    from app.models.report import CaseReport
    from app.models.sources import (
        CaseDocument,
        CaseSource,
    )
    from app.models.user import User


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_cases"),
        CheckConstraint("source_revision >= 0", name="ck_cases_source_revision_nonnegative"),
        Index("ix_cases_user_id_updated_at", "user_id", "updated_at"),
        Index("ix_cases_latest_analysis_result_id", "latest_analysis_result_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="fk_cases_user_id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New case",
        server_default=text("'New case'"),
    )
    source_revision: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    latest_analysis_result_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_analysis_results.id",
            name="fk_cases_latest_analysis_result_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    chat_messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage",
        back_populates="case",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatMessage.ordinal",
        lazy="selectin",
    )

    user: Mapped[User | None] = relationship(
        "User",
        back_populates="cases",
    )
    documents: Mapped[list[CaseDocument]] = relationship(
        "CaseDocument",
        back_populates="case",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sources: Mapped[list[CaseSource]] = relationship(
        "CaseSource",
        back_populates="case",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    analysis_results: Mapped[list[CaseAnalysisResult]] = relationship(
        "CaseAnalysisResult",
        back_populates="case",
        passive_deletes=True,
        foreign_keys="CaseAnalysisResult.case_id",
    )
    latest_analysis_result: Mapped[CaseAnalysisResult | None] = relationship(
        "CaseAnalysisResult",
        foreign_keys=[latest_analysis_result_id],
        post_update=True,
    )
    reports: Mapped[list[CaseReport]] = relationship(
        "CaseReport",
        back_populates="case",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


__all__ = ["Case"]
