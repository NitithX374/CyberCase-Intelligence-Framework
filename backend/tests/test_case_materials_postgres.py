import asyncio
import hashlib
from uuid import uuid4

from sqlalchemy import select

from app.models import Case
from app.models.caseMaterials import CaseDocument
from app.services.case_materials import CaseMaterialsService, buildCaseEvidenceSnapshot
from run_recovery_support import isolated_database


def test_case_materials_are_revisioned_and_snapshots_are_reproducible():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Native evidence"))

            async with factory() as db, db.begin():
                service = CaseMaterialsService(db)
                narrative = await service.admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="The witness reported a blue vehicle.",
                    provenance_json={"origin": "analyst-authored"},
                )
                document = await service.addDocument(
                    case_id=case_id,
                    user_id=None,
                    filename="report.txt",
                    mime_type="text/plain",
                    content=b"original bytes",
                    extraction={
                        "provider": "native_test",
                        "config_json": {"mode": "native"},
                        "extracted_text": "The report records a second vehicle.",
                        "provenance_json": {"pages": [{"page_number": 1}]},
                        "warnings_json": [],
                    },
                )
                source = await service.admitExtraction(
                    case_id=case_id,
                    user_id=None,
                    extraction_id=document.extractions[0].id,
                )
                assert source.source_kind == "reviewed_document"
                narrative_id = narrative.id

            async with factory() as db, db.begin():
                snapshot = await buildCaseEvidenceSnapshot(
                    db, case_id=case_id, user_id=None
                )
                repeated = await buildCaseEvidenceSnapshot(
                    db, case_id=case_id, user_id=None
                )
                assert snapshot.id == repeated.id
                assert len(snapshot.manifest_json) == 2
                assert snapshot.text_sha256 == hashlib.sha256(
                    snapshot.input_text.encode("utf-8")
                ).hexdigest()
                assert snapshot.manifest_sha256

            async with factory() as db, db.begin():
                service = CaseMaterialsService(db)
                await service.addRevision(
                    case_id=case_id,
                    user_id=None,
                    source_id=narrative_id,
                    exact_text="The witness later corrected the vehicle colour.",
                    provenance_json={"origin": "signed-correction"},
                )

            async with factory() as db, db.begin():
                updated = await buildCaseEvidenceSnapshot(
                    db, case_id=case_id, user_id=None
                )
                assert updated.id != snapshot.id
                assert any(item["revision"] == 2 for item in updated.manifest_json)
                assert all(item["source_id"] != str(narrative_id) or item["revision"] == 2 for item in updated.manifest_json)

            async with factory() as db, db.begin():
                await CaseMaterialsService(db).archiveSource(
                    case_id=case_id,
                    user_id=None,
                    source_id=narrative_id,
                )

            async with factory() as db, db.begin():
                archived = await buildCaseEvidenceSnapshot(
                    db, case_id=case_id, user_id=None
                )
                assert all(item["source_id"] != str(narrative_id) for item in archived.manifest_json)
                saved_document = await db.scalar(
                    select(CaseDocument).where(CaseDocument.case_id == case_id)
                )
                assert saved_document.content_bytes == b"original bytes"

    asyncio.run(exercise())


def test_case_materials_case_lock_serializes_concurrent_admission():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Concurrent evidence"))

            async def admit(text):
                async with factory() as db, db.begin():
                    source = await CaseMaterialsService(db).admitText(
                        case_id=case_id,
                        user_id=None,
                        source_kind="narrative",
                        exact_text=text,
                        provenance_json={"source": text},
                    )
                    return source.id

            source_ids = await asyncio.gather(
                admit("First source"),
                admit("Second source"),
            )
            assert source_ids[0] != source_ids[1]
            async with factory() as db:
                case = await db.get(Case, case_id)
                assert case.evidence_revision == 2

    asyncio.run(exercise())
