"""Add result and evidence bindings for Case-owned reports."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009_case_report_bindings"
down_revision = "0008_case_clarifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_reports",
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "chat_reports",
        sa.Column("analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "chat_reports",
        sa.Column("evidence_snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.drop_constraint(
        "fk_chat_reports_analysis_message_id_chat_messages",
        "chat_reports",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_chat_reports_analysis_message_id_chat_messages",
        "chat_reports",
        "chat_messages",
        ["analysis_message_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_chat_reports_case_id_cases",
        "chat_reports",
        "cases",
        ["case_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_chat_reports_analysis_result_id_case_analysis_results",
        "chat_reports",
        "case_analysis_results",
        ["analysis_result_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_chat_reports_evidence_snapshot_id_case_evidence_snapshots",
        "chat_reports",
        "case_evidence_snapshots",
        ["evidence_snapshot_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.alter_column(
        "chat_reports",
        "analysis_message_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.create_index(
        "ix_chat_reports_case_id_created_at",
        "chat_reports",
        ["case_id", "created_at"],
    )
    op.create_index(
        "ix_chat_reports_analysis_result_id",
        "chat_reports",
        ["analysis_result_id"],
    )
    op.execute(
        sa.text(
            """
            UPDATE chat_reports AS report
            SET case_id = thread.id
            FROM chat_threads AS thread
            WHERE report.case_id IS NULL
              AND report.thread_id = thread.id
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE chat_reports AS report
            SET analysis_result_id = message.analysis_result_id,
                evidence_snapshot_id = result.snapshot_id
            FROM chat_messages AS message, case_analysis_results AS result
            WHERE report.analysis_result_id IS NULL
              AND report.analysis_message_id = message.id
              AND message.analysis_result_id IS NOT NULL
              AND result.id = message.analysis_result_id
              AND result.case_id = report.case_id
              AND result.status = 'validated'
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_chat_reports_analysis_result_id", table_name="chat_reports")
    op.drop_index("ix_chat_reports_case_id_created_at", table_name="chat_reports")
    op.drop_constraint(
        "fk_chat_reports_evidence_snapshot_id_case_evidence_snapshots",
        "chat_reports",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_chat_reports_analysis_result_id_case_analysis_results",
        "chat_reports",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_chat_reports_case_id_cases",
        "chat_reports",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_chat_reports_analysis_message_id_chat_messages",
        "chat_reports",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_chat_reports_analysis_message_id_chat_messages",
        "chat_reports",
        "chat_messages",
        ["analysis_message_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "chat_reports",
        "analysis_message_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.drop_column("chat_reports", "evidence_snapshot_id")
    op.drop_column("chat_reports", "analysis_result_id")
    op.drop_column("chat_reports", "case_id")
