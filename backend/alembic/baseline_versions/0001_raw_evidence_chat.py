"""Create the raw-evidence chat schema.

Revision ID: 0001_raw_evidence_chat
Revises:
Create Date: 2026-08-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_raw_evidence_chat"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), server_default="New chat", nullable=False),
        sa.Column("status", sa.String(length=24), server_default="idle", nullable=False),
        sa.Column("next_message_ordinal", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "status IN ('idle', 'processing', 'awaiting_followup', 'answered', 'failed')",
            name="ck_chat_threads_status",
        ),
        sa.CheckConstraint("next_message_ordinal > 0", name="ck_chat_threads_next_message_ordinal_positive"),
        sa.PrimaryKeyConstraint("id", name="pk_chat_threads"),
    )
    op.create_index("ix_chat_threads_updated_at", "chat_threads", ["updated_at"])
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("ordinal > 0", name="ck_chat_messages_ordinal_positive"),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="ck_chat_messages_role"),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"], name="fk_chat_messages_thread_id_chat_threads", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_chat_messages"),
        sa.UniqueConstraint("thread_id", "ordinal", name="uq_chat_messages_thread_id_ordinal"),
        sa.UniqueConstraint("thread_id", "id", name="uq_chat_messages_thread_id_id"),
    )
    op.create_table(
        "chat_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="queued", nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_fingerprint", sa.CHAR(length=64), nullable=False),
        sa.Column("request_payload", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lease_owner", sa.String(length=255), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="ck_chat_runs_status"),
        sa.CheckConstraint("attempt_count >= 0", name="ck_chat_runs_attempt_count_nonnegative"),
        sa.ForeignKeyConstraint(["request_message_id"], ["chat_messages.id"], name="fk_chat_runs_request_message_id_chat_messages", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"], name="fk_chat_runs_thread_id_chat_threads", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_chat_runs"),
        sa.UniqueConstraint("thread_id", "idempotency_key", name="uq_chat_runs_thread_id_idempotency_key"),
    )
    op.create_index("ix_chat_runs_thread_id_created_at", "chat_runs", ["thread_id", "created_at"])
    op.create_index("ix_chat_runs_status_lease_expires_at", "chat_runs", ["status", "lease_expires_at"])
    op.create_index(
        "ux_chat_runs_one_active_per_thread",
        "chat_runs",
        ["thread_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued', 'running')"),
    )
    op.create_table(
        "rag_contexts",
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("context", sa.Text(), nullable=False),
        sa.Column("mitre_table", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["chat_runs.id"], name="fk_rag_contexts_run_id_chat_runs", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"], name="fk_rag_contexts_thread_id_chat_threads", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("retrieval_context_id", name="pk_rag_contexts"),
        sa.UniqueConstraint("run_id", name="uq_rag_contexts_run_id"),
    )
    op.create_table(
        "chat_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("source_snapshot_json", postgresql.JSONB(), nullable=False),
        sa.Column("source_snapshot_hash", sa.CHAR(length=64), nullable=False),
        sa.Column("analysis_message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=False),
        sa.Column("prompt_version", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=False),
        sa.Column("decoding_settings", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("validation_status", sa.String(length=16), nullable=False),
        sa.Column("validation_errors_json", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("structured_report", postgresql.JSONB(), nullable=True),
        sa.Column("failure_code", sa.String(length=80), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.CheckConstraint("version_number > 0", name="ck_chat_reports_version_number_positive"),
        sa.CheckConstraint("status IN ('completed', 'failed')", name="ck_chat_reports_status"),
        sa.CheckConstraint("validation_status IN ('validated', 'failed')", name="ck_chat_reports_validation_status"),
        sa.ForeignKeyConstraint(["analysis_message_id"], ["chat_messages.id"], name="fk_chat_reports_analysis_message_id_chat_messages", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["retrieval_context_id"], ["rag_contexts.retrieval_context_id"], name="fk_chat_reports_retrieval_context_id_rag_contexts", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"], name="fk_chat_reports_thread_id_chat_threads", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_chat_reports"),
        sa.UniqueConstraint("thread_id", "idempotency_key", name="uq_chat_reports_thread_id_idempotency_key"),
        sa.UniqueConstraint("thread_id", "version_number", name="uq_chat_reports_thread_id_version_number"),
    )
    op.create_index("ix_chat_reports_thread_id_created_at", "chat_reports", ["thread_id", "created_at"])


def downgrade() -> None:
    op.drop_table("chat_reports")
    op.drop_table("rag_contexts")
    op.drop_table("chat_runs")
    op.drop_table("chat_messages")
    op.drop_table("chat_threads")
