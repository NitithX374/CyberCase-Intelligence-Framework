from __future__ import annotations

from alembic import op

revision = "0008_chat_client_request_id"
down_revision = "0007_report_content_only"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS client_request_id VARCHAR(255)")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_chat_messages_case_id_client_request_id "
        "ON chat_messages (case_id, client_request_id) "
        "WHERE client_request_id IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index("ux_chat_messages_case_id_client_request_id", table_name="chat_messages")
    op.drop_column("chat_messages", "client_request_id")
