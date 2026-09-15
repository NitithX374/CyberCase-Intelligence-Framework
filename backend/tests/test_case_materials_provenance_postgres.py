import asyncio
from uuid import uuid4

from app.models import Case
from app.services.case_materials import CaseMaterialsService
from run_recovery_support import isolated_database


def test_document_receive_binds_page_spans_to_case_evidence():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Document provenance"))
            async with factory() as db, db.begin():
                await CaseMaterialsService(db).add_document(
                    case_id=case_id,
                    user_id=None,
                    filename="case.pdf",
                    mime_type="application/pdf",
                    content=b"original bytes",
                    extraction={
                        "provider": "native_pdf",
                        "config_json": {},
                        "extracted_text": "first page\n\nsecond page",
                        "provenance_json": {
                            "pages": [
                                {"page_number": 1, "merged_text": "first page"},
                                {"page_number": 2, "merged_text": "second page"},
                            ]
                        },
                        "warnings_json": [],
                    },
                )
                sources = await CaseMaterialsService(db).list_evidence(case_id, None)
                assert len(sources) == 1
                source = sources[0]
                assert source.source_kind == "document"
                case = await db.get(Case, case_id)
                assert case is not None
                assert case.evidence_revision == 1
                pages = source.provenance_json["pages"]
                assert pages[0]["start_offset"] == 0
                assert pages[0]["end_offset"] == pages[1]["start_offset"]
                assert pages[0]["merged_text"] == "first page"

    asyncio.run(exercise())
