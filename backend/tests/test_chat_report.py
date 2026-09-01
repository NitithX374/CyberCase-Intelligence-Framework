import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

from app.models.chat import ChatMessage, ChatThread
from app.models.rag_context import RagContext
from app.schemas.reports import ReportClaim
from app.services.reports import report_generation
from app.services.reports.report_snapshot import build_current_report_snapshot
from app.services.reports.report_template import build_template_report
from app.services.reports.report_validation import source_snapshot_hash, validate_structured_report


def report_snapshot(*, with_rag: bool = True):
    thread_id = uuid4()
    source_id = uuid4()
    retrieval_id = "retrieval-1" if with_rag else None
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
    context = (
        RagContext(
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
        if with_rag
        else None
    )
    return build_current_report_snapshot(thread, rag_context=context)


def test_report_snapshot_uses_raw_messages_analysis_and_run_context() -> None:
    snapshot = report_snapshot()
    assert snapshot.source_messages[0].content == "A public server was exploited."
    assert snapshot.retrieval_context_id == "retrieval-1"
    assert snapshot.mitre_rows[0].technique_id == "T1190"
    assert snapshot.unresolved_issues == ["The affected account is unknown"]
    assert "extraction" not in snapshot.model_dump(mode="json")


def test_report_snapshot_supports_general_analysis_without_rag_context() -> None:
    snapshot = report_snapshot(with_rag=False)
    report = build_template_report(snapshot)

    assert snapshot.retrieval_context_id is None
    assert snapshot.mitre_rows == []
    assert snapshot.analysis_answer == "The reported behavior is consistent with exploitation."
    assert "ไม่ได้ใช้กับกรณีนี้" in report.sections[3].items[0]


def test_report_snapshot_hash_ignores_capture_time() -> None:
    snapshot = report_snapshot(with_rag=False)
    later_snapshot = snapshot.model_copy(
        update={"created_at": snapshot.created_at + timedelta(minutes=5)}
    )

    assert source_snapshot_hash(snapshot) == source_snapshot_hash(later_snapshot)


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


class ReportGenerationTests(unittest.IsolatedAsyncioTestCase):
    async def test_generation_does_not_block_on_custom_binding_validation(self) -> None:
        snapshot = report_snapshot()
        report = build_template_report(snapshot).model_copy(
            update={
                "claims": [
                    ReportClaim(
                        claim_id="generic-claim",
                        section_id="case_summary",
                        text="A generic report claim.",
                        support_type="general_technical_knowledge",
                        source_message_ids=["external-source"],
                    )
                ]
            }
        )

        with patch.object(report_generation, "build_template_report", return_value=report):
            result = await report_generation.run_report_generation(snapshot)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.report, report)
        self.assertEqual(result.validation_errors, ())
