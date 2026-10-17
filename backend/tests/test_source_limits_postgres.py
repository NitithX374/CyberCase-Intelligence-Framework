from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from functools import partial
from types import SimpleNamespace
from uuid import uuid4

import pytest
from case_chat_support import TRACE, seeded_case
from httpx import ASGITransport, AsyncClient
from isolated_database import isolated_database
from sqlalchemy import func, select

import app.analysis.routes as analysis_router
import app.chat.routes as chat_router
import app.sources.routes as source_routes
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
from app.sources.bundle import WITH_SOURCES, analysable_bundle
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


def recognized(text: str) -> IngestedDocument:
    return IngestedDocument(
        filename="case.pdf",
        media_type="application/pdf",
        extraction_method=ExtractionMethod.DOCUMENT_RECOGNITION,
        pages=[
            DocumentPage(
                page_number=1, text=text, text_method="ocr", verification_status="machine_read"
            )
        ],
        full_text=text,
    )


class ReadAgain:
    def __init__(self, text: str) -> None:
        self.text = text
        self.read: list[tuple[bytes, str]] = []
        self.closed = False

    async def ingest(self, content: bytes, filename: str) -> IngestedDocument:
        self.read.append((content, filename))
        return recognized(self.text)

    async def aclose(self) -> None:
        self.closed = True


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


async def readings(factory, case_id) -> list[tuple[str, bool]]:
    async with factory() as db:
        rows = await db.scalars(
            select(CaseSource).where(CaseSource.case_id == case_id).order_by(CaseSource.created_at)
        )
        return [(row.exact_text, row.deactivated_at is None) for row in rows]


async def source_ids(factory, case_id) -> list[str]:
    async with factory() as db:
        rows = await db.scalars(
            select(CaseSource.id)
            .where(CaseSource.case_id == case_id)
            .order_by(CaseSource.created_at)
        )
        return [str(row) for row in rows]


async def read_bundle(factory, case_id):
    async with factory() as db:
        case = await db.scalar(select(Case).options(*WITH_SOURCES).where(Case.id == case_id))
        return analysable_bundle(case)


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


async def test_a_document_read_again_is_a_new_source_and_its_earlier_reading_is_off(monkeypatch):
    reader = ReadAgain("Text read again from the page images.")
    monkeypatch.setattr(source_routes, "build_document_ingestion_service", lambda: reader)
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        stored_document = await add_document(factory, case_id, user_id, SENTENCE)
        [earlier] = await source_ids(factory, case_id)
        async with signed_in(factory, user_id) as client:
            reply = await client.post(f"/cases/{case_id}/documents/{stored_document.id}/reingest")

        assert reply.status_code == 200
        body = reply.json()
        assert body["id"] != earlier
        assert body["document_id"] == str(stored_document.id)
        assert body["exact_text"] == "Text read again from the page images."
        assert body["deactivated_at"] is None
        assert body["filename"] == "case.pdf"
        assert body["mime_type"] == "application/pdf"
        assert body["provenance_json"]["extraction_method"] == "document_recognition"
        assert reader.read == [(b"bytes", "case.pdf")]
        assert reader.closed
        assert await stored(factory, case_id) == (2, 1, 3)
        assert await readings(factory, case_id) == [
            (SENTENCE, False),
            ("Text read again from the page images.", True),
        ]
        bundle = await read_bundle(factory, case_id)
        assert [source.source_id for source in bundle.sources] == [body["id"]]


async def test_reading_a_document_again_does_not_count_its_old_text_as_well(monkeypatch):
    text = (SENTENCE * 5).strip()
    monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", weight_in_payload(text))
    monkeypatch.setattr(source_routes, "build_document_ingestion_service", lambda: ReadAgain(text))
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        stored_document = await add_document(factory, case_id, user_id, text)
        async with signed_in(factory, user_id) as client:
            reply = await client.post(f"/cases/{case_id}/documents/{stored_document.id}/reingest")

        assert reply.status_code == 200
        assert await stored(factory, case_id) == (2, 1, 3)


async def test_a_document_that_is_not_in_the_case_is_not_read_again(monkeypatch):
    built: list[ReadAgain] = []

    def build() -> ReadAgain:
        built.append(ReadAgain(SENTENCE))
        return built[-1]

    monkeypatch.setattr(source_routes, "build_document_ingestion_service", build)
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        async with signed_in(factory, user_id) as client:
            reply = await client.post(f"/cases/{case_id}/documents/{uuid4()}/reingest")

        assert reply.status_code == 404
        assert reply.json()["detail"]["code"] == "document_not_found"
        assert built == []
        assert await stored(factory, case_id) == (0, 0, 1)


async def test_a_turned_off_source_is_left_out_of_the_analysis_until_it_is_turned_on():
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        first = await add_text(factory, case_id, user_id, SENTENCE)
        second = await add_text(factory, case_id, user_id, "The VPN logs were kept.")
        async with signed_in(factory, user_id) as client:
            off = await client.patch(f"/cases/{case_id}/sources/{first.id}", json={"active": False})
            bundle_while_off = await read_bundle(factory, case_id)
            listed = await client.get(f"/cases/{case_id}/sources")
            on = await client.patch(f"/cases/{case_id}/sources/{first.id}", json={"active": True})
            bundle_after = await read_bundle(factory, case_id)

        assert off.status_code == 200
        assert off.json()["deactivated_at"] is not None
        assert [source.source_id for source in bundle_while_off.sources] == [str(second.id)]
        assert [row["deactivated_at"] is None for row in listed.json()] == [False, True]
        assert on.status_code == 200
        assert on.json()["deactivated_at"] is None
        assert [source.source_id for source in bundle_after.sources] == [
            str(first.id),
            str(second.id),
        ]
        assert await stored(factory, case_id) == (2, 0, 5)


async def test_turning_a_source_off_twice_changes_the_case_once():
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        source = await add_text(factory, case_id, user_id, SENTENCE)
        async with signed_in(factory, user_id) as client:
            for _ in range(2):
                reply = await client.patch(
                    f"/cases/{case_id}/sources/{source.id}", json={"active": False}
                )
                assert reply.status_code == 200

        assert await stored(factory, case_id) == (1, 0, 3)


async def test_a_case_with_every_source_turned_off_has_nothing_to_analyse():
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        source = await add_text(factory, case_id, user_id, SENTENCE)
        async with signed_in(factory, user_id) as client:
            await client.patch(f"/cases/{case_id}/sources/{source.id}", json={"active": False})

        with pytest.raises(SourceError) as refused:
            await read_bundle(factory, case_id)

        assert refused.value.code == "case_sources_missing"


async def test_only_the_sources_that_are_on_count_against_the_budget(monkeypatch):
    text = (SENTENCE * 5).strip()
    monkeypatch.setattr(source_service, "SOURCE_TOKEN_BUDGET", weight_in_payload(text))
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        first = await add_text(factory, case_id, user_id, text)
        async with signed_in(factory, user_id) as client:
            await client.patch(f"/cases/{case_id}/sources/{first.id}", json={"active": False})
            added = await client.post(f"/cases/{case_id}/sources", json={"exact_text": text})
            back_on = await client.patch(
                f"/cases/{case_id}/sources/{first.id}", json={"active": True}
            )

        assert added.status_code == 201
        assert back_on.status_code == 413
        assert back_on.json()["detail"]["code"] == "source_too_large"
        assert await readings(factory, case_id) == [(text, False), (text, True)]


async def test_a_source_is_not_turned_on_or_off_while_the_case_is_analysed():
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        source = await add_text(factory, case_id, user_id, SENTENCE)
        async with signed_in(factory, user_id) as client:
            with analysing(case_id):
                busy = await client.patch(
                    f"/cases/{case_id}/sources/{source.id}", json={"active": False}
                )

        assert busy.status_code == 409
        assert busy.json()["detail"]["code"] == "analysis_in_progress"
        assert await readings(factory, case_id) == [(SENTENCE.strip(), True)]


async def test_a_source_that_is_not_in_the_case_is_not_found():
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        async with signed_in(factory, user_id) as client:
            reply = await client.patch(
                f"/cases/{case_id}/sources/{uuid4()}", json={"active": False}
            )

        assert reply.status_code == 404
        assert reply.json()["detail"]["code"] == "source_not_found"


async def test_an_earlier_reading_of_a_document_cannot_be_turned_on(monkeypatch):
    monkeypatch.setattr(
        source_routes, "build_document_ingestion_service", lambda: ReadAgain("Read again.")
    )
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        stored_document = await add_document(factory, case_id, user_id, SENTENCE)
        [earlier] = await source_ids(factory, case_id)
        async with signed_in(factory, user_id) as client:
            await client.post(f"/cases/{case_id}/documents/{stored_document.id}/reingest")
            refused = await client.patch(
                f"/cases/{case_id}/sources/{earlier}", json={"active": True}
            )

        assert refused.status_code == 409
        assert refused.json()["detail"]["code"] == "source_replaced"
        assert await readings(factory, case_id) == [(SENTENCE, False), ("Read again.", True)]


async def test_a_turned_off_document_is_not_read_again(monkeypatch):
    built: list[ReadAgain] = []

    def build() -> ReadAgain:
        built.append(ReadAgain(SENTENCE))
        return built[-1]

    monkeypatch.setattr(source_routes, "build_document_ingestion_service", build)
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None, with_source=False)
        stored_document = await add_document(factory, case_id, user_id, SENTENCE)
        [source_id] = await source_ids(factory, case_id)
        async with signed_in(factory, user_id) as client:
            await client.patch(f"/cases/{case_id}/sources/{source_id}", json={"active": False})
            refused = await client.post(f"/cases/{case_id}/documents/{stored_document.id}/reingest")

        assert refused.status_code == 409
        assert refused.json()["detail"]["code"] == "source_inactive"
        assert built == []
