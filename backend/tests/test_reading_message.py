import json

from app.llm.request import stage_payload
from app.llm.settings import AnalysisPipelineConfig
from app.trace.trace import CaseProviderReadingReply


def test_prompt_json_message_is_compact_without_changing_source_text():
    content = {"case_sources": [{"source_id": "S1", "text": "  ไทย\r\n\tJohn sent an email.  "}]}
    compact = stage_payload(
        AnalysisPipelineConfig(model="test/model"),
        "system",
        content,
        CaseProviderReadingReply,
        grammar=False,
    )
    message = compact["messages"][0]["content"]
    assert message == json.dumps(content, ensure_ascii=False, separators=(",", ":"))
    assert json.loads(message) == content
    assert "output_config" not in compact


def test_existing_grammar_stage_serialization_stays_unchanged():
    content = {"claims": []}
    payload = stage_payload(
        AnalysisPipelineConfig(model="test/model"), "system", content, CaseProviderReadingReply
    )
    assert payload["messages"][0]["content"] == json.dumps(content, ensure_ascii=False)
    assert payload["output_config"]["format"]["type"] == "json_schema"
