from pathlib import Path
import re


BASELINE = Path(__file__).parents[1] / "alembic" / "baseline_versions"


def test_migration_chain_is_clean_and_linear() -> None:
    migrations = sorted(BASELINE.glob("*.py"))
    assert [path.name for path in migrations] == [
        "0001_raw_evidence_chat.py",
        "0002_optional_report_retrieval_context.py",
        "0003_user_oauth_and_thread_ownership.py",
        "0004_password_accounts.py",
        "0005_case_domain.py",
        "0006_case_materials.py",
        "0007_case_runs_and_results.py",
        "0008_case_clarifications.py",
        "0009_case_report_bindings.py",
        "0010_preserve_reports_after_chat_delete.py",
    ]
    baseline_source = migrations[0].read_text(encoding="utf-8")
    optional_context_source = migrations[1].read_text(encoding="utf-8")
    assert 'revision = "0001_raw_evidence_chat"' in baseline_source
    assert "down_revision = None" in baseline_source
    assert 'revision = "0002_optional_report_context"' in optional_context_source
    assert 'down_revision = "0001_raw_evidence_chat"' in optional_context_source
    oauth_source = migrations[2].read_text(encoding="utf-8")
    password_source = migrations[3].read_text(encoding="utf-8")
    assert 'down_revision = "0002_optional_report_context"' in oauth_source
    assert 'down_revision = "0003_user_oauth_threads"' in password_source
    case_source = migrations[4].read_text(encoding="utf-8")
    assert 'revision = "0005_case_domain"' in case_source
    assert 'down_revision = "0004_password_accounts"' in case_source
    assert 'INSERT INTO cases' in case_source
    assert 'fk_chat_threads_id_cases' in case_source
    materials_source = migrations[5].read_text(encoding="utf-8")
    workflow_source = migrations[6].read_text(encoding="utf-8")
    clarification_source = migrations[7].read_text(encoding="utf-8")
    report_source = migrations[8].read_text(encoding="utf-8")
    preserve_source = migrations[9].read_text(encoding="utf-8")
    assert 'revision = "0006_case_materials"' in materials_source
    assert 'down_revision = "0005_case_domain"' in materials_source
    assert 'revision = "0007_case_runs_and_results"' in workflow_source
    assert 'down_revision = "0006_case_materials"' in workflow_source
    assert 'revision = "0008_case_clarifications"' in clarification_source
    assert 'down_revision = "0007_case_runs_and_results"' in clarification_source
    assert 'revision = "0009_case_report_bindings"' in report_source
    assert 'down_revision = "0008_case_clarifications"' in report_source
    assert "UPDATE chat_reports AS report" in report_source
    assert "analysis_message_id" in report_source
    assert 'revision = "0010_preserve_chat_reports"' in preserve_source
    assert 'down_revision = "0009_case_report_bindings"' in preserve_source
    assert 'ondelete="SET NULL"' in preserve_source
    revision_ids = re.findall(
        r'^revision = "([^"]+)"$',
        "\n".join([
            baseline_source,
            optional_context_source,
            oauth_source,
            password_source,
            case_source,
            materials_source,
            workflow_source,
            clarification_source,
        ]),
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
