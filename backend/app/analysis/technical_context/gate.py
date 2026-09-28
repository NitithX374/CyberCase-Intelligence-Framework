from __future__ import annotations

import logging
from collections.abc import Sequence

from app.analysis.technical_context.contracts import (
    MitreApplicabilityRecord,
    skipped_mitre_applicability,
)
from app.analysis.technical_context.gate_llm import evaluate_mitre_applicability
from app.config import settings
from app.sources.bundle import CaseSourceItem

logger = logging.getLogger(__name__)


async def never_applicable(*, case_sources: Sequence[CaseSourceItem]) -> MitreApplicabilityRecord:
    return skipped_mitre_applicability()


def chosen_gate():
    if settings.mitre_gate_mode == "never":
        return never_applicable
    if settings.mitre_gate_mode == "encoder":
        from app.analysis.technical_context.gate_encoder import evaluate_mitre_applicability_encoder

        return evaluate_mitre_applicability_encoder
    return evaluate_mitre_applicability


async def mitre_gate(*, case_sources: Sequence[CaseSourceItem]) -> MitreApplicabilityRecord:
    return await chosen_gate()(case_sources=case_sources)


def shadowing_gate():
    if settings.mitre_gate_shadow != "encoder" or settings.mitre_gate_mode != "llm":
        return None
    from app.analysis.technical_context.gate_encoder import evaluate_mitre_applicability_encoder

    return evaluate_mitre_applicability_encoder


async def mitre_shadow(
    *, case_sources: Sequence[CaseSourceItem]
) -> MitreApplicabilityRecord | None:
    gate = shadowing_gate()
    if gate is None:
        return None
    try:
        return MitreApplicabilityRecord.model_validate(await gate(case_sources=case_sources))
    except Exception as error:
        logger.warning("MITRE shadow gate unavailable: %r", error)
        return skipped_mitre_applicability("mitre_shadow_unavailable")


__all__ = ["chosen_gate", "mitre_gate", "mitre_shadow", "never_applicable", "shadowing_gate"]
