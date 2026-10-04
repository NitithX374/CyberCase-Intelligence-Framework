import json
import re
from dataclasses import replace
from datetime import UTC, datetime
from io import BytesIO
from uuid import uuid4

import pytest
from pypdf import PdfReader

from app.analysis.prompts import CASE_CHECKLIST
from app.analysis.technical_context.contracts import (
    CaseTechnicalAugmentation,
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.models.source import CaseSource
from app.reports.contracts import CaseReportInput
from app.reports.display import (
    CHECKLIST_TOPICS,
    SOURCE_KINDS,
    build_case_report_content,
    thai_date,
)
from app.reports.render import (
    ReportIssue,
    quoted,
    render_case_report_html,
    render_case_report_pdf,
)
from app.reports.schemas import CaseReportContent, ReportQuoteContext
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseFollowupExchange,
    CaseNearPassage,
    CaseQuoteDifference,
    CaseReviewFlag,
    CaseSourceCitation,
    CaseUnverifiedCitation,
)
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseSummaryUnit,
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


QUOTED_SOURCE = (
    "The victim called the bank. The caller said the account had been frozen. "
    "He asked for a transfer of 52,000 baht to a safe account."
)


def _input_quoting(text: str, quote: str) -> CaseReportInput:
    report_input = _input()
    source = replace(report_input.source_bundle.sources[0], text=text)
    bundle = CaseSourceBundle(revision=1, sources=(source,))
    trace = report_input.analysis_trace
    claim = trace.claims[0].model_copy(
        update={
            "supporting_citations": [
                CaseSourceCitation(source_id=source.source_id, exact_quote=quote)
            ]
        }
    )
    return report_input.model_copy(
        update={
            "source_bundle": bundle,
            "analysis_trace": resolve_case_trace(
                trace.model_copy(update={"claims": [claim]}), bundle
            ),
        }
    )


def test_a_quote_is_printed_inside_its_sentence() -> None:
    report_input = _input_quoting(QUOTED_SOURCE, "a transfer of 52,000 baht")
    html = render_case_report_html(_stored(report_input), ISSUE)

    assert (
        "“The caller said the account had been frozen. He asked for "
        "<strong>a transfer of 52,000 baht</strong> to a safe account.”"
    ) in html
    assert html == render_case_report_html(build_case_report_content(report_input), ISSUE)


def test_the_stored_report_keeps_each_quote_as_the_trace_holds_it() -> None:
    [finding] = _stored(_input_quoting(QUOTED_SOURCE, "a transfer of 52,000 baht")).findings

    assert finding.supporting_quotes == ["a transfer of 52,000 baht"]
    assert finding.supporting_contexts == [
        ReportQuoteContext(
            before="The caller said the account had been frozen. He asked for ",
            after=" to a safe account.",
        )
    ]


SUPPORT_LINES = (
    "ไม่พบข้อความที่อ้างในเอกสาร",
    "ข้อความที่อ้างบางส่วนไม่พบในเอกสาร",
    "ไม่ได้เชื่อมกับข้อสังเกตใด",
)


def _input_with_support(*supports: str | None) -> CaseReportInput:
    report_input = _input()
    trace = report_input.analysis_trace
    party, event, impact = supports
    trace = trace.model_copy(
        update={
            "involved_parties": [
                trace.involved_parties[0].model_copy(update={"support": party}),
                trace.involved_parties[0].model_copy(update={"support": "bound"}),
            ],
            "timeline": [trace.timeline[0].model_copy(update={"support": event})],
            "impacts": [trace.impacts[0].model_copy(update={"support": impact})],
        }
    )
    return report_input.model_copy(update={"analysis_trace": trace})


def test_a_new_report_stores_the_support_of_each_party_event_and_impact() -> None:
    report = _stored(_input_with_support("mixed", "unbound", "no_claim"))

    assert [party.support for party in report.parties] == ["mixed", "bound"]
    assert [event.support for event in report.timeline] == ["unbound"]
    assert [impact.support for impact in report.impacts] == ["no_claim"]


def test_a_new_report_prints_a_plain_line_for_what_no_checked_quotation_supports() -> None:
    html = render_case_report_html(
        _stored(_input_with_support("mixed", "unbound", "no_claim")), ISSUE
    )

    for line in SUPPORT_LINES:
        assert html.count(line) == 1, line
    assert "badge" not in html.split("<main>")[1].split("</main>")[0]


def test_a_bound_item_is_printed_as_before() -> None:
    html = render_case_report_html(_stored(_input_with_support("bound", "bound", "bound")), ISSUE)

    for line in SUPPORT_LINES:
        assert line not in html


def test_a_report_stored_before_the_status_existed_validates_and_prints_no_status_line() -> None:
    written = _stored(_input_with_support("unbound", "unbound", "unbound")).model_dump(mode="json")
    for key in ("parties", "timeline", "impacts"):
        for row in written[key]:
            del row["support"]

    stored = CaseReportContent.model_validate(written)
    html = render_case_report_html(stored, ISSUE)

    assert [party.support for party in stored.parties] == [None, None]
    for line in SUPPORT_LINES:
        assert line not in html
    assert "บุคคลและหน่วยงานที่เกี่ยวข้อง" in html


def test_an_analysis_stored_before_the_status_existed_makes_a_report_with_none() -> None:
    report = build_case_report_content(_input())

    assert [party.support for party in report.parties] == [None]
    assert [event.support for event in report.timeline] == [None]
    assert [impact.support for impact in report.impacts] == [None]


TOLERATED_LINE = "พบในเอกสารเมื่อไม่นับรูปแบบ"


def _input_with_tolerated(
    supporting: list[tuple[str, str]], contradicting: list[tuple[str, str]] | None = None
) -> CaseReportInput:
    report_input = _input()
    trace = report_input.analysis_trace
    claim = trace.claims[0]
    cited = claim.supporting_citations[0]

    def with_differences(pairs: list[tuple[str, str]]) -> CaseSourceCitation:
        return cited.model_copy(
            update={
                "tolerated_differences": [
                    CaseQuoteDifference(written=written, source=source) for written, source in pairs
                ]
            }
        )

    claim = claim.model_copy(
        update={
            "supporting_citations": [with_differences(supporting)],
            "contradicting_citations": (
                [with_differences(contradicting)] if contradicting is not None else []
            ),
        }
    )
    return report_input.model_copy(
        update={"analysis_trace": trace.model_copy(update={"claims": [claim]})}
    )


def test_a_new_report_stores_what_the_locator_tolerated_beside_each_quote() -> None:
    report = _stored(
        _input_with_tolerated([("apple", "Apple"), ("", "-")], [("resign", "re-sign")])
    )

    [finding] = report.findings
    assert [[(p.written, p.source) for p in places] for places in finding.supporting_tolerated] == [
        [("apple", "Apple"), ("", "-")]
    ]
    assert [
        [(p.written, p.source) for p in places] for places in finding.contradicting_tolerated
    ] == [[("resign", "re-sign")]]


def test_a_tolerated_quote_is_printed_with_a_plain_line_per_difference() -> None:
    html = render_case_report_html(
        _stored(_input_with_tolerated([("apple", "Apple"), ("", "-"), ("5,000", "")])), ISSUE
    )

    assert f"{TOLERATED_LINE} — ข้อความวิเคราะห์เขียน «apple» เอกสารเขียน «Apple»" in html
    assert f"{TOLERATED_LINE} — เอกสารมี «-» ที่ข้อความวิเคราะห์ตัดออก" in html
    assert f"{TOLERATED_LINE} — ข้อความวิเคราะห์เติม «5,000»" in html
    assert html.index("ข้อความจากหลักฐาน:") < html.index(TOLERATED_LINE)
    assert "badge" not in html.split("<main>")[1].split("</main>")[0]


def test_the_line_of_a_contradicting_quote_follows_that_quote() -> None:
    html = render_case_report_html(
        _stored(_input_with_tolerated([], [("resign", "re-sign")])), ISSUE
    )

    assert html.count(TOLERATED_LINE) == 1
    assert html.index("ข้อความที่ขัดแย้ง:") < html.index(TOLERATED_LINE)


def test_a_quote_the_locator_tolerated_nothing_in_prints_no_line() -> None:
    html = render_case_report_html(_stored(_input()), ISSUE)

    assert TOLERATED_LINE not in html


def test_a_report_stored_before_tolerated_differences_validates_and_prints_no_line() -> None:
    written = _stored(_input_with_tolerated([("apple", "Apple")])).model_dump(mode="json")
    for finding in written["findings"]:
        del finding["supporting_tolerated"], finding["contradicting_tolerated"]

    stored = CaseReportContent.model_validate(written)
    html = render_case_report_html(stored, ISSUE)

    assert stored.findings[0].supporting_tolerated == []
    assert TOLERATED_LINE not in html
    assert "ข้อความจากหลักฐาน:" in html


def test_a_report_stored_before_quote_contexts_still_prints() -> None:
    written = _stored(_input_quoting(QUOTED_SOURCE, "a transfer of 52,000 baht")).model_dump(
        mode="json"
    )
    for finding in written["findings"]:
        del finding["supporting_contexts"], finding["contradicting_contexts"]
        del finding["unverified_quotes"]

    html = render_case_report_html(CaseReportContent.model_validate(written), ISSUE)

    assert "“a transfer of 52,000 baht”" in html
    assert "<strong>a transfer" not in html


def _input_with_unverified(*items: CaseUnverifiedCitation) -> CaseReportInput:
    report_input = _input()
    trace = report_input.analysis_trace
    claim = trace.claims[0].model_copy(update={"unverified_citations": list(items)})
    return report_input.model_copy(
        update={"analysis_trace": trace.model_copy(update={"claims": [claim]})}
    )


def test_an_unverified_quote_is_printed_with_each_place_the_source_differs() -> None:
    source_id = _input().source_bundle.sources[0].source_id
    near = CaseNearPassage(
        source_text="พบการใช้ PowerShell.exe เชื่อมต่อไปยัง 198.51.100.23",
        differences=[
            CaseQuoteDifference(written="198.51.100.24", source="198.51.100.23"),
            CaseQuoteDifference(written="ทันที", source=""),
            CaseQuoteDifference(written="", source="PowerShell.exe"),
        ],
    )
    written = "พบการใช้ เชื่อมต่อไปยัง 198.51.100.24 ทันที"
    html = render_case_report_html(
        _stored(
            _input_with_unverified(
                CaseUnverifiedCitation(
                    source_id=source_id,
                    role="supporting",
                    written_quote=written,
                    near_passage=near,
                )
            )
        ),
        ISSUE,
    )

    assert f"ไม่พบข้อความนี้แบบตรงตัวในต้นฉบับ:</span> “{written}”" in html
    assert "ผลวิเคราะห์ยกมาว่า «198.51.100.24» ต้นฉบับเขียน «198.51.100.23»" in html
    assert "ผลวิเคราะห์เติม «ทันที»" in html
    assert "ต้นฉบับมี «PowerShell.exe» ที่ผลวิเคราะห์ตัดออก" in html


def test_an_unverified_quote_with_no_near_passage_prints_only_that_it_was_not_found() -> None:
    source_id = _input().source_bundle.sources[0].source_id
    report = _stored(
        _input_with_unverified(
            CaseUnverifiedCitation(
                source_id=source_id, role="supporting", written_quote="ข้อความที่ไม่มีในต้นฉบับ"
            )
        )
    )
    html = render_case_report_html(report, ISSUE)

    assert report.findings[0].unverified_quotes[0].places == []
    assert "ไม่พบข้อความนี้แบบตรงตัวในต้นฉบับ" in html
    assert "ผลวิเคราะห์ยกมาว่า" not in html
    assert "ผลวิเคราะห์เติม" not in html


def test_a_quote_that_is_its_whole_sentence_is_printed_plain() -> None:
    report = _stored(_input_quoting(SOURCE_TEXT, SOURCE_TEXT))
    html = render_case_report_html(report, ISSUE)

    assert report.findings[0].supporting_contexts == [ReportQuoteContext()]
    assert f"“{SOURCE_TEXT}”" in html
    assert "<strong>พบการใช้" not in html


def test_a_trimmed_ocr_context_is_marked_and_reads_as_plain_text() -> None:
    [quote] = quoted(
        ["123-4-56789"],
        [
            ReportQuoteContext(
                before="<tr><td>3 มีนาคม 2569</td><td>",
                after="</td><td>52,000 บาท</td></tr><page_number>2</page_number>",
                cut_before=True,
                cut_after=True,
            )
        ],
    )

    assert quote == "“… 3 มีนาคม 2569 <strong>123-4-56789</strong> 52,000 บาท …”"


def test_a_quote_context_is_escaped() -> None:
    [quote] = quoted(
        ["the link"],
        [ReportQuoteContext(before='<script>alert("x")</script> Click ', after=" now.")],
    )

    assert "&lt;script&gt;" in quote
    assert "<script>" not in quote


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


def test_a_gap_named_by_its_checklist_key_reads_as_words() -> None:
    report_input = _input()
    trace = report_input.analysis_trace
    gap = trace.gaps[0].model_copy(update={"gap_key": "how_much", "topic": "how_much"})
    report = build_case_report_content(
        report_input.model_copy(update={"analysis_trace": trace.model_copy(update={"gaps": [gap]})})
    )

    [row] = report.gaps
    assert row.topic == "ขอบเขตความเสียหาย"
    assert report.recommendations[0].startswith("ตรวจสอบเพิ่มเติมในประเด็น ขอบเขตความเสียหาย")
    assert "how_much" not in report.model_dump_json()


def test_every_checklist_key_has_a_report_topic() -> None:
    assert set(CHECKLIST_TOPICS) == set(CASE_CHECKLIST)


SUMMARY_UNITS = (
    ("พบการใช้ PowerShell", ["A-01"], "bound"),
    ("มีการเชื่อมต่อออกภายนอก", ["A-01", "A-02"], "mixed"),
    ("ผู้สั่งงานคือบุคคลภายใน", [], "no_claim"),
    ("มีการลบข้อมูลสำรอง", ["A-03"], "unbound"),
)


def _input_with_summary_units() -> CaseReportInput:
    report_input = _input()
    trace = report_input.analysis_trace
    first = trace.claims[0]
    second = first.model_copy(update={"claim_id": "A-02", "text": "มีการเชื่อมต่อออกภายนอก"})
    third = first.model_copy(
        update={
            "claim_id": "A-03",
            "text": "มีการลบข้อมูลสำรอง",
            "epistemic_status": "not_confirmed",
            "supporting_citations": [],
        }
    )
    trace = trace.model_copy(
        update={
            "claims": [first, second, third],
            "summary": "สรุป [A-01]",
            "summary_units": [
                CaseSummaryUnit(text=text, claim_ids=claim_ids, support=support)
                for text, claim_ids, support in SUMMARY_UNITS
            ],
        }
    )
    return report_input.model_copy(
        update={"analysis_trace": trace, "analysis_summary": "สรุป [A-01]"}
    )


def test_a_new_report_stores_each_summary_unit_with_the_finding_numbers_it_rests_on() -> None:
    report = _stored(_input_with_summary_units())

    assert [(unit.text, unit.references, unit.support) for unit in report.summary_units] == [
        ("พบการใช้ PowerShell", [1], "bound"),
        ("มีการเชื่อมต่อออกภายนอก", [1, 2], "mixed"),
        ("ผู้สั่งงานคือบุคคลภายใน", [], "no_claim"),
        ("มีการลบข้อมูลสำรอง", [3], "unbound"),
    ]
    assert report.summary == "สรุป [A-01]"
    assert "A-0" not in report.model_dump_json().replace("A-01]", "")


def test_a_new_report_prints_the_summary_by_unit_with_the_finding_numbers() -> None:
    html = render_case_report_html(_stored(_input_with_summary_units()), ISSUE)
    summary = html.split('id="case_summary"')[1].split("</h3>")[1].split("<h3>")[0]

    assert summary.count('class="body unit"') == 4
    assert "พบการใช้ PowerShell [ข้อ 1]</p>" in summary
    assert "มีการเชื่อมต่อออกภายนอก [ข้อ 1, 2]</p>" in summary
    assert "ผู้สั่งงานคือบุคคลภายใน</p>" in summary
    assert "มีการลบข้อมูลสำรอง [ข้อ 3]</p>" in summary
    assert "[A-0" not in html


def test_a_summary_unit_is_followed_by_a_plain_line_unless_its_claims_are_all_checked() -> None:
    html = render_case_report_html(_stored(_input_with_summary_units()), ISSUE)
    summary = html.split('id="case_summary"')[1].split("</h3>")[1].split("<h3>")[0]

    assert summary.count("ข้อความที่อ้างบางส่วนไม่พบในเอกสาร") == 1
    assert summary.count("ไม่ได้เชื่อมกับข้อสังเกตใด") == 1
    assert summary.count("ไม่พบข้อความที่อ้างในเอกสาร") == 1
    after_bound_unit = summary.split("พบการใช้ PowerShell [ข้อ 1]</p>")[1]
    assert "unit-note" not in after_bound_unit.split('class="body unit"')[0]
    assert "badge" not in summary


def test_a_summary_unit_is_escaped_in_the_report() -> None:
    report_input = _input_with_summary_units()
    trace = report_input.analysis_trace.model_copy(
        update={
            "summary_units": [
                CaseSummaryUnit(text="<script>alert(1)</script> **bold**", support="no_claim")
            ]
        }
    )
    report = _stored(report_input.model_copy(update={"analysis_trace": trace}))

    html = render_case_report_html(report, ISSUE)

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt; bold" in html


def test_a_report_stored_before_the_units_existed_prints_its_summary_as_before() -> None:
    written = _stored(_input_with_summary_units()).model_dump(mode="json")
    del written["summary_units"]

    stored = CaseReportContent.model_validate(written)
    html = render_case_report_html(stored, ISSUE)

    assert stored.summary_units == []
    assert 'class="body unit"' not in html
    assert "สรุป [A-01]" in html


def test_an_analysis_stored_before_the_units_existed_makes_a_report_with_none() -> None:
    assert build_case_report_content(_input()).summary_units == []


EDGE_LINE = "ตรวจ: ต้นฉบับมีเครื่องหมาย"
IGNORED_LINE = "ตรวจ: ต้นฉบับกับ quote ต่างกันที่เครื่องหมาย"


def _input_with_flags(
    supporting: list[str], contradicting: list[str] | None = None
) -> CaseReportInput:
    report_input = _input()
    trace = report_input.analysis_trace
    claim = trace.claims[0]
    cited = claim.supporting_citations[0]

    def with_flags(details: list[str]) -> CaseSourceCitation:
        return cited.model_copy(
            update={
                "review_flags": [
                    CaseReviewFlag(kind="meaning_mark", verdict="rule_warning", detail=detail)
                    for detail in details
                ]
            }
        )

    claim = claim.model_copy(
        update={
            "supporting_citations": [with_flags(supporting)],
            "contradicting_citations": (
                [with_flags(contradicting)] if contradicting is not None else []
            ),
        }
    )
    return report_input.model_copy(
        update={"analysis_trace": trace.model_copy(update={"claims": [claim]})}
    )


def test_a_new_report_stores_the_marks_to_review_beside_each_quote() -> None:
    report = _stored(_input_with_flags(["? edge", "~ % ignored"], ["< ignored"]))

    [finding] = report.findings
    assert [[(m.marks, m.place) for m in marks] for marks in finding.supporting_marked] == [
        [("?", "edge"), ("~ %", "ignored")]
    ]
    assert [[(m.marks, m.place) for m in marks] for marks in finding.contradicting_marked] == [
        [("<", "ignored")]
    ]


def test_a_flagged_quote_is_printed_with_a_plain_line_for_each_reason() -> None:
    html = render_case_report_html(_stored(_input_with_flags(["? edge", "~ % ignored"])), ISSUE)

    assert f"{EDGE_LINE} ? ที่ quote ไม่ได้รวมไว้" in html
    assert f"{IGNORED_LINE} ~ % ซึ่งอาจเปลี่ยนความหมาย" in html
    assert html.index("ข้อความจากหลักฐาน:") < html.index(EDGE_LINE) < html.index(IGNORED_LINE)
    assert "badge" not in html.split("<main>")[1].split("</main>")[0]


def test_the_line_of_a_contradicting_quote_follows_that_quote_too() -> None:
    html = render_case_report_html(_stored(_input_with_flags([], ["% edge"])), ISSUE)

    assert html.count(EDGE_LINE) == 1
    assert html.index("ข้อความที่ขัดแย้ง:") < html.index(EDGE_LINE)


def test_a_quote_with_no_flag_prints_no_review_line() -> None:
    html = render_case_report_html(_stored(_input()), ISSUE)

    assert EDGE_LINE not in html
    assert IGNORED_LINE not in html


def test_a_flag_does_not_change_the_status_or_the_sources_of_a_finding() -> None:
    flagged = _stored(_input_with_flags(["? edge"])).findings[0]
    plain = _stored(_input()).findings[0]

    assert flagged.status == plain.status
    assert flagged.source_labels == plain.source_labels
    assert flagged.supporting_quotes == plain.supporting_quotes


def test_a_report_stored_before_the_flags_validates_and_prints_no_line() -> None:
    written = _stored(_input_with_flags(["? edge"])).model_dump(mode="json")
    for finding in written["findings"]:
        del finding["supporting_marked"], finding["contradicting_marked"]

    stored = CaseReportContent.model_validate(written)
    html = render_case_report_html(stored, ISSUE)

    assert stored.findings[0].supporting_marked == []
    assert EDGE_LINE not in html
    assert "ข้อความจากหลักฐาน:" in html


def test_an_analysis_stored_before_the_flags_existed_makes_a_report_with_none() -> None:
    [finding] = build_case_report_content(_input()).findings

    assert finding.supporting_marked == [[]]
    assert finding.contradicting_marked == []
