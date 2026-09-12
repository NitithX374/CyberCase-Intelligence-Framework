"""Integration test: CaseRun ownership & cascade/restrict integration test.

Verifies:
1. Deleting a CaseRun cascades to its CaseAnalysisResult and RagContext.
2. Deleting a CaseRun preserves the parent Case and the CaseEvidenceSnapshot.
3. If cases.latest_analysis_result_id or chat_messages.analysis_result_id referenced the result, they are set to NULL.
4. Attempting to delete a CaseEvidenceSnapshot that is referenced by a CaseRun fails with a ForeignKeyViolation / RESTRICT error.
"""

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.models.ragContext import RagContext
from run_recovery_support import isolated_database


def test_caserun_deletion_cascades_result_and_rag_preserves_snapshot():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            snapshot_id = uuid4()
            run_id = uuid4()
            result_id = uuid4()
            retrieval_id = f"ctx-{uuid4()}"

            async with factory() as db, db.begin():
                case = Case(id=case_id, title="CaseRun Ownership Test")
                db.add(case)
                db.add(ChatThread(id=case_id, case_id=case_id, title="Ownership Thread"))

                snapshot = CaseEvidenceSnapshot(
                    id=snapshot_id,
                    case_id=case_id,
                    evidence_revision=1,
                    format_version="v1",
                    manifest_json=[],
                    input_text="Malicious actor deployed beacon.",
                    text_sha256="a" * 64,
                    manifest_sha256="b" * 64,
                )
                db.add(snapshot)
                await db.flush()

                run = CaseRun(
                    id=run_id,
                    case_id=case_id,
                    operation="analysis",
                    snapshot_id=snapshot_id,
                    idempotency_key="ownership-run-1",
                    request_fingerprint="c" * 64,
                    status="completed",
                )
                db.add(run)
                await db.flush()

                rag = RagContext(
                    retrieval_context_id=retrieval_id,
                    case_id=case_id,
                    case_run_id=run_id,
                    evidence_snapshot_id=snapshot_id,
                    query_text="beacon detection",
                    query_sha256="d" * 64,
                    context_text="T1071 Application Layer Protocol",
                    mitre_table=[{"technique_id": "T1071", "name": "Application Layer Protocol"}],
                )
                db.add(rag)
                await db.flush()

                result = CaseAnalysisResult(
                    id=result_id,
                    case_id=case_id,
                    run_id=run_id,
                    snapshot_id=snapshot_id,
                    retrieval_context_id=retrieval_id,
                    schema_version="case_analysis_trace_v1",
                    status="validated",
                    answer="Analysis complete.",
                    summary="Beacon observed.",
                    trace_json={"claims": []},
                    execution_receipt_json={"calls": []},
                )
                db.add(result)
                await db.flush()

                case.latest_analysis_result_id = result_id

                msg = ChatMessage(
                    thread_id=case_id,
                    ordinal=1,
                    role="assistant",
                    content="Report ready.",
                    message_kind="conversation",
                    analysis_result_id=result_id,
                )
                db.add(msg)

            # Verify all objects exist before deletion
            async with factory() as db:
                assert await db.get(CaseRun, run_id) is not None
                assert await db.get(CaseAnalysisResult, result_id) is not None
                assert await db.get(RagContext, retrieval_id) is not None
                assert await db.get(CaseEvidenceSnapshot, snapshot_id) is not None
                assert await db.get(Case, case_id) is not None

            # Delete the CaseRun
            async with factory() as db, db.begin():
                run_to_delete = await db.get(CaseRun, run_id)
                await db.delete(run_to_delete)

            # Verify cascade & preservation
            async with factory() as db:
                # CaseRun is gone
                assert await db.get(CaseRun, run_id) is None
                # Cascaded: CaseAnalysisResult is gone
                assert await db.get(CaseAnalysisResult, result_id) is None
                # Cascaded: RagContext is gone
                assert await db.get(RagContext, retrieval_id) is None
                # PRESERVED: CaseEvidenceSnapshot still exists!
                preserved_snapshot = await db.get(CaseEvidenceSnapshot, snapshot_id)
                assert preserved_snapshot is not None
                assert preserved_snapshot.case_id == case_id
                # PRESERVED: Case still exists, latest_analysis_result_id set to NULL
                preserved_case = await db.get(Case, case_id)
                assert preserved_case is not None
                assert preserved_case.latest_analysis_result_id is None
                # PRESERVED: ChatMessage exists, analysis_result_id set to NULL
                msg_row = await db.scalar(select(ChatMessage).where(ChatMessage.thread_id == case_id))
                assert msg_row is not None
                assert msg_row.analysis_result_id is None

    asyncio.run(exercise())


def test_caserun_snapshot_fk_restrict_prevents_premature_snapshot_deletion():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            snapshot_id = uuid4()
            run_id = uuid4()

            async with factory() as db, db.begin():
                case = Case(id=case_id, title="RESTRICT Snapshot Test")
                db.add(case)
                snapshot = CaseEvidenceSnapshot(
                    id=snapshot_id,
                    case_id=case_id,
                    evidence_revision=1,
                    format_version="v1",
                    manifest_json=[],
                    input_text="Admitted evidence text.",
                    text_sha256="1" * 64,
                    manifest_sha256="2" * 64,
                )
                db.add(snapshot)
                await db.flush()

                run = CaseRun(
                    id=run_id,
                    case_id=case_id,
                    operation="analysis",
                    snapshot_id=snapshot_id,
                    idempotency_key="restrict-run-1",
                    request_fingerprint="3" * 64,
                    status="queued",
                )
                db.add(run)

            # Attempting to delete the snapshot directly MUST raise an integrity error due to RESTRICT on fk_case_runs_snapshot_id
            async with factory() as db:
                snapshot_to_delete = await db.get(CaseEvidenceSnapshot, snapshot_id)
                await db.delete(snapshot_to_delete)
                with pytest.raises((IntegrityError, DBAPIError)) as exc_info:
                    await db.commit()
                # Ensure it specifically caught the foreign key violation
                assert "fk_case_runs_snapshot_id" in str(exc_info.value) or "foreign key constraint" in str(exc_info.value).lower()

            # Verify snapshot still exists after failed deletion
            async with factory() as db:
                persisted = await db.get(CaseEvidenceSnapshot, snapshot_id)
                assert persisted is not None

    asyncio.run(exercise())
