import copy
import importlib.util
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from app.analysis.technical_context.contracts import (
    CaseTechnicalAugmentation,
    skipped_mitre_applicability,
)
from app.reports.schemas import (
    CaseReportContent,
    ReportEvent,
    ReportFinding,
    ReportImpact,
    ReportParty,
    ReportSource,
    ReportUnverifiedQuote,
)
from app.trace.citations import CaseSourceCitation, CaseUnverifiedCitation
from app.trace.claims import CaseAnalysisClaim, CaseClaimGrounding
from app.trace.messages import (
    ChatAnswerUnit,
    MessageMetadata,
    message_trace,
    serialize_message_metadata,
)
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseTimelineItem,
    CaseViewExtraction,
)

MIGRATION = (
    Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0003_strip_retired_fields.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location("strip_retired_fields", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


migration = load_migration()

QUOTE = "John sent an email."

VERDICT_DIAGNOSTICS = {
    "model": "historical/model",
    "label": "entailment",
    "entailment": 0.9,
    "threshold": 0.5,
    "neutral": 0.08,
    "contradiction": 0.02,
    "p_supported": 0.8,
    "selected_citation_indices": [0],
    "considered_citation_indices": [0],
    "selected_evidence_unit_ids": ["S1:U001-0000000000000000"],
    "source_similarities": [0.7],
    "selector_threshold": 0.2,
    "selection_ms": 1.5,
    "raw_tokens": 20,
    "truncated": False,
    "duration_ms": 4.0,
}

EXTRACTOR_SETTINGS = {
    "revision": "c" * 40,
    "library_version": "historical-version",
    "device": "cpu",
    "threshold": 0.5,
    "quantization": "int8",
    "runtime_revision": "d" * 40,
    "field_resolution_issues": [],
}


def citation() -> CaseSourceCitation:
    return CaseSourceCitation(
        source_id="S1",
        exact_quote=QUOTE,
        evidence_unit_ids=["S1:U001-0000000000000000"],
        pointer_state="direct",
        start=0,
        end=len(QUOTE),
    )


def claim() -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text=QUOTE,
        epistemic_status="reported",
        supporting_source_ids=["S1"],
        supporting_citations=[citation()],
        unverified_citations=[CaseUnverifiedCitation(source_id="S1", role="supporting")],
        semantic_grounding=CaseClaimGrounding(
            verdict="supported",
            reason="lr_supported",
            method="b1-lr-wice-train-v1",
            artifact_sha256="a" * 64,
        ),
    )


def trace() -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="John sent an email [A-01].",
        claims=[claim()],
        involved_parties=[CaseInvolvedParty(name="John", role="Sender", claim_ids=["A-01"])],
        timeline=[CaseTimelineItem(event="An email was sent.", claim_ids=["A-01"])],
        impacts=[CaseImpactItem(description="The mailbox was exposed.", claim_ids=["A-01"])],
        view_extraction=CaseViewExtraction(
            method="llm-views",
            model="google/gemma-4-26b-a4b-it",
            input_claim_ids=["A-01"],
            excluded_claim_ids=[],
            duration_ms=120.0,
        ),
    )


def with_retired_claim(stored: dict) -> None:
    stored["reasoning_summary"] = "Written by an earlier reader."
    stored["semantic_grounding"].update(VERDICT_DIAGNOSTICS)
    stored["supporting_citations"][0]["tolerated_differences"] = [
        {"written": "john", "source": "John"}
    ]
    stored["supporting_citations"][0]["review_flags"] = [{"kind": "meaning_mark"}]
    stored["unverified_citations"][0].update(
        {"written_quote": "A quote.", "near_passage": None, "meaning_passage": None}
    )


def test_the_migration_strips_an_analysis_trace_back_to_what_the_analysis_writes_now():
    current = trace().model_dump(mode="json")
    stored = copy.deepcopy(current)
    stored["grounding"] = {"claims": 1, "evidence_ids_claimed": 1}
    with_retired_claim(stored["claims"][0])
    for name in ("involved_parties", "timeline", "impacts"):
        stored[name][0]["projection_grounding"] = {"verdict": "supported", "reason": "entailed"}
        stored[name][0]["field_spans"] = {}
    stored["view_extraction"].update(EXTRACTOR_SETTINGS)

    with pytest.raises(ValidationError):
        CaseAnalysisTrace.model_validate(stored)

    migration.strip_trace(stored)

    assert stored == current
    assert stored["view_extraction"]["model"] == "google/gemma-4-26b-a4b-it"
    assert stored["view_extraction"]["duration_ms"] == 120.0
    assert CaseAnalysisTrace.model_validate(stored) == trace()


def test_the_migration_strips_the_shadow_decision_from_the_technical_context():
    augmentation = CaseTechnicalAugmentation(
        status="not_applicable", applicability=skipped_mitre_applicability()
    ).model_dump(mode="json")
    current = {"technical_augmentation": augmentation, "sources_read": {"source_ids": ["S1"]}}
    stored = copy.deepcopy(current)
    stored["technical_augmentation"]["shadow_applicability"] = augmentation["applicability"]

    with pytest.raises(ValidationError):
        CaseTechnicalAugmentation.model_validate(stored["technical_augmentation"])

    migration.strip_external_context(stored)

    assert stored == current


def test_the_migration_strips_a_report_back_to_what_a_report_stores_now():
    current = CaseReportContent(
        title="An incident",
        summary="John sent an email.",
        parties=[ReportParty(name="John", role=None)],
        timeline=[ReportEvent(time=None, event="An email was sent.")],
        impacts=[ReportImpact(description="The mailbox was exposed.")],
        findings=[
            ReportFinding(
                ordinal=1,
                text=QUOTE,
                status="reported",
                is_inference=False,
                unverified_quotes=[ReportUnverifiedQuote()],
            )
        ],
        sources=[ReportSource(label="S1", kind="narrative", detail="Statement")],
    ).model_dump(mode="json")
    stored = copy.deepcopy(current)
    for name in ("parties", "timeline", "impacts"):
        stored[name][0]["projection_grounding"] = {"verdict": "supported"}
    [finding] = stored["findings"]
    finding.update(
        {
            "supporting_tolerated": [],
            "contradicting_tolerated": [],
            "supporting_marked": [],
            "contradicting_marked": [],
            "reasoning_summary": "Written by an earlier reader.",
        }
    )
    finding["unverified_quotes"][0].update(
        {"written_quote": "A quote.", "places": [], "meaning_passage": None}
    )

    with pytest.raises(ValidationError):
        CaseReportContent.model_validate(stored)

    migration.strip_report(stored)

    assert stored == current
    assert stored["sources"][0]["label"] == "S1"


def test_the_migration_strips_a_chat_message_back_to_what_chat_stores_now():
    current = serialize_message_metadata(
        {
            "analysis_trace": message_trace(trace()),
            "answer_units": [
                ChatAnswerUnit(
                    text=QUOTE,
                    basis="case_fact",
                    claim_ids=["A-01"],
                    supporting_source_ids=["S1"],
                    supporting_citations=[citation()],
                )
            ],
        }
    )
    stored = copy.deepcopy(current)
    stored["analysis_trace"]["grounding"] = {"claims": 1}
    with_retired_claim(stored["analysis_trace"]["claims"][0])
    stored["answer_units"][0]["supporting_citations"][0]["review_flags"] = []
    stored["answer_units"][0]["supporting_citations"][0]["tolerated_differences"] = []

    with pytest.raises(ValidationError):
        TypeAdapter(MessageMetadata).validate_python(stored)

    migration.strip_message(stored)

    assert stored == current


def test_a_record_without_retired_fields_is_left_as_it_is():
    current = trace().model_dump(mode="json")

    assert migration.stripped(current, migration.strip_trace) == current
    assert migration.stripped(None, migration.strip_trace) is None
    assert migration.stripped({}, migration.strip_message) == {}
