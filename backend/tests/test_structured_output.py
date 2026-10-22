import json
from typing import Literal

import pytest
from pydantic import BaseModel

from app.analysis.technical_context.gate_llm import ProviderMitreApplicability
from app.analysis.views import DerivedCaseViewsReply
from app.chat.compose import ChatReply
from app.llm.schema import structured_output_schema
from app.trace.claims import CaseAssessmentTrace
from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply


def keys_in(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in keys_in(child)}
    if isinstance(value, list):
        return {key for child in value for key in keys_in(child)}
    return set()


def shape(prop: dict) -> dict:
    return {key: prop[key] for key in ("enum", "type")}


@pytest.mark.parametrize(
    "model",
    [
        CaseProviderJudgement,
        CaseProviderReadingReply,
        DerivedCaseViewsReply,
        CaseAssessmentTrace,
        ProviderMitreApplicability,
        ChatReply,
    ],
)
def test_no_schema_sent_to_a_provider_has_a_const(model) -> None:
    assert "const" not in keys_in(structured_output_schema(model))


def test_no_contract_asks_a_model_for_a_version() -> None:
    assert list(structured_output_schema(CaseAssessmentTrace)["properties"]) == ["gaps"]
    assert list(structured_output_schema(CaseProviderReadingReply)["properties"]) == ["claims"]
    assert list(structured_output_schema(CaseProviderJudgement)["properties"]) == [
        "summary",
        "gaps",
    ]


class Kinds(BaseModel):
    one: Literal["a"]
    two: Literal["x", "y"]
    number: Literal[3]
    flag: Literal[True]


def test_pydantic_writes_a_const_for_a_single_value_literal() -> None:
    assert "const" in keys_in(Kinds.model_json_schema())


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
