from app.database import Base
import app.models


def test_schema_contains_only_product_runtime_tables() -> None:
    assert set(Base.metadata.tables) == {
        "chat_threads",
        "chat_messages",
        "chat_runs",
        "rag_contexts",
        "chat_reports",
    }


def test_case_state_columns_and_tables_are_absent() -> None:
    assert "case_state_versions" not in Base.metadata.tables
    assert "current_case_state_version_id" not in Base.metadata.tables["chat_threads"].c
    assert "run_id" in Base.metadata.tables["rag_contexts"].c
    assert "case_state_version_id" not in Base.metadata.tables["rag_contexts"].c


def test_rag_context_is_bound_one_to_one_to_chat_run() -> None:
    table = Base.metadata.tables["rag_contexts"]
    assert {str(target.column) for key in table.foreign_keys for target in [key]} >= {
        "chat_runs.id",
        "chat_threads.id",
    }
    assert any(
        constraint.name == "uq_rag_contexts_run_id"
        for constraint in table.constraints
    )


def test_report_uses_analysis_and_retrieval_bindings() -> None:
    columns = set(Base.metadata.tables["chat_reports"].c.keys())
    assert {"analysis_message_id", "retrieval_context_id"}.issubset(columns)
    assert "extraction_message_id" not in columns
    assert "extraction_version" not in columns
