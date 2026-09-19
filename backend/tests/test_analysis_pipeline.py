"""The analysis pipeline is a list of stages, so an ablation can leave one out.

The technical-context stage used to be unreachable. The workflow took the
applicability gate and the RAG client as arguments, and every caller left both
at None, so six hundred lines of MITRE retrieval never ran against a real
analysis. A stage list makes that impossible to miss: a stage either appears in
the list or it does not.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.case_analysis.pipeline import (
    CASE_ANALYSIS_STAGES,
    AnalysisInput,
    AnalysisStage,
    TechnicalContextStage,
    analysis_stages,
    run_pipeline,
    without,
)
from app.services.sources import CaseSourceBundle, CaseSourceItem


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


def test_the_deployed_pipeline_runs_every_stage():
    assert [stage.name for stage in CASE_ANALYSIS_STAGES] == [
        "technical_context",
        "analysis",
        "verify",
    ]


def test_an_ablation_drops_a_stage_by_name():
    assert [stage.name for stage in without("technical_context")] == ["analysis", "verify"]


def test_the_two_arms_differ_by_one_stage():
    """A is the baseline; B adds the step whose worth the experiment measures."""

    direct = [stage.name for stage in analysis_stages("direct")]
    verify = [stage.name for stage in analysis_stages("verify")]
    revise = [stage.name for stage in analysis_stages("revise")]

    assert direct == ["technical_context", "analysis"]
    assert verify == direct + ["verify"]
    assert revise == verify
    # The arms that verify differ only in whether they ask for a second try.
    assert analysis_stages("verify")[-1].max_revisions == 0
    assert analysis_stages("revise")[-1].max_revisions >= 1


def test_without_the_retrieval_stage_the_model_is_given_no_technical_context():
    bundle, trace = case_with_one_narrative()
    seen = []

    async def fake_analysis(**kwargs):
        seen.append(kwargs)
        return CaseAnalysisOutput(answer="Answered.", trace=trace, execution_receipt={})

    async def unreachable_gate(**_kwargs):
        raise AssertionError("an ablated stage must not run")

    stages = without(
        "technical_context",
        stages=(
            TechnicalContextStage(applicability_gate=unreachable_gate),
            AnalysisStage(analysis_request=fake_analysis),
        ),
    )
    artifacts = asyncio.run(run_pipeline(AnalysisInput(sources=bundle), stages))

    assert len(seen) == 1
    assert seen[0]["technical_context"] is None
    assert seen[0]["retrieval_context_id"] is None
    assert artifacts.answer == "Answered."
    assert "technical_augmentation" not in artifacts.receipt


def test_the_pipeline_needs_no_case_row_to_run():
    """What the experiment depends on: sources in, artifacts out, no database."""

    bundle, trace = case_with_one_narrative()

    async def fake_analysis(**kwargs):
        assert "case_id" not in kwargs and "session_factory" not in kwargs
        return CaseAnalysisOutput(answer="Answered.", trace=trace, execution_receipt={})

    artifacts = asyncio.run(
        run_pipeline(
            AnalysisInput(sources=bundle, response_language="thai"),
            (AnalysisStage(analysis_request=fake_analysis),),
        )
    )
    assert artifacts.trace is trace
