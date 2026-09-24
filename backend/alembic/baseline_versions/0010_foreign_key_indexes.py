from __future__ import annotations

from alembic import op

revision = "0010_foreign_key_indexes"
down_revision = "0009_followup_gap_key"
branch_labels = None
depends_on = None


FOREIGN_KEY_INDEXES = (
    ("ix_cases_latest_analysis_result_id", "cases", "latest_analysis_result_id"),
    ("ix_chat_messages_analysis_result_id", "chat_messages", "analysis_result_id"),
    ("ix_chat_messages_in_reply_to_message_id", "chat_messages", "in_reply_to_message_id"),
    ("ix_case_sources_document_id", "case_sources", "document_id"),
    ("ix_case_sources_origin_message_id", "case_sources", "origin_message_id"),
)


def upgrade() -> None:
    for name, table, column in FOREIGN_KEY_INDEXES:
        op.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({column})")


def downgrade() -> None:
    for name, _table, _column in FOREIGN_KEY_INDEXES:
        op.execute(f"DROP INDEX IF EXISTS {name}")
