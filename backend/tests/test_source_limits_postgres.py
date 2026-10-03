from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from functools import partial
from types import SimpleNamespace

import pytest
from case_chat_support import TRACE, seeded_case
from httpx import ASGITransport, AsyncClient
from isolated_database import isolated_database
from sqlalchemy import func, select

import app.analysis.routes as analysis_router
import app.chat.routes as chat_router
import app.sources.service as source_service
from app.analysis.pipeline import AnalysisArtifacts
from app.analysis.run import run_case_analysis
from app.auth.guard import get_current_user
from app.cases.running import analysing
from app.database import get_db
from app.llm.request import token_count
from app.llm.settings import SOURCE_OVERHEAD_TOKENS, SOURCE_TOKEN_BUDGET
from app.main import app
from app.models.case import Case
from app.models.document import CaseDocument
from app.models.source import CaseSource
from app.sources.ingestion.contracts import DocumentPage, ExtractionMethod, IngestedDocument
from app.sources.service import SourceError, SourceService, weight_in_payload
from app.trace.trace import CaseAnalysisTrace

pytestmark = pytest.mark.asyncio

SENTENCE = "The attacker logged in to the VPN gateway and copied the payroll archive. "
BACKSLASH = chr(92)
LOG_LINE = '{"path": "C:' + BACKSLASH + "Users" + BACKSLASH + 'svc", "message": "denied"}' + chr(10)
WAIT = 10


def document(text: str) -> IngestedDocument:
    return IngestedDocument(
        filename="case.pdf",
        media_type="application/pdf",
        extraction_method=ExtractionMethod.NATIVE_PDF,
        pages=[
            DocumentPage(
                page_number=1, text=text, text_method="native", verification_status="native"
            )
        ],
        full_text=text,
    )


async def stored(factory, case_id) -> tuple[int, int, int]:
    async with factory() as db:
        sources = await db.scalar(
            select(func.count()).select_from(CaseSource).where(CaseSource.case_id == case_id)
        )
        documents = await db.scalar(
            select(func.count()).select_from(CaseDocument).where(CaseDocument.case_id == case_id)
        )
        revision = (await db.get(Case, case_id)).source_revision
    return sources, documents, revision


async def add_text(factory, case_id, user_id, text: str):
    async with factory() as db, db.begin():
        return await SourceService(db).add_text_source(
            case_id=case_id,
            user_id=user_id,
            source_kind="narrative",
            text=text,
            provenance_json={},
        )


async def add_document(factory, case_id, user_id, text: str):
    async with factory() as db, db.begin():
        return await SourceService(db).add_document(
            case_id=case_id, user_id=user_id, ingested=document(text), content=b"bytes"
        )


@asynccontextmanager
async def signed_in(factory, user_id):
    async def request_session():
        async with factory() as session:
            yield session

    app.app.dependency_overrides[get_db] = request_session
    app.app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user_id)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test/api/v1",
        ) as client:
            yield client
    finally:
        app.app.dependency_overrides.pop(get_db, None)
        app.app.dependency_overrides.pop(get_current_user, None)


async def test_sources_up_to_the_ceiling_are_accepted_and_the_next_one_is_refused(monkeypatch):
    text = (SENTENCE * 5).strip()
    monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", weight_in_payload(text))
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)

        await add_text(factory, case_id, user_id, text)
        with pytest.raises(SourceError) as refused:
            await add_text(factory, case_id, user_id, text)

        assert refused.value.code == "source_too_large"
        assert refused.value.status_code == 413
        assert await stored(factory, case_id) == (1, 0, 2)


async def test_the_ceiling_counts_every_source_of_the_case_not_just_the_new_one(monkeypatch):
    text = (SENTENCE * 5).strip()
    monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", 2 * weight_in_payload(text) - 1)
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)

        await add_text(factory, case_id, user_id, text)
        with pytest.raises(SourceError) as refused:
            await add_text(factory, case_id, user_id, text)

        assert refused.value.code == "source_too_large"


async def test_a_source_is_weighed_as_it_sits_in_a_stage_payload_not_as_typed(monkeypatch):
    text = (LOG_LINE * 40).strip()
    assert token_count(json.dumps(text, ensure_ascii=False)) > token_count(text)
    monkeypatch.setattr(
        source_service, "SOURCE_TOKEN_BUDGET", token_count(text) + SOURCE_OVERHEAD_TOKENS
    )
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)

        with pytest.raises(SourceError) as refused:
            await add_text(factory, case_id, user_id, text)

        assert refused.value.code == "source_too_large"
        assert await stored(factory, case_id) == (0, 0, 1)


async def test_every_source_carries_its_own_overhead_in_the_count(monkeypatch):
    monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", SOURCE_OVERHEAD_TOKENS + 50)
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)

        await add_text(factory, case_id, user_id, "a")
        with pytest.raises(SourceError) as refused:
            await add_text(factory, case_id, user_id, "a")

        assert refused.value.code == "source_too_large"


async def test_a_document_over_the_ceiling_is_refused_and_leaves_nothing_behind(monkeypatch):
    text = (SENTENCE * 20).strip()
    monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", weight_in_payload(text) - 1)
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)

        with pytest.raises(SourceError) as refused:
            await add_document(factory, case_id, user_id, text)

        assert refused.value.code == "source_too_large"
        assert refused.value.status_code == 413
        assert await stored(factory, case_id) == (0, 0, 1)


async def test_a_source_cannot_be_added_while_the_case_is_being_analysed():
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)

        with analysing(case_id):
            with pytest.raises(SourceError) as text_refused:
                await add_text(factory, case_id, user_id, SENTENCE)
            with pytest.raises(SourceError) as document_refused:
                await add_document(factory, case_id, user_id, SENTENCE)

        assert text_refused.value.code == document_refused.value.code == "analysis_in_progress"
        assert text_refused.value.status_code == document_refused.value.status_code == 409
        assert await stored(factory, case_id) == (0, 0, 1)

        await add_text(factory, case_id, user_id, SENTENCE)
        assert await stored(factory, case_id) == (1, 0, 2)


async def test_the_source_routes_answer_with_the_coded_refusals(monkeypatch):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        async with signed_in(factory, user_id) as client:
            monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", 20)
            too_large = await client.post(
                f"/cases/{case_id}/sources", json={"exact_text": SENTENCE * 10}
            )
            monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", SOURCE_TOKEN_BUDGET)
            with analysing(case_id):
                busy = await client.post(f"/cases/{case_id}/sources", json={"exact_text": SENTENCE})
            too_long = await client.post(
                f"/cases/{case_id}/sources", json={"exact_text": "a" * 250_001}
            )
            heavy = await client.post(
                f"/cases/{case_id}/sources", json={"exact_text": (SENTENCE * 4_000)[:250_000]}
            )
            accepted = await client.post(
                f"/cases/{case_id}/sources", json={"exact_text": (SENTENCE * 2_000)[:120_000]}
            )

        assert too_large.status_code == 413
        assert too_large.json()["detail"]["code"] == "source_too_large"
        assert busy.status_code == 409
        assert busy.json()["detail"]["code"] == "analysis_in_progress"
        assert too_long.status_code == 422
        assert heavy.status_code == 413
        assert heavy.json()["detail"]["code"] == "source_too_large"
        assert accepted.status_code == 201


async def test_a_chat_message_has_a_length_limit(monkeypatch):
    async def answered_by_the_model(**_kwargs):
        raise AssertionError("an over-long message reached the chat")

    monkeypatch.setattr(chat_router, "send_case_message", answered_by_the_model)
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        async with signed_in(factory, user_id) as client:
            refused = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "a" * 4_001}
            )

        assert refused.status_code == 422


async def blocked_analysis(monkeypatch, factory):
    entered, release = asyncio.Event(), asyncio.Event()
    runs: list[None] = []

    async def pipeline(_data):
        runs.append(None)
        entered.set()
        await release.wait()
        return AnalysisArtifacts(trace=CaseAnalysisTrace.model_validate(TRACE))

    monkeypatch.setattr(
        analysis_router,
        "run_case_analysis",
        partial(run_case_analysis, session_factory=factory, pipeline=pipeline),
    )
    return entered, release, runs


async def test_a_second_analysis_of_a_case_is_refused_while_one_is_running(monkeypatch):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        entered, release, runs = await blocked_analysis(monkeypatch, factory)
        async with signed_in(factory, user_id) as client:
            first = asyncio.create_task(client.post(f"/cases/{case_id}/analysis"))
            try:
                await asyncio.wait_for(entered.wait(), WAIT)
                second = await asyncio.wait_for(client.post(f"/cases/{case_id}/analysis"), WAIT)
            finally:
                release.set()
            finished = await first
            third = await client.post(f"/cases/{case_id}/analysis")

        assert second.status_code == 409
        assert second.json()["detail"]["code"] == "analysis_in_progress"
        assert finished.status_code == 200
        assert third.status_code == 200
        assert len(runs) == 2, "the refused request ran nothing"


async def test_two_analyses_asked_for_at_once_run_only_one(monkeypatch):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        entered, release, runs = await blocked_analysis(monkeypatch, factory)
        async with signed_in(factory, user_id) as client:
            both = asyncio.gather(
                client.post(f"/cases/{case_id}/analysis"),
                client.post(f"/cases/{case_id}/analysis"),
            )
            try:
                await asyncio.wait_for(entered.wait(), WAIT)
                await asyncio.sleep(0.05)
            finally:
                release.set()
            replies = await asyncio.wait_for(both, WAIT)

        assert sorted(reply.status_code for reply in replies) == [200, 409]
        assert len(runs) == 1


async def test_a_streamed_second_analysis_gets_the_refusal_as_an_error_event(monkeypatch):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        entered, release, _ = await blocked_analysis(monkeypatch, factory)
        async with signed_in(factory, user_id) as client:
            first = asyncio.create_task(client.post(f"/cases/{case_id}/analysis"))
            try:
                await asyncio.wait_for(entered.wait(), WAIT)
                second = await asyncio.wait_for(
                    client.post(
                        f"/cases/{case_id}/analysis", headers={"accept": "text/event-stream"}
                    ),
                    WAIT,
                )
            finally:
                release.set()
            await first

        assert "event: error" in second.text
        assert '"status": 409' in second.text
        assert "analysis_in_progress" in second.text
