import copy
import importlib.util
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.reports.schemas import CaseReportContent, ReportFinding, ReportSource

MIGRATION = (
    Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0005_strip_inference_flag.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location("strip_inference_flag", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


migration = load_migration()


def finding(ordinal: int) -> ReportFinding:
    return ReportFinding(
        ordinal=ordinal,
        text=f"John sent email {ordinal}.",
        status="reported",
        supporting_contexts=[],
        contradicting_contexts=[],
        unverified_quotes=[],
    )


def report() -> dict:
    return CaseReportContent(
        title="An incident",
        summary="John sent two emails.",
        views_derived_from_claims=False,
        summary_units=[],
        findings=[finding(1), finding(2)],
        sources=[ReportSource(label="E-01", kind="narrative", detail="Statement")],
    ).model_dump(mode="json")


def test_the_migration_strips_a_report_back_to_what_a_report_stores_now():
    current = report()
    stored = copy.deepcopy(current)
    for item in stored["findings"]:
        item["is_inference"] = False

    with pytest.raises(ValidationError):
        CaseReportContent.model_validate(stored)

    migration.strip_report(stored)

    assert stored == current
    assert CaseReportContent.model_validate(stored).model_dump(mode="json") == current


def test_the_downgrade_gives_every_finding_back_the_flag_the_earlier_code_requires():
    restored = report()

    migration.restore_report(restored)

    assert [item["is_inference"] for item in restored["findings"]] == [False, False]
    assert migration.changed(restored, migration.restore_report) == restored
    migration.strip_report(restored)
    assert restored == report()


def test_a_record_without_the_flag_is_left_as_it_is():
    current = report()

    assert migration.changed(current, migration.strip_report) == current
    assert migration.changed(None, migration.strip_report) is None
    assert migration.changed({}, migration.strip_report) == {}
    assert migration.changed({}, migration.restore_report) == {}
    assert migration.changed({"findings": [None]}, migration.restore_report) == {"findings": [None]}
