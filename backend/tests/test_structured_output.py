import json
from typing import Literal

import pytest
from pydantic import BaseModel

from app.analysis.technical_context.gate_llm import ProviderMitreApplicability
from app.chat.compose import ChatReply
from app.llm.schema import structured_output_schema
from app.trace.claims import CaseAssessmentTrace
from app.trace.trace import CaseProviderAnalysis, CaseProviderJudgement, CaseProviderReadingReply


def keys_in(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in keys_in(child)}
    if isinstance(value, list):
        return {key for child in value for key in keys_in(child)}
    return set()


def shape(prop: dict) -> dict:
    return {key: prop[key] for key in ("enum", "type")}


def test_case_provider_analysis_schema_exposes_grounded_claim_roles() -> None:
    schema = structured_output_schema(CaseProviderAnalysis)
    assert shape(schema["properties"]["version"]) == {
        "enum": ["case_analysis_trace_v1"],
        "type": "string",
    }
    for section in ("involved_parties", "timeline", "impacts", "claims", "gaps"):
        assert section in schema["properties"]
    assert set(schema["required"]) == set(schema["properties"])


def test_claims_are_written_before_the_fields_that_point_at_them() -> None:
    order = list(structured_output_schema(CaseProviderAnalysis)["properties"])
    assert order[:2] == ["version", "claims"]
    for pointing in ("summary", "involved_parties", "timeline", "impacts"):
        assert order.index(pointing) > order.index("claims")


def test_the_provider_is_not_asked_for_document_locators() -> None:
    schema = structured_output_schema(CaseProviderAnalysis)
    citation = schema["$defs"]["CaseProviderCitation"]
    assert set(citation["properties"]) == {"source_id", "exact_quote"}


@pytest.mark.parametrize(
    "model",
    [
        CaseProviderAnalysis,
        CaseProviderJudgement,
        CaseProviderReadingReply,
        CaseAssessmentTrace,
        ProviderMitreApplicability,
        ChatReply,
    ],
)
def test_no_schema_sent_to_a_provider_has_a_const(model) -> None:
    assert "const" not in keys_in(structured_output_schema(model))


def test_pydantic_writes_a_const_for_a_single_value_literal() -> None:
    assert "const" in keys_in(CaseProviderJudgement.model_json_schema())


def test_each_version_the_judgement_and_the_assessment_must_write_is_a_one_item_enum() -> None:
    judgement = structured_output_schema(CaseProviderJudgement)
    assessment = structured_output_schema(CaseAssessmentTrace)

    assert shape(judgement["properties"]["version"]) == {
        "enum": ["case_analysis_trace_v1"],
        "type": "string",
    }
    assert shape(assessment["properties"]["version"]) == {
        "enum": ["case_assessment_v1"],
        "type": "string",
    }


class Kinds(BaseModel):
    one: Literal["a"]
    two: Literal["x", "y"]
    number: Literal[3]
    flag: Literal[True]


def test_a_literal_becomes_an_enum_that_keeps_its_type() -> None:
    properties = structured_output_schema(Kinds)["properties"]

    assert shape(properties["one"]) == {"enum": ["a"], "type": "string"}
    assert shape(properties["two"]) == {"enum": ["x", "y"], "type": "string"}
    assert shape(properties["number"]) == {"enum": [3], "type": "integer"}
    assert shape(properties["flag"]) == {"enum": [True], "type": "boolean"}


def test_the_schema_a_provider_gets_is_plain_json_without_const_anywhere() -> None:
    text = json.dumps(structured_output_schema(CaseProviderJudgement))

    assert '"const"' not in text
    assert '"enum"' in text
