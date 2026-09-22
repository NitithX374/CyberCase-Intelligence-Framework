import app.models  # noqa: F401
from app.database import Base
from app.schemas.chat import ChatMessageRead


def test_schema_contains_only_product_runtime_tables() -> None:
    assert set(Base.metadata.tables) == {
        "cases",
        "users",
        "chat_messages",
        "case_reports",
        "case_documents",
        "document_extractions",
        "case_sources",
        "case_analysis_results",
    }


def test_run_and_retrieval_tables_are_gone() -> None:
    """An analysis is not a job, so there is no row describing one."""

    assert "case_runs" not in Base.metadata.tables
    assert "rag_contexts" not in Base.metadata.tables
    assert "run_id" not in Base.metadata.tables["case_analysis_results"].c


def test_case_state_tables_are_absent() -> None:
    assert "case_state_versions" not in Base.metadata.tables
    assert "case_clarifications" not in Base.metadata.tables
    assert "chat_threads" not in Base.metadata.tables
    assert "case_evidence_revisions" not in Base.metadata.tables
    assert "case_evidence_snapshots" not in Base.metadata.tables


def test_case_owns_chat_messages() -> None:
    messages = Base.metadata.tables["chat_messages"]
    cases = Base.metadata.tables["cases"]
    assert any(
        foreign_key.target_fullname == "cases.id"
        for foreign_key in messages.c["case_id"].foreign_keys
    )
    assert any(
        constraint.name == "uq_chat_messages_case_id_ordinal" for constraint in messages.constraints
    )
    assert cases.c["user_id"].nullable


def test_case_owns_its_analysis() -> None:
    cases = Base.metadata.tables["cases"]
    results = Base.metadata.tables["case_analysis_results"]
    messages = Base.metadata.tables["chat_messages"]
    assert cases.c["source_revision"].nullable is False
    assert cases.c["latest_analysis_result_id"].nullable
    assert results.c["source_revision"].nullable is False
    assert any(fk.ondelete == "CASCADE" for fk in results.c["case_id"].foreign_keys)
    assert messages.c["analysis_result_id"].nullable
    assert messages.c["message_kind"].nullable is False
    assert "in_reply_to_message_id" in messages.c
    assert messages.c["in_reply_to_message_id"].nullable
    assert "retrieval_context_id" not in messages.c


def test_report_stores_content_and_nothing_else() -> None:
    """A template render has no provider, prompt, latency or token count."""

    table = Base.metadata.tables["case_reports"]
    columns = set(table.c.keys())
    assert columns == {
        "id",
        "case_id",
        "analysis_result_id",
        "version_number",
        "structured_report",
        "created_at",
    }
    assert table.c["analysis_result_id"].nullable is False
    assert table.c["structured_report"].nullable is False
    # One report per analysis; regenerating returns the one that exists.
    assert any(
        constraint.name == "uq_case_reports_analysis_result_id" for constraint in table.constraints
    )


def test_retrieval_context_id_points_at_no_table() -> None:
    """It labels what was retrieved; the retrieval itself is stored with the analysis."""

    table = Base.metadata.tables["case_analysis_results"]
    assert table.c["retrieval_context_id"].foreign_keys == set()


def test_chat_message_does_not_own_retrieval_identity() -> None:
    assert "retrieval_context_id" not in Base.metadata.tables["chat_messages"].c
    assert "retrieval_context_id" not in ChatMessageRead.model_fields
