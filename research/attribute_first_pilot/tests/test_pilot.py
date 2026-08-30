"""Unit tests for the Attribute-First Reasoning Pilot components."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from research.attribute_first_pilot.contracts import (
    AnswerabilityEnum,
    AttributeContract,
    BenchmarkSuite,
    ConditionEnum,
    EpistemicStateEnum,
    ItemRunResult,
    ModelCallUsage,
    PilotRunOutput,
    QuestionTypeEnum,
    SentenceEvidence,
    GenerationResult,
    AttributePredictionResult,
)
from research.attribute_first_pilot.evaluator import (
    calculate_evidence_metrics,
    calculate_macro_f1,
    evaluate_attributes,
    evaluate_efficiency,
    generate_markdown_report,
)
from research.attribute_first_pilot.prompts import (
    build_attribute_first_messages,
    build_attribute_prediction_messages,
    build_direct_baseline_messages,
)
from research.attribute_first_pilot.runner import (
    DEFAULT_BENCHMARK_PATH,
    export_manual_scoring_template,
    load_benchmark,
    run_single_item,
)
from research.attribute_first_pilot.provider import PilotLlmProvider, clean_json_text


def test_attribute_contract_valid():
    """Test standard validation of AttributeContract."""
    data = {
        "answerability": "SUFFICIENT",
        "question_type": "IMPACT",
        "relevant_evidence_ids": ["S1", "S2"],
        "epistemic_state": "SUPPORTED",
        "missing_information": [],
    }
    contract = AttributeContract.model_validate(data)
    assert contract.answerability == AnswerabilityEnum.SUFFICIENT
    assert contract.question_type == QuestionTypeEnum.IMPACT
    assert contract.epistemic_state == EpistemicStateEnum.SUPPORTED
    assert contract.relevant_evidence_ids == ["S1", "S2"]


def test_attribute_contract_invalid_enum():
    """Test that invalid enums raise ValidationError."""
    with pytest.raises(Exception):
        AttributeContract.model_validate({
            "answerability": "MAYBE",
            "question_type": "IMPACT",
            "epistemic_state": "SUPPORTED",
        })


def test_clean_json_text():
    """Test stripping markdown code fences."""
    raw = "```json\n{\"answerability\": \"SUFFICIENT\"}\n```"
    cleaned = clean_json_text(raw)
    assert cleaned == "{\"answerability\": \"SUFFICIENT\"}"


def test_benchmark_json_integrity():
    """Validate all items in benchmark.json match the Pydantic schema."""
    assert DEFAULT_BENCHMARK_PATH.exists(), f"Benchmark file missing at {DEFAULT_BENCHMARK_PATH}"
    suite = load_benchmark(DEFAULT_BENCHMARK_PATH)
    assert len(suite.items) >= 24, f"Benchmark suite should contain >= 24 items, got {len(suite.items)}"

    all_ids = set()
    for item in suite.items:
        assert item.id not in all_ids, f"Duplicate item id: {item.id}"
        all_ids.add(item.id)
        assert len(item.context_sentences) >= 2, f"Item {item.id} has too few sentences"
        assert item.question, f"Item {item.id} has empty question"
        assert item.gold_attributes is not None, f"Item {item.id} missing gold attributes"

        # Check sentence ID validity in relevant evidence
        sentence_ids = {s.id for s in item.context_sentences}
        for ev_id in item.gold_attributes.relevant_evidence_ids:
            assert ev_id in sentence_ids, f"Item {item.id} references non-existent sentence ID {ev_id}"


def test_prompt_builders():
    """Test that prompt builder functions construct the expected message structure."""
    context = "[S1] Fact 1.\n[S2] Fact 2."
    question = "Did exfiltration occur?"

    # B0 Direct
    b0_msgs = build_direct_baseline_messages(context, question)
    assert len(b0_msgs) == 2
    assert "Answer the analytical cybersecurity question" in b0_msgs[0]["content"]
    assert "[S1] Fact 1." in b0_msgs[1]["content"]

    # A1 Predict
    a1_pred_msgs = build_attribute_prediction_messages(context, question)
    assert len(a1_pred_msgs) == 2
    assert "JSON only" in a1_pred_msgs[0]["content"]
    assert "answerability" in a1_pred_msgs[0]["content"]

    # A1 Gen / A2
    attr = AttributeContract(
        answerability=AnswerabilityEnum.SUFFICIENT,
        question_type=QuestionTypeEnum.IMPACT,
        relevant_evidence_ids=["S1"],
        epistemic_state=EpistemicStateEnum.SUPPORTED,
        missing_information=[],
    )
    a1_gen_msgs = build_attribute_first_messages(context, question, attr)
    assert len(a1_gen_msgs) == 2
    assert '"SUFFICIENT"' in a1_gen_msgs[0]["content"]


def test_macro_f1_calculation():
    """Test macro F1 calculation."""
    gold = ["A", "B", "A", "C"]
    pred = ["A", "B", "B", "C"]
    labels = ["A", "B", "C"]
    score = calculate_macro_f1(gold, pred, labels)
    assert 0.0 <= score <= 1.0


def test_evidence_metrics_calculation():
    """Test evidence precision/recall/F1 calculation."""
    gold_sets = [{"S1", "S2"}, {"S3"}]
    pred_sets = [{"S1", "S2"}, {"S3", "S4"}]
    p, r, f = calculate_evidence_metrics(gold_sets, pred_sets)
    assert p == (1.0 + 0.5) / 2
    assert r == (1.0 + 1.0) / 2
    assert 0.0 <= f <= 1.0


def test_runner_mock_single_item(tmp_path):
    """Test executing a mock item through PilotLlmProvider dry_run."""
    import asyncio
    suite = load_benchmark(DEFAULT_BENCHMARK_PATH)
    item = suite.items[0]

    provider = PilotLlmProvider(model="meta-llama/llama-3.1-8b-instruct", dry_run=True)
    res = asyncio.run(run_single_item(item, provider))

    assert res.benchmark_id == item.id
    assert res.direct.answer.startswith("[DRY RUN]")
    assert res.predicted_attributes.attributes is not None
    assert res.predicted_attributes.attributes.answerability == AnswerabilityEnum.SUFFICIENT
    assert res.attribute_first.answer.startswith("[DRY RUN]")
    assert res.oracle_attribute.answer.startswith("[DRY RUN]")

    # Test export template
    run_output = PilotRunOutput(
        timestamp="2026-08-22T00:00:00Z",
        model="meta-llama/llama-3.1-8b-instruct",
        temperature=0.0,
        total_items=1,
        results=[res],
    )
    csv_file = tmp_path / "manual_scoring_test.csv"
    export_manual_scoring_template(run_output, csv_file)
    assert csv_file.exists()
    content = csv_file.read_text(encoding="utf-8")
    assert "case_01_c0_original" in content


def test_evaluator_report_generation():
    """Test evaluating mock run output and generating report."""
    suite = load_benchmark(DEFAULT_BENCHMARK_PATH)
    item = suite.items[0]

    mock_res = ItemRunResult(
        benchmark_id=item.id,
        base_case_id=item.base_case_id,
        condition=item.condition.value,
        question=item.question,
        gold_attributes=item.gold_attributes,
        direct=GenerationResult(
            answer="Exfiltration occurred.", latency_ms=100.0, usage=ModelCallUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70), model="test"
        ),
        predicted_attributes=AttributePredictionResult(
            attributes=item.gold_attributes, latency_ms=80.0, usage=ModelCallUsage(prompt_tokens=40, completion_tokens=30, total_tokens=70), model="test"
        ),
        attribute_first=GenerationResult(
            answer="Exfiltration occurred as per attributes.", latency_ms=90.0, usage=ModelCallUsage(prompt_tokens=60, completion_tokens=25, total_tokens=85), model="test"
        ),
        oracle_attribute=GenerationResult(
            answer="Exfiltration occurred.", latency_ms=85.0, usage=ModelCallUsage(prompt_tokens=60, completion_tokens=25, total_tokens=85), model="test"
        ),
    )

    run_output = PilotRunOutput(
        timestamp="2026-08-22T00:00:00Z",
        model="meta-llama/llama-3.1-8b-instruct",
        temperature=0.0,
        total_items=1,
        results=[mock_res],
    )

    attr_report = evaluate_attributes(run_output)
    assert attr_report.answerability_acc == 1.0
    assert attr_report.epistemic_acc == 1.0
    assert attr_report.evidence_f1 == 1.0

    eff_report = evaluate_efficiency(run_output)
    assert eff_report.total_calls == 4
    assert eff_report.b0_latency_mean == 100.0

    report_md = generate_markdown_report(run_output, attr_report, eff_report)
    assert "# CyberCase Attribute-First Reasoning Pilot" in report_md
    assert "Answerability Accuracy" in report_md
