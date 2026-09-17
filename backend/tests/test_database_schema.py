from app.database import Base
import app.models  # noqa: F401


def test_schema_contains_only_product_runtime_tables() -> None:
    assert set(Base.metadata.tables) == {
        "cases",
        "users",
        "chat_messages",
        "rag_contexts",
        "case_reports",
        "case_documents",
        "document_extractions",
        "case_evidence_sources",
        "case_runs",
        "case_analysis_results",
    }


def test_case_state_columns_and_tables_are_absent() -> None:
    assert "case_state_versions" not in Base.metadata.tables
    assert "case_clarifications" not in Base.metadata.tables
    assert "chat_threads" not in Base.metadata.tables
    assert "case_evidence_revisions" not in Base.metadata.tables
    assert "case_evidence_snapshots" not in Base.metadata.tables
    assert "case_run_id" in Base.metadata.tables["rag_contexts"].c
    assert "case_id" in Base.metadata.tables["rag_contexts"].c
    assert "case_state_version_id" not in Base.metadata.tables["rag_contexts"].c


def test_case_owns_chat_messages() -> None:
    messages = Base.metadata.tables["chat_messages"]
    cases = Base.metadata.tables["cases"]
    assert any(
        foreign_key.target_fullname == "cases.id"
        for foreign_key in messages.c["case_id"].foreign_keys
    )
    assert any(
        constraint.name == "uq_chat_messages_case_id_ordinal"
        for constraint in messages.constraints
    )
    assert cases.c["user_id"].nullable


def test_case_first_workflow_schema_is_case_owned() -> None:
    cases = Base.metadata.tables["cases"]
    runs = Base.metadata.tables["case_runs"]
    results = Base.metadata.tables["case_analysis_results"]
    messages = Base.metadata.tables["chat_messages"]
    assert cases.c["evidence_revision"].nullable is False
    assert cases.c["latest_analysis_result_id"].nullable
    assert "request_message_id" not in runs.c
    assert "operation" not in runs.c
    assert "context_analysis_result_id" not in runs.c
    assert results.c["run_id"].nullable is False
    assert any(fk.ondelete == "CASCADE" for fk in results.c["run_id"].foreign_keys)
    assert messages.c["analysis_result_id"].nullable
    assert messages.c["message_kind"].nullable is False
    assert "in_reply_to_message_id" in messages.c
    assert messages.c["in_reply_to_message_id"].nullable
    assert messages.c["client_request_id"].nullable
    assert "clarification_id" not in runs.c


def test_rag_context_is_bound_one_to_one_to_case_run() -> None:
    table = Base.metadata.tables["rag_contexts"]
    assert {str(target.column) for key in table.foreign_keys for target in [key]} >= {
        "case_runs.id",
        "cases.id",
    }
    assert any(
        constraint.name == "uq_rag_contexts_case_run_id"
        for constraint in table.constraints
    )


def test_report_uses_analysis_and_retrieval_bindings() -> None:
    table = Base.metadata.tables["case_reports"]
    columns = set(table.c.keys())
    assert {
        "case_id",
        "analysis_result_id",
        "retrieval_context_id",
    }.issubset(columns)
    assert table.c["case_id"].nullable is False
    assert table.c["analysis_result_id"].nullable is False
    assert table.c["retrieval_context_id"].nullable is True
    assert "evidence_snapshot_id" not in columns
    assert "source_snapshot_hash" not in columns
    assert "source_snapshot_json" not in columns
    assert "thread_id" not in columns
    assert "analysis_message_id" not in columns
    assert "extraction_message_id" not in columns
    assert "extraction_version" not in columns


def test_retrieval_context_foreign_keys_enforce_restrict() -> None:
    report_table = Base.metadata.tables["case_reports"]
    report_fk = next(
        fk for fk in report_table.foreign_keys
        if fk.target_fullname == "rag_contexts.retrieval_context_id"
    )
    assert report_fk.ondelete == "RESTRICT"

    analysis_table = Base.metadata.tables["case_analysis_results"]
    analysis_fk = next(
        fk for fk in analysis_table.foreign_keys
        if fk.target_fullname == "rag_contexts.retrieval_context_id"
    )
    assert analysis_fk.ondelete == "RESTRICT"
