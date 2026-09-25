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
        "case_sources",
        "case_analysis_results",
    }


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
    assert any(
        constraint.name == "uq_case_reports_analysis_result_id" for constraint in table.constraints
    )


def test_an_analysis_keeps_its_retrieval_and_version_inside_its_trace() -> None:
    columns = Base.metadata.tables["case_analysis_results"].c
    assert "retrieval_context_id" not in columns
    assert "schema_version" not in columns
    assert "run_id" not in columns


def test_a_case_source_is_a_document_or_a_narrative_and_is_never_archived() -> None:
    table = Base.metadata.tables["case_sources"]
    kinds = next(
        constraint for constraint in table.constraints if constraint.name == "ck_case_sources_kind"
    )
    assert str(kinds.sqltext) == "source_kind IN ('document', 'narrative')"
    assert "archived_at" not in table.c


def test_chat_message_does_not_own_retrieval_identity() -> None:
    assert "retrieval_context_id" not in ChatMessageRead.model_fields
