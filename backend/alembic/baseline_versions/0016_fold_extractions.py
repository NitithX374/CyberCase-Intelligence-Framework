from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0016_fold_extractions"
down_revision = "0015_schema_cleanup"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM document_extractions AS extraction
                WHERE NOT EXISTS (
                    SELECT 1 FROM case_sources AS source
                    WHERE source.document_id = extraction.document_id
                      AND source.source_kind = 'document'
                      AND source.exact_text = extraction.extracted_text
                )
            ) THEN
                RAISE EXCEPTION 'An extraction holds text its document source does not';
            END IF;
            IF EXISTS (SELECT 1 FROM case_documents WHERE archived_at IS NOT NULL) THEN
                RAISE EXCEPTION 'case_documents.archived_at is set on some documents';
            END IF;
            IF EXISTS (SELECT 1 FROM users WHERE avatar_url IS NOT NULL) THEN
                RAISE EXCEPTION 'users.avatar_url is set on some users';
            END IF;
            IF EXISTS (
                SELECT 1 FROM case_sources
                WHERE origin_message_id IS NOT NULL AND archived_at IS NULL
            ) THEN
                RAISE EXCEPTION 'An active source still has an origin_message_id';
            END IF;
        END $$;
        """
    )

    op.execute(
        """
        DELETE FROM cases AS c
        WHERE c.user_id IS NULL
          AND NOT EXISTS (SELECT 1 FROM case_sources WHERE case_id = c.id)
          AND NOT EXISTS (SELECT 1 FROM case_documents WHERE case_id = c.id)
          AND NOT EXISTS (SELECT 1 FROM chat_messages WHERE case_id = c.id)
          AND NOT EXISTS (SELECT 1 FROM case_analysis_results WHERE case_id = c.id)
          AND NOT EXISTS (SELECT 1 FROM case_reports WHERE case_id = c.id)
        """
    )

    op.execute(
        """
        UPDATE case_analysis_results
        SET external_context_json = external_context_json
            - 'source_reference_type' - 'source_revision' - 'evidence_revision'
        WHERE external_context_json ?| array['source_reference_type', 'source_revision',
                                             'evidence_revision']
        """
    )
    op.execute(
        "UPDATE case_sources SET provenance_json = provenance_json - 'extraction_id' "
        "WHERE provenance_json ? 'extraction_id'"
    )
    op.execute(
        "UPDATE case_sources SET source_metadata_json = source_metadata_json - 'evidence_role' "
        "WHERE source_metadata_json ? 'evidence_role'"
    )
    op.execute(
        "UPDATE chat_messages SET metadata_json = metadata_json - 'action' "
        "WHERE metadata_json ->> 'action' = 'follow_up'"
    )

    op.drop_table("document_extractions")

    op.drop_index("ix_case_sources_origin_message_id", table_name="case_sources")
    op.drop_constraint("fk_case_sources_origin_message_id", "case_sources", type_="foreignkey")
    op.drop_column("case_sources", "origin_message_id")
    op.drop_column("case_documents", "archived_at")
    op.drop_column("users", "avatar_url")
    op.drop_column("case_analysis_results", "answer")


def downgrade() -> None:
    op.add_column("case_analysis_results", sa.Column("answer", sa.Text(), nullable=True))
    op.execute("UPDATE case_analysis_results SET answer = summary")
    op.alter_column("case_analysis_results", "answer", nullable=False)

    op.add_column("users", sa.Column("avatar_url", sa.String(length=1024), nullable=True))
    op.add_column(
        "case_documents",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "case_sources",
        sa.Column("origin_message_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_case_sources_origin_message_id",
        "case_sources",
        "chat_messages",
        ["origin_message_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_case_sources_origin_message_id", "case_sources", ["origin_message_id"])

    op.create_table(
        "document_extractions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column(
            "config_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column(
            "provenance_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "warnings_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["case_documents.id"],
            name="fk_document_extractions_document_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_extractions"),
    )
    op.create_index(
        "ix_document_extractions_document_id_created_at",
        "document_extractions",
        ["document_id", "created_at"],
    )
    op.execute(
        """
        INSERT INTO document_extractions
            (id, document_id, provider, extracted_text, provenance_json, warnings_json, created_at)
        SELECT gen_random_uuid(), source.document_id,
               coalesce(source.provenance_json ->> 'provider', 'unknown'),
               source.exact_text, source.provenance_json,
               coalesce(source.provenance_json -> 'warnings', '[]'::jsonb), source.created_at
        FROM case_sources AS source
        WHERE source.source_kind = 'document' AND source.document_id IS NOT NULL
        """
    )
