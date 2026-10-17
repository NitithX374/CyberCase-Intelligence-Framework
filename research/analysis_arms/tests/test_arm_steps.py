from __future__ import annotations

import asyncio
from uuid import uuid4

import analysis_arms

from app.analysis import pipeline as pipeline_module
from app.analysis.pipeline import AnalysisInput
from app.sources.bundle import CaseSourceBundle, CaseSourceItem


def steps_run_by(monkeypatch, run) -> list[str]:
    called: list[str] = []

    def record(name):
        async def step(data, so_far, **_kwargs):
            called.append(name)
            return so_far

        return step

    for name in ("retrieve_technical_context", "write_analysis", "bind_to_case"):
        monkeypatch.setattr(pipeline_module, name, record(name))
        monkeypatch.setattr(analysis_arms, name, record(name))

    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="narrative",
        text="The finance share was encrypted overnight.",
    )
    asyncio.run(run(AnalysisInput(sources=CaseSourceBundle(revision=3, sources=(source,)))))
    return called


def test_the_verify_arm_runs_every_expensive_step(monkeypatch):
    assert steps_run_by(monkeypatch, analysis_arms.verify) == [
        "retrieve_technical_context",
        "write_analysis",
        "bind_to_case",
    ]


def test_the_baseline_arm_is_the_shipped_one_minus_binding(monkeypatch):
    direct = steps_run_by(monkeypatch, analysis_arms.direct)
    verify = steps_run_by(monkeypatch, analysis_arms.verify)

    assert direct == ["retrieve_technical_context", "write_analysis"]
    assert verify == direct + ["bind_to_case"]
