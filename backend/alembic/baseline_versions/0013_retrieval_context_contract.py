"""Remove redundant chat and external-context retrieval fields.

Revision ID: 0013_retrieval_context_contract
Revises: 0012_analysis_assessment_status
Create Date: 2026-09-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0013_retrieval_context_contract"
down_revision = "0012_analysis_assessment_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("chat_messages", "retrieval_context_id")
    op.execute(
        "UPDATE case_analysis_results "
        "SET external_context_json = external_context_json - 'mitre_table' "
        "WHERE external_context_json ? 'mitre_table'"
    )


def downgrade() -> None:
    op.add_column(
        "chat_messages",
        sa.Column("retrieval_context_id", sa.String(length=160), nullable=True),
    )
    op.execute(
        "UPDATE case_analysis_results "
        "SET external_context_json = jsonb_set("
        "external_context_json, '{mitre_table}', "
        "external_context_json #> '{technical_augmentation,mitre_table}', true) "
        "WHERE external_context_json #> '{technical_augmentation,mitre_table}' IS NOT NULL"
    )
