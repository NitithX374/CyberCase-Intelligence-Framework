"""Allow reports without optional MITRE retrieval context."""

from alembic import op
import sqlalchemy as sa


revision = "0002_optional_report_context"
down_revision = "0001_raw_evidence_chat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "chat_reports",
        "retrieval_context_id",
        existing_type=sa.String(length=160),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "chat_reports",
        "retrieval_context_id",
        existing_type=sa.String(length=160),
        nullable=False,
    )
