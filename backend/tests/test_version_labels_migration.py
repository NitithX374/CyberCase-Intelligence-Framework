import copy
import importlib.util
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.analysis.technical_context.contracts import (
    CaseTechnicalAugmentation,
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.reports.schemas import CaseReportContent, ReportFinding, ReportSource
from app.sources.bundle import (
    CaseSourceBundle,
    CaseSourceItem,
    SourcesRead,
    sources_read,
)
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAssessmentTrace,
    CaseFollowupExchange,
    FollowupSnapshot,
    followup_snapshot,
)
from app.trace.messages import message_trace, serialize_message_metadata
from app.trace.trace import CaseAnalysisTrace

MIGRATION = (
    Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0004_strip_version_labels.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location("strip_version_labels", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


migration = load_migration()

QUOTE = "John sent an email."


def trace() -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="John sent an email [A-01].",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text=QUOTE,
                epistemic_status="reported",
                supporting_source_ids=["S1"],
            )
        ],
    )


def gap() -> CaseAnalysisGap:
    return CaseAnalysisGap(
        gap_id="G-01",
        gap_key="when",
        topic="Incident time",
        status="NOT_PROVIDED",
        description="The incident time is missing.",
        reason="Timing fixes the chronology.",
        priority="high",
        askable=True,
        clarification_question="When did the incident happen?",
    )


def external_context() -> dict:
    bundle = CaseSourceBundle(revision=1, sources=(CaseSourceItem("S1", "narrative", QUOTE),))
    history = (CaseFollowupExchange("QA-01", "when", "When?", "On Monday."),)
    applicability = MitreApplicabilityRecord(
        decision="RETRIEVE", source_message_ids=["S1"], trigger_text=["sent an email"]
    )
    return {
        "legal_relevance": {"provisions": [], "provider": "", "query_sent": ""},
        "technical_augmentation": CaseTechnicalAugmentation(
            status="retrieved_from_rag", applicability=applicability
        ).model_dump(mode="json"),
        "sources_read": sources_read(bundle),
        "followup_history": followup_snapshot(history),
    }


def test_the_migration_strips_an_analysis_trace_back_to_what_the_analysis_writes_now():
    current = trace().model_dump(mode="json")
    stored = {"version": "case_analysis_trace_v1", "validation_status": "validated", **current}

    with pytest.raises(ValidationError):
        CaseAnalysisTrace.model_validate(stored)

    migration.strip_trace(stored)

    assert stored == current
    assert CaseAnalysisTrace.model_validate(stored) == trace()


def test_the_migration_strips_an_assessment_back_to_what_the_assessment_writes_now():
    current = CaseAssessmentTrace(gaps=[gap()]).model_dump(mode="json")
    stored = {"version": "case_assessment_v1", **current}

    with pytest.raises(ValidationError):
        CaseAssessmentTrace.model_validate(stored)

    migration.strip_trace(stored)

    assert stored == current


def test_the_migration_strips_the_labels_of_the_records_an_analysis_keeps_beside_its_trace():
    current = external_context()
    stored = copy.deepcopy(current)
    stored["technical_augmentation"]["version"] = "case_mitre_augmentation_v1"
    stored["technical_augmentation"]["applicability"]["version"] = "mitre_applicability_v1"
    stored["sources_read"]["version"] = "sources_read_v1"
    stored["followup_history"]["version"] = "followup_snapshot_v1"

    for model, name in (
        (CaseTechnicalAugmentation, "technical_augmentation"),
        (SourcesRead, "sources_read"),
        (FollowupSnapshot, "followup_history"),
    ):
        with pytest.raises(ValidationError):
            model.model_validate(stored[name])

    migration.strip_external_context(stored)

    assert stored == current


def test_the_migration_leaves_a_follow_up_history_that_is_not_a_record_alone():
    augmentation = CaseTechnicalAugmentation(
        status="not_applicable", applicability=skipped_mitre_applicability()
    ).model_dump(mode="json")
    stored = {"technical_augmentation": augmentation, "followup_history": [{"version": "kept"}]}

    migration.strip_external_context(stored)

    assert stored == {
        "technical_augmentation": augmentation,
        "followup_history": [{"version": "kept"}],
    }


def test_the_migration_strips_a_report_back_to_what_a_report_stores_now():
    current = CaseReportContent(
        title="An incident",
        summary="John sent an email.",
        views_derived_from_claims=False,
        summary_units=[],
        findings=[
            ReportFinding(
                ordinal=1,
                text=QUOTE,
                status="reported",
                supporting_contexts=[],
                contradicting_contexts=[],
                unverified_quotes=[],
            )
        ],
        sources=[ReportSource(label="S1", kind="narrative", detail="Statement")],
    ).model_dump(mode="json")
    stored = {"version": "case_report_content_v1", **current}

    with pytest.raises(ValidationError):
        CaseReportContent.model_validate(stored)

    migration.strip_report(stored)

    assert stored == current


def test_the_migration_strips_a_chat_message_back_to_what_chat_stores_now():
    current = serialize_message_metadata({"analysis_trace": message_trace(trace())})
    stored = copy.deepcopy(current)
    stored["analysis_trace"].update(
        {"version": "case_analysis_trace_v1", "validation_status": "validated"}
    )

    assert serialize_message_metadata(stored) == current

    migration.strip_message(stored)

    assert stored == current


def test_a_record_without_labels_is_left_as_it_is():
    current = trace().model_dump(mode="json")

    assert migration.stripped(current, migration.strip_trace) == current
    assert migration.stripped(None, migration.strip_trace) is None
    assert migration.stripped({}, migration.strip_external_context) == {}
    assert migration.stripped({}, migration.strip_message) == {}
