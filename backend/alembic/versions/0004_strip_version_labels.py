import copy
from collections.abc import Callable

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0004_strip_version_labels"
down_revision = "0003_strip_retired_fields"
branch_labels = None
depends_on = None

TRACE_LABELS = frozenset({"version", "validation_status"})
RECORD_LABELS = frozenset({"version"})


def drop(record: object, fields: frozenset[str]) -> None:
    if isinstance(record, dict):
        for field in fields.intersection(record):
            del record[field]


def field(record: object, name: str) -> object:
    return record.get(name) if isinstance(record, dict) else None


def strip_trace(trace: object) -> None:
    drop(trace, TRACE_LABELS)


def strip_external_context(context: object) -> None:
    drop(field(context, "followup_history"), RECORD_LABELS)
    drop(field(context, "sources_read"), RECORD_LABELS)
    augmentation = field(context, "technical_augmentation")
    drop(augmentation, RECORD_LABELS)
    drop(field(augmentation, "applicability"), RECORD_LABELS)


def strip_report(report: object) -> None:
    drop(report, RECORD_LABELS)


def strip_message(metadata: object) -> None:
    drop(field(metadata, "analysis_trace"), TRACE_LABELS)


Strip = Callable[[object], None]


def stripped(value: object, strip: Strip) -> object:
    cleaned = copy.deepcopy(value)
    strip(cleaned)
    return cleaned


def rewrite(table_name: str, column_name: str, strip: Strip) -> None:
    table = sa.table(
        table_name,
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column(column_name, postgresql.JSONB()),
    )
    column = table.c[column_name]
    bind = op.get_bind()
    rows = bind.execute(sa.select(table.c.id, column).where(column.is_not(None))).all()
    for row_id, value in rows:
        cleaned = stripped(value, strip)
        if cleaned != value:
            bind.execute(
                sa.update(table).where(table.c.id == row_id).values({column_name: cleaned})
            )


def upgrade() -> None:
    rewrite("case_analysis_results", "trace_json", strip_trace)
    rewrite("case_analysis_results", "external_context_json", strip_external_context)
    rewrite("case_reports", "structured_report", strip_report)
    rewrite("chat_messages", "metadata_json", strip_message)


def downgrade() -> None:
    pass
