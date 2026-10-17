import sqlalchemy as sa

from alembic import op

revision = "0002_source_deactivation"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "case_sources",
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("case_sources", "deactivated_at")
