"""Keep frozen reports when an optional ChatThread is removed."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0010_preserve_chat_reports"
down_revision = "0009_case_report_bindings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_chat_reports_thread_id_chat_threads",
        "chat_reports",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_chat_reports_thread_id_chat_threads",
        "chat_reports",
        "chat_threads",
        ["thread_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column(
        "chat_reports",
        "thread_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM chat_reports WHERE thread_id IS NULL"))
    op.drop_constraint(
        "fk_chat_reports_thread_id_chat_threads",
        "chat_reports",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_chat_reports_thread_id_chat_threads",
        "chat_reports",
        "chat_threads",
        ["thread_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "chat_reports",
        "thread_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
