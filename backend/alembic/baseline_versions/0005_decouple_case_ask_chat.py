"""Decouple Case Ask from CaseRun: add client_request_id to chat_messages, purge operation and request_message_id from case_runs."""

import sqlalchemy as sa
from alembic import op

revision = "0005_decouple_case_ask_chat"
down_revision = "0004_external_context_json"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. ChatMessage client_request_id
    op.add_column(
        "chat_messages",
        sa.Column("client_request_id", sa.String(255), nullable=True),
    )
    op.create_index(
        "ux_chat_messages_case_id_client_request_id",
        "chat_messages",
        ["case_id", "client_request_id"],
        unique=True,
        postgresql_where=sa.text("client_request_id IS NOT NULL"),
    )

    # 2. CaseRun: drop request_message_id and operation
    op.drop_constraint("fk_case_runs_request_message_id", "case_runs", type_="foreignkey")
    op.drop_constraint("ck_case_runs_operation", "case_runs", type_="check")
    op.drop_column("case_runs", "request_message_id")
    op.drop_column("case_runs", "operation")


def downgrade() -> None:
    op.add_column(
        "case_runs",
        sa.Column("operation", sa.String(16), nullable=False, server_default="analysis"),
    )
    op.create_check_constraint(
        "ck_case_runs_operation",
        "case_runs",
        "operation IN ('analysis', 'ask')",
    )
    op.add_column(
        "case_runs",
        sa.Column("request_message_id", sa.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_case_runs_request_message_id",
        "case_runs",
        "chat_messages",
        ["request_message_id"],
        ["id"],
        ondelete="NO ACTION",
    )

    op.drop_index(
        "ux_chat_messages_case_id_client_request_id",
        table_name="chat_messages",
    )
    op.drop_column("chat_messages", "client_request_id")
