from datetime import datetime, timezone
from uuid import uuid4

from app.models.chat import ChatMessage, ChatThread
from app.models.rag_context import RagContext
from app.services.reports.report_snapshot import build_current_report_snapshot
from app.services.reports.report_template import build_template_report
from app.services.reports.report_validation import validate_structured_report


def report_snapshot():
    thread_id = uuid4()
    source_id = uuid4()
    retrieval_id = "retrieval-1"
    thread = ChatThread(id=thread_id, title="Demo case", status="answered")
    thread.messages = [
        ChatMessage(
            id=source_id,
            thread_id=thread_id,
            ordinal=1,
            role="user",
            content="A public server was exploited.",
            metadata_json={"evidence_kind": "initial_case_narrative"},
        ),
        ChatMessage(
            id=uuid4(),
            thread_id=thread_id,
            ordinal=2,
            role="assistant",
            content="The reported behavior is consistent with exploitation.",
            retrieval_context_id=retrieval_id,
            metadata_json={
                "analysis_kind": "grounded_main_analysis",
                "analysis_trace": {"version": "analysis_trace_v2"},
                "chat_followup": {
                    "gap_analysis": {
                        "gaps": [{"description": "The affected account is unknown"}]
                    }
                },
            },
        ),
    ]
    context = RagContext(
        retrieval_context_id=retrieval_id,
        thread_id=thread_id,
        run_id=uuid4(),
        context="External MITRE context",
        mitre_table=[
            {
                "technique_id": "T1190",
                "name": "Exploit Public-Facing Application",
                "description": "External technical description",
            }
        ],
        created_at=datetime.now(timezone.utc),
    )
    return build_current_report_snapshot(thread, rag_context=context)


def test_report_snapshot_uses_raw_messages_analysis_and_run_context() -> None:
    snapshot = report_snapshot()
    assert snapshot.source_messages[0].content == "A public server was exploited."
    assert snapshot.retrieval_context_id == "retrieval-1"
    assert snapshot.mitre_rows[0].technique_id == "T1190"
    assert snapshot.unresolved_issues == ["The affected account is unknown"]
    assert "extraction" not in snapshot.model_dump(mode="json")


def test_deterministic_report_validates_against_source_and_mitre_bindings() -> None:
    snapshot = report_snapshot()
    report = build_template_report(snapshot)
    validate_structured_report(
        report,
        source_message_ids={str(item.message_id) for item in snapshot.source_messages},
        mitre_ids={row.technique_id for row in snapshot.mitre_rows},
    )
    assert report.status == "provisional_unverified"
    assert len(report.sections) == 7
    assert report.claims[0].source_message_ids
