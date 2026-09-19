"""A report stores its content, not the story of how it was made.

The report is a deterministic template render of a saved analysis — it makes no
model call. The columns that described a provider request (prompt version,
latency, token counts) always held constants or NULL, and the five columns
recording whether it worked described an operation that either returns a report
or raises. One report per analysis replaces the idempotency key.

Revision ID: 0007_report_content_only
Revises: 0006_source_vocabulary
Create Date: 2026-09-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007_report_content_only"
down_revision = "0006_source_vocabulary"
branch_labels = None
depends_on = None

DROPPED = (
    "idempotency_key",
    "retrieval_context_id",
    "prompt_version",
    "status",
    "validation_status",
    "validation_errors_json",
    "failure_code",
    "failure_message",
    "finished_at",
    "latency_ms",
    "input_tokens",
    "output_tokens",
)


def upgrade() -> None:
    # A report that never completed has no content to keep.
    op.execute("DELETE FROM case_reports WHERE status <> 'completed' OR structured_report IS NULL")

    op.drop_constraint("uq_case_reports_case_id_idempotency_key", "case_reports", type_="unique")
    op.drop_constraint("ck_case_reports_status", "case_reports", type_="check")
    op.drop_constraint("ck_case_reports_validation_status", "case_reports", type_="check")
    op.execute("DROP INDEX IF EXISTS ix_case_reports_analysis_result_id")

    for column in DROPPED:
        op.drop_column("case_reports", column)

    op.alter_column("case_reports", "structured_report", nullable=False)
    op.create_unique_constraint(
        "uq_case_reports_analysis_result_id", "case_reports", ["analysis_result_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_case_reports_analysis_result_id", "case_reports", type_="unique")
    op.alter_column("case_reports", "structured_report", nullable=True)
    op.add_column("case_reports", sa.Column("output_tokens", sa.Integer(), nullable=True))
    op.add_column("case_reports", sa.Column("input_tokens", sa.Integer(), nullable=True))
    op.add_column("case_reports", sa.Column("latency_ms", sa.Float(), nullable=True))
    op.add_column(
        "case_reports", sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("case_reports", sa.Column("failure_message", sa.Text(), nullable=True))
    op.add_column("case_reports", sa.Column("failure_code", sa.String(length=80), nullable=True))
    op.add_column(
        "case_reports",
        sa.Column(
            "validation_errors_json",
            sa.dialects.postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "case_reports",
        sa.Column(
            "validation_status", sa.String(length=16), server_default="validated", nullable=False
        ),
    )
    op.add_column(
        "case_reports",
        sa.Column("status", sa.String(length=16), server_default="completed", nullable=False),
    )
    op.add_column(
        "case_reports",
        sa.Column("prompt_version", sa.String(length=120), server_default="", nullable=False),
    )
    op.add_column(
        "case_reports", sa.Column("retrieval_context_id", sa.String(length=160), nullable=True)
    )
    op.add_column(
        "case_reports",
        sa.Column("idempotency_key", sa.String(length=255), server_default="", nullable=False),
    )
    op.create_unique_constraint(
        "uq_case_reports_case_id_idempotency_key", "case_reports", ["case_id", "idempotency_key"]
    )
    op.create_index("ix_case_reports_analysis_result_id", "case_reports", ["analysis_result_id"])
