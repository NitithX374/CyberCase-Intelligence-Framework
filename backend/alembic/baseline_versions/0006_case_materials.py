"""Add immutable Case materials, evidence revisions, and snapshots."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006_case_materials"
down_revision = "0005_case_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("evidence_revision", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_check_constraint(
        "ck_cases_evidence_revision_nonnegative",
        "cases",
        "evidence_revision >= 0",
    )
    op.create_table(
        "case_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=160), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("content_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("content_bytes", sa.LargeBinary(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("size_bytes >= 0", name="ck_case_documents_size_nonnegative"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_documents_case_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_case_documents"),
    )
    op.create_index("ix_case_documents_case_id_created_at", "case_documents", ["case_id", "created_at"])
    op.create_table(
        "document_extractions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("provenance_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("warnings_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("revision > 0", name="ck_document_extractions_revision_positive"),
        sa.ForeignKeyConstraint(["document_id"], ["case_documents.id"], name="fk_document_extractions_document_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_document_extractions"),
        sa.UniqueConstraint("document_id", "revision", name="uq_document_extractions_document_revision"),
    )
    op.create_index("ix_document_extractions_document_id_created_at", "document_extractions", ["document_id", "created_at"])
    op.create_table(
        "case_evidence_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_kind", sa.String(length=40), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("origin_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_metadata_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "source_kind IN ('reviewed_document', 'narrative', 'clarification_answer', 'explicit_chat_addition', 'legacy_unbound')",
            name="ck_case_evidence_sources_kind",
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_evidence_sources_case_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["case_documents.id"], name="fk_case_evidence_sources_document_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["origin_message_id"], ["chat_messages.id"], name="fk_case_evidence_sources_origin_message_id", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_case_evidence_sources"),
    )
    op.create_index("ix_case_evidence_sources_case_id_created_at", "case_evidence_sources", ["case_id", "created_at"])
    op.create_table(
        "case_evidence_revisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("exact_text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("provenance_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("extraction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("admitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("revision > 0", name="ck_case_evidence_revisions_revision_positive"),
        sa.ForeignKeyConstraint(["extraction_id"], ["document_extractions.id"], name="fk_case_evidence_revisions_extraction_id", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["case_evidence_sources.id"], name="fk_case_evidence_revisions_source_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_case_evidence_revisions"),
        sa.UniqueConstraint("source_id", "revision", name="uq_case_evidence_revisions_source_revision"),
    )
    op.create_index("ix_case_evidence_revisions_source_id_revision", "case_evidence_revisions", ["source_id", "revision"])
    op.create_table(
        "case_evidence_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_revision", sa.Integer(), nullable=False),
        sa.Column("format_version", sa.String(length=40), nullable=False),
        sa.Column("manifest_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("manifest_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("evidence_revision >= 0", name="ck_case_evidence_snapshots_revision_nonnegative"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], name="fk_case_evidence_snapshots_case_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_case_evidence_snapshots"),
        sa.UniqueConstraint("case_id", "evidence_revision", "manifest_sha256", name="uq_case_evidence_snapshots_identity"),
    )
    op.create_index("ix_case_evidence_snapshots_case_id_created_at", "case_evidence_snapshots", ["case_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_case_evidence_snapshots_case_id_created_at", table_name="case_evidence_snapshots")
    op.drop_table("case_evidence_snapshots")
    op.drop_index("ix_case_evidence_revisions_source_id_revision", table_name="case_evidence_revisions")
    op.drop_table("case_evidence_revisions")
    op.drop_index("ix_case_evidence_sources_case_id_created_at", table_name="case_evidence_sources")
    op.drop_table("case_evidence_sources")
    op.drop_index("ix_document_extractions_document_id_created_at", table_name="document_extractions")
    op.drop_table("document_extractions")
    op.drop_index("ix_case_documents_case_id_created_at", table_name="case_documents")
    op.drop_table("case_documents")
    op.drop_constraint("ck_cases_evidence_revision_nonnegative", "cases", type_="check")
    op.drop_column("cases", "evidence_revision")
