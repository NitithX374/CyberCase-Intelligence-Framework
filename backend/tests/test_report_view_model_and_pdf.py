from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

from pypdf import PdfReader

from app.models.chat import ChatMessage, ChatThread
from app.models.rag_context import RagContext
from app.schemas.reports import ChatReportRead
from app.services.reports.report_html import render_chat_report_html
from app.services.reports.report_pdf import render_chat_report_pdf
from app.services.reports.report_snapshot import build_current_report_snapshot
from app.services.reports.report_template import build_template_report
from app.services.reports.report_view_model_builder import build_report_view_model


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
- 12 มกราคม 2568 เวลา 09.30 น. - คนร้ายเจาะเข้าสู่ระบบ WEB-01 ผ่านช่องโหว่ IIS Web Server
- 12 มกราคม 2568 เวลา 10.15 น. - คนร้ายติดตั้ง Application Shim ฐานข้อมูล SDB เพื่อคงสิทธิ์การเข้าถึง (Persistence)
- 12 มกราคม 2568 ช่วงบ่าย - ตรวจพบการสื่อสารออกไปยัง IP ปลายทาง 198.51.100.23

### 3. Relevant MITRE ATT&CK Context
พบเทคนิค T1546.011 (Application Shimming) สอดคล้องกับการคงสิทธิ์""",
            retrieval_context_id=retrieval_id,
            metadata_json={
                "analysis_kind": "grounded_main_analysis",
                "analysis_trace": {
                    "version": "analysis_trace_v3",
                    "summary": """## ภาพรวมคดี
จากการตรวจสอบข้อมูลสำนวนคดี พบว่าคนร้ายได้ทำการโจมตีเจาะระบบเซิร์ฟเวอร์ WEB-01 ผ่านช่องโหว่บน IIS Web Application โดยมีพฤติกรรมฝังตัวผ่าน Application Shimming

## ลำดับเหตุการณ์สำคัญ
- 12 มกราคม 2568 เวลา 09.30 น. - คนร้ายเจาะเข้าสู่ระบบ WEB-01 ผ่านช่องโหว่ IIS Web Server
- 12 มกราคม 2568 เวลา 10.15 น. - คนร้ายติดตั้ง Application Shim ฐานข้อมูล SDB เพื่อคงสิทธิ์การเข้าถึง
- 12 มกราคม 2568 ช่วงบ่าย - ตรวจพบการสื่อสารออกไปยัง IP ปลายทาง 198.51.100.23""",
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
        source_snapshot=snapshot.model_dump(mode="json"),
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
    assert view_model.timeline_rows[0].time_display == "12 มกราคม 2568 เวลา 09.30 น."
    assert view_model.timeline_rows[0].source_evidence == "ข้อความ #1"

    # 3. Gaps extracted properly (NO "ไม่พบข้อขัดแย้ง...")
    assert len(view_model.unresolved_issues) >= 1
    assert "ไม่พบข้อมูลการส่งข้อมูลออกนอกระบบ" in view_model.unresolved_issues[0].description
    assert view_model.unresolved_issues[0].description != view_model.i18n["empty_gaps"]

    # 4. Dynamic Next steps
    assert len(view_model.verification_actions) >= 1
    assert any("เอกสาร" in act.action or "ต้นทาง" in act.action for act in view_model.verification_actions)

    # 5. MITRE Mapping with clean structured fields (NOT degraded to technique_id or "General")
    assert len(view_model.mitre_rows) >= 1
    assert view_model.mitre_rows[0].technique_id == "T1546.011"
    assert view_model.mitre_rows[0].technique_name == "Event Triggered Execution: Application Shimming"
    assert view_model.mitre_rows[0].tactic == "Persistence, Privilege Escalation"
    assert "คนร้ายติดตั้ง Shim" in view_model.mitre_rows[0].case_evidence_support
    assert view_model.mitre_rows[0].source == "MITRE ATT&CK Knowledge Base"
    assert "external_mitre_retrieval" not in view_model.mitre_rows[0].source

    # 6. Evidence and IOCs
    assert len(view_model.evidence_rows) == 2
    assert view_model.has_indicators is True
    assert any(ioc.value == "198.51.100.23" for ioc in view_model.indicator_rows)
    assert any(ioc.value == "sdbinst.exe" for ioc in view_model.indicator_rows)


def test_report_view_model_finding_provenance_multi_source_and_fallback():
    thread_id = uuid4()
    msg1_id = uuid4()
    msg3_id = uuid4()
    msg5_id = uuid4()
    analysis_msg_id = uuid4()
    retrieval_id = "retrieval-ctx-multi"

    thread = ChatThread(id=thread_id, title="Multi-source provenance test", status="answered")
    thread.messages = [
        ChatMessage(id=msg1_id, thread_id=thread_id, ordinal=1, role="user", content="Initial narrative", metadata_json={"evidence_kind": "initial_case_narrative"}),
        ChatMessage(id=uuid4(), thread_id=thread_id, ordinal=2, role="assistant", content="What port was open?", metadata_json={"evidence_kind": "analyst_question"}),
        ChatMessage(id=msg3_id, thread_id=thread_id, ordinal=3, role="user", content="Port 443 was exposed to Internet.", metadata_json={"evidence_kind": "clarification_answer"}),
        ChatMessage(id=uuid4(), thread_id=thread_id, ordinal=4, role="assistant", content="Any further details?", metadata_json={"evidence_kind": "analyst_question"}),
        ChatMessage(id=msg5_id, thread_id=thread_id, ordinal=5, role="user", content="Later found web shell named cmd.aspx.", metadata_json={"evidence_kind": "added_case_information"}),
        ChatMessage(id=analysis_msg_id, thread_id=thread_id, ordinal=6, role="assistant", content="Analysis output", retrieval_context_id=retrieval_id, metadata_json={"analysis_kind": "grounded_main_analysis", "analysis_trace": {"claims": [
            {"claim_id": "c1", "text": "Exposure on port 443 identified", "epistemic_status": "reported", "source_message_ids": [str(msg3_id)]},
            {"claim_id": "c2", "text": "Initial entry and web shell linked", "epistemic_status": "reported", "source_message_ids": [str(msg1_id), str(msg5_id)]},
            {"claim_id": "c3", "text": "Unresolvable source claim", "epistemic_status": "reported", "source_message_ids": ["non-existent-msg-id"]},
        ]}}),
    ]

    context = RagContext(retrieval_context_id=retrieval_id, thread_id=thread_id, run_id=uuid4(), context="External context", mitre_table=[], created_at=datetime.now(timezone.utc))
    snapshot = build_current_report_snapshot(thread, rag_context=context)
    structured = build_template_report(snapshot)

    report_read = ChatReportRead(
        report_id=uuid4(),
        thread_id=thread_id,
        version_number=1,
        idempotency_key="idem-multi-1",
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
        latency_ms=100.0,
        input_tokens=100,
        output_tokens=100,
        source_snapshot=snapshot.model_dump(mode="json"),
    )

    # 1. Thai View Model
    vm_th = build_report_view_model(report_read, thread_title=thread.title, language="th")
    assert vm_th.timeline_rows == []
    assert vm_th.evidence_rows[0].source_type == "ข้อความ #3"
    assert vm_th.evidence_rows[1].source_type == "ข้อความ #1, #5"
    assert vm_th.evidence_rows[2].source_type == "ข้อมูลจากสำนวนที่ผู้ใช้ส่ง"
    assert "#1" not in vm_th.evidence_rows[2].source_type

    # 2. English View Model
    vm_en = build_report_view_model(report_read, thread_title=thread.title, language="en")
    assert vm_en.evidence_rows[0].source_type == "Message #3"
    assert vm_en.evidence_rows[1].source_type == "Message #1, #5"
    assert vm_en.evidence_rows[2].source_type == "User-submitted case material"
    assert "#1" not in vm_en.evidence_rows[2].source_type


def test_pdf_generation_produces_valid_pdf_bytes():
    report_read, title = make_realistic_report_read()
    pdf_bytes = render_chat_report_pdf(report_read, thread_title=title, language="th")
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


def test_pdf_generation_splits_long_evidence_across_pages():
    report_read, title = make_realistic_report_read()
    source_snapshot = dict(report_read.source_snapshot or {})
    trace = dict(source_snapshot["analysis_trace"])
    claims = list(trace["claims"])
    claims[0] = {**claims[0], "text": "รายละเอียดข้อเท็จจริงจากเอกสารฉบับยาว " * 800}
    trace["claims"] = claims
    source_snapshot["analysis_trace"] = trace
    long_report = report_read.model_copy(
        update={"source_snapshot": source_snapshot}
    )

    pdf_bytes = render_chat_report_pdf(long_report, thread_title=title, language="th")

    assert pdf_bytes.startswith(b"%PDF")
    assert len(PdfReader(BytesIO(pdf_bytes)).pages) > 1


def test_html_rendering_contains_standalone_sections():
    report_read, title = make_realistic_report_read()
    html = render_chat_report_html(report_read, thread_title=title, language="th")

    # Verify standalone 1..7 sections
    assert "1. บทสรุปคดี" in html
    assert "2. ลำดับเหตุการณ์สำคัญ" in html
    assert "3. ข้อเท็จจริงที่รายงานและแหล่งอ้างอิง" in html
    assert "4. บริบททางเทคนิคภายนอก (ถ้ามี)" in html
    assert "5. ประเด็นที่ต้องยืนยันเพิ่มเติม" in html
    assert "6. แนวทางตรวจสอบเพิ่มเติม" in html
    assert "7. ขอบเขตและข้อจำกัด" in html
    assert "ภาคผนวก: ข้อมูลตรวจสอบย้อนกลับของรายงาน" in html

    # Verify absence of legacy section numbering in headings
    assert "5.1 สรุปคดี" not in html
    assert "5.2 ตัวบ่งชี้ที่พบ" not in html
    assert "5.3 MITRE ATT&CK Mapping" not in html
