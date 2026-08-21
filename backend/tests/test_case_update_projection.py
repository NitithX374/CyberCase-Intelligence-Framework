import unittest
from uuid import uuid4

from app.services.case_state.update_projection import (
    CASE_UPDATE_VERSION,
    build_case_update_projection,
    empty_case_state_delta,
)
from app.services.case_state.mutator import CaseStateDelta


class CaseUpdateProjectionTests(unittest.TestCase):
    def test_updated_projection_binds_adjacent_versions_and_exact_delta(self) -> None:
        parent_id = uuid4()
        child_id = uuid4()
        delta = {
            "changes": [
                {
                    "target_type": "fact",
                    "target_id": "F-002",
                    "field": None,
                    "old_value": None,
                    "new_value": {
                        "fact_id": "F-002",
                        "statement": "A login was reported.",
                        "category": "access",
                        "status": "reported",
                        "confidence": "unknown",
                    },
                }
            ]
        }

        projection = build_case_update_projection(
            parent_id=parent_id,
            parent_version=3,
            child_id=child_id,
            child_version=4,
            delta_json=delta,
        )

        self.assertEqual(projection["version"], CASE_UPDATE_VERSION)
        self.assertEqual(projection["status"], "updated")
        self.assertEqual(projection["parent_version"], 3)
        self.assertEqual(projection["child_version"], 4)
        self.assertEqual(
            projection["delta"],
            CaseStateDelta.model_validate(delta).model_dump(mode="json"),
        )

    def test_no_change_projection_keeps_one_version_and_empty_delta(self) -> None:
        version_id = uuid4()

        projection = build_case_update_projection(
            parent_id=version_id,
            parent_version=2,
            child_id=None,
            child_version=None,
            delta_json=empty_case_state_delta(),
        )

        self.assertEqual(projection["status"], "no_change")
        self.assertEqual(projection["parent_version"], 2)
        self.assertIsNone(projection["child_version"])
        self.assertEqual(projection["delta"], {"changes": []})

    def test_projection_rejects_non_adjacent_child_version(self) -> None:
        with self.assertRaisesRegex(ValueError, "immediately follow"):
            build_case_update_projection(
                parent_id=uuid4(),
                parent_version=2,
                child_id=uuid4(),
                child_version=4,
                delta_json=empty_case_state_delta(),
            )

    def test_no_change_projection_rejects_changes(self) -> None:
        with self.assertRaisesRegex(ValueError, "no-change"):
            build_case_update_projection(
                parent_id=uuid4(),
                parent_version=2,
                child_id=None,
                child_version=None,
                delta_json={
                    "changes": [
                        {
                            "target_type": "fact",
                            "target_id": "F-002",
                            "field": "status",
                            "old_value": "unknown",
                            "new_value": "reported",
                        }
                    ]
                },
            )


if __name__ == "__main__":
    unittest.main()
