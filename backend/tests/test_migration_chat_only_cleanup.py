from pathlib import Path
import re


BASELINE = Path(__file__).parents[1] / "alembic" / "baseline_versions"


def test_migration_chain_is_one_clean_demo_baseline() -> None:
    migrations = list(BASELINE.glob("*.py"))
    assert [path.name for path in migrations] == ["0001_raw_evidence_chat.py"]
    source = migrations[0].read_text(encoding="utf-8")
    assert 'revision = "0001_raw_evidence_chat"' in source
    assert "down_revision = None" in source


def test_baseline_declares_only_surviving_tables() -> None:
    source = (BASELINE / "0001_raw_evidence_chat.py").read_text(encoding="utf-8")
    created = re.findall(r'op\.create_table\(\s*"([^"]+)"', source)
    assert created == [
        "chat_threads",
        "chat_messages",
        "chat_runs",
        "rag_contexts",
        "chat_reports",
    ]
    assert "case_state_versions" not in source
    assert "users" not in source
    assert "case_state_version_id" not in source
