from __future__ import annotations

from collections.abc import Sequence

from app.config import settings
from app.services.analysis.mitre_gate.llm import (
    MitreApplicabilityRecord,
    evaluate_mitre_applicability,
    skipped_mitre_applicability,
)
from app.services.sources.case_source_bundle import CaseSourceItem


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
    return await chosen_gate()(case_sources=case_sources)


__all__ = ["chosen_gate", "mitre_gate", "never_applicable"]
