import asyncio
from uuid import uuid4

from isolated_database import isolated_database

from app.models import Case
from app.schemas.sources import CaseSourceRead
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
