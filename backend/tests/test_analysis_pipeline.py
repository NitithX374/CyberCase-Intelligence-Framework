"""The production analysis runs three steps, and the arms compose those same three.

The technical-context step used to be unreachable. The workflow took the
applicability gate and the RAG client as arguments, and every caller left both
at None, so six hundred lines of MITRE retrieval never ran against a real
analysis. `analyse_case` makes that impossible to miss: the steps are named in
one function, in order, with no switch between them — and these tests hold
that shape rather than trusting it.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

from app.services.analysis import pipeline as pipeline_module
from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    analyse_case,
    bind_to_case,
    write_analysis,
)
from app.services.sources import CaseSourceBundle, CaseSourceItem
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
    """Which steps a composition actually called, in order."""

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


def test_the_shipped_analysis_runs_every_step(monkeypatch):
    assert steps_run_by(monkeypatch, analyse_case) == [
        "retrieve_technical_context",
        "write_analysis",
        "bind_to_case",
    ]


def test_the_baseline_arm_is_the_shipped_one_minus_binding(monkeypatch):
    """direct and verify differ by one step, which is what the comparison measures."""

    direct = steps_run_by(monkeypatch, analysis_arms.direct)
    verify = steps_run_by(monkeypatch, analysis_arms.verify)

    assert direct == ["retrieve_technical_context", "write_analysis"]
    assert verify == direct + ["bind_to_case"]


def test_a_step_left_out_means_the_model_is_given_no_technical_context():
    """The ablation is a composition that omits the step, not a flag it reads."""

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
    """Which is why the arm that skips it reports none — deliberately."""

    bundle, trace = case_with_one_narrative()
    data = AnalysisInput(sources=bundle)

    unbound = AnalysisArtifacts(trace=trace)
    bound = asyncio.run(bind_to_case(data, unbound))

    assert unbound.trace.grounding is None
    assert bound.trace.grounding is not None
    assert bound.receipt["verification"]["rounds"][0]["citations_verified"] == 1


def test_the_analysis_needs_no_case_row_to_run():
    """What the experiment depends on: sources in, artifacts out, no database."""

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
