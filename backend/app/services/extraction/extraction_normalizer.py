from __future__ import annotations

from collections.abc import Mapping

from app.services.extraction.extraction_contracts import (
    CaseState, LegacyBaselineExtractionV1,
)

def normalize_case_state(value: object) -> CaseState:
    """Safely normalize any case state object, mapping, or legacy payload to canonical CaseState."""

    if isinstance(value, CaseState):
        return value
    if isinstance(value, LegacyBaselineExtractionV1):
        return CaseState(
            facts=[],
            entities=value.entities,
            relationships=value.relationships,
            evidence=value.evidence,
            timeline=value.timeline,
            impacts=[],
            missing_information=value.missing_information,
            warnings=value.warnings,
        )
    if isinstance(value, Mapping):
        data = {
            "facts": value.get("facts", []),
            "entities": value.get("entities", []),
            "relationships": value.get("relationships", []),
            "evidence": value.get("evidence", []),
            "timeline": value.get("timeline", []),
            "impacts": value.get("impacts", []),
            "missing_information": value.get("missing_information", []),
            "warnings": value.get("warnings", []),
        }
        return CaseState.model_validate(data)
    raise TypeError(f"Cannot normalize {type(value)} to CaseState")
