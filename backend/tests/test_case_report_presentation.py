import json
import re
from datetime import UTC, datetime
from io import BytesIO
from uuid import uuid4

import pytest
from pypdf import PdfReader

from app.analysis.technical_context.contracts import (
    CaseTechnicalAugmentation,
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.models.source import CaseSource
from app.reports.contracts import CaseReportInput
from app.reports.display import SOURCE_KINDS, build_case_report_content, thai_date
from app.reports.render import ReportIssue, render_case_report_html, render_case_report_pdf
from app.reports.schemas import CaseReportContent
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseFollowupExchange,
    CaseSourceCitation,
)
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseTimelineItem,
)

ISSUE = ReportIssue(version_number=2, created_at=datetime(2026, 9, 24, 6, 22, tzinfo=UTC))
SOURCE_TEXT = "พบการใช้ PowerShell.exe เชื่อมต่อไปยัง 198.51.100.23"


def _applicability(source_id: str) -> MitreApplicabilityRecord:
    return MitreApplicabilityRecord(
        decision="RETRIEVE",
        source_message_ids=[source_id],
        trigger_text=[SOURCE_TEXT],
    )


def _input(technical: bool = False) -> CaseReportInput:
    source_id = str(uuid4())
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
                    CaseSourceCitation(source_id=source_id, exact_quote=SOURCE_TEXT)
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
        augmentation = CaseTechnicalAugmentation(
            status="retrieved_with_matches",
            applicability=_applicability(source_id),
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
                    text=SOURCE_TEXT,
                    document_id=str(uuid4()),
                    filename="หลักฐาน.pdf",
                ),
            ),
        ),
        analysis_summary=trace.summary,
        analysis_trace=trace,
        technical_augmentation=augmentation,
    )


def _with_augmentation(augmentation: CaseTechnicalAugmentation | None) -> CaseReportInput:
    return _input().model_copy(update={"technical_augmentation": augmentation})


def _rag_only_input() -> CaseReportInput:
    report_input = _input()
    source_id = report_input.source_bundle.sources[0].source_id
    augmentation = CaseTechnicalAugmentation(
        status="retrieved_from_rag",
        applicability=_applicability(source_id),
        retrieval_context_id="retrieval-1",
        mitre_table=[
            {"technique_id": "T1059.001", "name": "PowerShell", "tactic": "execution"},
            {"technique_id": "S0096", "name": "Systeminfo", "entity_type": "Software"},
        ],
    )
    return report_input.model_copy(update={"technical_augmentation": augmentation})


def _stored(report_input: CaseReportInput) -> CaseReportContent:
    written = json.loads(
        json.dumps(build_case_report_content(report_input).model_dump(mode="json"))
    )
    return CaseReportContent.model_validate(written)


def test_the_report_rows_carry_the_analysis_and_its_references() -> None:
    report = build_case_report_content(_input())

    [party] = report.parties
    assert (party.name, party.references) == ("ผู้ใช้ A", ["E-01"])
    assert report.timeline[0].event == "มีการเรียกใช้ PowerShell"
    assert report.impacts[0].references == ["E-01"]
    [gap] = report.gaps
    assert (gap.topic, gap.priority, gap.status) == ("ผู้ใช้ที่สั่งงาน", "สูง", "ยังไม่มีข้อมูล")
    assert "G-01" not in gap.model_dump_json()
    assert report.recommendations[0].startswith("ตรวจสอบเพิ่มเติมในประเด็น ผู้ใช้ที่สั่งงาน")
    assert "ข้อสันนิษฐาน" not in report.limitations[0]


ANSWER = "เหตุการณ์เกิดขึ้นเวลา 23:30 ของวันที่ 12 พฤษภาคม"


def _input_citing_a_followup_answer(*, with_history: bool) -> CaseReportInput:
    report_input = _input()
    trace = report_input.analysis_trace
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
    return report_input.model_copy(update={"analysis_trace": cited, "followup_history": history})


def test_a_claim_resting_on_a_followup_answer_cites_it() -> None:
    report = build_case_report_content(_input_citing_a_followup_answer(with_history=True))

    assert report.findings[0].source_labels == ["E-01", "Q-01"]
    assert report.parties[0].references == ["E-01", "Q-01"]


def test_an_id_no_exchange_backs_gets_no_reference() -> None:
    report = build_case_report_content(_input_citing_a_followup_answer(with_history=False))

    assert report.findings[0].source_labels == ["E-01"]
    assert [source.label for source in report.sources] == ["E-01"]


def test_a_claim_without_a_verified_quote_still_names_its_source() -> None:
    report_input = _input()
    trace = report_input.analysis_trace
    unquoted = trace.model_copy(
        update={"claims": [trace.claims[0].model_copy(update={"supporting_citations": []})]}
    )
    report = build_case_report_content(report_input.model_copy(update={"analysis_trace": unquoted}))

    assert report.findings[0].source_labels == ["E-01"]
    assert report.findings[0].supporting_quotes == []
    assert report.parties[0].references == ["E-01"]
    assert report.impacts[0].references == ["E-01"]


def test_a_quoted_claim_names_only_the_sources_its_quotes_come_from() -> None:
    report_input = _input()
    second = CaseSourceItem(source_id=str(uuid4()), source_kind="narrative", text="คำบอกเล่าเพิ่มเติม")
    bundle = report_input.source_bundle
    trace = report_input.analysis_trace
    claim = trace.claims[0]
    named = trace.model_copy(
        update={
            "claims": [
                claim.model_copy(
                    update={
                        "supporting_source_ids": [*claim.supporting_source_ids, second.source_id]
                    }
                )
            ]
        }
    )
    report = build_case_report_content(
        report_input.model_copy(
            update={
                "analysis_trace": named,
                "source_bundle": CaseSourceBundle(
                    revision=bundle.revision, sources=(*bundle.sources, second)
                ),
            }
        )
    )

    assert report.findings[0].source_labels == ["E-01"]


def test_the_report_says_why_the_system_stopped_asking() -> None:
    report_input = _input()
    trace = report_input.analysis_trace

    def limitations(stop_reason: str | None) -> list[str]:
        paused = report_input.model_copy(
            update={"analysis_trace": trace.model_copy(update={"stop_reason": stop_reason})}
        )
        return build_case_report_content(paused).limitations

    spent = limitations("max_rounds_reached")
    assert any("ครบจำนวนรอบ" in item for item in spent)

    exhausted = limitations("gaps_exhausted")
    assert any("ถามทุกประเด็นที่ถามได้แล้ว" in item for item in exhausted)
    assert spent != exhausted, "the two reasons must not read the same"

    assert limitations(None) == limitations("round_budget_spent")


def test_no_internal_identifier_reaches_the_reader() -> None:
    report = _stored(_input(technical=True))
    pdf = PdfReader(BytesIO(render_case_report_pdf(report, ISSUE)))

    rendered = "\n".join(
        [
            report.model_dump_json(),
            render_case_report_html(report, ISSUE),
            *(page.extract_text() for page in pdf.pages),
        ]
    )

    for pattern, what in ((r"G-\d{2}", "gap"), (r"MA-\d{2}", "ATT&CK association")):
        assert not re.search(pattern, rendered), f"an internal {what} id reached the reader"


def test_the_report_does_not_claim_chat_answers_are_excluded() -> None:
    limitations = build_case_report_content(_input()).limitations
    assert any("คำถามติดตามผล" in item for item in limitations)
    assert not any("ไม่รวมคำตอบจาก Chat" in item for item in limitations)


def test_jinja_report_renders_sections_and_escapes_case_content() -> None:
    html = render_case_report_html(_stored(_input(technical=True)), ISSUE)

    assert "1. สรุปข้อเท็จจริงของคดี" in html
    assert "2. ข้อเท็จจริงและตัวบ่งชี้ที่ตรวจพบ" in html
    assert "3. การจำแนกพฤติกรรมตามกรอบ MITRE ATT&amp;CK" in html
    assert "7. ข้อจำกัดและข้อสงวนของรายงาน" in html
    assert "T1059.001" in html
    assert "MITRE ATT&amp;CK เป็นข้อมูลภายนอก" in html
    assert "&lt;script&gt;กิจกรรม PowerShell ปรากฏในหลักฐาน&lt;/script&gt;" in html
    assert "<script>กิจกรรม PowerShell ปรากฏในหลักฐาน</script>" not in html


def test_the_document_is_printed_from_the_stored_copy() -> None:
    report_input = _input(technical=True)
    stored = _stored(report_input)

    assert render_case_report_html(stored, ISSUE) == render_case_report_html(
        build_case_report_content(report_input), ISSUE
    )


def test_the_document_names_its_version_and_dates() -> None:
    analysed = datetime(2026, 9, 23, 20, 0, tzinfo=UTC)
    report_input = _input().model_copy(update={"analysis_created_at": analysed})
    html = render_case_report_html(_stored(report_input), ISSUE)

    assert "24 กันยายน 2569 เวลา 13.22 น." in html
    assert "ลงวันที่ 24 กันยายน 2569" in html
    assert "ฉบับที่ 2" in html, "the page footer names the version"
    assert thai_date(analysed) == "24 กันยายน 2569"


def test_an_untitled_case_is_not_printed_under_its_placeholder() -> None:
    report_input = _input().model_copy(update={"case_title": "New case"})
    html = render_case_report_html(_stored(report_input), ISSUE)

    assert "ไม่ได้ระบุชื่อเรื่อง" in html
    assert "New case" not in html


def test_every_reference_resolves_in_the_source_register() -> None:
    report = build_case_report_content(_input_citing_a_followup_answer(with_history=True))

    assert report.findings[0].source_labels == ["E-01", "Q-01"]
    assert [(source.label, source.detail) for source in report.sources] == [
        ("E-01", "หลักฐาน.pdf"),
        ("Q-01", "คำถาม: เหตุการณ์เกิดขึ้นเมื่อใด"),
    ]


def test_a_technique_points_at_the_finding_it_rests_on() -> None:
    report = build_case_report_content(_input(technical=True))

    assert report.techniques_matched
    [technique] = report.techniques
    assert (technique.technique_id, technique.name) == ("T1059.001", "PowerShell")
    assert technique.findings == [1], "finding 1 in the findings table"
    assert technique.references == ["E-01"]
    assert report.mapping_note is None
    assert report.rationale_note is None


def test_report_accepts_all_rag_rows_without_claim_mapping() -> None:
    report = build_case_report_content(_rag_only_input())

    assert not report.techniques_matched
    assert [(row.technique_id, row.tactic) for row in report.techniques] == [
        ("T1059.001", "execution"),
        ("S0096", ""),
    ]
    html = render_case_report_html(report, ISSUE)
    assert "ยังไม่ได้วิเคราะห์ความเชื่อมโยงกับข้อเท็จจริงรายข้อ" in html
    assert any("RAG service" in item for item in report.limitations)


@pytest.mark.parametrize(
    ("augmentation", "mapping", "rationale"),
    [
        (None, "ไม่มีผลการเสริมข้อมูล MITRE ที่บันทึกไว้", "ไม่มีการอนุมาน mapping"),
        (
            CaseTechnicalAugmentation(
                status="not_applicable", applicability=skipped_mitre_applicability()
            ),
            "ไม่พบเงื่อนไขที่จำเป็นต้องใช้ MITRE ATT&amp;CK",
            "ระบบข้ามการค้นหา MITRE",
        ),
        (
            CaseTechnicalAugmentation(
                status="insufficient_context",
                applicability=_applicability("source"),
                retrieval_context_id="retrieval-thin",
            ),
            "ข้อมูลทางเทคนิคภายนอกไม่เพียงพอ",
            "ยังไม่มีบริบททางเทคนิคเพียงพอ",
        ),
        (
            CaseTechnicalAugmentation(
                status="failed",
                applicability=_applicability("source"),
                failure_code="rag_service_unavailable",
            ),
            "ไม่สามารถเชื่อมต่อกับบริการภายนอกได้ในขณะนี้ จึงไม่แสดง mapping",
            "ยังไม่สามารถอธิบาย mapping ได้",
        ),
    ],
)
def test_a_case_without_techniques_says_why_in_sections_three_and_four(
    augmentation, mapping, rationale
) -> None:
    report = _stored(_with_augmentation(augmentation))
    html = render_case_report_html(report, ISSUE)

    assert report.techniques == []
    section_three = html.split('id="mitre_attack_mapping"')[1].split('id="mapping_rationale"')[0]
    section_four = html.split('id="mapping_rationale"')[1].split('id="evidence_to_examine"')[0]
    assert mapping in section_three
    assert rationale in section_four


def test_the_source_register_names_exactly_the_kinds_a_case_source_can_have() -> None:
    [constraint] = [
        constraint
        for constraint in CaseSource.__table__.constraints
        if constraint.name == "ck_case_sources_kind"
    ]
    assert set(SOURCE_KINDS) == set(re.findall(r"'(\w+)'", str(constraint.sqltext)))
