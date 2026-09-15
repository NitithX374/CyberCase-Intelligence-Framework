from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.services.cases.caseService import serializeCase
from app.services.workflow.caseRunService import analysis_freshness


def test_analysis_freshness_compares_case_and_result_revision() -> None:
    case = SimpleNamespace(evidence_revision=3)

    assert analysis_freshness(case, None) == "missing"
    assert analysis_freshness(case, SimpleNamespace(evidence_revision=3)) == "current"
    assert analysis_freshness(case, SimpleNamespace(evidence_revision=2)) == "stale"


def test_case_serialization_reports_result_freshness_without_snapshot_state() -> None:
    now = datetime.now(timezone.utc)
    case = SimpleNamespace(
        id=uuid4(),
        user_id=None,
        title="Case",
        evidence_revision=1,
        latest_analysis_result_id=uuid4(),
        latest_analysis_result=SimpleNamespace(evidence_revision=1),
        chat_messages=[],
        case_runs=[],
        created_at=now,
        updated_at=now,
    )

    serialized = serializeCase(case)

    assert serialized.analysis_freshness == "current"
    assert serialized.status == "answered"
