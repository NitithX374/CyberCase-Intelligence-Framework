"""Add Case-owned runs, immutable analysis results, and Chat publication links."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_case_runs_and_results"
down_revision = "0006_case_materials"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operation", sa.String(length=16), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_fingerprint", sa.CHAR(length=64), nullable=False),
        sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("pipeline_config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("status", sa.String(length=16), server_default=sa.text("'queued'"), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lease_owner", sa.String(length=255), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("operation IN ('analysis', 'ask')", name="ck_case_runs_operation"),
        sa.CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="ck_case_runs_status"),
        sa.CheckConstraint("attempt_count >= 0", name="ck_case_runs_attempt_count_nonnegative"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_runs_case_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["request_message_id"], ["chat_messages.id"], name="fk_case_runs_request_message_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["case_evidence_snapshots.id"], name="fk_case_runs_snapshot_id", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_case_runs"),
        sa.UniqueConstraint("case_id", "idempotency_key", name="uq_case_runs_case_id_idempotency_key"),
    )
    op.create_index("ux_case_runs_one_active_per_case", "case_runs", ["case_id"], unique=True, postgresql_where=sa.text("status IN ('queued', 'running')"))
    op.create_index("ix_case_runs_status_lease_expires_at", "case_runs", ["status", "lease_expires_at"])
    op.create_index("ix_case_runs_case_id_created_at", "case_runs", ["case_id", "created_at"])
    op.create_table(
        "case_analysis_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("schema_version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=24), server_default=sa.text("'validated'"), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("trace_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("execution_receipt_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=True),
        sa.Column("pipeline_config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("provider_metadata_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('validated', 'legacy_unbound')", name="ck_case_analysis_results_status"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_analysis_results_case_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["case_runs.id"], name="fk_case_analysis_results_run_id", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["case_evidence_snapshots.id"], name="fk_case_analysis_results_snapshot_id", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_case_analysis_results"),
        sa.UniqueConstraint("run_id", name="uq_case_analysis_results_run_id"),
    )
    op.create_index("ix_case_analysis_results_case_id_created_at", "case_analysis_results", ["case_id", "created_at"])
    op.add_column("case_runs", sa.Column("context_analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_case_runs_context_result_id", "case_runs", "case_analysis_results", ["context_analysis_result_id"], ["id"], ondelete="RESTRICT")
    op.add_column("cases", sa.Column("latest_analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_cases_latest_analysis_result_id", "cases", "case_analysis_results", ["latest_analysis_result_id"], ["id"], ondelete="SET NULL")
    op.add_column("chat_messages", sa.Column("message_kind", sa.String(length=32), server_default=sa.text("'conversation'"), nullable=False))
    op.add_column("chat_messages", sa.Column("analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_check_constraint("ck_chat_messages_message_kind", "chat_messages", "message_kind IN ('conversation', 'analysis_result', 'followup_question')")
    op.create_foreign_key("fk_chat_messages_analysis_result_id", "chat_messages", "case_analysis_results", ["analysis_result_id"], ["id"], ondelete="SET NULL")
    op.create_index("ux_chat_messages_analysis_result_publication", "chat_messages", ["analysis_result_id"], unique=True, postgresql_where=sa.text("message_kind = 'analysis_result' AND analysis_result_id IS NOT NULL"))


def downgrade() -> None:
    op.drop_index("ux_chat_messages_analysis_result_publication", table_name="chat_messages")
    op.drop_constraint("fk_chat_messages_analysis_result_id", "chat_messages", type_="foreignkey")
    op.drop_constraint("ck_chat_messages_message_kind", "chat_messages", type_="check")
    op.drop_column("chat_messages", "analysis_result_id")
    op.drop_column("chat_messages", "message_kind")
    op.drop_constraint("fk_cases_latest_analysis_result_id", "cases", type_="foreignkey")
    op.drop_column("cases", "latest_analysis_result_id")
    op.drop_constraint("fk_case_runs_context_result_id", "case_runs", type_="foreignkey")
    op.drop_column("case_runs", "context_analysis_result_id")
    op.drop_index("ix_case_analysis_results_case_id_created_at", table_name="case_analysis_results")
    op.drop_table("case_analysis_results")
    op.drop_index("ix_case_runs_case_id_created_at", table_name="case_runs")
    op.drop_index("ix_case_runs_status_lease_expires_at", table_name="case_runs")
    op.drop_index("ux_case_runs_one_active_per_case", table_name="case_runs")
    op.drop_table("case_runs")
