"""Unit tests for CyberCase Jinja2 Report HTML rendering (Thai & English)."""

from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.schemas.reports import (
    ChatReportRead,
    ReportSection,
    StructuredReport,
)
from app.services.reports.report_html import (
    get_report_css,
    render_chat_report_html,
    render_chat_report_html_from_view_model,
)
from app.services.reports.report_view_model import (
    I18N_STRINGS,
    ReportViewModel,
    TimelineViewRow,
    EvidenceViewRow,
    IndicatorViewRow,
    RelationshipViewRow,
    MitreMappingViewRow,
    UnresolvedIssueViewRow,
    VerificationActionViewRow,
    ProvenanceViewRow,
    build_report_view_model,
)


def _sample_view_model(language: str = "th", has_indicators: bool = True) -> ReportViewModel:
    indicators = (
        [
            IndicatorViewRow(
                indicator_type="IP Address",
                value="203.0.113.50",
                note="C2 Connection Observed",
            ),
            IndicatorViewRow(
                indicator_type="SHA-256 Hash",
                value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                note="Agent Payload Hash",
            ),
        ]
        if has_indicators
        else []
    )

    lang = language if language in ("th", "en") else "th"
    i18n = I18N_STRINGS[lang]

    return ReportViewModel(
        report_id="rpt-12345-test",
        case_title="เหตุการณ์ตรวจพบการเข้าถึงโดยไม่ได้รับอนุญาต" if lang == "th" else "Unauthorized Access Incident",
        generated_date="2026-08-22 10:30 UTC",
        report_status=i18n["status_provisional"],
        version_label="Version 1",
        language=lang,
        i18n=i18n,
        summary_paragraphs=[
            "เมื่อวันที่ 2026-08-21 มีการรายงานว่าพบการเชื่อมต่อไปยังเครื่องแม่ข่ายไฟล์โดยไม่ได้รับอนุญาต",
            "จากข้อมูลที่ได้รับ ตรวจพบการเรียกใช้งานสคริปต์ PowerShell ผิดปกติ",
        ] if lang == "th" else [
            "On 2026-08-21, unauthorized access to the internal file server was reported.",
            "Based on available telemetry, anomalous PowerShell execution was detected.",
        ],
        timeline_rows=[
            TimelineViewRow(
                order=1,
                time_display="2026-08-21 08:30",
                event="ตรวจพบการล็อกอินเข้าสู่ระบบผ่าน RDP" if lang == "th" else "RDP login detected",
                source_evidence="Security Event Log (E-001)",
                actors="admin_user",
                status="reported",
            ),
            TimelineViewRow(
                order=2,
                time_display="ต่อมา" if lang == "th" else "Subsequently",
                event="มีการดาวน์โหลดไฟล์สคริปต์จากภายนอก" if lang == "th" else "Script downloaded from external source",
                source_evidence="Firewall Log (E-002)",
                actors="คนร้าย" if lang == "th" else "Threat Actor",
                status="reported",
            ),
        ],
        evidence_rows=[
            EvidenceViewRow(
                item_id="E-001",
                title="Security Event Log",
                artifact_type="Event Log",
                description="Windows Event 4624 Successful Logon",
                source_type="เซิร์ฟเวอร์" if lang == "th" else "Server",
                confidence="high",
            ),
        ],
        has_indicators=has_indicators,
        indicator_rows=indicators,
        has_relationships=True,
        relationship_rows=[
            RelationshipViewRow(
                statement="คนร้าย เข้าถึง ระบบแม่ข่ายไฟล์ โดยไม่ได้รับอนุญาต" if lang == "th" else "Threat Actor accessed File Server without authorization",
                subject_name="คนร้าย" if lang == "th" else "Threat Actor",
                predicate="accessed_without_authorization",
                object_name="ระบบแม่ข่ายไฟล์" if lang == "th" else "File Server",
                status="reported",
                confidence="high",
            ),
        ],
        relationship_graph_image=None,
        has_mitre_mappings=True,
        mitre_rows=[
            MitreMappingViewRow(
                finding="Execution: PowerShell",
                case_evidence_support="ตรวจพบการสั่งทำงานคำสั่ง PowerShell ที่ถูกเข้ารหัส" if lang == "th" else "Encoded PowerShell command observed",
                technique_id="T1059.001",
                technique_name="PowerShell",
                status_display=i18n["status_reported_analysis"],
                tactic="Execution",
                source="vector",
                relevance="cited_in_answer",
            ),
        ],
        unresolved_issues=[
            UnresolvedIssueViewRow(
                description="ยังไม่สามารถระบุแหล่งที่มาภายนอกของคำสั่งดาวน์โหลดได้" if lang == "th" else "External download source remains unverified",
                category="ข้อมูลที่ขาดหาย" if lang == "th" else "Missing Information",
                reason="ยังไม่ได้รับข้อมูล Network Flow เพิ่มเติม" if lang == "th" else "Additional NetFlow logs not yet available",
            ),
        ],
        verification_actions=[
            VerificationActionViewRow(
                order=1,
                action="ตรวจพิสูจน์พยานหลักฐานต้นฉบับเพื่อยืนยันเหตุการณ์" if lang == "th" else "Examine raw forensic artifacts to verify incident timeline",
            ),
        ],
        limitations=[
            "รายงานนี้เป็นรายงานเบื้องต้นสำหรับการวิเคราะห์เหตุการณ์" if lang == "th" else "This report represents preliminary investigative orientation",
        ],
        provenance_rows=[
            ProvenanceViewRow(label="Report ID", value="rpt-12345-test"),
            ProvenanceViewRow(label="Version", value="v1"),
        ],
    )


def test_render_chat_report_html_thai() -> None:
    vm = _sample_view_model(language="th", has_indicators=True)
    html = render_chat_report_html_from_view_model(vm)

    assert '<html lang="th">' in html
    assert "5.1 สรุปเหตุการณ์" in html
    assert "5.2 ลำดับเหตุการณ์" in html
    assert "5.3 หลักฐานและตัวบ่งชี้สำคัญ" in html
    assert "5.4 ความสัมพันธ์ของเหตุการณ์และองค์ประกอบในคดี" in html
    assert "5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping" in html
    assert "5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม" in html
    assert "5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ" in html

    assert "เหตุการณ์ตรวจพบการเข้าถึงโดยไม่ได้รับอนุญาต" in html
    assert "T1059.001" in html
    assert "PowerShell" in html
    assert "ต่อมา" in html
    assert "203.0.113.50" in html


def test_render_chat_report_html_english() -> None:
    vm = _sample_view_model(language="en", has_indicators=True)
    html = render_chat_report_html_from_view_model(vm)

    assert '<html lang="en">' in html
    assert "5.1 Incident Summary" in html
    assert "5.2 Chronological Timeline" in html
    assert "5.3 Evidence & Key Indicators" in html
    assert "5.4 Case Elements & Relationships" in html
    assert "5.5 Technical Analysis & MITRE ATT&CK Mapping" in html
    assert "5.6 Unestablished Issues & Recommended Next Steps" in html
    assert "5.7 System Limitations & Provenance" in html

    assert "Unauthorized Access Incident" in html
    assert "T1059.001" in html
    assert "Subsequently" in html
    assert "Threat Actor accessed File Server without authorization" in html


def test_render_chat_report_html_omits_ioc_table_when_empty() -> None:
    vm = _sample_view_model(language="th", has_indicators=False)
    html = render_chat_report_html_from_view_model(vm)

    assert "5.3 หลักฐานและตัวบ่งชี้สำคัญ" in html
    assert "ทะเบียนหลักฐาน (Evidence Register)" in html
    assert "ตัวบ่งชี้ความเสี่ยงทางไซเบอร์" not in html


def test_render_chat_report_html_is_deterministic() -> None:
    vm = _sample_view_model(language="en", has_indicators=True)
    html1 = render_chat_report_html_from_view_model(vm)
    html2 = render_chat_report_html_from_view_model(vm)

    assert html1 == html2
