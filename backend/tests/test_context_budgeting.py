from app.services.followup.context import build_bounded_context
from app.services.followup.contracts import ClarificationExchange, GapAnalysis, GapItem
from app.services.llm.tokenBudget import (
    estimate_json_tokens,
    estimate_tokens,
    get_safe_input_token_budget,
    log_context_budget_diagnostics,
)


def test_safe_input_token_budget_default() -> None:
    budget = get_safe_input_token_budget()
    assert budget >= 80_000


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
