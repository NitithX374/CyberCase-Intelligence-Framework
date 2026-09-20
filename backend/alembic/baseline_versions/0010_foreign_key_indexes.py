"""Index the foreign keys Postgres left bare.

Postgres indexes the side a foreign key points *at*, never the side that
points. So every one of these columns was a sequential scan waiting for a
delete: removing one ``case_analysis_results`` row made the server read all of
``chat_messages`` to find the rows whose ``analysis_result_id`` had to be set
to NULL, and all of ``cases`` for ``latest_analysis_result_id``. Deleting a
case did that once per analysis it owned.

Two of the five are also read by the application, not only by the referential
check. ``in_reply_to_message_id`` is how a follow-up answer is found from the
question it answers, which runs on every clarification round.

CONCURRENTLY is not used: Alembic runs a migration inside a transaction, and
Postgres refuses a concurrent build there. On a table large enough to care,
build these by hand outside the migration first — ``CREATE INDEX IF NOT
EXISTS`` then finds them already present and does nothing.

Revision ID: 0010_foreign_key_indexes
Revises: 0009_followup_gap_key
Create Date: 2026-09-20
"""

from __future__ import annotations

from alembic import op

revision = "0010_foreign_key_indexes"
down_revision = "0009_followup_gap_key"
branch_labels = None
depends_on = None


# (index name, table, column)
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
