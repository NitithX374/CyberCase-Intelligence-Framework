import asyncio
from uuid import uuid4

from app.services.followup.decision import evaluate_followup_outcome
from app.services.followup.schemas import (
    FollowUpDecision,
    GapAnalysis,
    GapAnalysisResult,
    GapItem,
)


class Analyzer:
    async def analyze(self, **kwargs):
        assert kwargs["raw_evidence"] == "raw evidence"
        return GapAnalysisResult(
            analysis=GapAnalysis(
                gaps=[
                    GapItem(
                        topic="affected account",
                        status="NOT_PROVIDED",
                        description="The affected account is missing",
                        affects="scope",
                        reason="It defines the target",
                        priority="high",
                        askable=True,
                    )
                ]
            )
        )


class Policy:
    async def decide(self, **kwargs):
        assert kwargs["raw_evidence"] == "raw evidence"
        return FollowUpDecision(
            decision="ask_followup",
            selected_gap="affected account",
            question="Which account was affected?",
        )


def test_followup_consumes_raw_evidence_without_case_state() -> None:
    result = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="Initial",
            clarification_exchanges=(),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            raw_evidence="raw evidence",
            analysis_answer="analysis",
            analysis_context={"mitre_table": []},
            gap_analyzer=Analyzer(),
            policy=Policy(),
        )
    )
    assert result.question is not None
    assert result.question == "Which account was affected?"
    gap_trace = result.metadata_json["chat_followup"]["gap_analysis"]
    assert gap_trace["status"] == "completed"
    assert gap_trace["gaps"] == [
        {
            "topic": "affected account",
            "status": "NOT_PROVIDED",
            "description": "The affected account is missing",
            "affects": "scope",
            "reason": "It defines the target",
            "priority": "high",
            "askable": True,
        }
    ]


def test_gap_analysis_contract_uses_free_text_affects_and_preserves_unknown() -> None:
    gap = GapItem.model_validate(
        {
            "topic": "incident time",
            "status": "EXPLICITLY_UNKNOWN",
            "description": "The investigator explicitly does not know the time.",
            "affects": "the current event sequence",
            "reason": "Timing constrains the sequence analysis.",
            "priority": "medium",
            "askable": False,
        }
    )

    assert gap.model_dump(mode="json") == {
        "topic": "incident time",
        "status": "EXPLICITLY_UNKNOWN",
        "description": "The investigator explicitly does not know the time.",
        "affects": "the current event sequence",
        "reason": "Timing constrains the sequence analysis.",
        "priority": "medium",
        "askable": False,
    }


def test_extract_llm_json_markdown_fences() -> None:
    from app.services.followup.helpers import _extract_llm_json

    raw = '```json\n{\n  "gaps": [\n    {\n      "topic": "Initial Vector",\n      "status": "not_provided",\n      "description": "Vector not clear",\n      "affects": "scope",\n      "reason": "needed",\n      "priority": "HIGH",\n      "askable": true\n    }\n  ]\n}\n```'
    parsed = _extract_llm_json(raw)
    assert "gaps" in parsed
    assert len(parsed["gaps"]) == 1

    gap_item = GapItem.model_validate(parsed["gaps"][0])
    assert gap_item.status == "NOT_PROVIDED"
    assert gap_item.priority == "high"


def test_extract_llm_json_surrounding_text() -> None:
    from app.services.followup.helpers import _extract_llm_json

    raw = 'Here is the gap analysis:\n\n```json\n{"gaps": []}\n```\nHope this helps!'
    parsed = _extract_llm_json(raw)
    assert parsed == {"gaps": []}


def test_extract_llm_text_and_thinking_blocks() -> None:
    from app.services.followup.helpers import _extract_llm_text

    # Anthropic payload with thinking block
    anthropic_payload = {
        "content": [
            {"type": "thinking", "thinking": "Let me analyze the case..."},
            {"type": "text", "text": '{"gaps": []}'},
        ]
    }
    assert _extract_llm_text(anthropic_payload) == '{"gaps": []}'

    # OpenRouter choices payload
    openrouter_payload = {
        "choices": [{"message": {"content": '{"decision": "proceed", "question": ""}'}}]
    }
    assert (
        _extract_llm_text(openrouter_payload)
        == '{"decision": "proceed", "question": ""}'
    )

    # Direct output_text payload
    output_text_payload = {"output_text": '{"decision": "proceed"}'}
    assert _extract_llm_text(output_text_payload) == '{"decision": "proceed"}'


def test_followup_schemas_lenient_coercion() -> None:
    # GapItem normalizes status and priority and ignores extra fields
    item = GapItem.model_validate(
        {
            "topic": "attacker IP",
            "status": "missing",
            "description": "IP is unknown",
            "affects": "attribution",
            "reason": "needed",
            "priority": "critical",
            "askable": "true",
            "extra_field": "should_be_ignored",
        }
    )
    assert item.status == "NOT_PROVIDED"
    assert item.priority == "high"
    assert item.askable is True

    # FollowUpDecision normalizes proceed with whitespace/non-null empty fields
    decision = FollowUpDecision.model_validate(
        {
            "decision": "proceed",
            "selected_gap": "None",
            "question": "",
            "extra_meta": 123,
        }
    )
    assert decision.decision == "proceed"
    assert decision.selected_gap is None
    assert decision.question == ""


def test_reconstruct_clarification_chain_with_bound_metadata() -> None:
    from app.models.chat import ChatMessage
    from app.services.chat.clarification_chain import reconstruct_clarification_chain

    messages = [
        ChatMessage(
            id=uuid4(),
            thread_id=uuid4(),
            ordinal=1,
            role="user",
            content="ระบบตรวจพบการพยายามล็อกอินผิดปกติ",
            metadata_json={"evidence_kind": "initial_case_narrative"},
        ),
        ChatMessage(
            id=uuid4(),
            thread_id=uuid4(),
            ordinal=2,
            role="assistant",
            content="เกิดเหตุการณ์ขึ้นกับบัญชีผู้ใช้ใด?",
            retrieval_context_id="ctx-123",
            metadata_json={
                "chat_followup": {
                    "kind": "clarification",
                    "action": "ask_followup",
                    "root_ordinal": 1,
                    "question": "เกิดเหตุการณ์ขึ้นกับบัญชีผู้ใช้ใด?",
                },
                "mitre_table": [{"technique_id": "T1110"}],
            },
        ),
        ChatMessage(
            id=uuid4(),
            thread_id=uuid4(),
            ordinal=3,
            role="user",
            content="ไม่ทราบครับ",
            metadata_json={"evidence_kind": "clarification_answer"},
        ),
    ]

    chain = reconstruct_clarification_chain(messages, root_ordinal=1)
    assert chain is not None
    assert chain.root_ordinal == 1
    assert len(chain.exchanges) == 1
    assert chain.exchanges[0].question == "เกิดเหตุการณ์ขึ้นกับบัญชีผู้ใช้ใด?"
    assert chain.exchanges[0].answer == "ไม่ทราบครับ"


def test_answer_indicates_unavailable_thai_and_english() -> None:
    from app.services.followup.contracts import answer_indicates_unavailable

    assert answer_indicates_unavailable("ไม่ทราบ") is True
    assert answer_indicates_unavailable("ไม่ทราบครับ") is True
    assert answer_indicates_unavailable("ยังไม่ทราบค่ะ") is True
    assert answer_indicates_unavailable("ไม่รู้") is True
    assert answer_indicates_unavailable("ไม่มีข้อมูล") is True
    assert answer_indicates_unavailable("ไม่แน่ใจครับ") is True
    assert answer_indicates_unavailable("ไม่มี") is True
    assert answer_indicates_unavailable("don't know") is True
    assert answer_indicates_unavailable("i dont know") is True
    assert answer_indicates_unavailable("unavailable") is True
    assert answer_indicates_unavailable("n/a") is True

    # Real positive answers should NOT be unavailable
    assert answer_indicates_unavailable("เป็นบัญชี admin ครับ") is False
    assert answer_indicates_unavailable("เกิดเหตุเมื่อวาน เวลา 14.00") is False


def test_evaluate_followup_proceeds_when_only_gap_is_explicitly_unknown() -> None:
    from app.services.followup.schemas import ClarificationExchange

    class UnknownAnalyzer:
        async def analyze(self, **kwargs):
            return GapAnalysisResult(
                analysis=GapAnalysis(
                    gaps=[
                        GapItem(
                            topic="incident time",
                            status="EXPLICITLY_UNKNOWN",
                            description="The investigator does not know the time.",
                            affects="A-01 — current event sequence",
                            reason="The timing cannot currently be established.",
                            priority="high",
                            askable=True,
                        )
                    ]
                )
            )

    resolution = asyncio.run(
        evaluate_followup_outcome(
            original_user_content="ระบบโดนโจมตี",
            clarification_exchanges=(
                ClarificationExchange(
                    question="เป้าหมายคือเครื่องไหน?",
                    answer="ไม่ทราบครับ",
                ),
            ),
            followup_root_ordinal=1,
            source_run_id=uuid4(),
            raw_evidence="[INITIAL CASE NARRATIVE]\nระบบโดนโจมตี\n\n[ADDED CASE INFORMATION #1]\nไม่ทราบครับ",
            analysis_answer="ผลวิเคราะห์",
            analysis_context={"mitre_table": []},
            gap_analyzer=UnknownAnalyzer(),
            policy=Policy(),
        )
    )
    assert resolution.question is None
    assert (
        resolution.metadata_json["chat_followup"]["reason_code"]
        == "unresolved_gaps_recorded"
    )
    assert (
        resolution.metadata_json["chat_followup"]["stop_reason"]
        == "no_eligible_canonical_gap"
    )
    assert resolution.gap_analysis is not None
    assert resolution.gap_analysis.gaps[0].status == "EXPLICITLY_UNKNOWN"
    assert resolution.gap_analysis.gaps[0].askable is False
