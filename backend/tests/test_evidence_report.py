from app.reports.render import render_case_report_html
from app.reports.schemas import CaseReportContent


def test_old_report_snapshots_still_load():
    report = CaseReportContent.model_validate(
        {
            "title": "Old report",
            "summary": "Incident",
            "parties": [{"name": "John", "role": "Victim", "support": "bound"}],
        }
    )
    assert "John" in render_case_report_html(report)
