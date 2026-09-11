"""Add first-class cases with one shared-identity chat thread each."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_case_domain"
down_revision = "0004_password_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), server_default="New case", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_cases_user_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_cases"),
    )
    op.create_index("ix_cases_user_id", "cases", ["user_id"])
    op.create_index("ix_cases_updated_at", "cases", ["updated_at"])
    op.execute(
        sa.text(
            """
            INSERT INTO cases (id, user_id, title, created_at, updated_at)
            SELECT id,
                   user_id,
                   CASE WHEN title = 'New chat' THEN 'New case' ELSE title END,
                   created_at,
                   updated_at
            FROM chat_threads
            """
        )
    )
    op.execute(sa.text("UPDATE chat_threads SET title = 'New case' WHERE title = 'New chat'"))
    op.create_foreign_key(
        "fk_chat_threads_id_cases",
        "chat_threads",
        "cases",
        ["id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_chat_threads_id_cases", "chat_threads", type_="foreignkey")
    op.drop_index("ix_cases_updated_at", table_name="cases")
    op.drop_index("ix_cases_user_id", table_name="cases")
    op.drop_table("cases")
