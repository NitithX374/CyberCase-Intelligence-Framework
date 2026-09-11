import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Case, CaseAnalysisResult, CaseEvidenceSnapshot, CaseReport, CaseRun, ChatThread
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
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunExecution import executeCaseRun
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


def _mock_output(snapshot, source_id):
    quote = "Threat actor APT29 used PowerShell."
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=quote,
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text=quote,
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
        evidence_sha256=snapshot.text_sha256,
    )
    return AnalysisOutput(
        answer=quote,
        trace=trace,
        execution_receipt={"test": "early-rag-persistence"},
    )


def test_rag_context_persisted_early_before_mapping_failure():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                case = Case(id=case_id, title="RAG Persistence Test")
                db.add(case)
                db.add(ChatThread(case_id=case_id, title=case.title))
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Threat actor APT29 used PowerShell.",
                    provenance_json={"origin": "analyst-authored"},
                )
                source_id = source.id

            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(
                        idempotency_key="rag-persist-key",
                        pipeline={"version": "main_case_analysis_v1"},
                    ),
                )
                run_id = run.id

            retrieval_id = f"ctx-{uuid4()}"
            mock_rag_response = QueryResponse(
                status="completed",
                context="MITRE ATT&CK T1059.001 Command and Scripting Interpreter: PowerShell",
                mitre_table=[
                    MitreTableRow(
                        technique_id="T1059.001",
                        name="PowerShell",
                    )
                ],
                retrieval_context_id=retrieval_id,
            )

            async def fake_rag_request(text: str):
                return mock_rag_response

            async def failing_mapping_request(**kwargs):
                raise RuntimeError("Downstream mapping crashed deliberately!")

            from app.services.case_analysis.mitreApplicabilityGate import MitreApplicabilityRecord

            async def force_applicable_gate(evidence_sources, **kwargs):
                return MitreApplicabilityRecord(
                    decision="RETRIEVE",
                    source_message_ids=[str(s.message_id) for s in evidence_sources],
                    trigger_text=["PowerShell"],
                )

            async def analysis_request(**kwargs):
                async with factory() as db:
                    claimed_run = await db.get(CaseRun, run_id)
                    snapshot = await db.get(CaseEvidenceSnapshot, claimed_run.snapshot_id)
                return _mock_output(snapshot, source_id)

            # Execute the case run. Downstream mapping will fail!
            await executeCaseRun(
                run_id,
                session_factory=factory,
                analysis_request=analysis_request,
                applicability_gate=force_applicable_gate,
                rag_request=fake_rag_request,
                mapping_request=failing_mapping_request,
            )

            async with factory() as db:
                saved_run = await db.get(CaseRun, run_id)
                # Run completes with mapping failure recorded in technical_augmentation
                assert saved_run.status == "completed"

                # But crucially: RagContext WAS persisted immediately when RAG retrieval succeeded!
                rag_ctx = await db.get(RagContext, retrieval_id)
                assert rag_ctx is not None
                assert rag_ctx.case_run_id == run_id
                assert rag_ctx.case_id == case_id
                assert "PowerShell" in rag_ctx.context_text
                assert len(rag_ctx.mitre_table) >= 1
                assert (
                    rag_ctx.mitre_table[0].get("technique_id")
                    or rag_ctx.mitre_table[0].get("external_id")
                ) == "T1059.001"

    asyncio.run(exercise())


def test_rag_context_persisted_early_survives_completion_failure():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                case = Case(id=case_id, title="RAG Persistence Crash Test")
                db.add(case)
                db.add(ChatThread(case_id=case_id, title=case.title))
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Threat actor APT29 used PowerShell.",
                    provenance_json={"origin": "analyst-authored"},
                )
                source_id = source.id

            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(
                        idempotency_key="rag-persist-crash-key",
                        pipeline={"version": "main_case_analysis_v1"},
                    ),
                )
                run_id = run.id

            retrieval_id = f"ctx-crash-{uuid4()}"
            mock_rag_response = QueryResponse(
                status="completed",
                context="MITRE ATT&CK T1059.001 Command and Scripting Interpreter: PowerShell",
                mitre_table=[
                    MitreTableRow(
                        technique_id="T1059.001",
                        name="PowerShell",
                    )
                ],
                retrieval_context_id=retrieval_id,
            )

            async def fake_rag_request(text: str):
                return mock_rag_response

            from app.services.case_analysis.mitreApplicabilityGate import MitreApplicabilityRecord

            async def force_applicable_gate(evidence_sources, **kwargs):
                return MitreApplicabilityRecord(
                    decision="RETRIEVE",
                    source_message_ids=[str(s.message_id) for s in evidence_sources],
                    trigger_text=["PowerShell"],
                )

            async def analysis_request(**kwargs):
                async with factory() as db:
                    claimed_run = await db.get(CaseRun, run_id)
                    snapshot = await db.get(CaseEvidenceSnapshot, claimed_run.snapshot_id)
                return _mock_output(snapshot, source_id)

            # Deliberately make downstream completion fail by monkeypatching complete_case_run
            import app.services.workflow.caseRunExecution as cre
            original_complete = cre.complete_case_run

            async def crashing_complete(*args, **kwargs):
                raise RuntimeError("Downstream completion crashed deliberately!")

            cre.complete_case_run = crashing_complete
            try:
                await executeCaseRun(
                    run_id,
                    session_factory=factory,
                    analysis_request=analysis_request,
                    applicability_gate=force_applicable_gate,
                    rag_request=fake_rag_request,
                )
            finally:
                cre.complete_case_run = original_complete

            # Verify that the run failed
            async with factory() as db:
                saved_run = await db.get(CaseRun, run_id)
                assert saved_run.status == "failed"

                # But crucially: RagContext WAS persisted early and SURVIVED the completion crash!
                rag_ctx = await db.get(RagContext, retrieval_id)
                assert rag_ctx is not None
                assert rag_ctx.case_run_id == run_id
                assert rag_ctx.case_id == case_id
                assert "PowerShell" in rag_ctx.context_text

    asyncio.run(exercise())


def test_rag_context_foreign_key_delete_restrict():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            run_id = uuid4()
            retrieval_id = f"ctx-restrict-{uuid4()}"
            async with factory() as db, db.begin():
                case = Case(id=case_id, title="RESTRICT Test")
                db.add(case)
                db.add(ChatThread(case_id=case_id, title=case.title))
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Test for restrict deletion.",
                    provenance_json={"origin": "analyst-authored"},
                )
                source_id = source.id

            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="restrict-run"),
                )
                run_id = run.id

            async with factory() as db:
                claimed = await claimCaseRun(db, run_id, "worker-restrict")
                snapshot_id = claimed.snapshot_id

            async with factory() as db, db.begin():
                rag = RagContext(
                    retrieval_context_id=retrieval_id,
                    case_id=case_id,
                    case_run_id=run_id,
                    evidence_snapshot_id=snapshot_id,
                    query_text="query",
                    query_sha256="abc",
                    context_text="context",
                    mitre_table=[],
                )
                db.add(rag)
                await db.flush()
                trace = CaseAnalysisTrace(
                    analysis_mode="case_overview",
                    summary="summary",
                    claims=[],
                    involved_parties=[],
                    timeline=[],
                    impacts=[],
                    evidence_sha256=claimed.text_sha256,
                )
                result = CaseAnalysisResult(
                    case_id=case_id,
                    run_id=run_id,
                    snapshot_id=snapshot_id,
                    schema_version="v1",
                    status="validated",
                    answer="answer",
                    summary="summary",
                    trace_json=trace.model_dump(mode="json"),
                    retrieval_context_id=retrieval_id,
                )
                db.add(result)
                case_obj = await db.get(Case, case_id)
                case_obj.latest_analysis_result_id = result.id

            # Attempting to delete RagContext directly must fail due to RESTRICT on CaseAnalysisResult
            async with factory() as db, db.begin():
                saved_rag = await db.get(RagContext, retrieval_id)
                assert saved_rag is not None
                await db.delete(saved_rag)
                with pytest.raises(IntegrityError):
                    await db.flush()

            # Generate a report bound to the analysis result and retrieval context
            from app.services.reports.case_report_persistence import CaseReportService
            from app.schemas.reports import CaseReportCreate

            async with factory() as db:
                service = CaseReportService(db)
                report_read = await service.generate_report(
                    case_id,
                    CaseReportCreate(idempotency_key="report-restrict-key"),
                    None,
                )
                assert report_read.retrieval_context_id == retrieval_id

            # Null out CaseAnalysisResult retrieval_context_id so only CaseReport references it
            async with factory() as db, db.begin():
                saved_result = await db.get(CaseAnalysisResult, result.id)
                saved_result.retrieval_context_id = None

            # Attempting to delete RagContext must STILL fail due to RESTRICT on CaseReport
            async with factory() as db, db.begin():
                saved_rag = await db.get(RagContext, retrieval_id)
                assert saved_rag is not None
                await db.delete(saved_rag)
                with pytest.raises(IntegrityError):
                    await db.flush()

    asyncio.run(exercise())
