"""Let a retried send find the message it already created.

Sending a chat message is now synchronous, and answering can take a model call,
so a client that times out and retries must not create a second message. The
client supplies an id with the send; a partial unique index makes the duplicate
impossible, and the service returns the existing exchange instead of asking
again.

Revision ID: 0008_chat_client_request_id
Revises: 0007_report_content_only
Create Date: 2026-09-19
"""

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
