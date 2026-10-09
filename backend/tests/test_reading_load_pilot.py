import json

import pytest

from app.llm.settings import AnalysisPipelineConfig
from app.trace.trace import CaseProviderReadingReply

pilot = pytest.importorskip("experiments.reading_load_pilot")


@pytest.mark.parametrize("case", json.loads(pilot.FIXTURES.read_bytes())["cases"])
def test_manual_gold_sources_and_compact_payload_preserve_the_fixture(case):
    config = AnalysisPipelineConfig(model="test/model")
    bundle, history, sources, content, sizes = pilot.prepare(case, config)
    all_source_ids = {item["source_id"] for item in content["case_sources"]}
    assert len(case["expected_facts"]) == 11
    assert all(set(fact["source_ids"]) <= all_source_ids for fact in case["expected_facts"])
    assert len({fact["fact_id"] for fact in case["expected_facts"]}) == 11
    for item, source in zip(
        content["case_sources"],
        (*bundle.sources, *pilot.followup_registry_items(history)),
        strict=True,
    ):
        assert "".join(unit["text"] for unit in item["evidence_units"]) == source.text
    assert (
        sizes["compact_addressing_estimated_tokens"] < sizes["legacy_addressing_estimated_tokens"]
    )
    assert sizes["compact_message_chars"] < sizes["legacy_message_chars"]


async def test_matched_conditions_use_identical_reading_content_and_canonical_binding(
    monkeypatch, tmp_path
):
    case = json.loads(pilot.FIXTURES.read_bytes())["cases"][0]
    config = AnalysisPipelineConfig(model="test/model")
    prepared = pilot.prepare(case, config)
    seen = []

    async def request_stage(**kwargs):
        seen.append(kwargs)
        return CaseProviderReadingReply.model_validate(
            {
                "version": "case_analysis_trace_v1",
                "claims": [
                    {
                        "claim_id": "A-01",
                        "claim_type": "reported",
                        "epistemic_status": "reported",
                        "text": "Jane Smith reported receiving an email from John on 12 May 2026.",
                        "supporting_citations": [
                            {
                                "source_id": case["sources"][0]["source_id"],
                                "evidence_unit_ids": ["U001"],
                            }
                        ],
                    }
                ],
            }
        )

    monkeypatch.setattr(pilot.provider, "request_stage", request_stage)
    for thinking in (8192, 0):
        selected = AnalysisPipelineConfig.model_validate(
            {**config.model_dump(), "thinking_tokens": thinking}
        )
        result = await pilot.run_condition(
            case, selected, prepared, tmp_path / f"thinking-{thinking}"
        )
        assert result["grounding"]["evidence_ids_resolved"] == 1
        assert result["status"] == "completed"
    assert seen[0]["content"] == seen[1]["content"]
    assert seen[0]["system"] == seen[1]["system"]
    assert all(item["stage"] == "case_reading" and "grammar" not in item for item in seen)
    assert all(item["config"].output_tokens == 32608 for item in seen)
