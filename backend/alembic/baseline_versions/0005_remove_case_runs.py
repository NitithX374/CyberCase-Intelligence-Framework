from __future__ import annotations

from alembic import op

revision = "0005_remove_case_runs"
down_revision = "0004_external_context_json"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_case_analysis_results_run_id", "case_analysis_results", type_="foreignkey"
    )
    op.drop_constraint("uq_case_analysis_results_run_id", "case_analysis_results", type_="unique")
    op.drop_column("case_analysis_results", "run_id")
    op.drop_column("case_analysis_results", "execution_receipt_json")

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

    op.drop_index("ix_cases_user_id_updated_at", table_name="cases")
    op.create_index("ix_cases_user_id", "cases", ["user_id"])
    op.create_index("ix_cases_updated_at", "cases", ["updated_at"])
    op.drop_index("ix_chat_messages_analysis_result_id", table_name="chat_messages")


def downgrade() -> None:
    raise NotImplementedError("0005_remove_case_runs cannot be reversed")
