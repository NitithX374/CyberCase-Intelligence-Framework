from __future__ import annotations

import re
from collections.abc import Mapping
from copy import deepcopy


_TARGET_IDENTIFIERS = {
    "fact": ("facts", "fact_id", "F"),
    "entity": ("entities", "entity_id", "ENT"),
    "relationship": ("relationships", "relationship_id", "REL"),
    "evidence": ("evidence", "evidence_id", "E"),
    "timeline": ("timeline", "event_id", "T"),
    "impact": ("impacts", "impact_id", "IMP"),
    "missing_information": ("missing_information", "missing_id", "MISS"),
}
_PLACEHOLDER_IDS = {
    "unknown",
    "none",
    "null",
    "n/a",
    "na",
    "unavailable",
    "not_provided",
    "not-provided",
}
_REFERENCE_FIELDS = {
    "relationship": {
        "subject_entity_id": "entity",
        "object_entity_id": "entity",
    },
    "timeline": {
        "actors": "entity",
        "evidence_ids": "evidence",
    },
    "impact": {
        "affected_entity_ids": "entity",
    },
}


def normalize_provider_delta_payload(
    payload: object,
    current_case_state: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise TypeError("Case State delta payload must be an object")
    normalized = deepcopy(dict(payload))
    changes = normalized.get("changes")
    if not isinstance(changes, list):
        return normalized

    used_ids = _collect_used_ids(current_case_state, changes)
    remapped_ids: dict[str, dict[str, str]] = {
        target_type: {} for target_type in _TARGET_IDENTIFIERS
    }

    for raw_change in changes:
        if not isinstance(raw_change, dict):
            continue
        target_type = raw_change.get("target_type")
        if target_type not in _TARGET_IDENTIFIERS:
            continue
        if raw_change.get("field") is not None or raw_change.get("old_value") is not None:
            continue
        new_value = raw_change.get("new_value")
        if not isinstance(new_value, dict):
            continue

        _, id_field, _ = _TARGET_IDENTIFIERS[target_type]
        target_id = raw_change.get("target_id")
        value_id = new_value.get(id_field)
        stable_id = _stable_existing_id(target_id, value_id)
        if stable_id is None:
            stable_id = _next_stable_id(target_type, used_ids[target_type])
        used_ids[target_type].add(stable_id)

        for provider_id in (target_id, value_id):
            if not _is_placeholder_id(provider_id):
                continue
            existing = remapped_ids[target_type].get(str(provider_id))
            if existing is not None and existing != stable_id:
                raise ValueError("ADD placeholder IDs must be unique per target type")
            remapped_ids[target_type][str(provider_id)] = stable_id

        if _is_placeholder_id(target_id) or _is_placeholder_id(value_id):
            raw_change["target_id"] = stable_id
            new_value[id_field] = stable_id

        if target_type == "fact" and new_value.get("category") == "unknown":
            new_value["category"] = "other"

    _rewrite_added_references(changes, remapped_ids)
    return normalized


def _collect_used_ids(
    current_case_state: Mapping[str, object],
    changes: list[object],
) -> dict[str, set[str]]:
    used_ids: dict[str, set[str]] = {
        target_type: set() for target_type in _TARGET_IDENTIFIERS
    }
    for target_type, (collection_name, id_field, _) in _TARGET_IDENTIFIERS.items():
        collection = current_case_state.get(collection_name)
        if isinstance(collection, list):
            used_ids[target_type].update(
                str(item[id_field])
                for item in collection
                if isinstance(item, Mapping) and isinstance(item.get(id_field), str)
            )
    for raw_change in changes:
        if not isinstance(raw_change, Mapping):
            continue
        target_type = raw_change.get("target_type")
        target_id = raw_change.get("target_id")
        if target_type in used_ids and isinstance(target_id, str):
            if not _is_placeholder_id(target_id):
                used_ids[target_type].add(target_id)
    return used_ids


def _stable_existing_id(target_id: object, value_id: object) -> str | None:
    stable_target = target_id if isinstance(target_id, str) and not _is_placeholder_id(target_id) else None
    stable_value = value_id if isinstance(value_id, str) and not _is_placeholder_id(value_id) else None
    if stable_target is not None and stable_value is not None:
        return stable_target if stable_target == stable_value else None
    return stable_target or stable_value


def _next_stable_id(target_type: str, used_ids: set[str]) -> str:
    prefix = _TARGET_IDENTIFIERS[target_type][2]
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$", re.IGNORECASE)
    next_number = max(
        (int(match.group(1)) for value in used_ids if (match := pattern.match(value))),
        default=0,
    ) + 1
    candidate = f"{prefix}-{next_number:03d}"
    while candidate in used_ids:
        next_number += 1
        candidate = f"{prefix}-{next_number:03d}"
    return candidate


def _is_placeholder_id(value: object) -> bool:
    if not isinstance(value, str):
        return True
    normalized = value.strip().casefold()
    return not normalized or normalized in _PLACEHOLDER_IDS or normalized.startswith("auto-")


def _rewrite_added_references(
    changes: list[object],
    remapped_ids: Mapping[str, Mapping[str, str]],
) -> None:
    for raw_change in changes:
        if not isinstance(raw_change, dict):
            continue
        target_type = raw_change.get("target_type")
        new_value = raw_change.get("new_value")
        if not isinstance(target_type, str) or not isinstance(new_value, dict):
            continue
        for field, referenced_type in _REFERENCE_FIELDS.get(target_type, {}).items():
            value = new_value.get(field)
            replacements = remapped_ids[referenced_type]
            if isinstance(value, str):
                new_value[field] = replacements.get(value, value)
            elif isinstance(value, list):
                new_value[field] = [
                    replacements.get(item, item) if isinstance(item, str) else item
                    for item in value
                ]
