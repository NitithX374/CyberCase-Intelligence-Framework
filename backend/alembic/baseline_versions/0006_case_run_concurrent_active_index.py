"""Allow multiple queued or running CaseRuns per Case."""

from alembic import op
import sqlalchemy as sa


revision = "0006_case_run_active_idx"
down_revision = "0005_decouple_case_ask_chat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ux_case_runs_one_active_per_case", table_name="case_runs")
    op.create_index(
        "ix_case_runs_active_per_case",
        "case_runs",
        ["case_id"],
        unique=False,
        postgresql_where=sa.text("status IN ('queued', 'running')"),
    )


def downgrade() -> None:
    op.drop_index("ix_case_runs_active_per_case", table_name="case_runs")
    op.create_index(
        "ux_case_runs_one_active_per_case",
        "case_runs",
        ["case_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued', 'running')"),
    )
