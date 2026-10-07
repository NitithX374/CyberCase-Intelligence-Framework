import asyncio

import pytest
from case_view_test_support import claim, reply, transfer_views
from pydantic import ValidationError

from app.analysis import views
from app.analysis.prompts import CASE_VIEWS_SYSTEM_PROMPT
from app.analysis.views import DerivedCaseViewsReply
from app.errors import CaseAnalysisFailure
from app.llm.settings import AnalysisPipelineConfig


async def test_batch_extracts_three_views_from_claims_only(monkeypatch):
    supplied = [claim(), claim("Jane reported a $500 loss.", claim_id="A-02")]
    output = transfer_views().model_copy(
        update={
            "impacts": reply(
                impacts=[{"description": "Jane reported a $500 loss.", "claim_ids": ["A-02"]}]
            ).impacts
        }
    )
    calls = []

    async def request(**kwargs):
        calls.append(kwargs)
        return output

    monkeypatch.setattr(views, "request_stage", request)
    config = AnalysisPipelineConfig(reading_thinking_tokens=2048)
    result = await views.derive_claim_views(supplied, config=config)
    assert len(calls) == 1
    call = calls[0]
    assert call["schema"] is DerivedCaseViewsReply
    assert call["stage"] == "case_views"
    assert call["temperature"] == 0
    assert call.get("grammar", True)
    assert call["content"] == {
        "claims": [{"claim_id": item.claim_id, "text": item.text} for item in supplied]
    }
    assert call["config"].model == config.model
    assert call["config"].providers == config.providers
    assert call["config"].thinking_tokens == 0
    assert call["config"].output_tokens == 4096
    assert config.thinking_tokens == 8192
    assert config.reading_thinking_tokens == 2048
    assert [row.name for row in result.parties] == ["Alice", "Company A"]
    assert result.timeline[0].time == "12 May 2026"
    assert result.impacts[0].claim_ids == ["A-02"]
    assert all(
        not row.field_spans and row.projection_grounding is None
        for row in [*result.parties, *result.timeline, *result.impacts]
    )
    assert result.extraction.method == "llm"
    assert result.extraction.status == "completed"


async def test_missing_role_time_and_suggested_loss_are_not_fabricated(monkeypatch):
    item = claim("Company A suspended the account; this could cause a loss.")

    async def request(**kwargs):
        assert kwargs["content"]["claims"][0]["text"] == item.text
        return reply(
            parties=[{"name": "Company A", "role": None, "claim_ids": ["A-01"]}],
            timeline=[
                {"time": None, "event": "Company A suspended the account.", "claim_ids": ["A-01"]}
            ],
        )

    monkeypatch.setattr(views, "request_stage", request)
    result = await views.derive_claim_views([item], config=AnalysisPipelineConfig())
    assert result.parties[0].role is None
    assert result.timeline[0].time is None
    assert result.impacts == []
    assert "Mere risk or an action does not establish loss" in CASE_VIEWS_SYSTEM_PROMPT
    assert "An action does not establish an actor or legal role" in CASE_VIEWS_SYSTEM_PROMPT


async def test_unknown_claim_ids_drop_whole_item_and_preserve_valid_neighbors(monkeypatch, caplog):
    output = reply(
        parties=[
            {"name": "Alice", "role": None, "claim_ids": ["A-01", "A-999"]},
            {"name": "Company A", "role": None, "claim_ids": ["A-01", "A-01"]},
        ],
        timeline=[{"time": None, "event": "Unlinked event", "claim_ids": ["A-999"]}],
        impacts=[{"description": "An unlinked loss", "claim_ids": ["A-999"]}],
    )

    async def request(**kwargs):
        return output

    monkeypatch.setattr(views, "request_stage", request)
    result = await views.derive_claim_views([claim()], config=AnalysisPipelineConfig())
    assert [row.name for row in result.parties] == ["Company A"]
    assert result.parties[0].claim_ids == ["A-01"]
    assert result.timeline == result.impacts == []
    assert result.extraction.items_dropped == 3
    assert result.extraction.status == "completed"
    assert caplog.text.count("unknown Claim IDs") == 3


def test_claim_links_require_nonempty_lists_and_output_rejects_backend_fields():
    with pytest.raises(ValidationError):
        reply(parties=[{"name": "Alice", "role": None, "claim_ids": []}])
    with pytest.raises(ValidationError):
        reply(parties=[{"name": "Alice", "role": None}])
    with pytest.raises(ValidationError):
        reply(parties=[{"name": "Alice", "role": None, "claim_ids": ["A-01"], "support": "bound"}])
    with pytest.raises(ValidationError):
        reply(summary="An invented analysis")


async def test_same_canonical_claim_set_includes_unresolved_claims_without_new_admission(
    monkeypatch,
):
    supplied = [claim(), claim("John sent an email.", claim_id="A-02", bound=False)]

    async def request(**kwargs):
        assert [item["claim_id"] for item in kwargs["content"]["claims"]] == ["A-01", "A-02"]
        return reply(parties=[{"name": "John", "role": None, "claim_ids": ["A-02"]}])

    monkeypatch.setattr(views, "request_stage", request)
    result = await views.derive_claim_views(supplied, config=AnalysisPipelineConfig())
    assert result.parties[0].support == "unbound"
    assert result.extraction.input_claim_ids == ["A-01", "A-02"]
    assert result.extraction.excluded_claim_ids == []


async def test_multiple_claim_links_and_distinct_aliases_remain_separate(monkeypatch):
    supplied = [
        claim("นายสมชาย ใจดีได้รับข้อความ", claim_id="A-01"),
        claim("นายสมชายรายงานเหตุ", claim_id="A-02"),
    ]

    async def request(**kwargs):
        return reply(
            parties=[
                {"name": "นายสมชาย ใจดี", "role": None, "claim_ids": ["A-01"]},
                {"name": "นายสมชาย", "role": None, "claim_ids": ["A-02"]},
            ],
            timeline=[
                {"time": None, "event": "มีการส่งข้อความและรายงานเหตุ", "claim_ids": ["A-01", "A-02"]}
            ],
        )

    monkeypatch.setattr(views, "request_stage", request)
    result = await views.derive_claim_views(supplied, config=AnalysisPipelineConfig())
    assert len(result.parties) == 2
    assert result.timeline[0].claim_ids == ["A-01", "A-02"]


@pytest.mark.parametrize(
    "error",
    [CaseAnalysisFailure("case_views_invalid", "Invalid schema"), RuntimeError("extractor bug")],
)
async def test_extractor_errors_are_logged_and_recorded_without_fabrication(
    monkeypatch, caplog, error
):
    async def request(**kwargs):
        raise error

    monkeypatch.setattr(views, "request_stage", request)
    result = await views.derive_claim_views([claim()], config=AnalysisPipelineConfig())
    assert result.parties == result.timeline == result.impacts == []
    assert result.extraction.status == "failed"
    assert result.extraction.warning
    assert "Judgement continues independently" in caplog.text


async def test_deadline_cancels_a_stalled_extractor(monkeypatch):
    cancelled = asyncio.Event()

    async def request(**kwargs):
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    monkeypatch.setattr(views, "request_stage", request)
    config = AnalysisPipelineConfig(timeout_seconds=0.01)
    result = await views.derive_claim_views([claim()], config=config)
    assert result.extraction.status == "failed"
    assert cancelled.is_set()


async def test_external_cancellation_is_not_swallowed(monkeypatch):
    started = asyncio.Event()

    async def request(**kwargs):
        started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(views, "request_stage", request)
    task = asyncio.create_task(views.derive_claim_views([claim()], config=AnalysisPipelineConfig()))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_no_claims_skip_provider_request(monkeypatch):
    async def forbidden(**kwargs):
        raise AssertionError("Empty Claims must not call the provider")

    monkeypatch.setattr(views, "request_stage", forbidden)
    result = await views.derive_claim_views([], config=AnalysisPipelineConfig())
    assert result.extraction.status == "skipped"
    assert result.extraction.input_claim_ids == []


async def test_resolvable_claim_links_do_not_create_a_semantic_role_verdict(monkeypatch):
    async def request(**kwargs):
        return reply(parties=[{"name": "John", "role": "Attacker", "claim_ids": ["A-01"]}])

    monkeypatch.setattr(views, "request_stage", request)
    result = await views.derive_claim_views(
        [claim("John sent an email.")], config=AnalysisPipelineConfig()
    )
    assert result.parties[0].support == "bound"
    assert result.parties[0].projection_grounding is None
    assert result.parties[0].field_spans == {}
