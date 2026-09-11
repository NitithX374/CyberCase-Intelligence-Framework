import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models import Case, CaseAnalysisResult, CaseRun, ChatMessage, ChatThread
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.schemas.caseRuns import CaseAnalysisCreate
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunExecution import executeCaseRun
from app.services.workflow.caseRunService import cleanupAbandonedCaseRuns
from app.services.workflow.caseRunService import CaseRunError, enqueue_case_analysis
from run_recovery_support import isolated_database


async def _case_with_source(factory):
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title="Case workflow"))
    async with factory() as db, db.begin():
        source = await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The witness reported a blue vehicle.",
            provenance_json={"origin": "analyst-authored"},
        )
        return case_id, source.id


async def _enqueue(factory, case_id, key, expected_revision=1):
    async with factory() as db, db.begin():
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(
                idempotency_key=key,
                response_language="english",
                expected_evidence_revision=expected_revision,
            ),
        )
        return run.id


def _output(snapshot: CaseEvidenceSnapshot, source_id) -> AnalysisOutput:
    quote = "The witness reported a blue vehicle."
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
        execution_receipt={"test": "case-run"},
    )


def test_case_analysis_is_case_owned_and_idempotent_under_postgres_race():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)

            async def submit():
                return await _enqueue(factory, case_id, "analysis-race")

            run_ids = await asyncio.gather(submit(), submit())
            assert run_ids[0] == run_ids[1]

            async with factory() as db:
                run = await db.get(CaseRun, run_ids[0])
                assert run is not None
                assert run.request_message_id is None
                assert run.snapshot_id is not None
                snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
                assert snapshot is not None
                assert snapshot.manifest_json[0]["source_id"] == str(source_id)
                assert await db.scalar(select(func.count()).select_from(ChatThread)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0

            with pytest.raises(CaseRunError, match="active analysis run"):
                await _enqueue(factory, case_id, "different-key")

    asyncio.run(exercise())


def test_case_analysis_completion_publishes_only_after_valid_case_run():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            run_id = await _enqueue(factory, case_id, "completion")
            captured = {}

            async def fake_analysis(**kwargs):
                captured.update(kwargs)
                async with factory() as db:
                    run = await db.get(CaseRun, run_id)
                    snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
                    return _output(snapshot, source_id)

            await executeCaseRun(
                run_id,
                session_factory=factory,
                analysis_request=fake_analysis,
            )

            async with factory() as db:
                run = await db.get(CaseRun, run_id)
                result = await db.scalar(
                    select(CaseAnalysisResult).where(CaseAnalysisResult.run_id == run_id)
                )
                assert run.status == "completed"
                assert run.request_message_id is None
                assert result is not None
                assert await db.scalar(select(func.count()).select_from(ChatThread)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0
                assert captured["analysis_context"]["source_reference_type"] == "case_evidence_source"
                assert captured["analysis_context"]["source_ids"] == [str(source_id)]

            async with factory() as db:
                snapshot_id = run.snapshot_id
            async with factory() as db:
                snapshot = await db.get(CaseEvidenceSnapshot, snapshot_id)
            async with factory() as db:
                duplicate = await complete_case_run(
                    db,
                    run_id,
                    1,
                    _output(snapshot, source_id),
                )
                assert duplicate is False

    asyncio.run(exercise())


def test_case_completion_failure_rolls_back_result_and_publication(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            run_id = await _enqueue(factory, case_id, "atomicity")
            async with factory() as db:
                claimed = await claimCaseRun(db, run_id, "worker-atomicity")
            assert claimed is not None

            async with factory() as db:
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
            assert snapshot is not None

            async def fail_publication(*_args, **_kwargs):
                raise RuntimeError("injected publication failure")

            from app.services.workflow import caseRunCompletion

            monkeypatch.setattr(
                caseRunCompletion,
                "supersede_prior_clarifications",
                fail_publication,
            )
            async with factory() as db:
                with pytest.raises(RuntimeError, match="injected publication failure"):
                    await complete_case_run(
                        db,
                        run_id,
                        claimed.attempt_count,
                        _output(snapshot, source_id),
                    )

            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatThread)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0
                run = await db.get(CaseRun, run_id)
                assert run.status == "running"

    asyncio.run(exercise())


def test_case_run_attempt_is_fenced_and_startup_cleanup_marks_it_failed():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            run_id = await _enqueue(factory, case_id, "stale-worker")
            async with factory() as db:
                claimed = await claimCaseRun(db, run_id, "worker-stale")
                assert claimed is not None
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
                assert snapshot is not None
                output = _output(snapshot, source_id)

            async with factory() as db, db.begin():
                run = await db.get(CaseRun, run_id, with_for_update=True)
            async with factory() as db:
                assert await complete_case_run(db, run_id, claimed.attempt_count - 1, output) is False

            assert await cleanupAbandonedCaseRuns(factory) == 1
            async with factory() as db:
                run = await db.get(CaseRun, run_id)
                assert run.status == "failed"
                assert run.error_code == "case_run_interrupted"
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0

    asyncio.run(exercise())


def test_case_run_atomic_claim_prevents_duplicate_execution():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            run_id = await _enqueue(factory, case_id, "atomic-claim")

            async def attempt_claim(worker_name):
                async with factory() as db:
                    return await claimCaseRun(db, run_id, worker_name)

            claimed1, claimed2 = await asyncio.gather(
                attempt_claim("worker-1"),
                attempt_claim("worker-2"),
            )
            # Exactly one worker wins the atomic CAS claim
            assert (claimed1 is not None) ^ (claimed2 is not None)
            winner = claimed1 or claimed2
            assert winner.attempt_count == 1

            async with factory() as db:
                run = await db.get(CaseRun, run_id)
                assert run.status == "running"
                assert run.attempt_count == 1

    asyncio.run(exercise())


def test_case_run_timeout_and_startup_preserves_terminal_records(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            run_id = await _enqueue(factory, case_id, "timeout-run")

            async def slow_analysis(**_kwargs):
                await asyncio.sleep(0.3)
                async with factory() as db:
                    run = await db.get(CaseRun, run_id)
                    snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
                    return _output(snapshot, source_id)

            from app.config import settings
            monkeypatch.setattr(settings, "case_run_timeout_seconds", 0.05)

            await executeCaseRun(
                run_id,
                session_factory=factory,
                analysis_request=slow_analysis,
            )

            async with factory() as db:
                timed_out_run = await db.get(CaseRun, run_id)
                assert timed_out_run.status == "failed"
                assert timed_out_run.error_code == "case_run_timeout"
                assert timed_out_run.finished_at is not None

            # Now verify startup cleanup handles both queued and running without touching completed or existing failed
            queued_id = await _enqueue(factory, case_id, "queued-clean")
            running_case_id, _ = await _case_with_source(factory)
            running_id = await _enqueue(factory, running_case_id, "running-clean")
            async with factory() as db:
                claimed = await claimCaseRun(db, running_id, "worker-running")
                assert claimed is not None

            cleaned_count = await cleanupAbandonedCaseRuns(factory)
            # Both queued_id and running_id must be cleaned; timed_out_run was already terminal
            assert cleaned_count == 2

            async with factory() as db:
                q_run = await db.get(CaseRun, queued_id)
                r_run = await db.get(CaseRun, running_id)
                t_run = await db.get(CaseRun, run_id)
                assert q_run.status == "failed"
                assert q_run.error_code == "case_run_interrupted"
                assert r_run.status == "failed"
                assert r_run.error_code == "case_run_interrupted"
                # Terminal run was untouched
                assert t_run.error_code == "case_run_timeout"

    asyncio.run(exercise())
