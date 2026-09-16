"""Rename provider_metadata_json to external_context_json on case_analysis_results."""

from alembic import op


revision = "0004_external_context_json"
down_revision = "0003_received_case_material"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "case_analysis_results",
        "provider_metadata_json",
        new_column_name="external_context_json",
    )


def downgrade() -> None:
    op.alter_column(
        "case_analysis_results",
        "external_context_json",
        new_column_name="provider_metadata_json",
    )
