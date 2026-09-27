import pytest
from pydantic import ValidationError

from app.services.analysis.provider import input_budget
from app.services.analysis.settings import AnalysisPipelineConfig, provider_order


def test_the_request_budget_is_output_plus_thinking() -> None:
    config = AnalysisPipelineConfig(model="test/model", output_tokens=1_024, thinking_tokens=2_048)

    assert config.max_tokens == 3_072


def test_thinking_switched_off_leaves_the_output_budget() -> None:
    config = AnalysisPipelineConfig(model="test/model", thinking_tokens=0)

    assert config.max_tokens == config.output_tokens


def test_a_thinking_budget_below_the_provider_minimum_is_refused() -> None:
    with pytest.raises(ValidationError, match="at least 1,024"):
        AnalysisPipelineConfig(model="test/model", thinking_tokens=512)


def test_budgets_that_exhaust_the_context_are_refused() -> None:
    with pytest.raises(ValidationError, match="exhaust context"):
        AnalysisPipelineConfig(
            model="test/model",
            context_tokens=24_000,
            output_tokens=16_384,
            thinking_tokens=4_096,
            safety_tokens=4_000,
        )


def test_thinking_comes_out_of_the_input_budget() -> None:
    config = AnalysisPipelineConfig(
        model="test/model",
        context_tokens=30_000,
        output_tokens=16_384,
        thinking_tokens=4_096,
        safety_tokens=4_000,
    )

    assert input_budget(config) == 5_520


def test_the_provider_list_keeps_its_order_and_drops_blanks_and_repeats() -> None:
    assert provider_order(" parasail/fp8, ,coreweave/fp8,parasail/fp8 ") == (
        "parasail/fp8",
        "coreweave/fp8",
    )
    assert provider_order("") == ()
