import re
from io import BytesIO
from uuid import uuid4

import pytest
from pypdf import PdfReader

from app.schemas.reports import PRELIMINARY_REPORT_SECTION_HEADINGS
from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseSourceCitation,
    CaseTimelineItem,
)
from app.services.analysis.mitre_gate.llm import MitreApplicabilityRecord
from app.services.reports.assembly import build_case_report, build_case_template_report
from app.services.reports.contracts import (
    CaseReportInput,
    CaseReportTechnicalAugmentation,
    ReportValidationError,
)
from app.services.reports.render_html import render_case_report_html
from app.services.reports.render_pdf import render_case_report_pdf
from app.services.sources import CaseSourceBundle, CaseSourceItem


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
        involved_parties=[
            CaseInvolvedParty(name="ผู้ใช้ A", role="ผู้เกี่ยวข้องที่ปรากฏในเอกสาร", claim_ids=["A-01"])
        ],
        timeline=[
            CaseTimelineItem(time="10:30 น.", event="มีการเรียกใช้ PowerShell", claim_ids=["A-01"])
        ],
        impacts=[CaseImpactItem(description="เกิดการเชื่อมต่อไปยังปลายทางภายนอก", claim_ids=["A-01"])],
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="<script>กิจกรรม PowerShell ปรากฏในหลักฐาน</script>",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[
                    CaseSourceCitation(source_id=source_id, exact_quote=evidence_text)
                ],
            )
        ],
        gaps=[
            CaseAnalysisGap(
                gap_id="G-01",
                gap_key="user_identity",
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
        analysis_summary=trace.summary,
        analysis_trace=trace.model_dump(mode="json"),
        technical_augmentation=augmentation,
    )


def _rag_only_input() -> CaseReportInput:
    report_input = _input(technical=True)
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
    augmentation = report_input.technical_augmentation
    assert augmentation is not None
    rag_augmentation = CaseReportTechnicalAugmentation.model_validate(
        {
            **augmentation.model_dump(mode="json"),
            "status": "retrieved_from_rag",
            "mitre_table": [
                {
                    "technique_id": "T1059.001",
                    "name": "PowerShell",
                    "description": "Command and scripting interpreter.",
                },
                {
                    "technique_id": "S0096",
                    "name": "Systeminfo",
                    "entity_type": "Software",
                    "description": "System information utility.",
                },
            ],
            "association_ids": [],
        }
    )
    return report_input.model_copy(
        update={
            "analysis_trace": trace.model_copy(update={"mitre_associations": []}).model_dump(
                mode="json"
            ),
            "technical_augmentation": rag_augmentation,
        }
    )


def test_report_uses_readable_sections_and_restores_analysis_context() -> None:
    report = build_case_template_report(_input())

    assert [section.heading for section in report.sections] == list(
        PRELIMINARY_REPORT_SECTION_HEADINGS.values()
    )
    assert report.sections[0].items[0].startswith("ผู้เกี่ยวข้อง: ผู้ใช้ A")
    assert "E-01" in report.sections[0].items[0]
    assert report.sections[0].items[1].startswith("ลำดับเหตุการณ์:")
    assert report.sections[0].items[2].startswith("ผลกระทบที่ปรากฏ:")
    assert report.claims[0].section_id == "case_evidence"
    # The gap's topic, not its id: G-01 means something to the pipeline and
    # nothing to whoever reads the report.
    assert report.sections[4].items[0].startswith("ผู้ใช้ที่สั่งงาน")
    assert "G-01" not in report.sections[4].items[0]
    assert "ข้อสันนิษฐาน" not in report.sections[6].items[0]


ANSWER = "เหตุการณ์เกิดขึ้นเวลา 23:30 ของวันที่ 12 พฤษภาคม"


def _input_citing_a_followup_answer(*, with_history: bool) -> CaseReportInput:
    """A case whose finding rests on something the reader told the system."""

    report_input = _input()
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)
    cited = trace.model_copy(
        update={
            "claims": [
                trace.claims[0].model_copy(
                    update={
                        "supporting_source_ids": [
                            *trace.claims[0].supporting_source_ids,
                            "QA-01",
                        ],
                        "supporting_citations": [
                            *trace.claims[0].supporting_citations,
                            CaseSourceCitation(source_id="QA-01", exact_quote=ANSWER),
                        ],
                    }
                )
            ]
        }
    )
    history = (
        (
            CaseFollowupExchange(
                qa_id="QA-01",
                gap_key="topic:time",
                question="เหตุการณ์เกิดขึ้นเมื่อใด",
                answer=ANSWER,
            ),
        )
        if with_history
        else ()
    )
    return report_input.model_copy(
        update={
            "analysis_trace": cited.model_dump(mode="json"),
            "followup_history": history,
        }
    )


def test_a_claim_resting_on_a_followup_answer_does_not_fail_the_report() -> None:
    """The analysis was allowed to cite the reader's answer, so the report is too.

    Validation used to compare every cited id against the source bundle alone.
    A QA id is not in it, so a case that had been clarified could not produce a
    report at all — the whole thing failed over a citation that had already
    been checked and found good.
    """

    report = build_case_report(_input_citing_a_followup_answer(with_history=True))

    cited = next(claim for claim in report.claims if "QA-01" in claim.source_ids)
    assert cited.source_ids == [cited.source_ids[0], "QA-01"]
    # Labelled apart from case material: a reader can see the finding rests on
    # something they said rather than on a document.
    assert any("Q-01" in item for item in report.sections[0].items)


def test_an_id_no_exchange_backs_is_still_refused() -> None:
    """Widening the allowlist is not the same as removing it."""

    with pytest.raises(ReportValidationError):
        build_case_report(_input_citing_a_followup_answer(with_history=False))


def test_the_report_says_why_the_system_stopped_asking() -> None:
    """A budget that ran out and a case with nothing left to ask read alike.

    Both leave gaps listed under "หลักฐานที่ควรตรวจสอบ". Only the limitations
    section can tell the reader which of the two produced them.
    """

    report_input = _input()
    trace = CaseAnalysisTrace.model_validate(report_input.analysis_trace)

    def limitations(stop_reason: str | None) -> list[str]:
        paused = report_input.model_copy(
            update={
                "analysis_trace": trace.model_copy(update={"stop_reason": stop_reason}).model_dump(
                    mode="json"
                )
            }
        )
        return build_case_template_report(paused).limitations

    spent = limitations("max_rounds_reached")
    assert any("ครบจำนวนรอบ" in item for item in spent)

    exhausted = limitations("gaps_exhausted")
    assert any("ถามทุกประเด็นที่ถามได้แล้ว" in item for item in exhausted)
    assert spent != exhausted, "the two reasons must not read the same"

    # A case still being clarified has no reason yet, and inventing one would
    # tell the reader the questions are over when they are not.
    assert limitations(None) == limitations("round_budget_spent")


def test_no_internal_identifier_reaches_the_reader() -> None:
    """G-01, A-01 and MA-01 are how the pipeline's parts name things to each other.

    They mean nothing to whoever reads the report, and printing one invites a
    reader to go looking for a register that does not exist. This is a guard,
    not a formatting preference: the ids leak whenever a renderer prints an
    item verbatim, which is easy to do by accident.
    """

    report_input = _input(technical=True)
    report = build_case_report(report_input)
    pdf = PdfReader(BytesIO(render_case_report_pdf(report_input, report, uuid4())))

    rendered = "\n".join(
        [
            *(item for section in report.sections for item in section.items),
            *(paragraph for section in report.sections for paragraph in section.paragraphs),
            *report.limitations,
            render_case_report_html(report_input, report),
            *(page.extract_text() for page in pdf.pages),
        ]
    )

    for pattern, what in ((r"G-\d{2}", "gap"), (r"MA-\d{2}", "ATT&CK association")):
        assert not re.search(pattern, rendered), f"an internal {what} id reached the reader"


def test_the_report_does_not_claim_chat_answers_are_excluded() -> None:
    """Claims may cite a follow-up answer, so the report must not deny it."""

    limitations = build_case_template_report(_input()).limitations
    assert any("คำถามติดตามผล" in item for item in limitations)
    assert not any("ไม่รวมคำตอบจาก Chat" in item for item in limitations)


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


def test_report_accepts_all_rag_rows_without_claim_mapping() -> None:
    report = build_case_template_report(_rag_only_input())

    mapping_items = report.sections[2].items
    rationale_items = report.sections[3].items
    assert any("T1059.001" in item for item in mapping_items)
    assert any("S0096" in item for item in mapping_items)
    assert any("RAG service" in item for item in rationale_items)


def test_pdf_report_is_generated_from_the_readable_report_content() -> None:
    report_input = _input(technical=True)
    report = build_case_template_report(report_input)
    pdf = render_case_report_pdf(report_input, report, uuid4())

    assert pdf.startswith(b"%PDF-")
    assert len(PdfReader(BytesIO(pdf)).pages) >= 1
