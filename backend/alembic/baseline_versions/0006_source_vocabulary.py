from __future__ import annotations

from alembic import op

revision = "0006_source_vocabulary"
down_revision = "0005_remove_case_runs"
branch_labels = None
depends_on = None

CONSTRAINTS = (
    ("case_sources", "pk_case_evidence_sources", "pk_case_sources"),
    ("case_sources", "ck_case_evidence_sources_kind", "ck_case_sources_kind"),
    ("case_sources", "fk_case_evidence_sources_case_id", "fk_case_sources_case_id"),
    ("case_sources", "fk_case_evidence_sources_document_id", "fk_case_sources_document_id"),
    (
        "case_sources",
        "fk_case_evidence_sources_origin_message_id",
        "fk_case_sources_origin_message_id",
    ),
    ("cases", "ck_cases_evidence_revision_nonnegative", "ck_cases_source_revision_nonnegative"),
)


def upgrade() -> None:
    op.rename_table("case_evidence_sources", "case_sources")
    op.execute(
        "ALTER INDEX IF EXISTS ix_case_evidence_sources_case_id_created_at "
        "RENAME TO ix_case_sources_case_id_created_at"
    )
    for table, old, new in CONSTRAINTS:
        op.execute(f'ALTER TABLE {table} RENAME CONSTRAINT "{old}" TO "{new}"')

    op.alter_column("cases", "evidence_revision", new_column_name="source_revision")
    op.alter_column("case_analysis_results", "evidence_revision", new_column_name="source_revision")


def downgrade() -> None:
    op.alter_column("case_analysis_results", "source_revision", new_column_name="evidence_revision")
    op.alter_column("cases", "source_revision", new_column_name="evidence_revision")
    for table, old, new in CONSTRAINTS:
        op.execute(f'ALTER TABLE {table} RENAME CONSTRAINT "{new}" TO "{old}"')
    op.execute(
        "ALTER INDEX IF EXISTS ix_case_sources_case_id_created_at "
        "RENAME TO ix_case_evidence_sources_case_id_created_at"
    )
    op.rename_table("case_sources", "case_evidence_sources")
