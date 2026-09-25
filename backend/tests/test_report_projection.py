import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.rag import QueryResponse
from app.services.analysis.mitre_gate.llm import MitreApplicabilityRecord
from app.services.analysis.steps.technical_context import run_case_mitre_augmentation
from app.services.reports.contracts import ReportGenerationConflict
from app.services.reports.projection import build_case_report_input
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem

CASE_ID = uuid4()
TRACE = {
    "version": "case_analysis_trace_v1",
    "analysis_mode": "case_overview",
    "validation_status": "validated",
    "summary": "Payroll files were encrypted.",
    "claims": [],
    "gaps": [],
    "mitre_associations": [],
}
NO_ANSWERS = {"version": "followup_snapshot_v1", "items": []}


def narrative(created_at):
    return SimpleNamespace(
        id=str(uuid4()),
        source_kind="narrative",
        exact_text="Payroll files were encrypted overnight.",
        document_id=None,
        provenance_json={},
        created_at=created_at,
        source_metadata_json={},
        document=None,
        filename=None,
    )


def message(ordinal: int, content: str, *, gap_key=None, replies_to=None):
    return SimpleNamespace(
        id=uuid4(),
        ordinal=ordinal,
        content=content,
        gap_key=gap_key,
        in_reply_to_message_id=replies_to,
    )


def sources_read(*sources) -> dict:
    return {"version": "sources_read_v1", "source_ids": [source.id for source in sources]}


def case_and_analysis(record, *, chat_messages=()):
    written = datetime.now(UTC)
    read = narrative(written)
    case = SimpleNamespace(
        id=CASE_ID,
        title="Encrypted payroll",
        source_revision=1,
        sources=[read],
        chat_messages=list(chat_messages),
    )
    result = SimpleNamespace(
        id=uuid4(),
        case_id=CASE_ID,
        status="validated",
        source_revision=1,
        summary=TRACE["summary"],
        created_at=written + timedelta(minutes=5),
        trace_json=TRACE,
        external_context_json=record(read),
    )
    return case, result


def test_a_report_lists_only_the_answers_its_analysis_read():
    first_question = message(1, "Was a warrant issued?", gap_key="arrest_warrant")
    first_answer = message(2, "No.", replies_to=first_question.id)
    later_question = message(3, "Who owns the laptop?", gap_key="laptop_owner")
    later_answer = message(4, "The accounting team.", replies_to=later_question.id)
    case, result = case_and_analysis(
        lambda read: {
            "sources_read": sources_read(read),
            "followup_history": {
                "version": "followup_snapshot_v1",
                "items": [
                    {
                        "qa_id": "QA-01",
                        "gap_key": "arrest_warrant",
                        "question": "Was a warrant issued?",
                        "answer": "No.",
                    }
                ],
            },
        },
        chat_messages=[first_question, first_answer, later_question, later_answer],
    )

    report_input = build_case_report_input(case, result)

    assert [(item.qa_id, item.question, item.answer) for item in report_input.followup_history] == [
        ("QA-01", "Was a warrant issued?", "No.")
    ]


def test_an_analysis_that_read_no_answers_reports_none():
    case, result = case_and_analysis(
        lambda read: {"sources_read": sources_read(read), "followup_history": NO_ANSWERS}
    )

    report_input = build_case_report_input(case, result)

    assert report_input.followup_history == ()
    assert [source.source_id for source in report_input.source_bundle.sources] == [
        case.sources[0].id
    ]


def test_a_row_without_a_followup_snapshot_is_refused_not_read_from_the_chat():
    case, result = case_and_analysis(lambda read: {"sources_read": sources_read(read)})

    with pytest.raises(ReportGenerationConflict) as refused:
        build_case_report_input(case, result)

    assert refused.value.code == "analysis_followup_snapshot_missing"


def test_a_row_without_a_source_snapshot_is_refused_not_guessed_from_time():
    case, result = case_and_analysis(lambda read: {"followup_history": NO_ANSWERS})

    with pytest.raises(ReportGenerationConflict) as refused:
        build_case_report_input(case, result)

    assert refused.value.code == "analysis_source_snapshot_missing"


def test_a_recorded_source_that_is_gone_is_refused():
    case, result = case_and_analysis(
        lambda read: {
            "sources_read": {"version": "sources_read_v1", "source_ids": [str(uuid4())]},
            "followup_history": NO_ANSWERS,
        }
    )

    with pytest.raises(ReportGenerationConflict) as refused:
        build_case_report_input(case, result)

    assert refused.value.code == "analysis_source_snapshot_invalid"


def insufficient_augmentation(read, retrieval_context_id):
    async def gate(**_kwargs):
        return MitreApplicabilityRecord(
            decision="RETRIEVE",
            source_message_ids=[read.id],
            trigger_text=["Payroll files were encrypted"],
        )

    async def rag(_query):
        return QueryResponse(
            status="completed",
            retrieval_context_id=retrieval_context_id,
            context="",
            mitre_table=[],
            legal_reference={},
        )

    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=read.id, source_kind="narrative", text=read.exact_text),),
    )
    return asyncio.run(
        run_case_mitre_augmentation(source_bundle=bundle, applicability_gate=gate, rag_request=rag)
    )


@pytest.mark.parametrize("retrieval_context_id", ["retrieval-thin", None])
def test_an_analysis_whose_retrieval_found_no_technique_still_reports(retrieval_context_id):
    outcomes = []

    def record(read):
        augmentation = insufficient_augmentation(read, retrieval_context_id)
        outcomes.append(augmentation)
        return {
            "sources_read": sources_read(read),
            "followup_history": NO_ANSWERS,
            "technical_augmentation": augmentation.to_metadata(),
        }

    case, result = case_and_analysis(record)

    report_input = build_case_report_input(case, result)

    assert outcomes[0].status == "insufficient_context"
    assert report_input.technical_augmentation.status == "insufficient_context"
    assert report_input.technical_augmentation.retrieval_context_id == retrieval_context_id
