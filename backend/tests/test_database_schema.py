from app.database import Base
from app.models import Case, ChatThread


def test_schema_contains_only_product_runtime_tables() -> None:
    assert set(Base.metadata.tables) == {
        "cases",
        "users",
        "chat_threads",
        "chat_messages",
        "rag_contexts",
        "case_reports",
        "case_documents",
        "document_extractions",
        "case_evidence_sources",
        "case_evidence_revisions",
        "case_evidence_snapshots",
        "case_runs",
        "case_analysis_results",
    }


def test_case_state_columns_and_tables_are_absent() -> None:
    assert "case_state_versions" not in Base.metadata.tables
    assert "case_clarifications" not in Base.metadata.tables
    assert "current_case_state_version_id" not in Base.metadata.tables["chat_threads"].c
    assert "case_run_id" in Base.metadata.tables["rag_contexts"].c
    assert "case_id" in Base.metadata.tables["rag_contexts"].c
    assert "case_state_version_id" not in Base.metadata.tables["rag_contexts"].c


def test_case_owns_one_shared_identity_chat_thread() -> None:
    cases = Base.metadata.tables["cases"]
    threads = Base.metadata.tables["chat_threads"]
    assert Case.chat_thread.property.uselist is False
    assert ChatThread.case.property.uselist is False
    assert any(
        foreign_key.target_fullname == "cases.id"
        for foreign_key in threads.c["case_id"].foreign_keys
    )
    assert cases.c["user_id"].nullable
    assert threads.c["id"].primary_key


def test_case_first_workflow_schema_is_case_owned() -> None:
    cases = Base.metadata.tables["cases"]
    runs = Base.metadata.tables["case_runs"]
    threads = Base.metadata.tables["chat_threads"]
    results = Base.metadata.tables["case_analysis_results"]
    messages = Base.metadata.tables["chat_messages"]
    assert cases.c["evidence_revision"].nullable is False
    assert cases.c["latest_analysis_result_id"].nullable
    assert runs.c["request_message_id"].nullable
    assert "context_analysis_result_id" not in runs.c
    assert "status" not in threads.c
    assert results.c["run_id"].nullable is False
    assert any(fk.ondelete == "CASCADE" for fk in results.c["run_id"].foreign_keys)
    assert messages.c["analysis_result_id"].nullable
    assert messages.c["message_kind"].nullable is False
    assert "in_reply_to_message_id" in messages.c
    assert messages.c["in_reply_to_message_id"].nullable
    assert "clarification_id" not in runs.c


def test_rag_context_is_bound_one_to_one_to_case_run() -> None:
    table = Base.metadata.tables["rag_contexts"]
    assert {str(target.column) for key in table.foreign_keys for target in [key]} >= {
        "case_runs.id",
        "cases.id",
        "case_evidence_snapshots.id",
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
        "evidence_snapshot_id",
        "retrieval_context_id",
    }.issubset(columns)
    assert table.c["case_id"].nullable is False
    assert table.c["analysis_result_id"].nullable is False
    assert table.c["evidence_snapshot_id"].nullable is False
    assert table.c["retrieval_context_id"].nullable is True
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


def test_chat_thread_has_unique_case_id() -> None:
    threads = Base.metadata.tables["chat_threads"]
    assert any(
        constraint.name == "uq_chat_threads_case_id"
        for constraint in threads.constraints
    )
