import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models import Case, CaseRun
from app.models.caseClarification import CaseClarification
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.schemas.caseClarifications import CaseClarificationAnswer
from app.schemas.caseRuns import CaseAnalysisCreate
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
    NativeCaseAnalysisClaim,
    NativeCaseEvidenceCitation,
    NativeCaseAnalysisTrace,
)
from app.services.case_materials import CaseMaterialsService
from app.services.followup.caseClarification import (
    CaseClarificationError,
    submit_clarification_answer,
)
from app.services.followup.caseClarification import load_case_clarification_exchanges
from app.services.followup.contracts import FollowUpResolution
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunExecution import executeCaseRun
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


async def _case(factory):
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title="Clarification history"))
        source = await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The witness reported a blue vehicle.",
            provenance_json={"origin": "test"},
        )
        return case_id, source.id


async def _enqueue(factory, case_id, key, revision):
    async with factory() as db, db.begin():
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(
                idempotency_key=key,
                response_language="english",
                expected_evidence_revision=revision,
            ),
        )
        return run.id


def _output(snapshot, source_id, quote, followup=False):
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
        evidence_sha256=snapshot.text_sha256,
    )
    return AnalysisOutput(
        answer=quote,
        trace=trace,
        execution_receipt={"test": "followup-history"},
        followup_question="When was the incident reported?" if followup else None,
        followup_metadata=(
            {"gap_id": "G-01", "topic": "Incident time", "gap_key": "topic:incident-time"}
            if followup
            else None
        ),
    )


async def _complete_initial(factory, case_id, source_id):
    run_id = await _enqueue(factory, case_id, "initial", 1)
    async with factory() as db:
        claimed = await claimCaseRun(db, run_id, "initial-worker")
        snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
    async with factory() as db:
        await complete_case_run(
            db,
            run_id,
            claimed.attempt_count,
            _output(snapshot, source_id, "The witness reported a blue vehicle.", followup=True),
        )
    return run_id


async def _answer(factory, case_id, clarification_id):
    request = CaseClarificationAnswer(
        answer="The incident was reported at 09:00.",
        idempotency_key="clarification-answer",
        response_language="english",
    )
    async with factory() as db, db.begin():
        _, run = await submit_clarification_answer(
            db,
            case_id=case_id,
            clarification_id=clarification_id,
            user_id=None,
            request=request,
        )
        return run.id, request


def test_case_followup_history_is_reconstructed_and_retry_is_bounded(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case(factory)
            await _complete_initial(factory, case_id, source_id)
            async with factory() as db:
                clarification = await db.scalar(
                    select(CaseClarification).where(CaseClarification.case_id == case_id)
                )
            answer_run_id, request = await _answer(factory, case_id, clarification.id)
            async with factory() as db:
                exchanges = await load_case_clarification_exchanges(db, case_id)
            assert len(exchanges) == 1
            assert exchanges[0].answer == request.answer
            async with factory() as db, db.begin():
                run = await db.get(CaseRun, answer_run_id, with_for_update=True)
                run.status = "failed"
                run.finished_at = datetime.now(timezone.utc)
            async with factory() as db, db.begin():
                _, retried = await submit_clarification_answer(
                    db,
                    case_id=case_id,
                    clarification_id=clarification.id,
                    user_id=None,
                    request=request,
                )
                assert retried.id == answer_run_id
                assert retried.status == "queued"

            async with factory() as db, db.begin():
                retried_run = await db.get(CaseRun, answer_run_id, with_for_update=True)
                retried_run.status = "failed"
                retried_run.finished_at = datetime.now(timezone.utc)
            newer_id = await _enqueue(factory, case_id, "newer", 2)
            async with factory() as db, db.begin():
                newer = await db.get(CaseRun, newer_id, with_for_update=True)
                newer.status = "failed"
                newer.finished_at = datetime.now(timezone.utc)
            async with factory() as db, db.begin():
                with pytest.raises(CaseClarificationError, match="superseded"):
                    await submit_clarification_answer(
                        db,
                        case_id=case_id,
                        clarification_id=clarification.id,
                        user_id=None,
                        request=request,
                    )

    asyncio.run(exercise())


def test_case_execution_passes_durable_exchanges_to_followup_policy(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case(factory)
            await _complete_initial(factory, case_id, source_id)
            async with factory() as db:
                clarification = await db.scalar(
                    select(CaseClarification).where(CaseClarification.case_id == case_id)
                )
            answer_run_id, _ = await _answer(factory, case_id, clarification.id)
            captured = {}

            async def fake_analysis(**kwargs):
                context = kwargs["analysis_context"]
                current_source_id = context["source_ids"][0]
                current_text = context["_source_text_by_source_id"][current_source_id]
                return _output_from_context(context, current_source_id, current_text)

            async def fake_followup(**kwargs):
                captured["exchanges"] = kwargs["clarification_exchanges"]
                return FollowUpResolution(question=None, metadata_json={})

            from app.services.workflow import caseRunExecution

            monkeypatch.setattr(caseRunExecution, "evaluate_followup_outcome", fake_followup)
            await executeCaseRun(
                answer_run_id,
                session_factory=factory,
                analysis_request=fake_analysis,
            )
            assert len(captured["exchanges"]) == 1
            assert captured["exchanges"][0].answer == "The incident was reported at 09:00."

    asyncio.run(exercise())


def _output_from_context(context, source_id, text):
    trace = NativeCaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=text,
        claims=[
            NativeCaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text=text,
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[
                    NativeCaseEvidenceCitation(
                        source_id=source_id,
                        source_revision=1,
                        exact_quote=text,
                    )
                ],
            )
        ],
        evidence_sha256=context["_evidence_sha256"],
    )
    return AnalysisOutput(answer=text, trace=trace, execution_receipt={"test": "history"})
