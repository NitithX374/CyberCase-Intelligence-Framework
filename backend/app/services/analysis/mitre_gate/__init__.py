"""Which gate decides whether a case needs ATT&CK at all.

The gate is something the research compares rather than something the system
simply has, so there are three of them and one setting picks between them:

    llm       a prompt, reading the whole case at once      (the default)
    encoder   XLM-R, reading one sentence at a time
    never     no retrieval, ever -- the ablation that says
              what the technical context was worth

The mode is read on each call rather than at import, so a test or an experiment
can change it without rebuilding the pipeline.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.config import settings
from app.services.analysis.mitre_gate.llm import (
    MitreApplicabilityRecord,
    evaluate_mitre_applicability,
    skipped_mitre_applicability,
)
from app.services.sources import CaseSourceItem


async def never_applicable(*, case_sources: Sequence[CaseSourceItem]) -> MitreApplicabilityRecord:
    return skipped_mitre_applicability()


def chosen_gate():
    if settings.mitre_gate_mode == "never":
        return never_applicable
    if settings.mitre_gate_mode == "encoder":
        from app.services.analysis.mitre_gate.encoder import (
            evaluate_mitre_applicability_encoder,
        )

        return evaluate_mitre_applicability_encoder
    return evaluate_mitre_applicability


async def mitre_gate(*, case_sources: Sequence[CaseSourceItem]) -> MitreApplicabilityRecord:
    """The configured gate, resolved at the moment it is asked."""

    return await chosen_gate()(case_sources=case_sources)


__all__ = ["chosen_gate", "mitre_gate", "never_applicable"]
