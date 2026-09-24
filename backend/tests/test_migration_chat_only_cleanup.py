import re
from pathlib import Path

BASELINE = Path(__file__).parents[1] / "alembic" / "baseline_versions"


def test_migration_chain_is_clean_and_linear() -> None:
    migrations = sorted(BASELINE.glob("*.py"))
    assert [path.name for path in migrations] == [
        "0001_canonical_case_system.py",
        "0002_case_run_active_index.py",
        "0003_received_case_material.py",
        "0004_external_context_json.py",
        "0005_remove_case_runs.py",
        "0006_source_vocabulary.py",
        "0007_report_content_only.py",
        "0008_chat_client_request_id.py",
        "0009_followup_gap_key.py",
        "0010_foreign_key_indexes.py",
        "0011_retrieval_context_reuse.py",
        "0012_analysis_assessment_status.py",
        "0013_retrieval_context_contract.py",
        "0014_archive_legacy_followup_sources.py",
        "0015_schema_cleanup.py",
        "0016_fold_extractions.py",
    ]
    baseline_source = migrations[0].read_text(encoding="utf-8")
    assert 'revision = "0001_canonical_case_system"' in baseline_source
    assert "down_revision = None" in baseline_source
    for path in migrations:
        source = path.read_text(encoding="utf-8")
        revision = re.search(r'^revision = "([^"]+)"$', source, re.MULTILINE)
        assert revision is not None
        assert len(revision.group(1)) <= 32


def test_retrieval_context_contract_migration_preserves_nested_mitre_data() -> None:
    source = (BASELINE / "0013_retrieval_context_contract.py").read_text(encoding="utf-8")
    assert 'down_revision = "0012_analysis_assessment_status"' in source
    assert 'op.drop_column("chat_messages", "retrieval_context_id")' in source
    assert "external_context_json = external_context_json - 'mitre_table'" in source
    assert "external_context_json #> '{technical_augmentation,mitre_table}'" in source
    assert "retrieval_context_json" not in source
    assert "archived_at" not in source


def test_baseline_declares_only_canonical_tables() -> None:
    source = (BASELINE / "0001_canonical_case_system.py").read_text(encoding="utf-8")
    created = re.findall(r'op\.create_table\(\s*"([^"]+)"', source)
    assert set(created) == {
        "users",
        "cases",
        "case_documents",
        "document_extractions",
        "case_evidence_sources",
        "case_runs",
        "case_analysis_results",
        "rag_contexts",
        "case_reports",
        "chat_messages",
    }
    assert "chat_threads" not in created
    assert "case_evidence_snapshots" not in created
    assert "case_evidence_revisions" not in created
    assert "case_clarifications" not in created
    assert "chat_runs" not in created
    assert "chat_reports" not in created
    assert "case_state_versions" not in source
