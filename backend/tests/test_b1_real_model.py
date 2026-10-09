from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

import pytest

from app.analysis import write
from app.analysis.views import DerivedCaseViews
from app.config import settings
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace import claim_validation
from app.trace.b1_verifier import ARTIFACT_SHA256, load_verifier
from app.trace.bind import bound_references
from app.trace.claims import CaseFollowupExchange
from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply, CaseViewExtraction

pytestmark = pytest.mark.skipif(
    os.getenv("B1_REAL_MODEL") != "1", reason="Explicit pinned-model integration run required"
)
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def verifier(monkeypatch):
    monkeypatch.setattr(settings, "claim_nli_path", str(ROOT / "backend/nli_mdeberta"))
    monkeypatch.setattr(
        settings, "claim_selector_path", str(ROOT / "backend/source_selector_mpnet")
    )
    return load_verifier()


@pytest.mark.asyncio
async def test_real_en_th_cross_document_and_qa_gate_completes_native_pipeline(
    monkeypatch, verifier
):
    first_text = "\n".join(
        ["John sent an email.", "Jane made a transfer.", "The weather was warm."]
    )
    second_text = "The transfer was 25,000 baht."
    sources = CaseSourceBundle(
        3,
        (
            CaseSourceItem(
                "S1",
                "document",
                first_text,
                "D1",
                "statement.pdf",
                {
                    "extraction_method": "ocr",
                    "verification_status": "unverified",
                    "warnings": ["OCR text"],
                    "pages": [{"page_number": 1, "start_offset": 0, "end_offset": len(first_text)}],
                },
            ),
            CaseSourceItem(
                "S2",
                "document",
                second_text,
                "D2",
                "transfer.pdf",
                {"pages": [{"page_number": 2, "start_offset": 0, "end_offset": len(second_text)}]},
            ),
        ),
    )
    history = (
        CaseFollowupExchange(
            qa_id="QA-03",
            gap_key="amount",
            question="จำนวนเงินเท่าไร",
            answer="ผู้เสียหายโอนเงินจำนวน 25,000 บาท",
        ),
    )
    cases = (
        ("A-01", "John sent an email.", [("S1", ["U001"])]),
        ("A-02", "John is the attacker.", [("S1", ["U001"])]),
        ("A-03", history[0].answer, [("QA-03", ["U001"])]),
        ("A-04", "ผู้เสียหายโอนเงินจำนวน 250,000 บาท", [("QA-03", ["U001"])]),
        ("A-05", "Jane transferred 25,000 baht.", [("S1", ["U002", "U003"]), ("S2", ["U001"])]),
    )
    reply = CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": claim_id,
                    "claim_type": "reported",
                    "text": text,
                    "epistemic_status": "reported",
                    "supporting_citations": [
                        {"source_id": source, "evidence_unit_ids": ids}
                        for source, ids in references
                    ],
                }
                for claim_id, text, references in cases
            ],
        }
    )
    calls, views_input = [], []

    async def request(**kwargs):
        calls.append(kwargs)
        if kwargs["stage"] == "case_reading":
            return reply
        return CaseProviderJudgement(
            version="case_analysis_trace_v1",
            summary="\n".join(
                f"{claim['text']} [{claim['claim_id']}]."
                for claim in kwargs["content"]["reading"]["claims"]
            ),
        )

    async def views(claims, *, config):
        views_input.extend(claim.claim_id for claim in claims)
        return DerivedCaseViews(
            [],
            [],
            [],
            CaseViewExtraction(
                method="llm",
                model="mock",
                duration_ms=0,
                input_claim_ids=views_input,
                excluded_claim_ids=[],
            ),
        )

    monkeypatch.setattr(claim_validation, "load_scorer", lambda: verifier)
    monkeypatch.setattr(write, "request_stage", request)
    monkeypatch.setattr(write, "derive_claim_views", views)
    trace = await write.write_trace(
        sources=sources, language="th", followup_history=history, config=AnalysisPipelineConfig()
    )
    assert [claim.semantic_grounding.verdict for claim in trace.claims] == [
        "supported",
        "not_supported",
        "supported",
        "not_supported",
        "supported",
    ]
    assert views_input == ["A-01", "A-02", "A-03", "A-04", "A-05"]
    assert [claim["claim_id"] for claim in calls[1]["content"]["reading"]["claims"]] == views_input
    assert "semantic_grounding" not in json.dumps(calls[1]["content"])
    assert "answer" not in calls[1]["content"]["followup_history"][0]
    assert trace.grounding.claims_admitted_to_judgement == 5
    assert trace.grounding.evidence_ids_claimed == trace.grounding.evidence_ids_resolved == 7
    assert trace.claims[-1].semantic_grounding.selected_citation_indices == [0, 2]
    assert trace.claims[-1].supporting_citations[-1].page_numbers == [2]
    registry = {source.source_id: source for source in sources.sources}
    registry["QA-03"] = CaseSourceItem("QA-03", "followup_answer", history[0].answer)
    for claim in trace.claims:
        for citation in claim.supporting_citations:
            source = registry[citation.source_id]
            assert citation.exact_quote == source.text[citation.start : citation.end]
            assert citation.pointer_state == "direct"
    bound = bound_references(trace)
    assert all(unit.support == "bound" for unit in bound.summary_units)
    output = ROOT / "tmp/b1-production"
    output.mkdir(parents=True, exist_ok=True)
    (output / "pipeline-smoke.json").write_text(
        json.dumps(
            {
                "artifact_sha256": ARTIFACT_SHA256,
                "nli_dtype": str(next(verifier.nli.model.parameters()).dtype),
                "device": str(next(verifier.nli.model.parameters()).device),
                "reader_and_judgement": "Mocked; real binding/selection/NLI/LR/admission/join/reference resolution",
                "trace": bound.model_dump(mode="json"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def test_real_selector_and_forward_nli_match_original_research_method(verifier):
    import sys
    from types import SimpleNamespace

    import numpy as np

    sys.path.insert(0, str(ROOT / "nli_grounding_experiment"))
    from src.nli import NLIRunner
    from src.semantic_filter import SemanticFilter

    claim = "Jane transferred 25,000 baht."
    units = ["Jane made a transfer.", "The transfer was 25,000 baht.", "The weather was warm."]
    selector = object.__new__(SemanticFilter)
    selector.model = verifier.selector.model
    similarities = selector.compute_similarities(
        [SimpleNamespace(claim=claim, evidence_units=units)]
    )[0]
    kept, indices = selector.filter_units(units, similarities, 0.2)
    actual = verifier.verify(claim, units)
    assert tuple(indices) == actual.indices == (0, 1)
    assert np.allclose(similarities, actual.similarities, atol=1e-6)
    runner = object.__new__(NLIRunner)
    runner.model, runner.tokenizer = verifier.nli.model, verifier.nli.tokenizer
    runner.device = next(runner.model.parameters()).device
    runner.entail_idx, runner.neutral_idx, runner.contra_idx = 0, 1, 2
    probabilities, metadata = runner.predict_probs(["\n".join(kept)], [claim], batch_size=1)
    assert np.allclose(probabilities[0], actual.nli.vector, atol=1e-6)
    assert metadata[0]["num_tokens"] == actual.nli.raw_tokens
    assert metadata[0]["truncated"] == actual.nli.truncated
    long_text = "The weather was warm. " * 200
    research_long, research_meta = runner.predict_probs([long_text], [claim], batch_size=1)
    current_long = verifier.nli.predict(long_text, claim)
    assert current_long.truncated and research_meta[0]["truncated"]
    assert np.allclose(research_long[0], current_long.vector, atol=1e-6)
    (ROOT / "tmp/b1-production/method-parity.json").write_text(
        json.dumps(
            {
                "selector_max_absolute_difference": float(
                    max(abs(a - b) for a, b in zip(similarities, actual.similarities, strict=True))
                ),
                "same_selected_indices": indices,
                "short_and_truncated_nli_match": True,
                "production": asdict(actual),
                "original_research_vector": probabilities[0].tolist(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
