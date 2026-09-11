from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID

from pypdf import PdfReader

from app.schemas.reports import ReportSection, StructuredReport
from app.services.reports.case_report_contracts import CaseReportInputSnapshot, CaseReportSource
from app.services.reports.case_report_pdf import render_case_report_pdf


def test_case_report_pdf_preserves_snapshot_content_and_page_structure() -> None:
    source_id = UUID("11111111-1111-1111-1111-111111111111")
    snapshot = CaseReportInputSnapshot(
        case_id=UUID("22222222-2222-2222-2222-222222222222"),
        thread_id=UUID("33333333-3333-3333-3333-333333333333"),
        thread_title="PDF regression fixture",
        analysis_result_id=UUID("44444444-4444-4444-4444-444444444444"),
        evidence_snapshot_id=UUID("55555555-5555-5555-5555-555555555555"),
        evidence_revision=1,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        sources=[
            CaseReportSource(
                source_id=source_id,
                source_kind="narrative",
                revision_id=UUID("66666666-6666-6666-6666-666666666666"),
                revision=1,
                exact_text="The witness reported a blue vehicle.",
                text_sha256="a" * 64,
                provenance_json={},
            )
        ],
        evidence_sha256="b" * 64,
        manifest_sha256="c" * 64,
        analysis_answer="The witness reported a blue vehicle.",
        analysis_summary="A bounded report fixture.",
        analysis_trace={},
    )
    section_ids = (
        "case_summary",
        "indicators_found",
        "mitre_attack_mapping",
        "mapping_rationale",
        "evidence_to_examine",
        "preliminary_recommendations",
        "system_limitations",
    )
    report = StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title="PDF regression fixture",
        sections=[
            ReportSection(
                section_id=section_id,
                heading=section_id,
                paragraphs=["Fixture paragraph."],
            )
            for section_id in section_ids
        ],
    )

    pdf = render_case_report_pdf(
        snapshot,
        report,
        UUID("77777777-7777-7777-7777-777777777777"),
    )
    extracted = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf)).pages)

    assert pdf.startswith(b"%PDF")
    assert len(PdfReader(BytesIO(pdf)).pages) == 1
    assert "CYBERCASE INTELLIGENCE FRAMEWORK" in extracted
    assert "Evidence snapshot sources" in extracted
    assert "The witness reported a blue vehicle." in extracted
