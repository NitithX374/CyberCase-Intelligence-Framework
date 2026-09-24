from __future__ import annotations

from alembic import op

revision = "0014_archive_followup_sources"
down_revision = "0013_retrieval_context_contract"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM case_sources AS source
                WHERE source.source_kind = 'followup_answer'
                  AND source.archived_at IS NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM chat_messages AS message
                      WHERE message.id = source.origin_message_id
                        AND message.case_id = source.case_id
                        AND message.role = 'user'
                        AND message.content = source.exact_text
                  )
            ) THEN
                RAISE EXCEPTION 'Unmatched active follow-up sources require manual review';
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        WITH archived AS (
            UPDATE case_sources
            SET archived_at = CURRENT_TIMESTAMP
            WHERE source_kind = 'followup_answer'
              AND archived_at IS NULL
            RETURNING case_id
        )
        UPDATE cases
        SET source_revision = source_revision + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN (SELECT DISTINCT case_id FROM archived)
        """
    )


def downgrade() -> None:
    raise RuntimeError(
        "Archived follow-up sources and monotonic source revisions cannot be restored safely"
    )
