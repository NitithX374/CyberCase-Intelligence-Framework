from __future__ import annotations

from alembic import op

revision = "0012_analysis_assessment_status"
down_revision = "0011_retrieval_context_reuse"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE case_analysis_results DROP CONSTRAINT ck_case_analysis_results_status")
    op.execute(
        "ALTER TABLE case_analysis_results "
        "ADD CONSTRAINT ck_case_analysis_results_status "
        "CHECK (status IN ('assessment', 'validated'))"
    )


def downgrade() -> None:
    op.execute("DELETE FROM case_analysis_results WHERE status = 'assessment'")
    op.execute("ALTER TABLE case_analysis_results DROP CONSTRAINT ck_case_analysis_results_status")
    op.execute(
        "ALTER TABLE case_analysis_results "
        "ADD CONSTRAINT ck_case_analysis_results_status "
        "CHECK (status IN ('validated'))"
    )
