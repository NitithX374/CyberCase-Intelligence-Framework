from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from uuid import UUID

from app.services.case_state.delta_models import (
    CaseStateDelta,
    CaseStateDeltaValue,
    CaseStateMutationFailure,
)
from app.services.extraction.llm_extraction import normalize_case_state, validate_baseline_extraction

def validate_case_state_delta(
    delta: CaseStateDelta | Mapping[str, object],
    *,
    source_message_id: UUID | None = None,
) -> CaseStateDelta:
    """Validate the delta contract before it reaches the merge."""

    if isinstance(delta, CaseStateDelta):
        return delta
    if isinstance(delta, Mapping):
        changes = delta.get("changes", [])
        return CaseStateDelta.model_validate({"changes": changes})
    raise TypeError(f"Cannot validate {type(delta)} as CaseStateDelta")


_TARGET_COLLECTIONS: dict[str, tuple[str, str]] = {
    "fact": ("facts", "fact_id"),
    "entity": ("entities", "entity_id"),
    "relationship": ("relationships", "relationship_id"),
    "evidence": ("evidence", "evidence_id"),
    "timeline": ("timeline", "event_id"),
    "impact": ("impacts", "impact_id"),
    "missing_information": ("missing_information", "missing_id"),
}


def _delta_value_mapping(
    value: CaseStateDeltaValue | None,
) -> dict[str, object]:
    if isinstance(value, CaseStateDeltaValue):
        return value.model_dump(mode="json", exclude_none=True)
    return {}


def apply_case_state_delta(
    parent_state: Mapping[str, object],
    delta: CaseStateDelta | Mapping[str, object],
    *,
    source_message_id: UUID | None = None,
) -> dict[str, object]:
    """Apply a validated delta without mutating the persisted parent snapshot."""

    try:
        parent = normalize_case_state(deepcopy(dict(parent_state)))
        validate_baseline_extraction(parent)
    except Exception as exc:
        raise CaseStateMutationFailure(
            "case_state_parent_invalid",
            "The current Case State is invalid",
        ) from exc

    try:
        delta = validate_case_state_delta(delta)
    except Exception as exc:
        raise CaseStateMutationFailure(
            "case_state_delta_invalid",
            "The Case State delta failed structural validation",
        ) from exc
    merged = parent.model_dump(mode="json")
    if not delta.changes:
        return merged
    if source_message_id is None:
        raise CaseStateMutationFailure(
            "case_state_mutation_input_missing",
            "A source message is required to apply a Case State delta",
        )

    for change in delta.changes:
        collection_name, id_field = _TARGET_COLLECTIONS[change.target_type]
        collection = merged.get(collection_name)
        if not isinstance(collection, list):
            raise CaseStateMutationFailure(
                "case_state_delta_invalid",
                "The delta targets an invalid Case State collection",
            )
        existing = {
            item.get(id_field): index
            for index, item in enumerate(collection)
            if isinstance(item, dict) and isinstance(item.get(id_field), str)
        }
        source_id = str(source_message_id)
        if change.field is None:
            if change.target_id in existing:
                raise CaseStateMutationFailure(
                    "case_state_delta_invalid",
                    "The delta attempts to add an existing Case State item",
                )
            value = _delta_value_mapping(change.new_value)
            if value.get(id_field) != change.target_id:
                raise CaseStateMutationFailure(
                    "case_state_delta_invalid",
                    "The delta value does not match its stable target ID",
                )
            value["source_message_ids"] = [source_id]
            collection.append(value)
            continue

        if change.target_id not in existing:
            raise CaseStateMutationFailure(
                "case_state_delta_invalid",
                "The delta modifies a nonexistent Case State item",
            )
        index = existing[change.target_id]
        item = collection[index]
        if not isinstance(item, dict):
            raise CaseStateMutationFailure(
                "case_state_delta_invalid",
                "The delta target is not a structured Case State item",
            )
        if change.field in {id_field, "source_message_ids"} or change.field not in item:
            raise CaseStateMutationFailure(
                "case_state_delta_invalid",
                "The delta field is not mutable",
            )
        if item.get(change.field) != change.old_value:
            raise CaseStateMutationFailure(
                "case_state_delta_stale_target",
                "The Case State field changed before the correction was applied",
            )
        item[change.field] = deepcopy(change.new_value)
        refs = item.get("source_message_ids")
        if not isinstance(refs, list):
            refs = []
        if source_id not in {str(value) for value in refs}:
            refs.append(source_id)
        item["source_message_ids"] = refs

    try:
        validated = validate_baseline_extraction(merged)
    except Exception as exc:
        raise CaseStateMutationFailure(
            "case_state_delta_invalid",
            "The merged Case State failed structural validation",
        ) from exc
    return validated.model_dump(mode="json")
