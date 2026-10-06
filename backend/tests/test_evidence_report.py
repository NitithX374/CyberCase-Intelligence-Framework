from app.reports.render import render_case_report_html
from app.reports.schemas import CaseReportContent, ReportEvent, ReportImpact, ReportParty
from app.trace.trace import CaseProjectionGrounding


def test_report_keeps_binding_and_projection_support_distinct():
    failed = CaseProjectionGrounding(verdict="not_supported", reason="neutral", model="fake-nli")
    unchecked = CaseProjectionGrounding(verdict="unassessed", reason="context_limit")
    report = CaseReportContent(
        title="An incident",
        summary="John sent an email.",
        parties=[
            ReportParty(name="John", role="Attacker", support="bound", projection_grounding=failed)
        ],
        timeline=[
            ReportEvent(
                time="13:00", event="Server encrypted", support="bound", projection_grounding=failed
            )
        ],
        impacts=[
            ReportImpact(
                description="Payroll lost", support="bound", projection_grounding=unchecked
            )
        ],
    )
    html = render_case_report_html(report)
    assert html.count("ข้อมูลนี้ไม่ได้รับการสนับสนุนจากข้อสังเกตที่เชื่อมไว้") == 2
    assert "ยังไม่ได้ประเมินความสอดคล้องของข้อมูลนี้กับข้อสังเกตที่เชื่อมไว้" in html
    assert CaseReportContent.model_validate_json(report.model_dump_json()) == report


def test_old_report_snapshots_still_load_without_projection_fields():
    report = CaseReportContent.model_validate(
        {
            "title": "Old report",
            "summary": "Incident",
            "parties": [{"name": "John", "role": "Victim", "support": "bound"}],
        }
    )
    assert report.parties[0].projection_grounding is None
    assert "John" in render_case_report_html(report)
