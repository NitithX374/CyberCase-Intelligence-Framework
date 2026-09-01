import json
from uuid import uuid4

import pytest

from app.config import settings
from app.services.case_analysis.case_analysis_prompt_builder import (
    build_case_analysis_prompt,
    build_overflow_case_context,
)
from app.services.followup.context import build_bounded_context
from app.services.followup.schemas import ClarificationExchange, GapAnalysis, GapItem
from app.services.llm.token_budget import (
    estimate_json_tokens,
    estimate_tokens,
    get_safe_input_token_budget,
    log_context_budget_diagnostics,
)


def payload_from_prompt(prompt: str) -> dict[str, object]:
    payload = prompt.split("<case_context_json>\n", 1)[1]
    return json.loads(payload.split("\n</case_context_json>", 1)[0])


# ── Test 1: Full evidence below budget survives 100% ─────────────────────────


def test_full_evidence_below_budget_survives_in_full() -> None:
    large_evidence = (
        "[INITIAL CASE NARRATIVE]\n"
        + "เหตุการณ์หลอกลวงให้เช่าพื้นที่ค้าขายสถานีรถไฟฟ้าห้วยขวาง " * 200
    )
    external_context = {
        "mitre_attack": "T1566.002",
        "notes": "External threat knowledge",
    }

    prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence=large_evidence,
        analysis_context={
            **external_context,
            "source_message_ids": ["msg-01"],
        },
        question=None,
        response_language="thai",
    )

    payload = payload_from_prompt(prompt)
    assert payload["raw_user_case_evidence"] == large_evidence.strip()
    assert payload["optional_external_context"] == external_context
    assert payload.get("context_truncated") is not True


# ── Test 2: External context empty does NOT trigger 50/50 allocation bug ─────


def test_empty_external_context_does_not_arbitrarily_cut_evidence() -> None:
    # 15,000+ characters of evidence with NO external context
    large_evidence = (
        "ข้อเท็จจริงในสำนวนคดีเกี่ยวกับการโอนเงินเข้าบัญชีธนาคารของผู้ต้องหา "
        * 250
    )
    assert len(large_evidence) > 15_000

    prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence=large_evidence,
        analysis_context={"source_message_ids": ["msg-01"]},
        question=None,
        response_language="thai",
    )

    payload = payload_from_prompt(prompt)
    # The entire evidence MUST be preserved without 50% truncation
    assert payload["raw_user_case_evidence"] == large_evidence.strip()
    assert len(str(payload["raw_user_case_evidence"])) == len(large_evidence.strip())
    assert payload["optional_external_context"] is None
    assert payload.get("context_truncated") is not True


# ── Test 3: Evidence priority over external context during overflow ─────────


def test_evidence_has_priority_over_external_context() -> None:
    evidence = "Authoritative evidence statement. " * 500
    external = {"large_rag_enrichment": "Extensive external knowledge. " * 500}

    # Simulate a tight budget where evidence fits alone, but evidence + external overflows
    evidence_tokens = estimate_tokens(evidence)
    tight_budget = evidence_tokens + 50

    overflow_str = build_overflow_case_context(
        payload={
            "analysis_mode": "case_overview",
            "response_language": "english",
            "raw_user_case_evidence": evidence,
            "authoritative_source_message_ids": ["msg-1"],
            "optional_external_context": external,
            "question": None,
        },
        prefix="",
        suffix="",
        token_budget=tight_budget,
    )
    result = json.loads(overflow_str)

    # Raw evidence must survive 100%
    assert result["raw_user_case_evidence"] == evidence
    assert result["context_truncated"] is True
    # External context must have been sacrificed / reduced
    assert (
        result["optional_external_context"] is None
        or len(str(result["optional_external_context"])) < len(str(external))
    )


# ── Test 4: 128K context safety (Large synthetic inputs close to budget) ────


def test_large_input_close_to_budget_accepted_without_truncation() -> None:
    budget = get_safe_input_token_budget()
    assert budget >= 80_000  # Default is 100_000

    # Build synthetic text of ~70,000 tokens (within 100,000 budget, far above legacy 20,000 chars)
    large_paragraph = "พยานหลักฐานในสำนวนคดีอาญาที่ ๑๒๓/๒๕๖๑ ตรวจสอบพบเส้นทางการเงิน " * 100
    large_evidence = "\n".join([f"หมวดที่ {i}: {large_paragraph}" for i in range(10)])
    assert len(large_evidence) > 60_000
    assert estimate_tokens(large_evidence) < budget

    prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence=large_evidence,
        analysis_context={"source_message_ids": ["msg-01"]},
        question=None,
        response_language="thai",
    )

    payload = payload_from_prompt(prompt)
    assert payload["raw_user_case_evidence"] == large_evidence.strip()
    assert payload.get("context_truncated") is not True


# ── Test 5: Overflow handling with explicit metadata and valid JSON ──────────


def test_overflow_produces_valid_json_with_truncation_metadata() -> None:
    huge_evidence = "Massive case text that exceeds even the safe budget. " * 50_000
    tight_budget = 1_500  # Artificially low budget to force overflow

    overflow_str = build_overflow_case_context(
        payload={
            "analysis_mode": "case_overview",
            "response_language": "english",
            "raw_user_case_evidence": huge_evidence,
            "authoritative_source_message_ids": ["msg-1"],
            "optional_external_context": {"context": "mitre"},
            "question": None,
        },
        prefix="prefix ",
        suffix=" suffix",
        token_budget=tight_budget,
    )

    # Must be valid JSON
    result = json.loads(overflow_str)
    assert result["context_truncated"] is True
    assert len(result["raw_user_case_evidence"]) > 0
    assert len(result["raw_user_case_evidence"]) < len(huge_evidence)
    assert result["optional_external_context"] is None


# ── Test 6: Thai Case Positional Regression (Complainant #2) ────────────────


def test_thai_case_positional_regression_preserves_all_complainants() -> None:
    # Construct a realistic multi-section Thai fraud case
    beginning_fact = "นางสาวพัชร์สิตา ผู้กล่าวหาที่ ๒ ได้เข้าแจ้งความร้องทุกข์"
    middle_fact_1 = "ส่งมอบเงินจำนวน ๒๗,๐๐๐ บาท"
    middle_fact_2 = "ห้องพัก RC ๓๐๖ รัชดาซิตี้คอนโด ซอยประชาราษฎร์บำเพ็ญ ๗"
    end_fact = "นัดหมายให้เริ่มเข้าขายสินค้าได้ในวันที่ ๒๕ มกราคม ๒๕๖๑"

    filler = "ข้อความบันทึกการสอบสวนเพิ่มเติมและรายละเอียดพยานหลักฐานประกอบสำนวน " * 60

    case_evidence = (
        f"[ส่วนต้น: ผู้กล่าวหา]\n{beginning_fact}\n{filler}\n"
        f"[ส่วนกลาง: การจ่ายเงิน]\n{middle_fact_1}\n{middle_fact_2}\n{filler}\n"
        f"[ส่วนท้าย: กำหนดนัด]\n{end_fact}\n"
    )

    # 1. Test Main Case Analysis prompt builder
    prompt = build_case_analysis_prompt(
        mode="case_overview",
        raw_evidence=case_evidence,
        analysis_context={"source_message_ids": ["msg-complainant-2"]},
        question=None,
        response_language="thai",
    )

    assert "นางสาวพัชร์สิตา" in prompt
    assert "๒๗,๐๐๐" in prompt
    assert "RC ๓๐๖" in prompt
    assert "๒๕ มกราคม ๒๕๖๑" in prompt

    # 2. Test Follow-up & Gap Analysis bounded context builder
    followup_context = build_bounded_context(
        original_user_content="สรุปคดีฉ้อโกงพื้นที่เช่า",
        clarification_exchanges=[],
        raw_evidence=case_evidence,
        analysis_answer="ภาพรวมคดีเบื้องต้น",
    )

    raw_ev_str = str(followup_context.get("raw_evidence"))
    assert "นางสาวพัชร์สิตา" in raw_ev_str
    assert "๒๗,๐๐๐" in raw_ev_str
    assert "RC ๓๐๖" in raw_ev_str
    assert "๒๕ มกราคม ๒๕๖๑" in raw_ev_str


# ── Test 7: Follow-up stage does not reintroduce character bottlenecks ──────


def test_followup_context_builder_preserves_large_evidence() -> None:
    large_evidence = (
        "[EVIDENCE NARRATIVE]\n"
        + "รายละเอียดพยานเอกสารและรายการเดินบัญชี " * 600
    )
    assert len(large_evidence) > 20_000  # Far larger than legacy 12,000 char cap

    context = build_bounded_context(
        original_user_content="ขอทราบภาพรวมคดี",
        clarification_exchanges=[
            ClarificationExchange(
                question="เกิดเหตุที่ใด?",
                answer="สถานีรถไฟฟ้าห้วยขวาง",
                gap_topic="สถานที่เกิดเหตุ",
                gap_key="topic:location",
            )
        ],
        raw_evidence=large_evidence,
        analysis_answer="บทสรุปผลการวิเคราะห์คดีเบื้องต้น",
        analysis_context={"mitre": "T1566"},
        gap_analysis=GapAnalysis(
            gaps=[
                GapItem(
                    topic="พยานบุคคล",
                    status="NOT_PROVIDED",
                    description="ไม่มีพยานบุคคล",
                    affects="A-01",
                    reason="ต้องการพยาน",
                    priority="high",
                    askable=True,
                )
            ]
        ),
    )

    # 100% of raw evidence must be retained
    assert context["raw_evidence"] == large_evidence
    assert len(str(context["raw_evidence"])) == len(large_evidence)
    assert context["clarification_exchanges"][0]["user_answer"] == "สถานีรถไฟฟ้าห้วยขวาง"
    assert context.get("context_truncated") is not True


# ── Test 8: Token Budget Diagnostics ────────────────────────────────────────


def test_token_budget_diagnostics_calculation() -> None:
    text = "นางสาวพัชร์สิตา ๒๗,๐๐๐ บาท"
    tokens = estimate_tokens(text)
    assert tokens > 0

    json_tokens = estimate_json_tokens({"text": text, "amount": 27000})
    assert json_tokens > tokens

    diag = log_context_budget_diagnostics(
        feature="test_feature",
        estimated_input_tokens=100,
        configured_input_token_budget=100_000,
        raw_evidence=text,
        external_context={"key": "val"},
        context_truncated=False,
        retained_evidence_ratio=1.0,
        retained_external_context_ratio=1.0,
    )

    assert diag.estimated_input_tokens == 100
    assert diag.configured_input_token_budget == 100_000
    assert diag.raw_evidence_character_length == len(text)
    assert diag.raw_evidence_estimated_tokens == tokens
    assert diag.context_truncated is False
    assert diag.retained_evidence_ratio == 1.0
