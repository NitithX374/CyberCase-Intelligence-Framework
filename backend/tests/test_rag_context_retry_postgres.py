"""Integration test: Early persistence of RagContext and retry reuse without re-calling RAG."""

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.ragContext import RagContext
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.rag import MitreTableRow, QueryResponse
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.workflow.caseMitreAugmentation import (
    CaseMitreAssociation,
    MitreApplicabilityRecord,
)
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunExecution import executeCaseRun
from app.services.workflow.caseRunService import (
    enqueue_case_analysis,
    requeue_failed_case_run,
)
from run_recovery_support import isolated_database


def _fake_output(evidence_sha256, source_id):
    quote = "Malicious executable powershell.exe observed connecting to C2."
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="PowerShell activity detected.",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="PowerShell execution observed.",
                epistemic_status="reported",
                supporting_source_ids=[str(source_id)],
                supporting_citations=[
                    CaseEvidenceCitation(
                        source_id=str(source_id),
                        source_revision=1,
                        exact_quote=quote,
                    )
                ],
            )
        ],
        involved_parties=[],
        timeline=[],
        impacts=[],
        evidence_sha256=evidence_sha256,
    )
    return AnalysisOutput(
        answer="Analysis: PowerShell detected.",
        trace=trace,
        execution_receipt={"calls": []},
    )


def test_rag_context_early_persistence_and_retry_reuse():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                case = Case(id=case_id, title="RAG Persistence & Retry Case")
                db.add(case)
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Malicious executable powershell.exe observed connecting to C2.",
                    provenance_json={"origin": "telemetry"},
                )
                source_id = source.id

            # 1. Enqueue Run 1
            async with factory() as db, db.begin():
                run_1 = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="run-1"),
                )
                run_1_id = run_1.id

            # Setup RAG mocks
            rag_call_count = 0

            async def mock_rag_request(query: str):
                nonlocal rag_call_count
                rag_call_count += 1
                return QueryResponse(
                    status="completed",
                    retrieval_context_id=f"retrieval-ctx-{run_1_id}",
                    context="Technique T1059.001 Command and Scripting Interpreter: PowerShell",
                    mitre_table=[
                        MitreTableRow(
                            technique_id="T1059.001",
                            name="PowerShell",
                            tactic="Execution",
                            score=0.95,
                        )
                    ],
                )

            async def mock_applicability_gate(*, source_run_id, evidence_sources):
                return MitreApplicabilityRecord(
                    decision="RETRIEVE",
                    source_message_ids=[str(source_id)],
                    trigger_text=["PowerShell"],
                    failure_code=None,
                )

            async def mock_mapping_request(*, claims, applicability, context, config, calls):
                return (
                    CaseMitreAssociation(
                        association_id="MA-01",
                        technique_id="T1059.001",
                        claim_ids=["A-01"],
                        reason="PowerShell claim maps to T1059.001",
                        status="candidate_only",
                        support_role="external_technical_context",
                    ),
                )

            async def mock_analysis_request(**kwargs):
                analysis_ctx = kwargs.get("analysis_context") or {}
                evidence_sha256 = analysis_ctx.get("_evidence_sha256")
                return _fake_output(evidence_sha256, source_id)

            # 2. Execute Run 1 - Fails at completion stage AFTER RAG retrieval & persistence
            import app.services.workflow.caseRunExecution as cre
            original_complete = cre.complete_case_run

            async def crashing_complete(*args, **kwargs):
                raise RuntimeError("Downstream completion crashed deliberately!")

            cre.complete_case_run = crashing_complete
            try:
                await executeCaseRun(
                    run_1_id,
                    session_factory=factory,
                    analysis_request=mock_analysis_request,
                    applicability_gate=mock_applicability_gate,
                    rag_request=mock_rag_request,
                    mapping_request=mock_mapping_request,
                )
            finally:
                cre.complete_case_run = original_complete

            # Verify Run 1 is failed
            async with factory() as db:
                failed_run = await db.get(CaseRun, run_1_id)
                assert failed_run.status == "failed"

                # CRITICAL: Early persistence check!
                # Even though mapping failed, RagContext MUST exist in database for this run!
                rag_row = await db.scalar(
                    select(RagContext).where(RagContext.case_run_id == run_1_id)
                )
                assert rag_row is not None
                assert rag_row.retrieval_context_id == f"retrieval-ctx-{run_1_id}"
                assert "T1059.001" in rag_row.context_text
                assert rag_call_count == 1

            # 3. Retry Run 1 (requeue and re-execute)
            async with factory() as db, db.begin():
                case = await db.get(Case, case_id)
                run_1_db = await db.get(CaseRun, run_1_id)
                await requeue_failed_case_run(db, case, run_1_db)
                assert run_1_db.status == "queued"

            # Retry execution succeeds with real complete_case_run

            await executeCaseRun(
                run_1_id,
                session_factory=factory,
                analysis_request=mock_analysis_request,
                applicability_gate=mock_applicability_gate,
                rag_request=mock_rag_request,
                mapping_request=mock_mapping_request,
            )

            # CRITICAL: RAG was NOT called again during retry! It reused persisted RagContext!
            assert rag_call_count == 1, "RAG should NOT be re-called on retry; persisted context must be reused"

            # Verify Run 1 completed successfully and result points to the reused RagContext
            async with factory() as db:
                completed_run = await db.get(CaseRun, run_1_id)
                assert completed_run.status == "completed"

                result = await db.scalar(
                    select(CaseAnalysisResult).where(CaseAnalysisResult.run_id == run_1_id)
                )
                assert result is not None
                assert result.retrieval_context_id == f"retrieval-ctx-{run_1_id}"

                # Exactly one RagContext exists for run 1
                rag_contexts = list((await db.scalars(
                    select(RagContext).where(RagContext.case_run_id == run_1_id)
                )).all())
                assert len(rag_contexts) == 1

            # 4. Contrast with a fresh run (Run 2) on the same case
            async with factory() as db, db.begin():
                run_2 = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="run-2"),
                )
                run_2_id = run_2.id

            async def mock_rag_request_2(query: str):
                nonlocal rag_call_count
                rag_call_count += 1
                return QueryResponse(
                    status="completed",
                    retrieval_context_id=f"retrieval-ctx-{run_2_id}",
                    context="Technique T1059.001 Command and Scripting Interpreter: PowerShell",
                    mitre_table=[
                        MitreTableRow(
                            technique_id="T1059.001",
                            name="PowerShell",
                            tactic="Execution",
                            score=0.95,
                        )
                    ],
                )

            await executeCaseRun(
                run_2_id,
                session_factory=factory,
                analysis_request=mock_analysis_request,
                applicability_gate=mock_applicability_gate,
                rag_request=mock_rag_request_2,
                mapping_request=mock_mapping_request,
            )

            # Fresh run DOES call RAG!
            assert rag_call_count == 2, "Fresh CaseRun must invoke RAG retrieval"

            async with factory() as db:
                rag_row_2 = await db.scalar(
                    select(RagContext).where(RagContext.case_run_id == run_2_id)
                )
                assert rag_row_2 is not None
                assert rag_row_2.retrieval_context_id == f"retrieval-ctx-{run_2_id}"

                # Total RagContext rows for case is 2 (one per run)
                total_rags = await db.scalar(
                    select(func.count()).select_from(RagContext).where(RagContext.case_id == case_id)
                )
                assert total_rags == 2

    asyncio.run(exercise())
