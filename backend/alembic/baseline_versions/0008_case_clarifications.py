"""Persist Case-owned clarification questions and answer linkage."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008_case_clarifications"
down_revision = "0007_case_runs_and_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_clarifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("origin_analysis_result_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("origin_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gap_key", sa.String(length=255), nullable=False),
        sa.Column("gap_id", sa.String(length=80), nullable=False),
        sa.Column("topic", sa.String(length=500), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("state", sa.String(length=16), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("answer_evidence_source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("question_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("answer_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("answer_fingerprint", sa.CHAR(length=64), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("state IN ('pending', 'answered', 'superseded')", name="ck_case_clarifications_state"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_clarifications_case_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["origin_analysis_result_id"], ["case_analysis_results.id"], name="fk_case_clarifications_origin_result_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["origin_snapshot_id"], ["case_evidence_snapshots.id"], name="fk_case_clarifications_origin_snapshot_id", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["answer_evidence_source_id"], ["case_evidence_sources.id"], name="fk_case_clarifications_answer_source_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["question_message_id"], ["chat_messages.id"], name="fk_case_clarifications_question_message_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["answer_message_id"], ["chat_messages.id"], name="fk_case_clarifications_answer_message_id", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_case_clarifications"),
        sa.UniqueConstraint("origin_analysis_result_id", "gap_key", name="uq_case_clarifications_origin_gap_key"),
    )
    op.create_index("ix_case_clarifications_case_id_state", "case_clarifications", ["case_id", "state"])
    op.create_index("ix_case_clarifications_case_id_created_at", "case_clarifications", ["case_id", "created_at"])
    op.add_column("case_runs", sa.Column("clarification_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_case_runs_clarification_id", "case_runs", "case_clarifications", ["clarification_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_case_runs_clarification_id", "case_runs", ["clarification_id"])


def downgrade() -> None:
    op.drop_index("ix_case_runs_clarification_id", table_name="case_runs")
    op.drop_constraint("fk_case_runs_clarification_id", "case_runs", type_="foreignkey")
    op.drop_column("case_runs", "clarification_id")
    op.drop_index("ix_case_clarifications_case_id_created_at", table_name="case_clarifications")
    op.drop_index("ix_case_clarifications_case_id_state", table_name="case_clarifications")
    op.drop_table("case_clarifications")
