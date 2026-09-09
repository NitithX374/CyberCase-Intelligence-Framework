"""Add users table and user_id to chat_threads for OAuth authentication and thread ownership.

Revision ID: 0003_user_oauth_threads
Revises: 0002_optional_report_context
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003_user_oauth_threads"
down_revision = "0002_optional_report_context"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("oauth_provider", sa.String(length=32), nullable=False),
        sa.Column("oauth_subject_id", sa.String(length=255), nullable=False),
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
        sa.UniqueConstraint(
            "oauth_provider",
            "oauth_subject_id",
            name="uq_users_oauth_provider_subject",
        ),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index(
        "ix_users_oauth_provider_subject",
        "users",
        ["oauth_provider", "oauth_subject_id"],
    )

    # 2. Add user_id column to chat_threads
    op.add_column(
        "chat_threads",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_chat_threads_user_id",
        "chat_threads",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_chat_threads_user_id", "chat_threads", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_threads_user_id", table_name="chat_threads")
    op.drop_constraint("fk_chat_threads_user_id", "chat_threads", type_="foreignkey")
    op.drop_column("chat_threads", "user_id")

    op.drop_index("ix_users_oauth_provider_subject", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
