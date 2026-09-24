from __future__ import annotations

from alembic import op

revision = "0011_retrieval_context_reuse"
down_revision = "0010_foreign_key_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE case_analysis_results ADD COLUMN IF NOT EXISTS retrieval_context_json JSONB"
    )


def downgrade() -> None:
    op.drop_column("case_analysis_results", "retrieval_context_json")
