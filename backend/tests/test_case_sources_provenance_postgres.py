import asyncio
from uuid import uuid4

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from isolated_database import isolated_database

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Case, User
from app.schemas.sources import CaseSourceRead
from app.services.auth.credentials import create_access_token
from app.services.sources.source_service import SourceService


def test_document_receive_binds_page_spans_to_case_evidence():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Document provenance"))
            async with factory() as db, db.begin():
                await SourceService(db).add_document(
                    case_id=case_id,
                    user_id=None,
                    filename="case.pdf",
                    mime_type="application/pdf",
                    content=b"original bytes",
                    extraction={
                        "provider": "native_pdf",
                        "extracted_text": "first page\n\nsecond page",
                        "provenance_json": {
                            "pages": [
                                {"page_number": 1, "merged_text": "first page"},
                                {"page_number": 2, "merged_text": "second page"},
                            ]
                        },
                    },
                )
                sources = await SourceService(db).list_sources(case_id, None)
                assert len(sources) == 1
                source = sources[0]
                assert source.source_kind == "document"
                case = await db.get(Case, case_id)
                assert case is not None
                assert case.source_revision == 1
                pages = source.provenance_json["pages"]
                assert pages[0]["start_offset"] == 0
                assert pages[0]["end_offset"] == pages[1]["start_offset"]
                assert pages[0]["merged_text"] == "first page"

    asyncio.run(exercise())


def test_a_source_names_the_file_it_was_read_from():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Named files"))
            async with factory() as db, db.begin():
                service = SourceService(db)
                await service.add_document(
                    case_id=case_id,
                    user_id=None,
                    filename="statement.pdf",
                    mime_type="application/pdf",
                    content=b"pdf",
                    extraction={"provider": "native_pdf", "extracted_text": "Received."},
                )
                narrative = await service.add_text_source(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    text="What happened.",
                    provenance_json={},
                )
                assert CaseSourceRead.model_validate(narrative).filename is None
                listed = await service.list_sources(case_id, None)
                assert {
                    source.source_kind: CaseSourceRead.model_validate(source).filename
                    for source in listed
                } == {"document": "statement.pdf", "narrative": None}

    asyncio.run(exercise())


def test_a_signed_in_write_opens_its_own_transaction(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-for-request-sessions-1234567890")
    fastapi_app = app
    while not isinstance(fastapi_app, FastAPI):
        fastapi_app = fastapi_app.app

    async def exercise():
        async with isolated_database() as factory:
            async with factory() as db, db.begin():
                user = User(email="sources@example.com", name="Analyst", password_hash="x")
                db.add(user)
                await db.flush()
                case = Case(user_id=user.id, title="Sources over HTTP")
                db.add(case)
                await db.flush()
                user_id, case_id = user.id, case.id

            async def request_session():
                async with factory() as session:
                    yield session

            fastapi_app.dependency_overrides[get_db] = request_session
            try:
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test/api/v1",
                    cookies={settings.jwt_cookie_name: create_access_token(user_id, user.email)},
                ) as client:
                    response = await client.post(
                        f"/cases/{case_id}/sources", json={"exact_text": "What happened."}
                    )
            finally:
                fastapi_app.dependency_overrides.clear()

            assert response.status_code == 201
            assert response.json()["exact_text"] == "What happened."

    asyncio.run(exercise())
