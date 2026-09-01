from pathlib import Path
import re


BASELINE = Path(__file__).parents[1] / "alembic" / "baseline_versions"


def test_migration_chain_is_clean_and_linear() -> None:
    migrations = sorted(BASELINE.glob("*.py"))
    assert [path.name for path in migrations] == [
        "0001_raw_evidence_chat.py",
        "0002_optional_report_retrieval_context.py",
    ]
    baseline_source = migrations[0].read_text(encoding="utf-8")
    optional_context_source = migrations[1].read_text(encoding="utf-8")
    assert 'revision = "0001_raw_evidence_chat"' in baseline_source
    assert "down_revision = None" in baseline_source
    assert 'revision = "0002_optional_report_context"' in optional_context_source
    assert 'down_revision = "0001_raw_evidence_chat"' in optional_context_source
    revision_ids = re.findall(
        r'^revision = "([^"]+)"$',
        "\n".join([baseline_source, optional_context_source]),
        flags=re.MULTILINE,
    )
    assert all(len(revision_id) <= 32 for revision_id in revision_ids)


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
