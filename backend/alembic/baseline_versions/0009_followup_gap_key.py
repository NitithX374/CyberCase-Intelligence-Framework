from __future__ import annotations

from alembic import op

revision = "0009_followup_gap_key"
down_revision = "0008_chat_client_request_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS gap_key VARCHAR(160)")


def downgrade() -> None:
    op.drop_column("chat_messages", "gap_key")
