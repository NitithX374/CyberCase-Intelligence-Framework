import asyncio
import hashlib
from uuid import uuid4

from app.models import Case
from app.services.case_materials import CaseMaterialsService
from run_recovery_support import isolated_database


def test_document_admission_binds_page_spans_to_the_admitted_text():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Document provenance"))
            async with factory() as db, db.begin():
                document = await CaseMaterialsService(db).addDocument(
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
                source = await CaseMaterialsService(db).admitExtraction(
                    case_id=case_id,
                    user_id=None,
                    extraction_id=document.extractions[0].id,
                )
                revision = source.revisions[0]
                pages = revision.provenance_json["pages"]
                assert pages[0]["start_offset"] == 0
                assert pages[0]["end_offset"] == pages[1]["start_offset"]
                assert pages[0]["text_sha256"] == hashlib.sha256(
                    "first page\n\n".encode()
                ).hexdigest()

            async with factory() as db, db.begin():
                revised = await CaseMaterialsService(db).addRevision(
                    case_id=case_id,
                    user_id=None,
                    source_id=source.id,
                    exact_text="first page\n\nupdated page",
                    provenance_json={
                        "pages": [
                            {"page_number": 1, "merged_text": "first page"},
                            {"page_number": 2, "merged_text": "updated page"},
                        ]
                    },
                )
                revised_pages = revised.revisions[-1].provenance_json["pages"]
                assert revised_pages[1]["start_offset"] == len("first page\n\n")
                assert revised_pages[1]["end_offset"] == len("first page\n\nupdated page")

    asyncio.run(exercise())
