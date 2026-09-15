"""Rename document evidence sources for automatic Case material receipt."""

from alembic import op
import sqlalchemy as sa


revision = "0003_received_case_material"
down_revision = "0002_case_run_active_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_case_evidence_sources_kind", "case_evidence_sources", type_="check")
    op.execute(
        sa.text(
            "UPDATE case_evidence_sources SET source_kind = 'document' "
            "WHERE source_kind = 'reviewed_document'"
        )
    )
    op.create_check_constraint(
        "ck_case_evidence_sources_kind",
        "case_evidence_sources",
        "source_kind IN ('document', 'narrative', 'followup_answer')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_case_evidence_sources_kind", "case_evidence_sources", type_="check")
    op.execute(
        sa.text(
            "UPDATE case_evidence_sources SET source_kind = 'reviewed_document' "
            "WHERE source_kind = 'document'"
        )
    )
    op.create_check_constraint(
        "ck_case_evidence_sources_kind",
        "case_evidence_sources",
        "source_kind IN ('reviewed_document', 'narrative', 'followup_answer')",
    )
