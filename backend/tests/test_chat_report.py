
import json
import unittest
from datetime import datetime, timezone
from uuid import uuid4

from app.config import settings
from app.models.chat import ChatMessage, ChatThread
from app.models.report import ChatReport
from app.schemas.reports import (
    ChatReportCreate,
    PRELIMINARY_REPORT_SECTION_HEADINGS,
    PRELIMINARY_REPORT_SECTION_IDS,
    REPORT_SECTION_HEADINGS,
    REPORT_SECTION_IDS,
    ReportSection,
    StructuredReport,
)
from app.services.extraction.llm_extraction import (
    BASELINE_EXTRACTION_PROMPT_VERSION,
    CaseState,
    ExtractedEntity,
    ExtractedEvidence,
    ExtractedRelationship,
    ExtractedTimelineEvent,
)
from app.services.reports.report_generation import (
    REPORT_TEMPLATE_MODEL,
    REPORT_TEMPLATE_PROMPT_VERSION,
    REPORT_TEMPLATE_PROVIDER,
    build_template_report,
    run_report_generation,
    validate_structured_report,
)
from app.services.reports.report_service import (
    ChatReportService,
    ReportGenerationConflict,
    build_current_report_snapshot,
)


class _ScalarList:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def all(self) -> list[object]:
        return self.values


class _Result:
    def __init__(self, value: object = None, values: list[object] | None = None) -> None:
        self.value = value
        self.values = values or ([] if value is None else [value])

    def scalar_one_or_none(self) -> object:
        return self.value

    def scalar_one(self) -> object:
        return self.value

    def scalars(self) -> _ScalarList:
        return _ScalarList(self.values)


class _Transaction:
    async def __aenter__(self) -> "_Transaction":
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> bool:
        return False


class FakeReportDb:
    """Small async-session double for report persistence/idempotency tests."""

    def __init__(self, thread: ChatThread) -> None:
        self.thread = thread
        self.reports: list[ChatReport] = []

    def begin(self) -> _Transaction:
        return _Transaction()

    async def execute(self, statement: object) -> _Result:
        entity = None
        column_descriptions = getattr(statement, "column_descriptions", ())
        if column_descriptions:
            entity = column_descriptions[0].get("entity")
        if entity is ChatThread:
            return _Result(self.thread)
        if entity is ChatReport:
            statement_text = str(statement).casefold()
            if "max(" in statement_text:
                return _Result(max((report.version_number for report in self.reports), default=None))
            return _Result(self.reports[0] if self.reports else None)
        return _Result(values=list(self.reports))

    def add(self, report: ChatReport) -> None:
        self.reports.append(report)

    async def flush(self) -> None:
        report = self.reports[-1]
        if report.id is None:
            report.id = uuid4()
        if report.created_at is None:
            report.created_at = datetime.now(timezone.utc)

    async def refresh(self, report: ChatReport) -> None:
        return None


class ChatReportTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.original_settings = {
            "chat_report_enabled": settings.chat_report_enabled,
            "chat_report_max_input_chars": settings.chat_report_max_input_chars,
        }
        settings.chat_report_enabled = True
        settings.chat_report_max_input_chars = 80_000

    def tearDown(self) -> None:
        for name, value in self.original_settings.items():
            setattr(settings, name, value)

    async def test_report_input_excludes_terminal_assistant_prose(self) -> None:
        thread = _report_thread()
        snapshot = build_current_report_snapshot(thread)

        serialized = json.dumps(snapshot.model_dump(mode="json"))
        self.assertNotIn("Terminal assistant prose must not enter the report", serialized)
        self.assertEqual(snapshot.source_messages[0].message_id, thread.messages[0].id)
        self.assertEqual(snapshot.mitre_rows[0].technique_id, "T1059.001")

    async def test_generation_is_deterministic(self) -> None:
        snapshot = build_current_report_snapshot(_report_thread())

        first = await run_report_generation(snapshot)
        second = await run_report_generation(snapshot)

        self.assertEqual(first.status, "completed")
        self.assertEqual(second.status, "completed")
        assert first.report is not None
        assert second.report is not None
        self.assertEqual(
            first.report.model_dump(mode="json"),
            second.report.model_dump(mode="json"),
        )
        self.assertEqual(first.provider, REPORT_TEMPLATE_PROVIDER)
        self.assertEqual(first.model, REPORT_TEMPLATE_MODEL)
        self.assertEqual(first.prompt_version, REPORT_TEMPLATE_PROMPT_VERSION)
        self.assertIsNone(first.input_tokens)
        self.assertIsNone(first.output_tokens)

    def test_template_preserves_statuses_and_does_not_pair_mitre_rows(self) -> None:
        snapshot = build_current_report_snapshot(_report_thread())
        source_id = snapshot.source_messages[0].message_id
        snapshot.extraction.evidence.append(
            ExtractedEvidence(
                evidence_id="E-002",
                title="Unresolved artifact",
                description="The artifact remains unresolved.",
                artifact_type="file",
                status="not_confirmed",
                confidence="low",
                source_type="user_reported",
                source_message_ids=[source_id],
            )
        )
        snapshot.extraction.entities = [
            ExtractedEntity(
                entity_id="entity-host",
                name="host-7",
                entity_type="host",
                reported_role="affected system",
                confidence="high",
                source_message_ids=[source_id],
            ),
            ExtractedEntity(
                entity_id="entity-user",
                name="account-a",
                entity_type="account",
                reported_role=None,
                confidence="medium",
                source_message_ids=[source_id],
            ),
        ]
        snapshot.extraction.relationships = [
            ExtractedRelationship(
                relationship_id="relationship-1",
                subject_entity_id="entity-user",
                predicate="accessed",
                object_entity_id="entity-host",
                statement="The account was described as accessing the host.",
                status="contradicted",
                confidence="low",
                source_message_ids=[source_id],
            )
        ]

        report = build_template_report(snapshot)

        self.assertEqual(
            tuple(section.section_id for section in report.sections),
            PRELIMINARY_REPORT_SECTION_IDS,
        )
        self.assertEqual(report.report_version, "preliminary_analysis_report_v1")
        self.assertEqual(
            tuple(section.heading for section in report.sections),
            tuple(
                PRELIMINARY_REPORT_SECTION_HEADINGS[section_id]
                for section_id in PRELIMINARY_REPORT_SECTION_IDS
            ),
        )
        self.assertEqual(report.status, "provisional_unverified")
        evidence_claims = [
            claim for claim in report.claims if claim.section_id == "indicators_found"
        ]
        self.assertEqual(
            [claim.support_type for claim in evidence_claims],
            ["user_reported", "extraction_candidate"],
        )
        self.assertIn("Status: reported", evidence_claims[0].text)
        self.assertIn("Confidence: medium", evidence_claims[0].text)
        self.assertIn("Status: not_confirmed", evidence_claims[1].text)
        timeline_claim = next(
            claim
            for claim in report.claims
            if claim.section_id == "evidence_to_examine"
        )
        self.assertEqual(timeline_claim.support_type, "extraction_candidate")
        self.assertIn("Status: unknown", timeline_claim.text)
        self.assertTrue(
            all(not claim.mitre_technique_ids for claim in report.claims)
        )
        self.assertNotIn(
            "mitre_mapping_candidate",
            {claim.support_type for claim in report.claims},
        )
        entity_section = next(
            section
            for section in report.sections
            if section.section_id == "evidence_to_examine"
        )
        self.assertTrue(
            any(
                "Persisted status: not available | Confidence: high" in item
                for item in entity_section.items
            )
        )
        self.assertTrue(
            any(
                "Status: contradicted | Confidence: low" in item
                for item in entity_section.items
            )
        )
        mitre_section = next(
            section
            for section in report.sections
            if section.section_id == "mitre_attack_mapping"
        )
        self.assertIn("Source: vector", mitre_section.items[0])
        self.assertIn("Relevance: cited_in_answer", mitre_section.items[0])
        self.assertIn("Score: 0.9", mitre_section.items[0])
        self.assertIn("no evidence or timeline pairing", mitre_section.paragraphs[0])
        rationale_section = next(
            section
            for section in report.sections
            if section.section_id == "mapping_rationale"
        )
        self.assertIn("Retrieval source: vector", rationale_section.items[0])
        self.assertIn("Evidence link: none persisted", rationale_section.items[0])
        self.assertIn("no evidence-linked rationale", rationale_section.items[0])
        self.assertNotIn("E-001", "\n".join(rationale_section.items))

    def test_template_has_explicit_empty_states(self) -> None:
        snapshot = build_current_report_snapshot(_report_thread())
        snapshot.extraction = CaseState()
        snapshot.mitre_rows = []

        report = build_template_report(snapshot)
        sections = {section.section_id: section for section in report.sections}

        self.assertEqual(report.claims, [])
        self.assertIn(
            "No evidence or indicator candidates",
            sections["indicators_found"].items[0],
        )
        self.assertTrue(
            any(
                "No entities" in item
                for item in sections["evidence_to_examine"].items
            )
        )
        self.assertTrue(
            any(
                "No relationships" in item
                for item in sections["evidence_to_examine"].items
            )
        )
        self.assertIn(
            "No timeline events", sections["evidence_to_examine"].items[0]
        )
        self.assertIn("No MITRE ATT&CK", sections["mitre_attack_mapping"].items[0])
        self.assertIn("No mapping rationale", sections["mapping_rationale"].items[0])
        self.assertTrue(
            any(
                "No extraction warnings" in item
                for item in sections["system_limitations"].items
            )
        )

    def test_template_truncation_is_stable_and_disclosed(self) -> None:
        snapshot = build_current_report_snapshot(_report_thread())
        source_id = snapshot.source_messages[0].message_id
        snapshot.extraction.timeline = [
            ExtractedTimelineEvent(
                event_id=f"T-{index:03d}",
                timestamp=None,
                timestamp_text=f"Reported time {index}",
                event=f"Reported event {index}",
                actors=[],
                evidence_ids=[],
                status="unknown",
                confidence="low",
                source_message_ids=[source_id],
            )
            for index in range(1, 41)
        ]

        report = build_template_report(snapshot)
        timeline_section = next(
            section
            for section in report.sections
            if section.section_id == "evidence_to_examine"
        )

        self.assertEqual(len(timeline_section.items), 32)
        self.assertTrue(timeline_section.items[0].startswith("T-001"))
        self.assertTrue(timeline_section.items[29].startswith("T-030"))
        self.assertIn("No entities", timeline_section.items[30])
        self.assertIn("No relationships", timeline_section.items[31])
        self.assertEqual(
            len(
                [
                    claim
                    for claim in report.claims
                    if claim.section_id == "evidence_to_examine"
                ]
            ),
            30,
        )
        self.assertIn(
            "Timeline events omitted 10 item(s)",
            "\n".join(report.limitations),
        )

    def test_legacy_report_contract_still_validates(self) -> None:
        legacy = StructuredReport(
            report_version="baseline_report_v1",
            status="provisional_unverified",
            title="Legacy report",
            sections=[
                ReportSection(
                    section_id=section_id,
                    heading=REPORT_SECTION_HEADINGS[section_id],
                    paragraphs=["Legacy persisted content."],
                    items=[],
                )
                for section_id in REPORT_SECTION_IDS
            ],
            claims=[],
            limitations=[],
        )

        validated = validate_structured_report(
            legacy,
            incident_ids=set(),
            mitre_ids=set(),
        )

        self.assertEqual(validated.report_version, "baseline_report_v1")
        self.assertEqual(
            tuple(section.section_id for section in validated.sections),
            REPORT_SECTION_IDS,
        )

    async def test_template_fails_closed_on_prompt_or_unsupported_id_text(self) -> None:
        snapshot = build_current_report_snapshot(_report_thread())
        snapshot.extraction.evidence[0].description = "Unexpected E-404 reference."

        unsupported = await run_report_generation(snapshot)
        snapshot.extraction.evidence[0].description = (
            "Prompt version: chat_report_prompt_v2."
        )
        prompt_leak = await run_report_generation(snapshot)

        self.assertEqual(unsupported.failure_code, "report_validation_failed")
        self.assertEqual(prompt_leak.failure_code, "report_validation_failed")

    async def test_report_service_persists_history_and_replays_same_idempotency_key(
        self,
    ) -> None:
        thread = _report_thread()
        db = FakeReportDb(thread)
        service = ChatReportService(db)
        request = ChatReportCreate(idempotency_key="request-1")

        first = await service.generate_report(thread.id, request)
        second = await service.generate_report(thread.id, request)

        self.assertEqual(first.report_id, second.report_id)
        self.assertEqual(first.version_number, 1)
        self.assertEqual(second.version_number, 1)
        self.assertEqual(first.provider, REPORT_TEMPLATE_PROVIDER)
        self.assertEqual(first.model, REPORT_TEMPLATE_MODEL)
        self.assertEqual(first.prompt_version, REPORT_TEMPLATE_PROMPT_VERSION)
        self.assertEqual(first.decoding_settings, {})
        self.assertIsNone(first.input_tokens)
        self.assertIsNone(first.output_tokens)
        self.assertEqual(len(db.reports), 1)

    async def test_validated_report_can_be_exported_as_pdf(self) -> None:
        thread = _report_thread()
        db = FakeReportDb(thread)
        service = ChatReportService(db)
        report = await service.generate_report(
            thread.id,
            ChatReportCreate(idempotency_key="pdf-request"),
        )

        content, filename = await service.get_report_pdf(thread.id, report.report_id)

        self.assertTrue(content.startswith(b"%PDF-"))
        self.assertEqual(filename, f"cybercase-report-v1-{report.report_id}.pdf")

    async def test_pdf_export_rejects_tampered_structured_report(self) -> None:
        thread = _report_thread()
        db = FakeReportDb(thread)
        service = ChatReportService(db)
        report = await service.generate_report(
            thread.id,
            ChatReportCreate(idempotency_key="tampered-pdf-request"),
        )
        assert db.reports[0].structured_report is not None
        db.reports[0].structured_report["claims"][0]["evidence_ids"] = ["E-404"]

        with self.assertRaises(ReportGenerationConflict) as context:
            await service.get_report_pdf(thread.id, report.report_id)

        self.assertEqual(context.exception.code, "report_pdf_requires_validated_report")

    def test_stale_or_failed_extraction_is_rejected(self) -> None:
        thread = _report_thread()
        terminal = thread.messages[-1]
        assert isinstance(terminal.metadata_json, dict)
        extraction = terminal.metadata_json["chat_extraction"]
        assert isinstance(extraction, dict)
        extraction["validation_status"] = "failed"

        with self.assertRaises(ReportGenerationConflict) as context:
            build_current_report_snapshot(thread)

        self.assertEqual(context.exception.code, "report_extraction_not_validated")


def _report_thread() -> ChatThread:
    thread_id = uuid4()
    root = ChatMessage(
        id=uuid4(),
        thread_id=thread_id,
        ordinal=1,
        role="user",
        content="A reported PowerShell event occurred on host-7.",
        metadata_json={},
    )
    terminal = ChatMessage(
        id=uuid4(),
        thread_id=thread_id,
        ordinal=2,
        role="assistant",
        content="Terminal assistant prose must not enter the report.",
        retrieval_context_id="context-1",
        metadata_json={
            "mitre_table": [
                {
                    "technique_id": "T1059.001",
                    "name": "PowerShell",
                    "entity_type": "technique",
                    "tactic": "Execution",
                    "score": 0.9,
                    "source": "vector",
                    "relevance": "cited_in_answer",
                    "description": "PowerShell execution mapping.",
                    "mitre_url": "https://attack.mitre.org/techniques/T1059/001/",
                },
                {"technique_id": "not-a-mitre-id", "name": "Ignore me"},
            ],
            "chat_extraction": {
                "version": "baseline_extraction_v2",
                "mode": "single_pass_llm",
                "status": "candidate",
                "entities": [],
                "evidence": [
                    {
                        "evidence_id": "E-001",
                        "title": "PowerShell event",
                        "description": "A PowerShell event was reported.",
                        "artifact_type": "command_line",
                        "status": "reported",
                        "confidence": "medium",
                        "source_type": "user_reported",
                        "source_message_ids": [str(root.id)],
                    }
                ],
                "timeline": [
                    {
                        "event_id": "T-001",
                        "timestamp": None,
                        "timestamp_text": "Time unknown",
                        "event": "The event was reported.",
                        "actors": [],
                        "evidence_ids": ["E-001"],
                        "status": "unknown",
                        "confidence": "unknown",
                        "source_message_ids": [str(root.id)],
                    }
                ],
                "warnings": [],
                "prompt_version": BASELINE_EXTRACTION_PROMPT_VERSION,
                "provider": "anthropic",
                "model": "claude-haiku-4-5-20251001",
                "validation_status": "validated",
                "source_message_ids": [str(root.id)],
                "raw_response": None,
            },
        },
    )
    thread = ChatThread(
        id=thread_id,
        title="PowerShell investigation",
        status="idle",
        next_message_ordinal=3,
    )
    thread.messages = [root, terminal]
    return thread

if __name__ == "__main__":
    unittest.main()
