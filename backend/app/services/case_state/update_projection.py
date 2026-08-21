from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from app.services.case_state.mutator import CaseStateDelta


CASE_UPDATE_VERSION = "case_update_v1"


def build_case_update_projection(
    *,
    parent_id: UUID,
    parent_version: int,
    child_id: UUID | None,
    child_version: int | None,
    delta_json: dict[str, object],
) -> dict[str, object]:
    delta = CaseStateDelta.model_validate(delta_json).model_dump(mode="json")
    has_child = child_id is not None and child_version is not None
    if has_child and child_version != parent_version + 1:
        raise ValueError("Case State child version must immediately follow its parent")
    if not has_child and delta["changes"]:
        raise ValueError("A no-change projection cannot contain delta changes")
    return {
        "version": CASE_UPDATE_VERSION,
        "status": "updated" if has_child else "no_change",
        "parent_case_state_version_id": str(parent_id),
        "parent_version": parent_version,
        "child_case_state_version_id": str(child_id) if child_id else None,
        "child_version": child_version,
        "delta": deepcopy(delta),
    }


def empty_case_state_delta() -> dict[str, object]:
    return CaseStateDelta(changes=[]).model_dump(mode="json")
