"""Drop chat status and context analysis result id.

Removes chat-centric residues:
- Drops status column and ck_chat_threads_status constraint from chat_threads
- Drops fk_case_runs_context_result_id and context_analysis_result_id from case_runs

Revision ID: 0002_drop_chat_status_and_context_result
Revises: 0001_canonical_case_system
Create Date: 2026-09-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_drop_chat_status_and_context_result"
down_revision = "0001_canonical_case_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop check constraint and status column from chat_threads
    op.drop_constraint("ck_chat_threads_status", "chat_threads", type_="check")
    op.drop_column("chat_threads", "status")

    # 2. Drop foreign key constraint and context_analysis_result_id column from case_runs
    op.drop_constraint("fk_case_runs_context_result_id", "case_runs", type_="foreignkey")
    op.drop_column("case_runs", "context_analysis_result_id")


def downgrade() -> None:
    # 1. Re-add context_analysis_result_id column and foreign key to case_runs
    op.add_column("case_runs", sa.Column("context_analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_case_runs_context_result_id",
        "case_runs",
        "case_analysis_results",
        ["context_analysis_result_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # 2. Re-add status column and check constraint to chat_threads
    op.add_column("chat_threads", sa.Column("status", sa.String(length=24), server_default="idle", nullable=False))
    op.create_check_constraint(
        "ck_chat_threads_status",
        "chat_threads",
        "status IN ('idle', 'processing', 'awaiting_followup', 'answered', 'failed')",
    )
