import copy
from collections.abc import Callable

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0003_strip_retired_fields"
down_revision = "0002_source_deactivation"
branch_labels = None
depends_on = None

TRACE_FIELDS = frozenset({"grounding"})
CLAIM_FIELDS = frozenset({"reasoning_summary"})
VERIFIER_FIELDS = frozenset(
    {
        "model",
        "label",
        "entailment",
        "threshold",
        "neutral",
        "contradiction",
        "p_supported",
        "selected_citation_indices",
        "considered_citation_indices",
        "selected_evidence_unit_ids",
        "source_similarities",
        "selector_threshold",
        "selection_ms",
        "raw_tokens",
        "truncated",
        "duration_ms",
    }
)
CITATION_FIELDS = frozenset({"tolerated_differences", "review_flags"})
UNVERIFIED_FIELDS = frozenset({"written_quote", "near_passage", "meaning_passage"})
VIEW_FIELDS = frozenset({"projection_grounding", "field_spans"})
EXTRACTION_FIELDS = frozenset(
    {
        "revision",
        "library_version",
        "device",
        "threshold",
        "quantization",
        "runtime_revision",
        "field_resolution_issues",
    }
)
AUGMENTATION_FIELDS = frozenset({"shadow_applicability"})
REPORT_VIEW_FIELDS = frozenset({"projection_grounding"})
REPORT_UNVERIFIED_FIELDS = frozenset({"written_quote", "places", "meaning_passage"})
REPORT_FINDING_FIELDS = frozenset(
    {
        "supporting_tolerated",
        "contradicting_tolerated",
        "supporting_marked",
        "contradicting_marked",
        "reasoning_summary",
    }
)


def drop(record: object, fields: frozenset[str]) -> None:
    if isinstance(record, dict):
        for field in fields.intersection(record):
            del record[field]


def field(record: object, name: str) -> object:
    return record.get(name) if isinstance(record, dict) else None


def items(record: object, name: str) -> list[object]:
    value = field(record, name)
    return value if isinstance(value, list) else []


def strip_citations(record: object) -> None:
    for name in ("supporting_citations", "contradicting_citations"):
        for citation in items(record, name):
            drop(citation, CITATION_FIELDS)


def strip_claim(claim: object) -> None:
    drop(claim, CLAIM_FIELDS)
    drop(field(claim, "semantic_grounding"), VERIFIER_FIELDS)
    strip_citations(claim)
    for citation in items(claim, "unverified_citations"):
        drop(citation, UNVERIFIED_FIELDS)


def strip_trace(trace: object) -> None:
    drop(trace, TRACE_FIELDS)
    for claim in items(trace, "claims"):
        strip_claim(claim)
    for name in ("involved_parties", "timeline", "impacts"):
        for row in items(trace, name):
            drop(row, VIEW_FIELDS)
    drop(field(trace, "view_extraction"), EXTRACTION_FIELDS)


def strip_external_context(context: object) -> None:
    drop(field(context, "technical_augmentation"), AUGMENTATION_FIELDS)


def strip_report(report: object) -> None:
    for name in ("parties", "timeline", "impacts"):
        for row in items(report, name):
            drop(row, REPORT_VIEW_FIELDS)
    for finding in items(report, "findings"):
        drop(finding, REPORT_FINDING_FIELDS)
        for quote in items(finding, "unverified_quotes"):
            drop(quote, REPORT_UNVERIFIED_FIELDS)


def strip_message(metadata: object) -> None:
    trace = field(metadata, "analysis_trace")
    drop(trace, TRACE_FIELDS)
    for claim in items(trace, "claims"):
        strip_claim(claim)
    for unit in items(metadata, "answer_units"):
        strip_citations(unit)


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
