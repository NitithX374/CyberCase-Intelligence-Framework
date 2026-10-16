from app.reports.render import render_case_report_html
from app.reports.schemas import CaseReportContent

PROJECTION_LINES = (
    "ข้อมูลนี้ไม่ได้รับการสนับสนุนจากข้อสังเกตที่เชื่อมไว้",
    "ยังไม่ได้ประเมินความสอดคล้องของข้อมูลนี้กับข้อสังเกตที่เชื่อมไว้",
)


def test_a_report_stored_with_projection_verdicts_prints_only_the_binding_support():
    failed = {"verdict": "not_supported", "reason": "neutral", "model": "fake-nli"}
    report = CaseReportContent.model_validate(
        {
            "title": "An incident",
            "summary": "John sent an email.",
            "parties": [
                {
                    "name": "John",
                    "role": "Attacker",
                    "support": "unbound",
                    "projection_grounding": failed,
                }
            ],
            "timeline": [
                {
                    "time": "13:00",
                    "event": "Server encrypted",
                    "support": "bound",
                    "projection_grounding": failed,
                }
            ],
            "impacts": [
                {
                    "description": "Payroll lost",
                    "support": "bound",
                    "projection_grounding": {"verdict": "unassessed", "reason": "context_limit"},
                }
            ],
        }
    )
    html = render_case_report_html(report)

    assert "projection_grounding" not in report.model_dump_json()
    assert not any(line in html for line in PROJECTION_LINES)
    assert "ไม่พบข้อความที่อ้างในเอกสาร" in html
    assert CaseReportContent.model_validate_json(report.model_dump_json()) == report


def test_old_report_snapshots_still_load_without_projection_fields():
    report = CaseReportContent.model_validate(
        {
            "title": "Old report",
            "summary": "Incident",
            "parties": [{"name": "John", "role": "Victim", "support": "bound"}],
        }
    )
    assert "John" in render_case_report_html(report)
