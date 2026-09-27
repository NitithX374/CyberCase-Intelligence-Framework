import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "title", sa.String(length=255), server_default=sa.text("'New case'"), nullable=False
        ),
        sa.Column("source_revision", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("latest_analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cases"),
        sa.CheckConstraint("source_revision >= 0", name="ck_cases_source_revision_nonnegative"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_cases_user_id", ondelete="SET NULL"
        ),
    )
    op.create_index("ix_cases_user_id_updated_at", "cases", ["user_id", "updated_at"])
    op.create_index("ix_cases_latest_analysis_result_id", "cases", ["latest_analysis_result_id"])

    op.create_table(
        "case_analysis_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column(
            "status", sa.String(length=24), server_default=sa.text("'validated'"), nullable=False
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("trace_json", postgresql.JSONB(), nullable=True),
        sa.Column("retrieval_context_json", postgresql.JSONB(), nullable=True),
        sa.Column(
            "pipeline_config",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "external_context_json",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_case_analysis_results"),
        sa.CheckConstraint(
            "status IN ('assessment', 'validated')", name="ck_case_analysis_results_status"
        ),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
            name="fk_case_analysis_results_case_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_case_analysis_results_case_id_created_at",
        "case_analysis_results",
        ["case_id", "created_at"],
    )
    op.create_foreign_key(
        "fk_cases_latest_analysis_result_id",
        "cases",
        "case_analysis_results",
        ["latest_analysis_result_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "case_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=160), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("content_bytes", sa.LargeBinary(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_case_documents"),
        sa.CheckConstraint("size_bytes >= 0", name="ck_case_documents_size_nonnegative"),
        sa.ForeignKeyConstraint(
            ["case_id"], ["cases.id"], name="fk_case_documents_case_id", ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_case_documents_case_id_created_at", "case_documents", ["case_id", "created_at"]
    )

    op.create_table(
        "case_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_kind", sa.String(length=40), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("exact_text", sa.Text(), nullable=False),
        sa.Column(
            "provenance_json",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "source_metadata_json",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_case_sources"),
        sa.CheckConstraint("source_kind IN ('document', 'narrative')", name="ck_case_sources_kind"),
        sa.ForeignKeyConstraint(
            ["case_id"], ["cases.id"], name="fk_case_sources_case_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["case_documents.id"],
            name="fk_case_sources_document_id",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_case_sources_case_id_created_at", "case_sources", ["case_id", "created_at"])
    op.create_index("ix_case_sources_document_id", "case_sources", ["document_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_request_id", sa.String(length=255), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "message_kind",
            sa.String(length=32),
            server_default=sa.text("'conversation'"),
            nullable=False,
        ),
        sa.Column("gap_key", sa.String(length=160), nullable=True),
        sa.Column("analysis_result_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("in_reply_to_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_chat_messages"),
        sa.UniqueConstraint("case_id", "ordinal", name="uq_chat_messages_case_id_ordinal"),
        sa.CheckConstraint("ordinal > 0", name="ck_chat_messages_ordinal_positive"),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="ck_chat_messages_role"),
        sa.CheckConstraint(
            "message_kind IN ('conversation', 'followup_question', 'followup_answer')",
            name="ck_chat_messages_message_kind",
        ),
        sa.ForeignKeyConstraint(
            ["case_id"], ["cases.id"], name="fk_chat_messages_case_id_cases", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["analysis_result_id"],
            ["case_analysis_results.id"],
            name="fk_chat_messages_analysis_result_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["in_reply_to_message_id"],
            ["chat_messages.id"],
            name="fk_chat_messages_in_reply_to_message_id",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_chat_messages_analysis_result_id", "chat_messages", ["analysis_result_id"])
    op.create_index(
        "ix_chat_messages_in_reply_to_message_id", "chat_messages", ["in_reply_to_message_id"]
    )
    op.create_index(
        "ux_chat_messages_case_id_client_request_id",
        "chat_messages",
        ["case_id", "client_request_id"],
        unique=True,
        postgresql_where=sa.text("client_request_id IS NOT NULL"),
    )

    op.create_table(
        "case_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_result_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("structured_report", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_case_reports"),
        sa.UniqueConstraint(
            "case_id", "version_number", name="uq_case_reports_case_id_version_number"
        ),
        sa.UniqueConstraint("analysis_result_id", name="uq_case_reports_analysis_result_id"),
        sa.CheckConstraint("version_number > 0", name="ck_case_reports_version_number_positive"),
        sa.ForeignKeyConstraint(
            ["case_id"], ["cases.id"], name="fk_case_reports_case_id_cases", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["analysis_result_id"],
            ["case_analysis_results.id"],
            name="fk_case_reports_analysis_result_id_case_analysis_results",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_case_reports_case_id_created_at", "case_reports", ["case_id", "created_at"])


def downgrade() -> None:
    op.drop_constraint("fk_cases_latest_analysis_result_id", "cases", type_="foreignkey")
    op.drop_table("case_reports")
    op.drop_table("chat_messages")
    op.drop_table("case_sources")
    op.drop_table("case_documents")
    op.drop_table("case_analysis_results")
    op.drop_table("cases")
    op.drop_table("users")
