from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0015_schema_cleanup"
down_revision = "0014_archive_followup_sources"
branch_labels = None
depends_on = None

REPORT_ANALYSIS_FK = "fk_case_reports_analysis_result_id_case_analysis_results"


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM users
                WHERE verification_hash IS NOT NULL OR verification_expires_at IS NOT NULL
            ) THEN
                RAISE EXCEPTION 'users.verification_* hold values; review them before dropping';
            END IF;
        END $$;
        """
    )
    op.drop_column("users", "verification_hash")
    op.drop_column("users", "verification_expires_at")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_chat_messages_case_id_ordinal", table_name="chat_messages")

    op.drop_index("ix_cases_user_id", table_name="cases")
    op.drop_index("ix_cases_updated_at", table_name="cases")
    op.create_index("ix_cases_user_id_updated_at", "cases", ["user_id", "updated_at"])

    op.drop_constraint(REPORT_ANALYSIS_FK, "case_reports", type_="foreignkey")
    op.create_foreign_key(
        REPORT_ANALYSIS_FK,
        "case_reports",
        "case_analysis_results",
        ["analysis_result_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(REPORT_ANALYSIS_FK, "case_reports", type_="foreignkey")
    op.create_foreign_key(
        REPORT_ANALYSIS_FK,
        "case_reports",
        "case_analysis_results",
        ["analysis_result_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.drop_index("ix_cases_user_id_updated_at", table_name="cases")
    op.create_index("ix_cases_updated_at", "cases", ["updated_at"])
    op.create_index("ix_cases_user_id", "cases", ["user_id"])

    op.create_index("ix_chat_messages_case_id_ordinal", "chat_messages", ["case_id", "ordinal"])
    op.create_index("ix_users_email", "users", ["email"])

    op.add_column(
        "users",
        sa.Column("verification_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("users", sa.Column("verification_hash", sa.String(length=64), nullable=True))
