from __future__ import annotations

import unicodedata
from collections.abc import Sequence

from pydantic import ValidationError

from app.services.case_analysis.mitre_applicability_contracts import (
    MitreApplicabilityRecord,
    ProviderMitreApplicability,
    skipped_mitre_applicability,
)
from app.services.chat.raw_evidence import RawEvidenceSource


def validate_mitre_applicability(
    payload: object,
    evidence_sources: Sequence[RawEvidenceSource],
) -> MitreApplicabilityRecord:
    try:
        provider_result = ProviderMitreApplicability.model_validate(payload)
    except ValidationError:
        return skipped_mitre_applicability("mitre_applicability_invalid_output")
    if provider_result.decision == "SKIP":
        return skipped_mitre_applicability()
    if not provider_result.source_message_ids or not provider_result.trigger_text:
        return skipped_mitre_applicability("mitre_applicability_invalid_grounding")

    source_text_by_id = {
        str(source.message_id): _normalize(source.content)
        for source in evidence_sources
    }
    cited_ids = provider_result.source_message_ids
    if any(source_id not in source_text_by_id for source_id in cited_ids):
        return skipped_mitre_applicability("mitre_applicability_invalid_grounding")

    matched_source_ids: set[str] = set()
    for trigger in provider_result.trigger_text:
        normalized_trigger = _normalize(trigger)
        matching_ids = {
            source_id
            for source_id in cited_ids
            if normalized_trigger in source_text_by_id[source_id]
        }
        if not normalized_trigger or not matching_ids:
            return skipped_mitre_applicability("mitre_applicability_invalid_grounding")
        matched_source_ids.update(matching_ids)
    if matched_source_ids != set(cited_ids):
        return skipped_mitre_applicability("mitre_applicability_invalid_grounding")
    return MitreApplicabilityRecord(
        decision="RETRIEVE",
        source_message_ids=cited_ids,
        trigger_text=provider_result.trigger_text,
    )


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value)


__all__ = ["validate_mitre_applicability"]
