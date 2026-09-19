"""Ask about a gap in a column, not in a JSON envelope.

The follow-up protocol used to live in ``metadata_json``: the round, the gap,
the disposition, the analysis it came from. Nothing about that blob was typed,
so every read of it re-checked every field, and half the protocol's code was
the system validating what it had written itself minutes earlier.

One nullable column replaces it. An assistant message with ``gap_key`` set is
a question about that gap; the user message that answers it points back with
``in_reply_to_message_id``. Which gaps have been asked is one SELECT DISTINCT.

Revision ID: 0009_followup_gap_key
Revises: 0008_chat_client_request_id
Create Date: 2026-09-19
"""

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
