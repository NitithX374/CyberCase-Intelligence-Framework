"""Unit tests for CyberCase formal PDF report rendering (Thai & English)."""

from datetime import datetime, timezone
from io import BytesIO
import re
from uuid import uuid4

from pypdf import PdfReader

from app.schemas.reports import (
    ChatReportRead,
    ReportClaim,
    ReportSection,
    StructuredReport,
)
from app.services.reports.report_pdf import render_chat_report_pdf


def _normalized_pdf_text(reader: PdfReader) -> str:
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    joined = " ".join(parts)
    return re.sub(r"\s+", " ", joined).strip()


def test_render_chat_report_pdf_contains_formal_metadata_and_sections_thai() -> None:
    report = _report_read()
    before = report.model_dump(mode="json")

    content = render_chat_report_pdf(
        report,
        thread_title="Suspicious PowerShell activity - เหตุการณ์น่าสงสัย",
        language="th",
    )

    assert content.startswith(b"%PDF-")
    reader = PdfReader(BytesIO(content))
    assert len(reader.pages) >= 1
    assert reader.metadata is not None
    assert reader.metadata.title == "Validated structured report"
    assert reader.metadata.author == "CyberCase Intelligence Framework"
    extracted = _normalized_pdf_text(reader)

    # Verify that all 7 formal Thai section headers are present
    for section_header in (
        "5.1 สรุปเหตุการณ์",
        "5.2 ลำดับเหตุการณ์",
        "5.3 หลักฐานและตัวบ่งชี้สำคัญ",
        "5.4 ความสัมพันธ์ของเหตุการณ์และองค์ประกอบในคดี",
        "5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping",
        "5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม",
        "5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ",
    ):
        assert section_header in extracted

    assert report.model_dump(mode="json") == before


def test_render_chat_report_pdf_contains_formal_metadata_and_sections_english() -> None:
    report = _report_read()
    before = report.model_dump(mode="json")

    content = render_chat_report_pdf(
        report,
        thread_title="Suspicious PowerShell activity Investigation",
        language="en",
    )

    assert content.startswith(b"%PDF-")
    reader = PdfReader(BytesIO(content))
    assert len(reader.pages) >= 1
    extracted = _normalized_pdf_text(reader)

    # Verify that all 7 formal English section headers are present
    for section_header in (
        "5.1 Incident Summary",
        "5.2 Chronological Timeline",
        "5.3 Evidence & Key Indicators",
        "5.4 Case Elements & Relationships",
        "5.5 Technical Analysis & MITRE ATT&CK Mapping",
        "5.6 Unestablished Issues & Recommended Next Steps",
        "5.7 System Limitations & Provenance",
    ):
        assert section_header in extracted

    assert report.model_dump(mode="json") == before


def test_render_deterministic_report_uses_lossless_tables_and_claim_queues() -> None:
    report, long_event = _deterministic_report_read()
    before = report.model_dump(mode="json")

    content = render_chat_report_pdf(
        report,
        thread_title="PowerShell: เหตุการณ์ | ตรวจสอบ",
        language="th",
    )

    assert content.startswith(b"%PDF-")
    reader = PdfReader(BytesIO(content))
    assert len(reader.pages) >= 2
    extracted = _normalized_pdf_text(reader)

    for semantic_text in (
        "5.1 สรุปเหตุการณ์",
        "5.2 ลำดับเหตุการณ์",
        "5.3 หลักฐานและตัวบ่งชี้สำคัญ",
        "5.4 ความสัมพันธ์ของเหตุการณ์และองค์ประกอบในคดี",
        "5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping",
        "T1059.001",
        "PowerShell",
        "LONG-EVENT-000",
        "LONG-EVENT-070",
        "LONG-EVENT-139",
        "TIMELINE-TAIL-UNIQUE",
    ):
        assert semantic_text in extracted

    assert 3_700 <= len(long_event) <= 3_800
    assert report.model_dump(mode="json") == before


def test_render_preliminary_report_uses_exact_numbered_headings_and_mixed_tables() -> None:
    report = _preliminary_deterministic_report_read()

    content = render_chat_report_pdf(
        report,
        thread_title="PowerShell preliminary analysis",
        language="th",
    )

    reader = PdfReader(BytesIO(content))
    extracted = _normalized_pdf_text(reader)
    for heading in (
        "5.1 สรุปเหตุการณ์",
        "5.2 ลำดับเหตุการณ์",
        "5.3 หลักฐานและตัวบ่งชี้สำคัญ",
        "5.4 ความสัมพันธ์ของเหตุการณ์และองค์ประกอบในคดี",
        "5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping",
        "5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม",
        "5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ",
    ):
        assert heading in extracted

    assert "T1059.001" in extracted
    assert "T-TH-1" in extracted


def _report_read() -> ChatReportRead:
    report_id = uuid4()
    thread_id = uuid4()
    sections = [
        ReportSection(
            section_id=section_id,
            heading=heading,
            paragraphs=[f"Content for {heading}."],
            items=(
                ["Legacy | item: remains a bullet."]
                if section_id == "case_background_scope"
                else []
            ),
        )
        for section_id, heading in (
            ("executive_summary", "Executive Summary"),
            ("case_background_scope", "Case Background and Scope"),
            ("evidence_findings", "Evidence Findings"),
            (
                "individuals_accounts_systems_roles",
                "Individuals, Accounts, Systems, and Reported Roles",
            ),
            ("chronological_timeline", "Chronological Timeline"),
            (
                "technical_analysis_mitre",
                "Technical Analysis and MITRE ATT&CK Mapping",
            ),
            (
                "conclusions_limitations_next_steps",
                "Conclusions, Limitations, and Recommended Next Investigative Steps",
            ),
        )
    ]
    structured = StructuredReport(
        report_version="baseline_report_v1",
        status="provisional_unverified",
        title="Validated structured report",
        sections=sections,
        claims=[
            ReportClaim(
                claim_id="claim-1",
                section_id="executive_summary",
                text="A user-reported event is retained as a candidate finding.",
                support_type="user_reported",
                evidence_ids=["E-1"],
            )
        ],
        limitations=["This report is not confirmed forensic evidence."],
    )
    now = datetime.now(timezone.utc)
    return ChatReportRead(
        report_id=report_id,
        thread_id=thread_id,
        version_number=4,
        idempotency_key="test-report",
        source_snapshot_hash="a" * 64,
        extraction_id=uuid4(),
        extraction_version="baseline_extraction_v1",
        prompt_version="chat_report_prompt_v1",
        provider="anthropic",
        model="claude-haiku-4-5-20251001",
        decoding_settings={"temperature": 0.0, "max_output_tokens": 8192},
        persistence_status="completed",
        validation_status="validated",
        report=structured,
        validation_errors=[],
        failure_code=None,
        failure_message=None,
        created_at=now,
        finished_at=now,
        latency_ms=100.0,
        input_tokens=100,
        output_tokens=200,
    )


def _deterministic_report_read() -> tuple[ChatReportRead, str]:
    evidence_item = (
        "E-TH-1 | Title: หลักฐาน: PowerShell | encoded | Description: "
        "คำอธิบาย: พบค่า | ที่ต้องตรวจสอบ | Artifact type: process:command | "
        "Status: reported | Confidence: medium | Source type: user_reported."
    )
    unmatched_evidence = (
        "E-UNMATCHED | Title: Unmatched item: stays | as bullet | Description: "
        "No exact claim exists | Artifact type: note | Status: candidate | "
        "Confidence: low | Source type: extraction."
    )
    ambiguous_evidence = (
        "E-FALLBACK | Title: ambiguous | Description: embedded | Description: "
        "original fallback | Artifact type: note | Status: candidate | "
        "Confidence: low | Source type: extraction."
    )
    event_tokens = [f"LONG-EVENT-{index:03d}:ค่า|ข้อมูล" for index in range(140)]
    long_event = " ".join(event_tokens)
    long_event = f"{long_event} {'x' * (3_740 - len(long_event))} TIMELINE-TAIL-UNIQUE"
    timeline_item = (
        f"T-TH-1 | Time: 2026-08-19T10:30:00+00:00 (10:30 | UTC) | Event: "
        f"{long_event} | Actors: analyst:หนึ่ง, host|alpha | Linked evidence: "
        "E-TH-1 | Status: reported | Confidence: medium."
    )
    unmatched_timeline = (
        "T-UNMATCHED | Time: not reported | Event: Unmatched event: stays | as "
        "bullet | Actors: none persisted | Linked evidence: none persisted | "
        "Status: candidate | Confidence: unknown."
    )
    sections_by_id = {
        "executive_summary": ReportSection(
            section_id="executive_summary",
            heading="Executive Summary",
            paragraphs=["Deterministic summary."],
            items=["Generation method: deterministic template; no language model narrative was used."],
        ),
        "case_background_scope": ReportSection(
            section_id="case_background_scope",
            heading="Case Background and Scope",
            paragraphs=["Ordered user-authored messages."],
            items=["Message 1 (user_reported): ผู้ใช้แจ้ง: พบ PowerShell | encoded command"],
        ),
        "evidence_findings": ReportSection(
            section_id="evidence_findings",
            heading="Evidence Findings",
            paragraphs=["Evidence remains unverified."],
            items=[evidence_item, evidence_item, unmatched_evidence, ambiguous_evidence],
        ),
        "individuals_accounts_systems_roles": ReportSection(
            section_id="individuals_accounts_systems_roles",
            heading="Individuals, Accounts, Systems, and Reported Roles",
            paragraphs=["Entities and relationships remain candidates."],
            items=[
                (
                    "Entity | Name: host:alpha | lab | Type: system | Reported role: "
                    "server: primary | suspected | Persisted status: not available | "
                    "Confidence: high."
                ),
                (
                    "Relationship | host:alpha | lab -> connected_to -> account | admin | "
                    "Statement: host:alpha | lab เชื่อมต่อ: account | admin | Status: "
                    "reported | Confidence: medium."
                ),
            ],
        ),
        "chronological_timeline": ReportSection(
            section_id="chronological_timeline",
            heading="Chronological Timeline",
            paragraphs=["Timeline values remain provisional."],
            items=[timeline_item, unmatched_timeline],
        ),
        "technical_analysis_mitre": ReportSection(
            section_id="technical_analysis_mitre",
            heading="Technical Analysis and MITRE ATT&CK Mapping",
            paragraphs=["Mapping candidates are not paired with evidence."],
            items=[
                (
                    "T1059.001 | Name: PowerShell: Command | Scripting | Mapping status: "
                    "candidate | Source: vector:search | Relevance: cited_in_answer | "
                    "Score: 0.9 | Tactic: execution:script | Entity type: attack-pattern | "
                    "Description: คำอธิบาย MITRE: candidate | ไม่ยืนยัน"
                )
            ],
        ),
        "conclusions_limitations_next_steps": ReportSection(
            section_id="conclusions_limitations_next_steps",
            heading="Conclusions, Limitations, and Recommended Next Investigative Steps",
            paragraphs=["No final conclusion is produced."],
            items=["Review every candidate against original artifacts."],
        ),
    }
    structured = StructuredReport(
        report_version="baseline_report_v1",
        status="provisional_unverified",
        title="รายงาน deterministic: PowerShell | ตรวจสอบ",
        sections=list(sections_by_id.values()),
        claims=[
            ReportClaim(
                claim_id="C-101",
                section_id="evidence_findings",
                text=evidence_item,
                support_type="user_reported",
                evidence_ids=["E-REF-A"],
            ),
            ReportClaim(
                claim_id="C-102",
                section_id="evidence_findings",
                text=evidence_item,
                support_type="extraction_candidate",
                evidence_ids=["E-REF-B"],
            ),
            ReportClaim(
                claim_id="C-201",
                section_id="chronological_timeline",
                text=timeline_item,
                support_type="user_reported",
                timeline_event_ids=["T-TH-1"],
            ),
        ],
        limitations=["Extraction warning: unverified timestamp."],
    )
    now = datetime(2026, 8, 19, 10, 30, tzinfo=timezone.utc)
    return (
        ChatReportRead(
            report_id=uuid4(),
            thread_id=uuid4(),
            version_number=1,
            idempotency_key="deterministic-test",
            source_snapshot_hash="b" * 64,
            extraction_id=uuid4(),
            extraction_version="baseline_extraction_v1",
            prompt_version="chat_report_template_v1",
            provider="deterministic",
            model="baseline_report_template_v1",
            decoding_settings={},
            persistence_status="completed",
            validation_status="validated",
            report=structured,
            validation_errors=[],
            failure_code=None,
            failure_message=None,
            created_at=now,
            finished_at=now,
            latency_ms=5.0,
            input_tokens=None,
            output_tokens=None,
        ),
        long_event,
    )


def _preliminary_deterministic_report_read() -> ChatReportRead:
    report, _ = _deterministic_report_read()
    assert report.report is not None
    sections_by_id = {s.section_id: s for s in report.report.sections}
    preliminary_sections = [
        ReportSection(
            section_id="case_summary",
            heading="5.1 สรุปคดี",
            paragraphs=sections_by_id["case_background_scope"].paragraphs,
            items=sections_by_id["case_background_scope"].items,
        ),
        ReportSection(
            section_id="indicators_found",
            heading="5.2 ตัวบ่งชี้ที่พบ",
            paragraphs=sections_by_id["evidence_findings"].paragraphs,
            items=sections_by_id["evidence_findings"].items,
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading="5.3 MITRE ATT&CK Mapping",
            paragraphs=sections_by_id["technical_analysis_mitre"].paragraphs,
            items=sections_by_id["technical_analysis_mitre"].items,
        ),
        ReportSection(
            section_id="mapping_rationale",
            heading="5.4 เหตุผลของการ mapping",
            paragraphs=["Rationale placeholder."],
            items=["T1059.001 | Retrieval source: vector:search | Relevance: cited_in_answer | Score: 0.9 | Evidence link: none persisted | Rationale status: retrieval metadata only; no evidence-linked rationale was persisted."],
        ),
        ReportSection(
            section_id="evidence_to_examine",
            heading="5.5 หลักฐานที่ควรตรวจสอบ",
            paragraphs=["Mixed examination candidates."],
            items=(
                sections_by_id["chronological_timeline"].items
                + sections_by_id["individuals_accounts_systems_roles"].items
            ),
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading="5.6 คำแนะนำเบื้องต้น",
            paragraphs=sections_by_id["conclusions_limitations_next_steps"].paragraphs,
            items=sections_by_id["conclusions_limitations_next_steps"].items,
        ),
        ReportSection(
            section_id="system_limitations",
            heading="5.7 ข้อจำกัดของระบบ",
            paragraphs=["System limitations placeholder."],
            items=["Extraction warning: preliminary boundary note."],
        ),
    ]
    structured = StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title="รายงานวิเคราะห์เบื้องต้น",
        sections=preliminary_sections,
        claims=report.report.claims,
        limitations=report.report.limitations,
    )
    return report.model_copy(
        update={
            "prompt_version": "chat_preliminary_analysis_template_v1",
            "model": "preliminary_analysis_template_v1",
            "report": structured,
        }
    )
