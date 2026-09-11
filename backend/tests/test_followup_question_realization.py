import asyncio
import json
from types import SimpleNamespace

from app.services.followup.contracts import GapAnalysis, GapItem
from app.services.followup.policy import AnthropicFollowUpPolicy


def test_question_realizer_receives_only_the_selected_gap(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "decision": "ask_followup",
                                "selected_gap": "incident time",
                                "question": "When did the incident occur?",
                            }
                        ),
                    }
                ]
            }

    class Client:
        async def post(self, url, *, headers, json):
            captured.update(json)
            return Response()

    monkeypatch.setattr(
        "app.services.followup.policy.resolve_core_llm_target",
        lambda model: SimpleNamespace(
            model=model,
            provider="anthropic",
            messages_url="https://example.test/messages",
            headers={},
        ),
    )
    gap = GapItem(
        topic="incident time",
        status="NOT_PROVIDED",
        description="The time is absent.",
        affects="case chronology",
        reason="Timing materially affects the analysis.",
        priority="high",
        askable=True,
    )
    result = asyncio.run(
        AnthropicFollowUpPolicy().decide_with_metadata(
            original_user_content="SECRET RAW CASE EVIDENCE",
            clarification_exchanges=(),
            gap_analysis=GapAnalysis(gaps=[gap]),
            raw_evidence="SECRET RAW CASE EVIDENCE",
            analysis_answer="SECRET GENERATED ANALYSIS",
            analysis_context={"secret": "SECRET CONTEXT"},
            client=Client(),
        )
    )
    serialized_message = captured["messages"][0]["content"]
    assert "incident time" in serialized_message
    assert "SECRET" not in serialized_message
    assert result.decision.question == "When did the incident occur?"
