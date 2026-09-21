"""Keep the retrieved context, so a round that changed nothing does not re-ask.

Every follow-up round re-ran the MITRE retrieval, and the case sources had not
moved: a follow-up answer is conversation, so ``source_revision`` stays where
it was. One case in the database shows six analyses at revision 1 whose
technique tables read 6, 6, 11, 10, 9, 9 -- same input, six answers, and the
report keeps whichever the last round happened to draw.

Reuse needs the context text the model was given, and that was the one part of
the retrieval nothing kept. ``external_context_json`` holds the table and the
ids and is read by the frontend on every analysis; the context is several
kilobytes of prose no reader wants, so it goes in a column of its own rather
than into a payload the browser already fetches.

Revision ID: 0011_retrieval_context_reuse
Revises: 0010_foreign_key_indexes
Create Date: 2026-09-20
"""

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
