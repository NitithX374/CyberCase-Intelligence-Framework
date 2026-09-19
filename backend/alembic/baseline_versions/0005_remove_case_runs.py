"""Remove the run: an analysis is no longer a job.

Analysis and Case Ask now happen inside the request that asks for them, so there
is nothing to queue, claim or poll. `case_runs` and the columns that pointed at
it go, and `rag_contexts` goes with them — it was written only by run completion
and read by nothing, while the same query, context and MITRE table are already
stored on `case_analysis_results.external_context_json`.

Revision ID: 0005_remove_case_runs
Revises: 0004_external_context_json
Create Date: 2026-09-19
"""

from __future__ import annotations

from alembic import op

revision = "0005_remove_case_runs"
down_revision = "0004_external_context_json"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Analyses stop belonging to a run.
    op.drop_constraint(
        "fk_case_analysis_results_run_id", "case_analysis_results", type_="foreignkey"
    )
    op.drop_constraint("uq_case_analysis_results_run_id", "case_analysis_results", type_="unique")
    op.drop_column("case_analysis_results", "run_id")
    op.drop_column("case_analysis_results", "execution_receipt_json")

    # The retrieval id stays as a label, but points at no table.
    op.drop_constraint(
        "fk_case_analysis_results_retrieval_context_id",
        "case_analysis_results",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_case_reports_retrieval_context_id_rag_contexts",
        "case_reports",
        type_="foreignkey",
    )

    op.execute("DROP TABLE IF EXISTS rag_contexts CASCADE")
    op.execute("DROP TABLE IF EXISTS case_runs CASCADE")

    # Pre-existing drift: 0001 created indexes the models never declared.
    op.drop_index("ix_cases_user_id_updated_at", table_name="cases")
    op.create_index("ix_cases_user_id", "cases", ["user_id"])
    op.create_index("ix_cases_updated_at", "cases", ["updated_at"])
    op.drop_index("ix_chat_messages_analysis_result_id", table_name="chat_messages")


def downgrade() -> None:
    # The dropped rows described work that has already finished; recreating the
    # tables would not bring them back, so this is not reversible.
    raise NotImplementedError("0005_remove_case_runs cannot be reversed")
