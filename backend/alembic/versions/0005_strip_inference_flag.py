import copy
from collections.abc import Callable

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005_strip_inference_flag"
down_revision = "0004_strip_version_labels"
branch_labels = None
depends_on = None

FLAG = "is_inference"


def items(record: object, name: str) -> list[object]:
    value = record.get(name) if isinstance(record, dict) else None
    return value if isinstance(value, list) else []


def strip_report(report: object) -> None:
    for finding in items(report, "findings"):
        if isinstance(finding, dict):
            finding.pop(FLAG, None)


def restore_report(report: object) -> None:
    for finding in items(report, "findings"):
        if isinstance(finding, dict):
            finding.setdefault(FLAG, False)


Change = Callable[[object], None]


def changed(value: object, change: Change) -> object:
    cleaned = copy.deepcopy(value)
    change(cleaned)
    return cleaned


def rewrite(table_name: str, column_name: str, change: Change) -> None:
    table = sa.table(
        table_name,
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column(column_name, postgresql.JSONB()),
    )
    column = table.c[column_name]
    bind = op.get_bind()
    rows = bind.execute(sa.select(table.c.id, column).where(column.is_not(None))).all()
    for row_id, value in rows:
        cleaned = changed(value, change)
        if cleaned != value:
            bind.execute(
                sa.update(table).where(table.c.id == row_id).values({column_name: cleaned})
            )


def upgrade() -> None:
    rewrite("case_reports", "structured_report", strip_report)


def downgrade() -> None:
    rewrite("case_reports", "structured_report", restore_report)
