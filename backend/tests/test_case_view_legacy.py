from app.trace.claims import CaseClaimGrounding
from app.trace.messages import MessageAnalysisTrace
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseInvolvedParty,
    CaseTimelineItem,
    CaseViewExtraction,
)


def test_saved_extraction_metadata_reads_without_the_retired_extractor_fields():
    saved = CaseViewExtraction.model_validate(
        {
            "method": "retired-local-extractor",
            "model": "historical/model",
            "revision": "c" * 40,
            "library_version": "historical-version",
            "device": "cpu",
            "threshold": 0.5,
            "quantization": "int8",
            "runtime_revision": "d" * 40,
            "field_resolution_issues": [],
            "input_claim_ids": ["A-01"],
            "excluded_claim_ids": [],
            "duration_ms": 120,
        }
    )
    assert saved.method == "retired-local-extractor"
    assert saved.status == "completed"
    assert saved.warning is None
    assert "library_version" not in saved.model_dump()
    assert CaseViewExtraction.model_validate_json(saved.model_dump_json()) == saved


def test_saved_view_rows_read_without_claim_spans_or_projection_verdicts():
    party = CaseInvolvedParty.model_validate(
        {
            "name": "John",
            "role": "Victim",
            "claim_ids": ["A-01"],
            "field_spans": {"name": {"claim_id": "A-01", "start": 0, "end": 4}},
            "projection_grounding": {"verdict": "supported", "reason": "entailed"},
        }
    )
    assert party.name == "John"
    assert "field_spans" not in party.model_dump()
    assert "projection_grounding" not in party.model_dump()
    event = CaseTimelineItem(time="12 May 2026", event="A transfer occurred.", claim_ids=["A-01"])
    assert event.time == "12 May 2026"


def test_a_saved_trace_reads_without_its_grounding_counters():
    saved = {
        "analysis_mode": "case_overview",
        "summary": "A transfer occurred [A-01].",
        "claims": [],
        "grounding": {"claims": 1, "evidence_ids_claimed": 2, "summary_ids_unknown": 0},
    }

    trace = CaseAnalysisTrace.model_validate(saved)
    message = MessageAnalysisTrace.model_validate(saved)

    assert "grounding" not in trace.model_dump()
    assert "grounding" not in message.model_dump()


def test_a_saved_verdict_reads_without_the_verifier_diagnostics():
    saved = CaseClaimGrounding.model_validate(
        {
            "verdict": "supported",
            "reason": "lr_supported",
            "method": "b1-lr-wice-train-v1",
            "artifact_sha256": "a" * 64,
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
    )

    assert saved.model_dump() == {
        "verdict": "supported",
        "reason": "lr_supported",
        "method": "b1-lr-wice-train-v1",
        "artifact_sha256": "a" * 64,
    }
