from io import BytesIO
from uuid import uuid4

from pypdf import PdfReader

from app.schemas.reports import PRELIMINARY_REPORT_SECTION_HEADINGS
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisTrace,
    CaseSourceCitation,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseTimelineItem,
)
from app.services.case_analysis.mitre_applicability_gate import MitreApplicabilityRecord
from app.services.case_materials import CaseSourceBundle, CaseSourceItem
from app.services.reports.case_report_contracts import (
    CaseReportInput,
    CaseReportTechnicalAugmentation,
)
from app.services.reports.case_report_html import render_case_report_html
from app.services.reports.case_report_pdf import render_case_report_pdf
from app.services.reports.case_report_template import build_case_template_report


def _input(technical: bool = False) -> CaseReportInput:
    source_id = str(uuid4())
    evidence_text = "พบการใช้ PowerShell.exe เชื่อมต่อไปยัง 198.51.100.23"
    association = CaseMitreAssociation(
        association_id="MA-01",
        technique_id="T1059.001",
        claim_ids=["A-01"],
        reason="พฤติกรรมในหลักฐานสอดคล้องกับการใช้ PowerShell",
        status="candidate_only",
        support_role="external_technical_context",
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="พบพฤติกรรมทางเทคนิคที่ควรตรวจสอบเพิ่มเติม",
        involved_parties=[CaseInvolvedParty(name="ผู้ใช้ A", role="ผู้เกี่ยวข้องที่ปรากฏในเอกสาร", claim_ids=["A-01"])],
        timeline=[CaseTimelineItem(time="10:30 น.", event="มีการเรียกใช้ PowerShell", claim_ids=["A-01"])],
        impacts=[CaseImpactItem(description="เกิดการเชื่อมต่อไปยังปลายทางภายนอก", claim_ids=["A-01"])],
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="<script>กิจกรรม PowerShell ปรากฏในหลักฐาน</script>",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=evidence_text)],
            )
        ],
        gaps=[
            CaseAnalysisGap(
                gap_id="G-01",
                topic="ผู้ใช้ที่สั่งงาน",
                status="NOT_PROVIDED",
                description="ยังไม่มีข้อมูลยืนยันว่าใครเป็นผู้สั่งงาน",
                affected_claim_ids=["A-01"],
                reason="หลักฐานที่มีไม่ระบุผู้ใช้งานอย่างชัดเจน",
                priority="high",
                askable=True,
            )
        ],
        mitre_associations=[association] if technical else [],
        retrieval_context_id="retrieval-1" if technical else None,
    )
    augmentation = None
    if technical:
        augmentation = CaseReportTechnicalAugmentation(
            version="case_mitre_augmentation_v1",
            status="retrieved_with_matches",
            applicability=MitreApplicabilityRecord(
                decision="RETRIEVE",
                source_message_ids=[source_id],
                trigger_text=[evidence_text],
            ),
            retrieval_context_id="retrieval-1",
            mitre_table=[
                {
                    "technique_id": "T1059.001",
                    "name": "PowerShell",
                    "description": "Command and scripting interpreter.",
                }
            ],
            association_ids=["MA-01"],
        )
    return CaseReportInput(
        case_id=uuid4(),
        case_title="คดีทดสอบ",
        analysis_result_id=uuid4(),
        source_bundle=CaseSourceBundle(
            revision=1,
            sources=(
                CaseSourceItem(
                    source_id=source_id,
                    source_kind="document",
                    text=evidence_text,
                    document_id=str(uuid4()),
                    filename="หลักฐาน.pdf",
                ),
            ),
        ),
        analysis_answer="ควรตรวจสอบผู้ใช้งานและต้นทางของคำสั่งเพิ่มเติม",
        analysis_summary=trace.summary,
        analysis_trace=trace.model_dump(mode="json"),
        technical_augmentation=augmentation,
    )


def test_report_uses_readable_sections_and_restores_analysis_context() -> None:
    report = build_case_template_report(_input())

    assert [section.heading for section in report.sections] == list(PRELIMINARY_REPORT_SECTION_HEADINGS.values())
    assert report.sections[0].items[0].startswith("ผู้เกี่ยวข้อง: ผู้ใช้ A")
    assert "E-01" in report.sections[0].items[0]
    assert report.sections[0].items[1].startswith("ลำดับเหตุการณ์:")
    assert report.sections[0].items[2].startswith("ผลกระทบที่ปรากฏ:")
    assert report.claims[0].section_id == "case_evidence"
    assert report.sections[4].items[0].startswith("G-01")
    assert "ข้อสันนิษฐาน" not in report.sections[6].items[0]


def test_jinja_report_renders_sections_and_escapes_case_content() -> None:
    report_input = _input(technical=True)
    report = build_case_template_report(report_input)
    html = render_case_report_html(report_input, report)

    assert "1. สรุปคดี" in html
    assert "2. ตัวบ่งชี้ที่พบ" in html
    assert "3. MITRE ATT&amp;CK Mapping" in html
    assert "T1059.001" in html
    assert "บริบททางเทคนิคภายนอก ไม่ใช่หลักฐานของคดี" in html
    assert "&lt;script&gt;กิจกรรม PowerShell ปรากฏในหลักฐาน&lt;/script&gt;" in html
    assert "<script>กิจกรรม PowerShell ปรากฏในหลักฐาน</script>" not in html


def test_pdf_report_is_generated_from_the_readable_report_content() -> None:
    report_input = _input(technical=True)
    report = build_case_template_report(report_input)
    pdf = render_case_report_pdf(report_input, report, uuid4())

    assert pdf.startswith(b"%PDF-")
    assert len(PdfReader(BytesIO(pdf)).pages) >= 1
