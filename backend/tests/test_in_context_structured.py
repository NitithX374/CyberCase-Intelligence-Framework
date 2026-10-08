import json

import httpx
import pytest
from pydantic import ValidationError

from app.analysis.technical_context.gate_llm import ProviderMitreApplicability
from app.analysis.views import DerivedCaseViewsReply
from app.chat.compose import ChatReply
from app.errors import CaseAnalysisFailure
from app.llm import request as provider
from app.llm import schema as contracts
from app.llm.openrouter import CoreLlmTarget
from app.llm.settings import AnalysisPipelineConfig
from app.trace.claims import CaseAssessmentTrace
from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply

STAGES = [
    ("case_assessment", CaseAssessmentTrace, {"version": "case_assessment_v1", "gaps": []}),
    ("case_reading", CaseProviderReadingReply, {"version": "case_analysis_trace_v1", "claims": []}),
    (
        "case_judgement",
        CaseProviderJudgement,
        {
            "version": "case_analysis_trace_v1",
            "summary": "No claims.",
            "gaps": [],
            "mitre_associations": [],
        },
    ),
    ("case_views", DerivedCaseViewsReply, {"parties": [], "timeline": [], "impacts": []}),
    ("chat_answer", ChatReply, {"units": [], "suggestion": "none"}),
    (
        "mitre_applicability",
        ProviderMitreApplicability,
        {"decision": "SKIP", "source_message_ids": [], "trigger_text": []},
    ),
]


def prompt_contract(payload):
    text = payload["system"].split("<response_contract>\n", 1)[1]
    return json.loads(text.split("\n</response_contract>", 1)[0])


@pytest.mark.parametrize("stage,model,reply", STAGES)
async def test_every_stage_uses_a_prompt_contract_and_local_validation(
    monkeypatch, stage, model, reply
):
    sent = []

    def respond(request):
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"output_text": json.dumps(reply)})

    monkeypatch.setattr(provider, "transport", httpx.MockTransport(respond))
    monkeypatch.setattr(
        provider,
        "resolve_core_llm_target",
        lambda model: CoreLlmTarget(
            model=model, messages_url="https://provider.test/messages", headers={}
        ),
    )
    content = {"source": "  ไทย\r\n\tJohn sent an email.  ", "claims": []}
    calls = []
    result = await provider.request_stage(
        config=AnalysisPipelineConfig(model="test/model", providers=("pinned",)),
        stage=stage,
        system="Stage instructions",
        content=content,
        schema=model,
        calls=calls,
    )
    [payload] = sent
    assert set(payload) == {"model", "max_tokens", "thinking", "system", "messages", "provider"}
    assert payload["system"].startswith("Stage instructions\n")
    contract = prompt_contract(payload)
    assert set(contract["required"]) == set(model.model_fields)
    assert contract["additionalProperties"] is False
    assert payload["provider"] == {"order": ["pinned"], "allow_fallbacks": False}
    assert json.loads(payload["messages"][0]["content"]) == content
    assert result == model.model_validate(reply)
    assert calls[0]["output_mode"] == "in_context_json"
    assert calls[0]["request_max_tokens"] == payload["max_tokens"]


@pytest.mark.parametrize("stage,model,reply", STAGES)
def test_missing_defaulted_fields_do_not_pass_the_wire_contract(stage, model, reply):
    omitted = {key: value for key, value in reply.items() if key != next(iter(reply))}
    with pytest.raises(ValidationError):
        contracts.validate_structured_json(model, json.dumps(omitted))


@pytest.mark.parametrize(
    "change",
    [
        {"basis": "unknown"},
        {"claim_ids": "A-01"},
        {"quotes": [{"source_id": "S1"}]},
        {"text": 42},
        {"extra": "unexpected"},
    ],
)
def test_chat_coercion_cannot_hide_a_broken_nested_wire_contract(change):
    unit = {"text": "A finding.", "basis": "case_fact", "claim_ids": [], "quotes": []}
    unit.update(change)
    with pytest.raises(ValidationError):
        contracts.validate_structured_json(
            ChatReply, json.dumps({"units": [unit], "suggestion": "none"})
        )


def test_contract_keeps_the_constraints_that_provider_grammar_did_not_support():
    contract = contracts.structured_output_schema(DerivedCaseViewsReply)
    assert contract["properties"]["parties"]["maxItems"] == 64
    assert contract["$defs"]["DerivedParty"]["properties"]["claim_ids"]["minItems"] == 1
    too_many = {"parties": [{}] * 65, "timeline": [], "impacts": []}
    with pytest.raises(ValidationError):
        contracts.validate_structured_json(DerivedCaseViewsReply, json.dumps(too_many))


def test_string_content_is_unchanged_and_schema_is_only_in_the_system_prompt():
    content = "  Thai ไทย\r\n\tSource text  "
    payload = provider.stage_payload(AnalysisPipelineConfig(), "system", content, ChatReply)
    assert payload["messages"] == [{"role": "user", "content": content}]
    assert prompt_contract(payload)["title"] == "ChatReply"
    assert "output_config" not in payload


async def test_input_budget_counts_the_in_context_contract_before_posting(monkeypatch):
    config = AnalysisPipelineConfig(model="test/model")
    seen = []

    def count(payload):
        seen.append(prompt_contract(payload))
        return provider.input_budget(config) + 1

    monkeypatch.setattr(provider, "token_count", count)
    monkeypatch.setattr(provider, "resolve_core_llm_target", lambda model: None)
    with pytest.raises(CaseAnalysisFailure, match="Stage input exceeds budget") as failure:
        await provider.request_stage(
            config=config, stage="chat_answer", system="system", content={}, schema=ChatReply
        )
    assert failure.value.code == "chat_answer_budget_exceeded"
    assert len(seen) == 1
