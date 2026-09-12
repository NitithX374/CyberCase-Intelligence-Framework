from pathlib import Path
from pathlib import Path
import re


BASELINE = Path(__file__).parents[1] / "alembic" / "baseline_versions"


def test_migration_chain_is_clean_and_linear() -> None:
    migrations = sorted(BASELINE.glob("*.py"))
    assert [path.name for path in migrations] == [
        "0001_canonical_case_system.py",
        "0002_drop_chat_status_and_context_result.py",
        "0003_case_run_request_no_action.py",
    ]
    baseline_source = migrations[0].read_text(encoding="utf-8")
    assert 'revision = "0001_canonical_case_system"' in baseline_source
    assert "down_revision = None" in baseline_source
    mig2_source = migrations[1].read_text(encoding="utf-8")
    assert 'revision = "0002_drop_chat_status_and_context_result"' in mig2_source
    assert 'down_revision = "0001_canonical_case_system"' in mig2_source
    mig3_source = migrations[2].read_text(encoding="utf-8")
    assert 'revision = "0003_case_run_request_no_action"' in mig3_source
    assert 'down_revision = "0002_drop_chat_status_and_context_result"' in mig3_source


def test_baseline_declares_only_canonical_tables() -> None:
    source = (BASELINE / "0001_canonical_case_system.py").read_text(encoding="utf-8")
    created = re.findall(r'op\.create_table\(\s*"([^"]+)"', source)
    assert set(created) == {
        "users",
        "cases",
        "case_documents",
        "document_extractions",
        "case_evidence_sources",
        "case_evidence_revisions",
        "case_evidence_snapshots",
        "case_runs",
        "case_analysis_results",
        "rag_contexts",
        "case_reports",
        "chat_threads",
        "chat_messages",
    }
    assert "case_clarifications" not in created
    assert "chat_runs" not in created
    assert "chat_reports" not in created
    assert "case_state_versions" not in source
