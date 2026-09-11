import asyncio
from io import BytesIO
from uuid import uuid4

from pypdf import PdfReader
from sqlalchemy import select

from app.models import Case, CaseAnalysisResult, CaseRun, ChatMessage
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.rag import MitreTableRow, QueryResponse
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
    CaseMitreAssociation,
    NativeCaseAnalysisClaim,
    NativeCaseEvidenceCitation,
    NativeCaseAnalysisTrace,
)
from app.services.case_analysis.mitreApplicabilityGate import MitreApplicabilityRecord
from app.services.case_materials import CaseMaterialsService
from app.services.clients.ragClient import RagCallFailure
from app.services.reports.case_report_persistence import CaseReportService
from app.schemas.reports import CaseReportCreate
from app.services.workflow.caseRunExecution import executeCaseRun
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


def _rows(*identifiers: str) -> list[MitreTableRow]:
    return [
        MitreTableRow(
            technique_id=identifier,
            name=f"Technique {identifier}",
            tactic="Execution",
            description=f"External definition for {identifier}.",
        )
        for identifier in identifiers
    ]


def _association(technique_id: str) -> CaseMitreAssociation:
    return CaseMitreAssociation(
        association_id="MA-01",
        technique_id=technique_id,
        claim_ids=["A-01"],
        reason=f"The Case claim supports the {technique_id} mapping.",
        status="candidate_only",
        support_role="external_technical_context",
    )


async def _new_run(factory, key: str):
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title=f"Case augmentation {key}"))
    async with factory() as db, db.begin():
        source = await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The evidence reports PowerShell network activity.",
            provenance_json={"origin": "analyst-authored"},
        )
    async with factory() as db, db.begin():
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(
                idempotency_key=key,
                response_language="english",
                expected_evidence_revision=1,
            ),
        )
    return case_id, source.id, run.id


async def _scenario(
    factory,
    key: str,
    response: QueryResponse | None,
    associations: tuple[CaseMitreAssociation, ...],
    rag_failure: RagCallFailure | None = None,
):
    case_id, source_id, run_id = await _new_run(factory, key)
    applicability = _retrieve_gate(str(source_id))
    calls: list[str] = []

    async def analysis(**_kwargs):
        calls.append("analysis")
        async with factory() as db:
            run = await db.get(CaseRun, run_id)
            snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
        quote = "The evidence reports PowerShell network activity."
        return AnalysisOutput(
            answer=quote,
            trace=CaseAnalysisTrace(
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
                evidence_sha256=snapshot.text_sha256,
            ),
            execution_receipt={"calls": []},
        )

    async def gate(**_kwargs):
        calls.append("gate")
        return applicability

    async def rag(_query):
        calls.append("rag")
        if rag_failure is not None:
            raise rag_failure
        assert response is not None
        return response

    async def mapping(**_kwargs):
        calls.append("mapping")
        return list(associations)

    await executeCaseRun(
        run_id,
        session_factory=factory,
        analysis_request=analysis,
        applicability_gate=gate,
        rag_request=rag,
        mapping_request=mapping,
    )
    async with factory() as db:
        result = await db.scalar(select(CaseAnalysisResult).where(CaseAnalysisResult.run_id == run_id))
        message = await db.scalar(select(ChatMessage).where(ChatMessage.analysis_result_id == result.id))
    async with factory() as db:
        report = await CaseReportService(db).generate_report(
            case_id,
            CaseReportCreate(idempotency_key=f"report-{key}"),
            None,
        )
    async with factory() as db:
        pdf, _ = await CaseReportService(db).get_report_pdf(case_id, report.report_id, None)
    assert result is not None
    assert message is None
    assert report.source_snapshot is not None
    pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf)).pages)
    return result, message, report, pdf_text, calls


def _retrieve_gate(source_id: str) -> MitreApplicabilityRecord:
    return MitreApplicabilityRecord(
        decision="RETRIEVE",
        source_message_ids=[source_id],
        trigger_text=["The evidence reports PowerShell network activity."],
    )


def _rag_response(rows: list[MitreTableRow], retrieval_id: str = "retrieval-native") -> QueryResponse:
    return QueryResponse(
        status="completed",
        retrieval_context_id=retrieval_id,
        context="External MITRE context.",
        mitre_table=rows,
    )


def test_native_worker_skip_publishes_and_reports_not_applicable_outcome():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id, run_id = await _new_run(factory, "skip")
            calls: list[str] = []

            async def analysis(**_kwargs):
                calls.append("analysis")
                async with factory() as db:
                    run = await db.get(CaseRun, run_id)
                    snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
                quote = "The evidence reports PowerShell network activity."
                return AnalysisOutput(
                    answer=quote,
                    trace=NativeCaseAnalysisTrace(
                        analysis_mode="case_overview",
                        summary=quote,
                        claims=[NativeCaseAnalysisClaim(
                            claim_id="A-01", claim_type="reported", text=quote, epistemic_status="reported",
                            supporting_source_ids=[str(source_id)],
                            supporting_citations=[NativeCaseEvidenceCitation(source_id=str(source_id), source_revision=1, exact_quote=quote)],
                        )],
                        evidence_sha256=snapshot.text_sha256,
                    ),
                    execution_receipt={"calls": []},
                )

            async def gate(**_kwargs):
                calls.append("gate")
                return {"decision": "SKIP", "source_message_ids": [], "trigger_text": []}

            async def forbidden_rag(_query):
                raise AssertionError("SKIP must not call RAG")

            result_id = run_id
            await executeCaseRun(
                run_id,
                session_factory=factory,
                analysis_request=analysis,
                applicability_gate=gate,
                rag_request=forbidden_rag,
            )
            async with factory() as db:
                result = await db.scalar(select(CaseAnalysisResult).where(CaseAnalysisResult.run_id == result_id))
            async with factory() as db:
                report = await CaseReportService(db).generate_report(case_id, CaseReportCreate(idempotency_key="report-skip"), None)
            async with factory() as db:
                pdf, _ = await CaseReportService(db).get_report_pdf(case_id, report.report_id, None)
            assert calls == ["analysis", "gate"]
            assert result.provider_metadata_json["technical_augmentation"]["status"] == "not_applicable"
            assert report.source_snapshot["technical_augmentation"]["status"] == "not_applicable"
            assert "not applicable" in "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf)).pages)

    asyncio.run(exercise())


def test_native_worker_technical_mapping_reaches_db_publication_and_report():
    async def exercise():
        async with isolated_database() as factory:
            response = _rag_response(_rows("T1059.001"))
            result, message, report, pdf_text, calls = await _scenario(
                factory,
                "technical-repeat",
                response,
                (_association("T1059.001"),),
            )
            assert calls == ["analysis", "gate", "rag", "mapping"]
            assert result.provider_metadata_json["technical_augmentation"]["status"] == "retrieved_with_matches"
            assert result.trace_json["mitre_associations"][0]["technique_id"] == "T1059.001"
            assert message is None
            assert report.source_snapshot["technical_augmentation"]["association_ids"] == ["MA-01"]
            assert "T1059.001" in pdf_text

    asyncio.run(exercise())


def test_native_worker_empty_retrieval_reports_insufficient_context():
    async def exercise():
        async with isolated_database() as factory:
            response = _rag_response([], "retrieval-empty")
            result, _message, report, pdf_text, calls = await _scenario(
                factory, "empty-run", response, ()
            )
            assert calls == ["analysis", "gate", "rag"]
            assert result.provider_metadata_json["technical_augmentation"]["status"] == "insufficient_context"
            assert report.source_snapshot["technical_augmentation"]["status"] == "insufficient_context"
            assert "insufficient" in pdf_text.lower()

    asyncio.run(exercise())


def test_native_worker_rag_failure_is_immutable_report_outcome():
    async def exercise():
        async with isolated_database() as factory:
            result, message, report, pdf_text, calls = await _scenario(
                factory,
                "failure-run",
                None,
                (),
                RagCallFailure("rag_timeout", "provider timed out"),
            )
            assert calls == ["analysis", "gate", "rag"]
            augmentation = result.provider_metadata_json["technical_augmentation"]
            assert augmentation["status"] == "failed"
            assert augmentation["failure_code"] == "rag_timeout"
            assert message is None
            assert report.source_snapshot["technical_augmentation"]["failure_code"] == "rag_timeout"
            assert "rag_timeout" in pdf_text
            case_id = result.case_id

            async with factory() as db, db.begin():
                result_row = await db.get(CaseAnalysisResult, result.id)
                result_row.provider_metadata_json = {"technical_augmentation": {"status": "not_applicable"}}
            async with factory() as db:
                saved = await CaseReportService(db).get_report(case_id, report.report_id, None)
                saved_pdf, _ = await CaseReportService(db).get_report_pdf(case_id, report.report_id, None)
            assert saved.source_snapshot["technical_augmentation"]["failure_code"] == "rag_timeout"
            assert "rag_timeout" in "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(saved_pdf)).pages)

    asyncio.run(exercise())


def test_native_worker_partial_mapping_preserves_retrieved_only_rows_without_claiming_them():
    async def exercise():
        async with isolated_database() as factory:
            result, _message, report, pdf_text, _calls = await _scenario(
                factory,
                "partial-run",
                _rag_response(_rows("T1059.001", "T1105"), "retrieval-partial"),
                (_association("T1059.001"),),
            )
            augmentation = result.provider_metadata_json["technical_augmentation"]
            assert augmentation["status"] == "retrieved_with_matches"
            assert [row["technique_id"] for row in augmentation["mitre_table"]] == ["T1059.001", "T1105"]
            assert report.source_snapshot["technical_augmentation"]["association_ids"] == ["MA-01"]
            assert "T1059.001" in pdf_text
            assert "T1105" not in pdf_text

    asyncio.run(exercise())


def test_native_worker_no_supported_match_is_distinct_from_empty_context():
    async def exercise():
        async with isolated_database() as factory:
            _result, _message, report, pdf_text, calls = await _scenario(
                factory,
                "no-match-run",
                _rag_response(_rows("T1018"), "retrieval-no-match"),
                (),
            )
            assert calls == ["analysis", "gate", "rag", "mapping"]
            assert report.source_snapshot["technical_augmentation"]["status"] == "retrieved_without_supported_match"
            assert "no supported Case association" in pdf_text

    asyncio.run(exercise())
