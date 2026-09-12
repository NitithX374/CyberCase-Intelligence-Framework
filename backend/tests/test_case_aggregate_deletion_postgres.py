"""Integration test: Comprehensive Case Aggregate Deletion across all 13 canonical tables.

Verifies:
1. Complete graph population across all 13 canonical tables (User + 12 case-scoped tables).
2. Deletion via CaseService.deleteCase removes all case-scoped records and preserves the User.
3. Direct SQL DELETE FROM cases WHERE id = ... cascades cleanly through PostgreSQL foreign keys.
4. Deleting one Case does not affect records belonging to a second parallel Case.
"""

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import func, select, text

from app.models.case import Case
from app.models.caseMaterials import (
    CaseDocument,
    CaseEvidenceSnapshot,
    DocumentExtraction,
    EvidenceRevision,
    EvidenceSource,
)
from app.models.report import CaseReport
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.models.ragContext import RagContext
from app.models.user import User
from app.services.cases.caseService import CaseService
from run_recovery_support import isolated_database

CASE_SCOPED_MODELS = (
    Case,
    ChatThread,
    ChatMessage,
    CaseDocument,
    DocumentExtraction,
    EvidenceSource,
    EvidenceRevision,
    CaseEvidenceSnapshot,
    CaseRun,
    RagContext,
    CaseAnalysisResult,
    CaseReport,
)


async def _populate_case_graph(db, user_id, case_id, prefix="test"):
    # 1. Case & ChatThread
    case = Case(id=case_id, user_id=user_id, title=f"Aggregate Case {prefix}")
    db.add(case)
    thread = ChatThread(id=case_id, case_id=case_id, user_id=user_id, title=f"Thread {prefix}")
    db.add(thread)
    await db.flush()

    # 2. ChatMessages
    msg1 = ChatMessage(
        thread_id=case_id,
        ordinal=1,
        role="user",
        content=f"Initial query {prefix}",
        message_kind="conversation",
    )
    db.add(msg1)
    await db.flush()

    msg2 = ChatMessage(
        thread_id=case_id,
        ordinal=2,
        role="assistant",
        content=f"Followup question {prefix}?",
        message_kind="followup_question",
        in_reply_to_message_id=msg1.id,
    )
    db.add(msg2)
    await db.flush()

    # 3. CaseDocument & DocumentExtraction
    doc = CaseDocument(
        case_id=case_id,
        filename=f"evidence_{prefix}.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        content_sha256="d" * 64,
        content_bytes=b"sample doc content",
    )
    db.add(doc)
    await db.flush()

    ext = DocumentExtraction(
        document_id=doc.id,
        revision=1,
        provider="tesseract",
        extracted_text=f"Extracted content from document {prefix}",
        text_sha256="e" * 64,
    )
    db.add(ext)
    await db.flush()

    # 4. EvidenceSource & EvidenceRevision
    src = EvidenceSource(
        case_id=case_id,
        source_kind="narrative",
        document_id=doc.id,
        origin_message_id=msg1.id,
        source_metadata_json={"origin": "investigator_note"},
    )
    db.add(src)
    await db.flush()

    rev = EvidenceRevision(
        source_id=src.id,
        revision=1,
        exact_text=f"Admitted evidence text {prefix}",
        text_sha256="1" * 64,
        extraction_id=ext.id,
    )
    db.add(rev)
    await db.flush()

    # 5. CaseEvidenceSnapshot
    snap = CaseEvidenceSnapshot(
        case_id=case_id,
        evidence_revision=1,
        format_version="v1",
        manifest_json=[{"source_id": str(src.id), "revision": 1}],
        input_text=f"Admitted evidence text {prefix}",
        text_sha256="2" * 64,
        manifest_sha256="3" * 64,
    )
    db.add(snap)
    await db.flush()

    # 6. CaseRun
    run = CaseRun(
        case_id=case_id,
        operation="analysis",
        snapshot_id=snap.id,
        idempotency_key=f"run-{prefix}",
        request_fingerprint="4" * 64,
        status="completed",
    )
    db.add(run)
    await db.flush()

    # 7. RagContext
    retrieval_id = f"retrieval-{case_id}"
    rag = RagContext(
        retrieval_context_id=retrieval_id,
        case_id=case_id,
        case_run_id=run.id,
        evidence_snapshot_id=snap.id,
        query_text=f"mitre query {prefix}",
        query_sha256="5" * 64,
        context_text="T1059 Command and Scripting Interpreter",
        mitre_table=[{"technique_id": "T1059", "name": "CLI"}],
    )
    db.add(rag)
    await db.flush()

    # 8. CaseAnalysisResult
    res = CaseAnalysisResult(
        case_id=case_id,
        run_id=run.id,
        snapshot_id=snap.id,
        retrieval_context_id=retrieval_id,
        schema_version="case_analysis_trace_v1",
        status="validated",
        answer=f"Analysis answer {prefix}",
        summary=f"Analysis summary {prefix}",
        trace_json={"claims": []},
        execution_receipt_json={"calls": []},
    )
    db.add(res)
    await db.flush()

    # Link latest_analysis_result_id and message result link
    case.latest_analysis_result_id = res.id
    msg2.analysis_result_id = res.id

    # 9. CaseReport
    rep = CaseReport(
        case_id=case_id,
        analysis_result_id=res.id,
        evidence_snapshot_id=snap.id,
        version_number=1,
        idempotency_key=f"report-{prefix}",
        source_snapshot_json={"text": f"Admitted evidence text {prefix}"},
        source_snapshot_hash="6" * 64,
        prompt_version="v1",
        provider="test",
        model="test",
        status="completed",
        validation_status="validated",
    )
    db.add(rep)
    await db.flush()


def test_case_service_delete_case_cleans_entire_aggregate():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            user_id = uuid4()
            case_id = uuid4()

            async with factory() as db, db.begin():
                user = User(
                    id=user_id,
                    email="aggregate-owner@example.com",
                    name="Aggregate Owner",
                    oauth_provider="test",
                    oauth_subject_id="agg-owner",
                )
                db.add(user)
                await db.flush()
                await _populate_case_graph(db, user_id, case_id, prefix="svc")

            # Verify all 12 case-scoped tables have data
            async with factory() as db:
                for model in CASE_SCOPED_MODELS:
                    count = await db.scalar(select(func.count()).select_from(model))
                    assert count >= 1, f"Expected {model.__tablename__} to have records before deletion"

            # Execute deletion through CaseService
            async with factory() as db:
                await CaseService(db).deleteCase(case_id, user_id=user_id)

            # Verify every case-scoped table is 0, user remains
            async with factory() as db:
                for model in CASE_SCOPED_MODELS:
                    count = await db.scalar(select(func.count()).select_from(model))
                    assert count == 0, f"Expected {model.__tablename__} to be completely emptied, found {count}"

                user_count = await db.scalar(select(func.count()).select_from(User))
                assert user_count == 1, "User aggregate must be preserved"

    asyncio.run(exercise())


def test_direct_sql_delete_cases_cascades_entire_aggregate():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            user_id = uuid4()
            case_id = uuid4()

            async with factory() as db, db.begin():
                user = User(
                    id=user_id,
                    email="sql-owner@example.com",
                    name="SQL Owner",
                    oauth_provider="test",
                    oauth_subject_id="sql-owner",
                )
                db.add(user)
                await db.flush()
                await _populate_case_graph(db, user_id, case_id, prefix="sql")

            # Execute deletion via direct SQL
            async with factory() as db, db.begin():
                await db.execute(text("DELETE FROM cases WHERE id = :cid"), {"cid": str(case_id)})

            # Verify every case-scoped table is 0, user remains
            async with factory() as db:
                for model in CASE_SCOPED_MODELS:
                    count = await db.scalar(select(func.count()).select_from(model))
                    assert count == 0, f"Expected {model.__tablename__} to be completely cascaded, found {count}"

                user_count = await db.scalar(select(func.count()).select_from(User))
                assert user_count == 1, "User aggregate must be preserved"

    asyncio.run(exercise())


def test_multi_case_isolation_on_aggregate_deletion():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            user_id = uuid4()
            case_a_id = uuid4()
            case_b_id = uuid4()

            async with factory() as db, db.begin():
                user = User(
                    id=user_id,
                    email="multi-owner@example.com",
                    name="Multi Owner",
                    oauth_provider="test",
                    oauth_subject_id="multi-owner",
                )
                db.add(user)
                await db.flush()
                await _populate_case_graph(db, user_id, case_a_id, prefix="case_a")
                await _populate_case_graph(db, user_id, case_b_id, prefix="case_b")

            # Delete Case A
            async with factory() as db:
                await CaseService(db).deleteCase(case_a_id, user_id=user_id)

            # Verify Case A is gone, but Case B is untouched
            async with factory() as db:
                assert await db.get(Case, case_a_id) is None
                case_b = await db.get(Case, case_b_id)
                assert case_b is not None

                # Check that Case B's rows across tables still exist
                assert await db.scalar(select(func.count()).select_from(ChatThread).where(ChatThread.case_id == case_b_id)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseDocument).where(CaseDocument.case_id == case_b_id)) == 1
                assert await db.scalar(select(func.count()).select_from(EvidenceSource).where(EvidenceSource.case_id == case_b_id)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseEvidenceSnapshot).where(CaseEvidenceSnapshot.case_id == case_b_id)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseRun).where(CaseRun.case_id == case_b_id)) == 1
                assert await db.scalar(select(func.count()).select_from(RagContext).where(RagContext.case_id == case_b_id)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_b_id)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseReport).where(CaseReport.case_id == case_b_id)) == 1

    asyncio.run(exercise())
