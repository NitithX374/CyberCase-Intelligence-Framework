"""Canonical Case System Baseline Migration.

Defines the 14 product runtime tables for the CyberCase Framework:
users, cases, case_documents, document_extractions, chat_threads,
chat_messages, case_evidence_sources, case_evidence_revisions,
case_evidence_snapshots, case_runs, case_analysis_results,
case_clarifications, rag_contexts, case_reports.

Revision ID: 0001_canonical_case_system
Revises: None
Create Date: 2026-09-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_canonical_case_system"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_hash", sa.String(length=64), nullable=True),
        sa.Column("verification_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_hash", sa.String(length=512), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("oauth_provider", sa.String(length=32), server_default="google", nullable=False),
        sa.Column("oauth_subject_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("oauth_provider", "oauth_subject_id", name="uq_users_provider_subject"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # 2. cases
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), server_default="New case", nullable=False),
        sa.Column("evidence_revision", sa.Integer(), server_default="0", nullable=False),
        sa.Column("latest_analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("evidence_revision >= 0", name="ck_cases_evidence_revision_nonnegative"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_cases_user_id", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_cases"),
    )
    op.create_index("ix_cases_user_id_updated_at", "cases", ["user_id", "updated_at"])

    # 3. case_documents
    op.create_table(
        "case_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=160), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("content_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("content_bytes", sa.LargeBinary(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("size_bytes >= 0", name="ck_case_documents_size_nonnegative"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_documents_case_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_case_documents"),
    )
    op.create_index("ix_case_documents_case_id_created_at", "case_documents", ["case_id", "created_at"])

    # 4. document_extractions
    op.create_table(
        "document_extractions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("provenance_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("warnings_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("revision > 0", name="ck_document_extractions_revision_positive"),
        sa.ForeignKeyConstraint(["document_id"], ["case_documents.id"], name="fk_document_extractions_document_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_document_extractions"),
        sa.UniqueConstraint("document_id", "revision", name="uq_document_extractions_document_revision"),
    )
    op.create_index("ix_document_extractions_document_id_created_at", "document_extractions", ["document_id", "created_at"])

    # 5. chat_threads
    op.create_table(
        "chat_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="idle", nullable=False),
        sa.Column("next_message_ordinal", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("next_message_ordinal > 0", name="ck_chat_threads_next_message_ordinal_positive"),
        sa.CheckConstraint(
            "status IN ('idle', 'processing', 'awaiting_followup', 'answered', 'failed')",
            name="ck_chat_threads_status",
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_chat_threads_case_id_cases", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_chat_threads"),
        sa.UniqueConstraint("case_id", name="uq_chat_threads_case_id"),
    )
    op.create_index("ix_chat_threads_case_id", "chat_threads", ["case_id"])
    op.create_index("ix_chat_threads_updated_at", "chat_threads", ["updated_at"])

    # 6. chat_messages
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=True),
        sa.Column("message_kind", sa.String(length=32), server_default="conversation", nullable=False),
        sa.Column("analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("ordinal > 0", name="ck_chat_messages_ordinal_positive"),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="ck_chat_messages_role"),
        sa.CheckConstraint(
            "message_kind IN ('conversation', 'analysis_result', 'followup_question')",
            name="ck_chat_messages_message_kind",
        ),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"], name="fk_chat_messages_thread_id_chat_threads", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_chat_messages"),
        sa.UniqueConstraint("thread_id", "ordinal", name="uq_chat_messages_thread_id_ordinal"),
        sa.UniqueConstraint("thread_id", "id", name="uq_chat_messages_thread_id_id"),
    )
    op.create_index("ix_chat_messages_analysis_result_id", "chat_messages", ["analysis_result_id"])
    op.create_index("ix_chat_messages_thread_id_ordinal", "chat_messages", ["thread_id", "ordinal"])

    # 7. case_evidence_sources
    op.create_table(
        "case_evidence_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_kind", sa.String(length=40), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("origin_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_metadata_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "source_kind IN ('reviewed_document', 'narrative', 'clarification_answer')",
            name="ck_case_evidence_sources_kind",
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_evidence_sources_case_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["case_documents.id"], name="fk_case_evidence_sources_document_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["origin_message_id"], ["chat_messages.id"], name="fk_case_evidence_sources_origin_message_id", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_case_evidence_sources"),
    )
    op.create_index("ix_case_evidence_sources_case_id_created_at", "case_evidence_sources", ["case_id", "created_at"])

    # 8. case_evidence_revisions
    op.create_table(
        "case_evidence_revisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("extraction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("exact_text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("provenance_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("revision > 0", name="ck_case_evidence_revisions_revision_positive"),
        sa.ForeignKeyConstraint(["extraction_id"], ["document_extractions.id"], name="fk_case_evidence_revisions_extraction_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["case_evidence_sources.id"], name="fk_case_evidence_revisions_source_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_case_evidence_revisions"),
        sa.UniqueConstraint("source_id", "revision", name="uq_case_evidence_revisions_source_id_revision"),
    )
    op.create_index("ix_case_evidence_revisions_source_id_created_at", "case_evidence_revisions", ["source_id", "created_at"])

    # 9. case_evidence_snapshots
    op.create_table(
        "case_evidence_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_revision", sa.Integer(), nullable=False),
        sa.Column("format_version", sa.String(length=40), nullable=False),
        sa.Column("manifest_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("manifest_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("evidence_revision >= 0", name="ck_case_evidence_snapshots_revision_nonnegative"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_evidence_snapshots_case_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_case_evidence_snapshots"),
        sa.UniqueConstraint("case_id", "evidence_revision", "manifest_sha256", name="uq_case_evidence_snapshots_identity"),
    )
    op.create_index("ix_case_evidence_snapshots_case_id_created_at", "case_evidence_snapshots", ["case_id", "created_at"])

    # 10. case_runs
    op.create_table(
        "case_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operation", sa.String(length=32), server_default="analysis", nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("context_analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("clarification_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_fingerprint", sa.CHAR(length=64), nullable=False),
        sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("pipeline_config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="queued", nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lease_owner", sa.String(length=255), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("attempt_count >= 0", name="ck_case_runs_attempt_count_nonnegative"),
        sa.CheckConstraint("operation IN ('analysis', 'ask', 'clarification')", name="ck_case_runs_operation"),
        sa.CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="ck_case_runs_status"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_runs_case_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["case_evidence_snapshots.id"], name="fk_case_runs_snapshot_id", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_case_runs"),
        sa.UniqueConstraint("case_id", "idempotency_key", name="uq_case_runs_case_id_idempotency_key"),
    )
    op.create_index("ix_case_runs_case_id_created_at", "case_runs", ["case_id", "created_at"])
    op.create_index("ix_case_runs_status_lease_expires_at", "case_runs", ["status", "lease_expires_at"])

    # 11. case_analysis_results
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

    # 12. case_clarifications
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
        sa.ForeignKeyConstraint(["answer_evidence_source_id"], ["case_evidence_sources.id"], name="fk_case_clarifications_answer_source_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["answer_message_id"], ["chat_messages.id"], name="fk_case_clarifications_answer_message_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_clarifications_case_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["origin_analysis_result_id"], ["case_analysis_results.id"], name="fk_case_clarifications_origin_result_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["origin_snapshot_id"], ["case_evidence_snapshots.id"], name="fk_case_clarifications_origin_snapshot_id", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["question_message_id"], ["chat_messages.id"], name="fk_case_clarifications_question_message_id", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_case_clarifications"),
        sa.UniqueConstraint("origin_analysis_result_id", "gap_key", name="uq_case_clarifications_origin_gap_key"),
    )
    op.create_index("ix_case_clarifications_case_id_created_at", "case_clarifications", ["case_id", "created_at"])
    op.create_index("ix_case_clarifications_case_id_state", "case_clarifications", ["case_id", "state"])

    # 13. rag_contexts
    op.create_table(
        "rag_contexts",
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_text", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("query_sha256", sa.CHAR(length=64), server_default=sa.text("''"), nullable=False),
        sa.Column("context_text", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("mitre_table", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_rag_contexts_case_id_cases", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_run_id"], ["case_runs.id"], name="fk_rag_contexts_case_run_id_case_runs", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_snapshot_id"], ["case_evidence_snapshots.id"], name="fk_rag_contexts_evidence_snapshot_id_case_evidence_snapshots", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("retrieval_context_id", name="pk_rag_contexts"),
        sa.UniqueConstraint("case_run_id", name="uq_rag_contexts_case_run_id"),
    )
    op.create_index("ix_rag_contexts_case_id_created_at", "rag_contexts", ["case_id", "created_at"])
    op.create_index("ix_rag_contexts_query_sha256", "rag_contexts", ["query_sha256"])

    # 14. case_reports
    op.create_table(
        "case_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("source_snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_snapshot_hash", sa.CHAR(length=64), nullable=False),
        sa.Column("analysis_result_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=True),
        sa.Column("prompt_version", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=False),
        sa.Column("decoding_settings", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("validation_status", sa.String(length=16), nullable=False),
        sa.Column("validation_errors_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("structured_report", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("failure_code", sa.String(length=80), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.CheckConstraint("status IN ('completed', 'failed')", name="ck_case_reports_status"),
        sa.CheckConstraint("validation_status IN ('validated', 'failed')", name="ck_case_reports_validation_status"),
        sa.CheckConstraint("version_number > 0", name="ck_case_reports_version_number_positive"),
        sa.ForeignKeyConstraint(["analysis_result_id"], ["case_analysis_results.id"], name="fk_case_reports_analysis_result_id_case_analysis_results", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_reports_case_id_cases", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_snapshot_id"], ["case_evidence_snapshots.id"], name="fk_case_reports_evidence_snapshot_id_case_evidence_snapshots", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["retrieval_context_id"], ["rag_contexts.retrieval_context_id"], name="fk_case_reports_retrieval_context_id_rag_contexts", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_case_reports"),
        sa.UniqueConstraint("case_id", "idempotency_key", name="uq_case_reports_case_id_idempotency_key"),
        sa.UniqueConstraint("case_id", "version_number", name="uq_case_reports_case_id_version_number"),
    )
    op.create_index("ix_case_reports_analysis_result_id", "case_reports", ["analysis_result_id"])
    op.create_index("ix_case_reports_case_id_created_at", "case_reports", ["case_id", "created_at"])

    # Circular foreign keys
    op.create_foreign_key(
        "fk_cases_latest_analysis_result_id",
        "cases",
        "case_analysis_results",
        ["latest_analysis_result_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_chat_messages_analysis_result_id",
        "chat_messages",
        "case_analysis_results",
        ["analysis_result_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_case_runs_request_message_id",
        "case_runs",
        "chat_messages",
        ["request_message_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_case_runs_context_result_id",
        "case_runs",
        "case_analysis_results",
        ["context_analysis_result_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_case_runs_clarification_id",
        "case_runs",
        "case_clarifications",
        ["clarification_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_case_runs_clarification_id", "case_runs", type_="foreignkey")
    op.drop_constraint("fk_case_runs_context_result_id", "case_runs", type_="foreignkey")
    op.drop_constraint("fk_case_runs_request_message_id", "case_runs", type_="foreignkey")
    op.drop_constraint("fk_chat_messages_analysis_result_id", "chat_messages", type_="foreignkey")
    op.drop_constraint("fk_cases_latest_analysis_result_id", "cases", type_="foreignkey")

    op.drop_table("case_reports")
    op.drop_table("rag_contexts")
    op.drop_table("case_clarifications")
    op.drop_table("case_analysis_results")
    op.drop_table("case_runs")
    op.drop_table("case_evidence_snapshots")
    op.drop_table("case_evidence_revisions")
    op.drop_table("case_evidence_sources")
    op.drop_table("chat_messages")
    op.drop_table("chat_threads")
    op.drop_table("document_extractions")
    op.drop_table("case_documents")
    op.drop_table("cases")
    op.drop_table("users")
