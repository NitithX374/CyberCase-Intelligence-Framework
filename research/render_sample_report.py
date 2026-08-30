"""Render sample CyberCase incident reports in both Thai and English (HTML & PDF)."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.schemas.reports import (
    ChatReportRead,
    PRELIMINARY_REPORT_SECTION_HEADINGS,
    ReportClaim,
    ReportSection,
    StructuredReport,
)
from app.services.reports.report_html import render_chat_report_html
from app.services.reports.report_pdf import render_chat_report_pdf

OUTPUT_DIR = Path(__file__).resolve().parent / "sample_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_sample_report() -> ChatReportRead:
    now = datetime(2026, 8, 22, 11, 0, tzinfo=timezone.utc)
    headings = PRELIMINARY_REPORT_SECTION_HEADINGS

    evidence_items = [
        "E-001 | Title: Firewall & Web Access Log | Description: พบการส่งคำสั่ง SQL Injection ผ่านพารามิเตอร์ login.php และมีการเชื่อมต่อไปยัง 203.0.113.195 | Artifact type: Web Server Log | Status: reported | Confidence: high | Source type: user_reported.",
        "E-002 | Title: Web Shell Script (c2_handler.php) | Description: พบไฟล์สคริปต์ควบคุมระยะไกล hash SHA-256 8f4e2b1a9c3d5e7f0a2b4c6d8e0f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f ถูกวางในโฟลเดอร์ /uploads/ | Artifact type: File | Status: reported | Confidence: high | Source type: user_reported.",
        "E-003 | Title: Endpoint Security Alert (SRV-DB01) | Description: พบการพยายามยกระดับสิทธิ์ผ่านการแก้ไข Registry HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options | Artifact type: Windows Registry | Status: reported | Confidence: medium | Source type: user_reported.",
    ]

    mitre_items = [
        "T1190 | Name: Exploit Public-Facing Application | Mapping status: candidate | Source: vector | Relevance: cited_in_answer | Score: 0.92 | Tactic: Initial Access | Entity type: technique | Description: มีการส่งคำสั่ง SQL Injection เพื่อเจาะระบบเว็บเซิร์ฟเวอร์.",
        "T1505.003 | Name: Server Software Component: Web Shell | Mapping status: candidate | Source: vector | Relevance: cited_in_answer | Score: 0.89 | Tactic: Persistence | Entity type: technique | Description: มีการวางไฟล์ c2_handler.php เพื่อควบคุมระบบจากระยะไกล.",
        "T1546.012 | Name: Event Triggered Execution: Image File Execution Options Injection | Mapping status: candidate | Source: graph | Relevance: cited_in_answer | Score: 0.84 | Tactic: Privilege Escalation | Entity type: technique | Description: มีการแก้ไข IFEO Registry key เพื่อดักจับการทำงานของโปรแกรม.",
    ]

    examine_items = [
        "T-001 | Time: 2026-08-21 02:14 | Event: คนร้ายส่งคำสั่ง SQL Injection ผ่านเว็บแอปพลิเคชัน | Actors: คนร้าย | Linked evidence: E-001 | Status: reported | Confidence: high.",
        "T-002 | Time: 2026-08-21 02:18 | Event: คนร้ายวางไฟล์เว็บเชลล์ c2_handler.php บนเว็บเซิร์ฟเวอร์ | Actors: คนร้าย | Linked evidence: E-002 | Status: reported | Confidence: high.",
        "T-003 | Time: ต่อมา | Event: คนร้ายเข้าถึงระบบฐานข้อมูลภายใน SRV-DB01 และพยายามยกระดับสิทธิ์ | Actors: คนร้าย, SRV-DB01 | Linked evidence: E-003 | Status: reported | Confidence: medium.",
        "Entity | Name: คนร้าย | Type: threat-actor | Reported role: ผู้บุกรุกไม่ระบุตัวตน | Persisted status: unconfirmed | Confidence: medium.",
        "Entity | Name: Web-FileServer-01 | Type: system | Reported role: เว็บเซิร์ฟเวอร์เป้าหมายด่านหน้า | Persisted status: confirmed | Confidence: high.",
        "Entity | Name: SRV-DB01 | Type: system | Reported role: เซิร์ฟเวอร์ฐานข้อมูลภายใน | Persisted status: confirmed | Confidence: high.",
        "Relationship | คนร้าย -> accessed_without_authorization -> Web-FileServer-01 | Statement: คนร้ายเข้าถึง Web-FileServer-01 โดยไม่ได้รับอนุญาต | Status: reported | Confidence: high.",
        "Relationship | คนร้าย -> placed -> Web Shell (c2_handler.php) | Statement: คนร้ายวางไฟล์ Web Shell (c2_handler.php) บนเซิร์ฟเวอร์ | Status: reported | Confidence: high.",
        "Relationship | คนร้าย -> targeted -> SRV-DB01 | Statement: คนร้ายพุ่งเป้าไปที่เซิร์ฟเวอร์ฐานข้อมูล SRV-DB01 | Status: reported | Confidence: medium.",
    ]

    sections = [
        ReportSection(
            section_id="case_summary",
            heading=headings["case_summary"],
            paragraphs=[
                "เมื่อวันที่ 2026-08-21 ได้รับรายงานเหตุการณ์ตรวจพบพฤติการณ์น่าสงสัยบนระบบ Web-FileServer-01 ขององค์กร",
                "จากการตรวจสอบบันทึกการเข้าถึง (Web Access Log) พบการส่งคำสั่ง SQL Injection ผ่านช่องทางรับข้อมูลบนเว็บไซต์",
                "ต่อมาผู้โจมตีได้ทำการอัปโหลดไฟล์เว็บเชลล์ c2_handler.php และพยายามเชื่อมต่อไปยังเซิร์ฟเวอร์ฐานข้อมูลภายใน SRV-DB01",
                "ในช่วงท้ายตรวจพบการพยายามแก้ไขค่า Registry เพื่อยกระดับสิทธิ์และคงการเข้าถึงในระบบ",
            ],
            items=["Message 1 (user_case_statement): ผู้ดูแลระบบแจ้งพบพฤติการณ์บุกรุกและไฟล์ผิดปกติบนเซิร์ฟเวอร์"],
        ),
        ReportSection(
            section_id="indicators_found",
            heading=headings["indicators_found"],
            paragraphs=[],
            items=evidence_items,
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading=headings["mitre_attack_mapping"],
            paragraphs=[],
            items=mitre_items,
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
            items=examine_items,
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading=headings["preliminary_recommendations"],
            paragraphs=[],
            items=[
                "ตัดการเชื่อมต่อเครือข่ายของเซิร์ฟเวอร์ Web-FileServer-01 และ SRV-DB01 เพื่อควบคุมขอบเขตความเสียหาย",
                "เก็บสำเนาพยานหลักฐานดิจิทัล (Memory Dump, Disk Image, Log Files) เพื่อตรวจพิสูจน์ตามหลักนิติวิทยาศาสตร์",
                "ตรวจสอบการสร้างบัญชีผู้ใช้ใหม่หรือสิทธิ์ที่ถูกเปลี่ยนแปลงบน Active Directory / Domain Controller",
                "ทำการปิดกั้นการสื่อสารกับ IP Address 203.0.113.195 ที่ระดับ Firewall",
            ],
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
        title="รายงานการวิเคราะห์เหตุการณ์: ตรวจพบการบุกรุกและติดตั้ง Web Shell บนเซิร์ฟเวอร์",
        sections=sections,
        claims=[],
        limitations=[
            "รายงานนี้เป็นรายงานสรุปผลการวิเคราะห์เบื้องต้น (Provisional / Unverified Report)",
            "ข้อมูลบางส่วนมาจากคำให้การของผู้ดูแลระบบและบันทึกข้อความเบื้องต้น",
            "Extraction warning: ยังไม่พบข้อมูล Traffic ขาออกทั้งหมดเพื่อยืนยันว่ามีการรั่วไหลของข้อมูล (Data Exfiltration) หรือไม่",
        ],
    )

    return ChatReportRead(
        report_id=uuid4(),
        thread_id=uuid4(),
        version_number=1,
        idempotency_key="sample-demo-report",
        source_snapshot_hash="9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b",
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
        latency_ms=12.5,
        input_tokens=150,
        output_tokens=300,
    )


def main() -> None:
    report_read = build_sample_report()

    # 1. Thai Version (HTML & PDF)
    html_th = render_chat_report_html(report_read, thread_title="Web Server Breach Incident", language="th")
    html_th_path = OUTPUT_DIR / "cybercase_incident_report_th.html"
    html_th_path.write_text(html_th, encoding="utf-8")
    print(f"[OK] Rendered Thai HTML to: {html_th_path}")

    pdf_th = render_chat_report_pdf(report_read, thread_title="Web Server Breach Incident", language="th")
    pdf_th_path = OUTPUT_DIR / "cybercase_incident_report_th.pdf"
    pdf_th_path.write_bytes(pdf_th)
    print(f"[OK] Rendered Thai PDF to: {pdf_th_path}")

    # 2. English Version (HTML & PDF)
    html_en = render_chat_report_html(report_read, thread_title="Web Server Breach Incident", language="en")
    html_en_path = OUTPUT_DIR / "cybercase_incident_report_en.html"
    html_en_path.write_text(html_en, encoding="utf-8")
    print(f"[OK] Rendered English HTML to: {html_en_path}")

    pdf_en = render_chat_report_pdf(report_read, thread_title="Web Server Breach Incident", language="en")
    pdf_en_path = OUTPUT_DIR / "cybercase_incident_report_en.pdf"
    pdf_en_path.write_bytes(pdf_en)
    print(f"[OK] Rendered English PDF to: {pdf_en_path}")


if __name__ == "__main__":
    main()
