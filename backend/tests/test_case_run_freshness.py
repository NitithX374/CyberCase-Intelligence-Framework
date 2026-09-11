from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.services.workflow.caseRunService import analysis_freshness
from app.services.cases.caseService import serializeCase


def test_analysis_freshness_is_missing_when_snapshot_is_unavailable() -> None:
    case = SimpleNamespace(evidence_revision=3)
    result = SimpleNamespace(snapshot=None)

    assert analysis_freshness(case, result) == "missing"


def test_analysis_freshness_compares_snapshot_revision() -> None:
    case = SimpleNamespace(evidence_revision=3)

    assert (
        analysis_freshness(
            case,
            SimpleNamespace(snapshot=SimpleNamespace(evidence_revision=3)),
        )
        == "current"
    )
    assert (
        analysis_freshness(
            case,
            SimpleNamespace(snapshot=SimpleNamespace(evidence_revision=2)),
        )
        == "stale"
    )


def test_case_serialization_reports_missing_freshness_without_snapshot() -> None:
    now = datetime.now(timezone.utc)
    case = SimpleNamespace(
        id=uuid4(),
        user_id=None,
        title="Case",
        evidence_revision=1,
        latest_analysis_result_id=uuid4(),
        latest_analysis_result=SimpleNamespace(snapshot=None),
        chat_thread=None,
        case_runs=[],
        clarifications=[],
        created_at=now,
        updated_at=now,
    )

    serialized = serializeCase(case)

    assert serialized.analysis_freshness == "missing"
