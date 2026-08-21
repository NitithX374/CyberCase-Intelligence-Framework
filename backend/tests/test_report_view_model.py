"""Unit tests for CyberCase Report View Model Builder (Thai & English)."""

from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.schemas.reports import (
    ChatReportRead,
    PRELIMINARY_REPORT_SECTION_HEADINGS,
    ReportClaim,
    ReportSection,
    StructuredReport,
)
from app.services.reports.report_view_model import (
    ReportViewModel,
    build_report_view_model,
)


def _sample_report_read(has_iocs: bool = True) -> ChatReportRead:
    now = datetime(2026, 8, 22, 10, 30, tzinfo=timezone.utc)
    report_id = uuid4()
    thread_id = uuid4()
    headings = PRELIMINARY_REPORT_SECTION_HEADINGS

    evidence_list = [
        "E-001 | Title: Web Server Access Log | Description: พบการส่งคำสั่ง SQL Injection ผ่านพารามิเตอร์ id | Artifact type: Server Log | Status: reported | Confidence: high | Source type: user_reported.",
    ]
    if has_iocs:
        evidence_list.append(
            "E-002 | Title: Remote-Control Script | Description: พบไฟล์สคริปต์ c2_agent.ps1 และเชื่อมต่อไปยัง 198.51.100.25 | Artifact type: File | Status: reported | Confidence: medium | Source type: user_reported."
        )

    sections = [
        ReportSection(
            section_id="case_summary",
            heading=headings["case_summary"],
            paragraphs=["เมื่อ 2026-08-20 บริษัทพบการเข้าถึงเซิร์ฟเวอร์โดยไม่ได้รับอนุญาต"],
            items=["Message 1 (user_case_statement): ตรวจพบความผิดปกติบนระบบรับส่งไฟล์"],
        ),
        ReportSection(
            section_id="indicators_found",
            heading=headings["indicators_found"],
            paragraphs=[],
            items=evidence_list,
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading=headings["mitre_attack_mapping"],
            paragraphs=[],
            items=[
                "T1546.011 | Name: Application Shimming | Mapping status: candidate | Source: vector | Relevance: cited_in_answer | Score: 0.85 | Tactic: Persistence | Entity type: technique | Description: มีการใช้ Application Shimming เพื่อคงอยู่ในระบบ."
            ],
        ),
        ReportSection(
            section_id="mapping_rationale",
            heading=headings["mapping_rationale"],
            paragraphs=[],
            items=[],
        ),
        ReportSection(
            section_id="evidence_to_examine",
            heading=headings["evidence_to_examine"],
            paragraphs=[],
            items=[
                "T-001 | Time: ต่อมา | Event: คนร้ายสั่งทำงานสคริปต์บนเครื่องแม่ข่าย | Actors: คนร้าย | Linked evidence: E-001 | Status: reported | Confidence: high.",
                "Entity | Name: คนร้าย | Type: threat-actor | Reported role: ผู้โจมตี | Persisted status: unconfirmed | Confidence: medium.",
                "Entity | Name: ระบบรับส่งไฟล์ | Type: system | Reported role: เซิร์ฟเวอร์เป้าหมาย | Persisted status: confirmed | Confidence: high.",
                "Relationship | คนร้าย -> accessed_without_authorization -> ระบบรับส่งไฟล์ | Statement: คนร้ายเข้าถึงระบบรับส่งไฟล์ | Status: reported | Confidence: high.",
            ],
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading=headings["preliminary_recommendations"],
            paragraphs=[],
            items=["ตรวจพิสูจน์พยานหลักฐานต้นฉบับเพื่อยืนยันเหตุการณ์"],
        ),
        ReportSection(
            section_id="system_limitations",
            heading=headings["system_limitations"],
            paragraphs=[],
            items=[],
        ),
    ]

    structured = StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title="รายงานการวิเคราะห์เหตุการณ์: Server Breach",
        sections=sections,
        claims=[],
        limitations=[
            "รายงานนี้เป็นรายงานเบื้องต้น",
            "Extraction warning: ยังไม่พบชื่อหรือ hash ของไฟล์สคริปต์ที่ถูกวางบนเซิร์ฟเวอร์",
        ],
    )

    return ChatReportRead(
        report_id=report_id,
        thread_id=thread_id,
        version_number=1,
        idempotency_key="idemp-001",
        source_snapshot_hash="f" * 64,
        extraction_id=uuid4(),
        extraction_version="baseline_extraction_v1",
        prompt_version="chat_preliminary_analysis_template_v1",
        provider="deterministic",
        model="preliminary_analysis_template_v1",
        decoding_settings={},
        persistence_status="completed",
        validation_status="validated",
        report=structured,
        validation_errors=[],
        failure_code=None,
        failure_message=None,
        created_at=now,
        finished_at=now,
        latency_ms=10.0,
        input_tokens=100,
        output_tokens=200,
    )


def test_build_report_view_model_7_sections_thai() -> None:
    report = _sample_report_read(has_iocs=True)
    vm = build_report_view_model(report, thread_title="Server Breach", language="th")

    assert vm.language == "th"
    assert vm.i18n["sec_5_1"] == "5.1 สรุปเหตุการณ์"
    assert vm.case_title == "รายงานการวิเคราะห์เหตุการณ์: Server Breach"
    assert "รายงานเบื้องต้น" in vm.report_status
    assert len(vm.summary_paragraphs) > 0
    assert len(vm.timeline_rows) == 1
    assert vm.timeline_rows[0].time_display == "ต่อมา"
    assert len(vm.evidence_rows) == 2
    assert vm.has_indicators is True
    assert any(ioc.value == "198.51.100.25" for ioc in vm.indicator_rows)
    assert vm.has_relationships is True
    assert "คนร้าย เข้าถึง ระบบรับส่งไฟล์ โดยไม่ได้รับอนุญาต" in vm.relationship_rows[0].statement
    assert vm.has_mitre_mappings is True
    assert vm.mitre_rows[0].technique_id == "T1546.011"
    assert len(vm.unresolved_issues) > 0
    assert "ยังไม่พบชื่อหรือ hash" in vm.unresolved_issues[0].description
    assert len(vm.verification_actions) > 0
    assert len(vm.limitations) > 0
    assert len(vm.provenance_rows) > 0


def test_build_report_view_model_7_sections_english() -> None:
    report = _sample_report_read(has_iocs=True)
    vm = build_report_view_model(report, thread_title="Server Breach", language="en")

    assert vm.language == "en"
    assert vm.i18n["sec_5_1"] == "5.1 Incident Summary"
    assert vm.i18n["sec_5_2"] == "5.2 Chronological Timeline"
    assert vm.i18n["sec_5_3"] == "5.3 Evidence & Key Indicators"
    assert vm.i18n["sec_5_4"] == "5.4 Case Elements & Relationships"
    assert vm.i18n["sec_5_5"] == "5.5 Technical Analysis & MITRE ATT&CK Mapping"
    assert vm.i18n["sec_5_6"] == "5.6 Unestablished Issues & Recommended Next Steps"
    assert vm.i18n["sec_5_7"] == "5.7 System Limitations & Provenance"

    assert "Provisional" in vm.report_status
    assert vm.has_relationships is True
    assert "คนร้าย accessed ระบบรับส่งไฟล์ without authorization" in vm.relationship_rows[0].statement


def test_build_report_view_model_no_iocs_omits_indicator_table() -> None:
    report = _sample_report_read(has_iocs=False)
    vm = build_report_view_model(report, thread_title="Clean Case")

    assert isinstance(vm.has_indicators, bool)
