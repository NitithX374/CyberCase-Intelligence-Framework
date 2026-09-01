import asyncio
import json
import logging
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.case_analysis.contracts import AnalysisTraceV3, CaseAnalysisResult
from app.services.case_analysis.gap_assembly import enrich_case_analysis_result
from app.services.followup.claim_transport import (
    GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS,
    build_gap_analysis_claim_transport,
)
from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.gap_analysis import AnthropicGapAnalysis
from app.services.followup.prompts import (
    GAP_ANALYSIS_PROMPT_VERSION,
    GAP_ANALYSIS_SYSTEM,
)
from app.services.followup.schemas import (
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)
from app.services.workflow.chat_run_completion import _serialize_analysis_trace
from app.services.workflow.outcome import AssistantOutcome


def claim_payload(index: int) -> dict[str, object]:
    text = f"Canonical claim {index}"
    if index == 64:
        text = "ผู้เสียหายระบุว่าทรัพย์สินถูกส่งมอบก่อนตรวจนับ"
    return {
        "claim_id": f"A-{index:02d}",
        "text": text,
        "claim_type": "reported",
        "epistemic_status": "reported",
    }


def trace_with_64_claims() -> AnalysisTraceV3:
    claims = [
        {
            **claim_payload(index),
            "supporting_source_message_ids": ["message-1"],
            "contradicting_source_message_ids": [],
            "reasoning_summary": None,
        }
        for index in range(1, 65)
    ]
    return AnalysisTraceV3.model_validate(
        {
            "analysis_mode": "case_overview",
            "summary": "The evidence supports sixty-four bounded claims.",
            "claims": claims,
            "gaps": [],
            "mitre_associations": [],
            "evidence_sha256": "a" * 64,
            "retrieval_context_id": None,
        }
    )


def test_dedicated_transport_preserves_all_64_claims_in_order() -> None:
    transported = build_gap_analysis_claim_transport(
        [claim_payload(index) for index in range(1, 65)]
    )
    claim_ids = [str(claim["claim_id"]) for claim in transported]
    assert len(transported) == 64
    assert claim_ids[0] == "A-01"
    assert claim_ids[31] == "A-32"
    assert claim_ids[32] == "A-33"
    assert claim_ids[63] == "A-64"
    assert len(set(claim_ids)) == 64


def test_gap_provider_payload_bypasses_generic_32_item_limiter(monkeypatch) -> None:
    captured: dict[str, object] = {}

    async def fake_post(client, messages_url, request_payload, headers):
        captured.update(request_payload)
        return {"gaps": []}, None, None

    monkeypatch.setattr(
        "app.services.followup.gap_analysis.resolve_core_llm_target",
        lambda model: SimpleNamespace(
            model="test-model",
            provider="openrouter",
            messages_url="https://example.invalid",
            headers={},
        ),
    )
    monkeypatch.setattr(AnthropicGapAnalysis, "_post", staticmethod(fake_post))
    asyncio.run(
        AnthropicGapAnalysis().analyze(
            original_user_content="case",
            clarification_exchanges=(),
            analysis_context={"generic_items": list(range(64))},
            analysis_claims=[claim_payload(index) for index in range(1, 65)],
            client=object(),
        )
    )
    messages = captured["messages"]
    content = messages[0]["content"]
    assert captured["system"] == GAP_ANALYSIS_SYSTEM
    assert GAP_ANALYSIS_PROMPT_VERSION == "gap_analysis_prompt_v7"
    assert "Case Gap Analysis component" in GAP_ANALYSIS_SYSTEM
    assert "MATERIAL unresolved factual issues" in GAP_ANALYSIS_SYSTEM
    assert "MATERIAL CASE-SPECIFIC GAPS" in GAP_ANALYSIS_SYSTEM
    assert "SCOPE OF UNCERTAINTY" in GAP_ANALYSIS_SYSTEM
    assert "DOCUMENT AND RECORD INCONSISTENCIES" in GAP_ANALYSIS_SYSTEM
    assert "ENTITY IDENTITY AND NAME VARIATION" in GAP_ANALYSIS_SYSTEM
    assert "TASK-SPECIFIC MATERIALITY" in GAP_ANALYSIS_SYSTEM
    assert "Do not propagate uncertainty to other facts" in GAP_ANALYSIS_SYSTEM
    assert "COMPATIBLE DESCRIPTIONS AND ALIASES" in GAP_ANALYSIS_SYSTEM
    assert "CyberCase Gap Analysis component" not in GAP_ANALYSIS_SYSTEM
    assert "incident-specific" not in GAP_ANALYSIS_SYSTEM
    assert "MITRE explanation" not in GAP_ANALYSIS_SYSTEM
    assert "retrieved MITRE/RAG context are analytical context" in GAP_ANALYSIS_SYSTEM
    assert content.startswith("Return all relevant case-specific gaps")
    encoded = content.split("<case_data_json>\n", 1)[1].split("\n</case_data_json>", 1)[
        0
    ]
    transmitted = json.loads(encoded)["analysis_claims"]
    assert len(transmitted) == 64
    assert transmitted[31]["claim_id"] == "A-32"
    assert transmitted[32]["claim_id"] == "A-33"
    assert transmitted[63]["claim_id"] == "A-64"


def test_transport_bounds_text_without_dropping_claims() -> None:
    claims = [claim_payload(index) for index in range(1, 65)]
    claims[-1]["text"] = "ก" * (GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS + 50)
    transported = build_gap_analysis_claim_transport(claims)
    assert len(transported) == 64
    assert len(str(transported[-1]["text"])) == GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS


def test_transport_rejects_claim_count_above_v3_contract() -> None:
    with pytest.raises(ValueError, match="exceeds the v3 claim limit"):
        build_gap_analysis_claim_transport(
            [claim_payload(index) for index in range(1, 66)]
        )


def test_a64_exact_link_survives_gap_stage_assembly_and_serialization() -> None:
    trace = trace_with_64_claims()
    source_run_id = uuid4()

    class Analyzer:
        async def analyze(self, **kwargs):
            transmitted = kwargs["analysis_claims"]
            assert len(transmitted) == 64
            assert transmitted[-1]["claim_id"] == "A-64"
            return GapAnalysisResult(
                analysis=GapAnalysis(
                    gaps=[
                        GapItem(
                            topic="ลำดับการส่งมอบ",
                            status="AMBIGUOUS",
                            description="ยังยืนยันลำดับการส่งมอบไม่ได้",
                            affects="A-64 — ต้องยืนยันช่วงเวลารับมอบ",
                            reason="ลำดับเวลามีผลต่อข้อสรุป",
                            priority="high",
                            askable=True,
                        )
                    ]
                )
            )

    class Policy:
        async def decide(self, **kwargs):
            return FollowUpDecision(
                decision="ask_followup",
                selected_gap="ลำดับการส่งมอบ",
                question="ทรัพย์สินถูกส่งมอบเมื่อใด?",
            )

    resolution = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="ทรัพย์สินสูญหาย",
            clarification_exchanges=(),
            followup_root_ordinal=1,
            source_run_id=source_run_id,
            raw_evidence="raw evidence",
            analysis_answer="analysis",
            analysis_context={},
            analysis_claims=[claim_payload(index) for index in range(1, 65)],
            gap_analyzer=Analyzer(),
            policy=Policy(),
        )
    )
    enriched = enrich_case_analysis_result(
        CaseAnalysisResult(answer="analysis", trace=trace),
        resolution.gap_analysis,
        source_message_ids={"message-1"},
    )
    assert enriched.trace is not None
    assert enriched.trace.gaps[0].affected_claim_ids == ["A-64"]
    outcome = AssistantOutcome(
        content="analysis",
        retrieval_context_id=None,
        metadata_json={},
        thread_status="answered",
        analysis_trace_draft=enriched.trace,
        evidence_sha256="a" * 64,
    )
    persisted = _serialize_analysis_trace(outcome)
    assert persisted is not None
    assert persisted["gaps"][0]["affected_claim_ids"] == ["A-64"]


def test_gap_failure_log_includes_source_run_id(caplog) -> None:
    source_run_id = uuid4()

    class FailingAnalyzer:
        async def analyze(self, **kwargs):
            raise RuntimeError("provider unavailable")

    with caplog.at_level(logging.WARNING, logger="app.chat"):
        asyncio.run(
            evaluate_followup_outcome(
                original_user_content="case",
                clarification_exchanges=(),
                followup_root_ordinal=1,
                source_run_id=source_run_id,
                gap_analyzer=FailingAnalyzer(),
            )
        )
    assert str(source_run_id) in caplog.text
    assert "failure_code=policy_error" in caplog.text
