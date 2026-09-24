from alembic import op
import sqlalchemy as sa


revision = "0002_case_run_active_index"
down_revision = "0001_canonical_case_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ux_case_runs_one_active_per_case",
        "case_runs",
        ["case_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued', 'running')"),
    )


def downgrade() -> None:
    op.drop_index("ux_case_runs_one_active_per_case", table_name="case_runs")
