from datetime import datetime, timezone
from uuid import uuid4

from app.models.chat import ChatMessage, ChatThread
from app.models.rag_context import RagContext
from app.schemas.reports import ChatReportRead
from app.services.reports.report_html import render_chat_report_html
from app.services.reports.report_pdf import render_chat_report_pdf
from app.services.reports.report_snapshot import build_current_report_snapshot
from app.services.reports.report_template import build_template_report
from app.services.reports.report_view_model import build_report_view_model


def make_realistic_report_read() -> tuple[ChatReportRead, str]:
    thread_id = uuid4()
    source_id = uuid4()
    analysis_msg_id = uuid4()
    retrieval_id = "retrieval-ctx-123"

    thread = ChatThread(id=thread_id, title="คดีแฮกเกอร์โจมตี IIS Web Server", status="answered")
    thread.messages = [
        ChatMessage(
            id=source_id,
            thread_id=thread_id,
            ordinal=1,
            role="user",
            content="พบการบุกรุกเข้าสู่เซิร์ฟเวอร์ WEB-01 ผ่านช่องโหว่ IIS และคนร้ายใช้เทคนิค Application Shimming เพื่อฝังตัวถาวร IP คนร้าย: 198.51.100.23 ไฟล์ต้องสงสัย: sdbinst.exe",
            metadata_json={"evidence_kind": "initial_case_narrative"},
        ),
        ChatMessage(
            id=analysis_msg_id,
            thread_id=thread_id,
            ordinal=2,
            role="assistant",
            content="""### 1. Overall Case Picture (ภาพรวมคดี)
จากการตรวจสอบข้อมูลสำนวนคดี พบว่าคนร้ายได้ทำการโจมตีเจาะระบบเซิร์ฟเวอร์ WEB-01 ผ่านช่องโหว่บน IIS Web Application โดยมีพฤติกรรมฝังตัวผ่าน Application Shimming

### 2. Key Sequence and Relationships (ลำดับเหตุการณ์และความสัมพันธ์สำคัญ)
- คนร้ายเจาะเข้าสู่ระบบ WEB-01 ผ่านช่องโหว่ IIS Web Server
- คนร้ายติดตั้ง Application Shim ฐานข้อมูล SDB เพื่อคงสิทธิ์การเข้าถึง (Persistence)
- ตรวจพบการสื่อสารออกไปยัง IP ปลายทาง 198.51.100.23

### 3. Relevant MITRE ATT&CK Context
พบเทคนิค T1546.011 (Application Shimming) สอดคล้องกับการคงสิทธิ์""",
            retrieval_context_id=retrieval_id,
            metadata_json={
                "analysis_kind": "grounded_main_analysis",
                "analysis_trace": {
                    "version": "analysis_trace_v2",
                    "claims": [
                        {"claim_id": "c1", "text": "คนร้ายเจาะเข้าสู่ระบบ WEB-01 ผ่านช่องโหว่ IIS Web Server", "claim_type": "event_progression", "epistemic_status": "reported", "source_message_ids": [str(source_id)]},
                        {"claim_id": "c2", "text": "คนร้ายติดตั้ง Application Shim เพื่อคงสิทธิ์", "claim_type": "event_progression", "epistemic_status": "reported", "source_message_ids": [str(source_id)]},
                    ],
                },
                "chat_followup": {
                    "gap_analysis": {
                        "gaps": [
                            {"description": "ไม่พบข้อมูลการส่งข้อมูลออกนอกระบบ (Data Exfiltration) และปริมาณข้อมูลที่ส่งออก"}
                        ]
                    }
                },
            },
        ),
    ]

    context = RagContext(
        retrieval_context_id=retrieval_id,
        thread_id=thread_id,
        run_id=uuid4(),
        context="External MITRE Context",
        mitre_table=[
            {
                "technique_id": "T1546.011",
                "name": "Event Triggered Execution: Application Shimming",
                "tactic": "Persistence, Privilege Escalation",
                "description": "Adversaries may establish persistence and/or elevate privileges by executing malicious content triggered by application shims.",
                "reason": "คนร้ายติดตั้ง Shim บนเซิร์ฟเวอร์ WEB-01 เพื่อให้โค้ดทำงานอัตโนมัติ",
            }
        ],
        created_at=datetime.now(timezone.utc),
    )

    snapshot = build_current_report_snapshot(thread, rag_context=context)
    structured = build_template_report(snapshot)

    report_read = ChatReportRead(
        report_id=uuid4(),
        thread_id=thread_id,
        version_number=1,
        idempotency_key="idem-key-1",
        source_snapshot_hash=snapshot.evidence_sha256,
        analysis_message_id=analysis_msg_id,
        retrieval_context_id=retrieval_id,
        prompt_version="prompt-v1",
        provider="openrouter",
        model="gpt-5.6-luna",
        decoding_settings={},
        persistence_status="completed",
        validation_status="validated",
        report=structured,
        validation_errors=[],
        failure_code=None,
        failure_message=None,
        created_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        latency_ms=120.0,
        input_tokens=500,
        output_tokens=300,
    )
    return report_read, thread.title


def test_view_model_extracts_timeline_and_gaps_without_contradictions():
    report_read, title = make_realistic_report_read()
    view_model = build_report_view_model(report_read, thread_title=title, language="th")

    # 1. Summary without raw markdown header
    assert len(view_model.summary_paragraphs) > 0
    assert not any("###" in p for p in view_model.summary_paragraphs)
    assert "คนร้ายได้ทำการโจมตีเจาะระบบ" in view_model.summary_paragraphs[0]

    # 2. Timeline extracted from sequence (NO contradiction)
    assert len(view_model.timeline_rows) >= 2
    assert "เจาะเข้าสู่ระบบ WEB-01" in view_model.timeline_rows[0].event
    assert "Application Shim" in view_model.timeline_rows[1].event

    # 3. Gaps extracted properly (NO "ไม่พบข้อขัดแย้ง...")
    assert len(view_model.unresolved_issues) >= 1
    assert "ไม่พบข้อมูลการส่งข้อมูลออกนอกระบบ" in view_model.unresolved_issues[0].description
    assert view_model.unresolved_issues[0].description != view_model.i18n["empty_gaps"]

    # 4. Dynamic Next steps
    assert len(view_model.verification_actions) >= 1
    assert any("Firewall" in act.action or "ส่งออก" in act.action for act in view_model.verification_actions)

    # 5. MITRE Mapping with clean source
    assert len(view_model.mitre_rows) >= 1
    assert view_model.mitre_rows[0].technique_id == "T1546.011"
    assert view_model.mitre_rows[0].source == "MITRE ATT&CK Knowledge Base"
    assert "external_mitre_retrieval" not in view_model.mitre_rows[0].source

    # 6. Evidence and IOCs
    assert len(view_model.evidence_rows) == 1
    assert view_model.has_indicators is True
    assert any(ioc.value == "198.51.100.23" for ioc in view_model.indicator_rows)
    assert any(ioc.value == "sdbinst.exe" for ioc in view_model.indicator_rows)


def test_pdf_generation_produces_valid_pdf_bytes():
    report_read, title = make_realistic_report_read()
    pdf_bytes = render_chat_report_pdf(report_read, thread_title=title, language="th")
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


def test_html_rendering_contains_standalone_sections():
    report_read, title = make_realistic_report_read()
    html = render_chat_report_html(report_read, thread_title=title, language="th")

    # Verify standalone 1..7 sections
    assert "1. ภาพรวมเหตุการณ์" in html
    assert "2. ลำดับเหตุการณ์สำคัญ" in html
    assert "3. ข้อเท็จจริงและหลักฐานสำคัญ" in html
    assert "4. ข้อมูลอ้างอิง MITRE ATT&CK ที่เกี่ยวข้อง" in html
    assert "5. ประเด็นที่ยังไม่สามารถยืนยันได้" in html
    assert "6. ประเด็นที่ควรตรวจสอบเพิ่มเติม" in html
    assert "7. ข้อจำกัดของรายงาน" in html
    assert "ภาคผนวก: ข้อมูลตรวจสอบย้อนกลับทางเทคนิค" in html

    # Verify absence of legacy section numbering in headings
    assert "5.1 สรุปคดี" not in html
    assert "5.2 ตัวบ่งชี้ที่พบ" not in html
    assert "5.3 MITRE ATT&CK Mapping" not in html
