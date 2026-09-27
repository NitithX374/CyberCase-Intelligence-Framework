from __future__ import annotations

import asyncio
import threading
from uuid import uuid4

import pytest
from case_mitre_test_support import _fixtures

from app.services.analysis import pipeline as pipeline_module
from app.services.analysis.clarification import Proceed
from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseAssessmentTrace,
    CaseSourceCitation,
)
from app.services.analysis.pipeline import (
    AnalysisAdvance,
    AnalysisArtifacts,
    AnalysisInput,
    advance_case,
    bind_to_case,
    write_analysis,
)
from app.services.analysis.steps.technical_context import CaseMitreAugmentation
from app.services.analysis.technical_context_contracts import skipped_mitre_applicability
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem
from app.services.workflow.run_analysis import UnassessedAdvance, store_outcome, think
from app.services.workflow.shared import CaseUnderAnalysis, CaseWorkflowError
from experiments import analysis_arms


def case_with_one_narrative(
    text: str = "The finance share was encrypted overnight.",
) -> tuple[CaseSourceBundle, CaseAnalysisTrace]:
    source_id = str(uuid4())
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The finance share was encrypted.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=text)],
    )
    bundle = CaseSourceBundle(
        revision=3,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=text),),
    )
    return bundle, CaseAnalysisTrace(
        analysis_mode="case_overview", summary=claim.text, claims=[claim]
    )


def steps_run_by(monkeypatch, run) -> list[str]:
    called: list[str] = []

    def record(name):
        async def step(data, so_far, **_kwargs):
            called.append(name)
            return so_far

        return step

    for name in ("retrieve_technical_context", "write_analysis", "bind_to_case"):
        monkeypatch.setattr(pipeline_module, name, record(name))
    monkeypatch.setattr(
        analysis_arms, "retrieve_technical_context", record("retrieve_technical_context")
    )
    monkeypatch.setattr(analysis_arms, "write_analysis", record("write_analysis"))
    monkeypatch.setattr(analysis_arms, "bind_to_case", record("bind_to_case"))

    bundle, _ = case_with_one_narrative()
    asyncio.run(run(AnalysisInput(sources=bundle)))
    return called


def test_the_verify_arm_runs_every_expensive_step(monkeypatch):
    assert steps_run_by(monkeypatch, analysis_arms.verify) == [
        "retrieve_technical_context",
        "write_analysis",
        "bind_to_case",
    ]


def test_assessment_question_short_circuits_every_expensive_step(monkeypatch):
    calls: list[str] = []

    async def assessment(_data):
        return CaseAssessmentTrace.model_validate(
            {
                "gaps": [
                    {
                        "gap_id": "G-01",
                        "gap_key": "incident:time",
                        "topic": "Incident time",
                        "status": "NOT_PROVIDED",
                        "description": "The incident time is missing.",
                        "reason": "Timing affects the chronology.",
                        "priority": "high",
                        "askable": True,
                        "clarification_question": "When did the incident happen?",
                    }
                ]
            }
        )

    async def expensive(name):
        calls.append(name)
        raise AssertionError(f"{name} ran after assessment decided to ask")

    monkeypatch.setattr(pipeline_module, "assess_gaps", assessment)
    monkeypatch.setattr(
        pipeline_module,
        "retrieve_technical_context",
        lambda *_args, **_kwargs: expensive("mitre_gate_or_rag"),
    )
    monkeypatch.setattr(
        pipeline_module,
        "write_analysis",
        lambda *_args, **_kwargs: expensive("main_analysis_model"),
    )
    monkeypatch.setattr(
        pipeline_module,
        "bind_to_case",
        lambda *_args, **_kwargs: expensive("binding"),
    )

    bundle, _ = case_with_one_narrative()
    outcome = asyncio.run(advance_case(AnalysisInput(sources=bundle)))

    assert outcome.artifacts is None
    assert outcome.decision.gap.gap_key == "incident:time"
    assert calls == []


def test_assessment_with_no_question_runs_the_full_analysis(monkeypatch):
    called: list[str] = []

    async def assessment(_data):
        return CaseAssessmentTrace(gaps=[])

    def record(name):
        async def step(_data, artifacts):
            called.append(name)
            return artifacts

        return step

    monkeypatch.setattr(pipeline_module, "assess_gaps", assessment)
    for name in ("retrieve_technical_context", "write_analysis", "bind_to_case"):
        monkeypatch.setattr(pipeline_module, name, record(name))

    bundle, _ = case_with_one_narrative()
    outcome = asyncio.run(advance_case(AnalysisInput(sources=bundle)))

    assert outcome.artifacts is not None
    assert called == ["retrieve_technical_context", "write_analysis", "bind_to_case"]


def test_the_baseline_arm_is_the_shipped_one_minus_binding(monkeypatch):
    direct = steps_run_by(monkeypatch, analysis_arms.direct)
    verify = steps_run_by(monkeypatch, analysis_arms.verify)

    assert direct == ["retrieve_technical_context", "write_analysis"]
    assert verify == direct + ["bind_to_case"]


def test_a_step_left_out_means_the_model_is_given_no_technical_context():
    bundle, trace = case_with_one_narrative()
    seen = []

    async def fake_write(**kwargs):
        seen.append(kwargs)
        return trace

    artifacts = asyncio.run(
        write_analysis(AnalysisInput(sources=bundle), AnalysisArtifacts(), request=fake_write)
    )

    assert len(seen) == 1
    assert seen[0]["technical_context"] is None
    assert artifacts.trace is trace
    assert artifacts.augmentation is None


def test_only_retrieved_context_reaches_the_writer():
    _, _, bundle, applicability, context = _fixtures()
    trace = CaseAnalysisTrace(analysis_mode="case_overview", summary="Summary.", claims=[])
    seen = []

    async def fake_write(**kwargs):
        seen.append(kwargs["technical_context"])
        return trace

    for status, expected in (
        ("retrieved_from_rag", context),
        ("insufficient_context", None),
    ):
        augmentation = CaseMitreAugmentation(status, applicability, context)
        asyncio.run(
            write_analysis(
                AnalysisInput(sources=bundle),
                AnalysisArtifacts(augmentation=augmentation),
                request=fake_write,
            )
        )
        assert seen[-1] is expected, status

    skipped = CaseMitreAugmentation("not_applicable", skipped_mitre_applicability(), None)
    assert AnalysisArtifacts(augmentation=skipped).technical_context is None


def test_binding_is_what_writes_the_grounding_report():
    bundle, trace = case_with_one_narrative()
    data = AnalysisInput(sources=bundle)

    unbound = AnalysisArtifacts(trace=trace)
    bound = asyncio.run(bind_to_case(data, unbound))

    assert unbound.trace.grounding is None
    assert bound.trace.grounding is not None
    assert bound.trace.grounding.citations_verified == 1


def test_binding_runs_off_the_event_loop(monkeypatch):
    bound_on: list[int] = []
    resolve = pipeline_module.resolve_case_trace

    def recording(*args, **kwargs):
        bound_on.append(threading.get_ident())
        return resolve(*args, **kwargs)

    monkeypatch.setattr(pipeline_module, "resolve_case_trace", recording)
    bundle, trace = case_with_one_narrative()

    async def bind() -> int:
        await bind_to_case(AnalysisInput(sources=bundle), AnalysisArtifacts(trace=trace))
        return threading.get_ident()

    loop_thread = asyncio.run(bind())

    assert len(bound_on) == 1
    assert bound_on[0] != loop_thread, "binding a large source would stall every other request"


def test_the_analysis_needs_no_case_row_to_run():
    bundle, trace = case_with_one_narrative()

    async def fake_write(**kwargs):
        assert "case_id" not in kwargs and "session_factory" not in kwargs
        return trace

    artifacts = asyncio.run(
        write_analysis(
            AnalysisInput(sources=bundle, response_language="thai"),
            AnalysisArtifacts(),
            request=fake_write,
        )
    )
    assert artifacts.trace is trace


def language_the_pipeline_is_given(*texts: str) -> str:
    seen: list[str] = []

    async def pipeline(data):
        seen.append(data.response_language)

    bundle = CaseSourceBundle(
        revision=1,
        sources=tuple(
            CaseSourceItem(source_id=f"s{index}", source_kind="narrative", text=text)
            for index, text in enumerate(texts)
        ),
    )
    asyncio.run(think(pipeline, CaseUnderAnalysis(case_id=uuid4(), source_bundle=bundle)))
    return seen[0]


def test_the_analysis_language_comes_from_the_case_sources():
    assert language_the_pipeline_is_given("Files were encrypted at 02:00.") == "english"
    assert language_the_pipeline_is_given("ไฟล์ถูกเข้ารหัสเมื่อเวลา 02:00 น.") == "thai"
    assert language_the_pipeline_is_given("Server log 10.0.0.5", "ผู้เสียหายแจ้งความ") == "thai", (
        "one Thai source makes the case Thai"
    )


def test_an_analysis_from_a_substituted_pipeline_is_stored_as_one_that_asks_nothing():
    bundle, trace = case_with_one_narrative()
    artifacts = AnalysisArtifacts(trace=trace)

    async def arm(_data):
        return artifacts

    outcome = asyncio.run(think(arm, CaseUnderAnalysis(case_id=uuid4(), source_bundle=bundle)))

    assert outcome == UnassessedAdvance(
        CaseAssessmentTrace(gaps=[]), Proceed("no_eligible_gap"), artifacts
    )
    assert isinstance(outcome, AnalysisAdvance)


def test_only_an_advance_with_a_trace_is_stored():
    bundle, _ = case_with_one_narrative()
    started = CaseUnderAnalysis(case_id=uuid4(), source_bundle=bundle)
    untraced = AnalysisAdvance(CaseAssessmentTrace(gaps=[]), Proceed("no_eligible_gap"))

    for outcome, code in ((None, "analysis_result_invalid"), (untraced, "analysis_trace_missing")):
        with pytest.raises(CaseWorkflowError) as refused:
            asyncio.run(store_outcome(None, started, outcome))
        assert refused.value.code == code
