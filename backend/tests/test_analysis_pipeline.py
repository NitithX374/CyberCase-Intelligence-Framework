from __future__ import annotations

import asyncio
from uuid import uuid4

from app.services.analysis import pipeline as pipeline_module
from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseAssessmentTrace,
    CaseSourceCitation,
)
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    advance_case,
    bind_to_case,
    write_analysis,
)
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem
from experiments import analysis_arms


def case_with_one_narrative() -> tuple[CaseSourceBundle, CaseAnalysisTrace]:
    source_id = str(uuid4())
    text = "The finance share was encrypted overnight."
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

    async def fake_analysis(**kwargs):
        seen.append(kwargs)
        return CaseAnalysisOutput(answer="Answered.", trace=trace, execution_receipt={})

    artifacts = asyncio.run(
        write_analysis(AnalysisInput(sources=bundle), AnalysisArtifacts(), request=fake_analysis)
    )

    assert len(seen) == 1
    assert seen[0]["technical_context"] is None
    assert seen[0]["retrieval_context_id"] is None
    assert artifacts.answer == "Answered."
    assert "technical_augmentation" not in artifacts.receipt


def test_binding_is_what_writes_the_grounding_report():
    bundle, trace = case_with_one_narrative()
    data = AnalysisInput(sources=bundle)

    unbound = AnalysisArtifacts(trace=trace)
    bound = asyncio.run(bind_to_case(data, unbound))

    assert unbound.trace.grounding is None
    assert bound.trace.grounding is not None
    assert bound.receipt["verification"]["rounds"][0]["citations_verified"] == 1


def test_the_analysis_needs_no_case_row_to_run():
    bundle, trace = case_with_one_narrative()

    async def fake_analysis(**kwargs):
        assert "case_id" not in kwargs and "session_factory" not in kwargs
        return CaseAnalysisOutput(answer="Answered.", trace=trace, execution_receipt={})

    artifacts = asyncio.run(
        write_analysis(
            AnalysisInput(sources=bundle, response_language="thai"),
            AnalysisArtifacts(),
            request=fake_analysis,
        )
    )
    assert artifacts.trace is trace
