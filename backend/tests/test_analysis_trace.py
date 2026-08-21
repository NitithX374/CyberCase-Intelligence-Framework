import json
import unittest

import httpx

from app.services.case_analysis import (
    AnalysisClaim,
    CaseAnalysisFailure,
    MainCaseAnalysisService,
    MitreAssociation,
    ProviderCaseAnalysis,
)
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError,
    AnalysisTraceStructureError,
    validate_analysis_trace,
)


def _case_state() -> dict[str, object]:
    return {
        "facts": [],
        "entities": [
            {"entity_id": "ENT-001"},
            {"entity_id": "ENT-002"},
        ],
        "relationships": [
            {
                "relationship_id": "REL-001",
                "subject_entity_id": "ENT-001",
                "object_entity_id": "ENT-002",
                "status": "not_established",
            }
        ],
        "evidence": [{"evidence_id": "E-001"}],
        "timeline": [{"event_id": "T-001"}],
        "impacts": [],
        "missing_information": [],
        "warnings": [],
    }


def _claim(**overrides: object) -> AnalysisClaim:
    payload: dict[str, object] = {
        "claim_id": "A-01",
        "claim_type": "reported",
        "text": "The reported relationship remains unestablished.",
        "epistemic_status": "not_established",
        "entity_ids": ["ENT-001", "ENT-002"],
        "relationship_ids": ["REL-001"],
        "evidence_ids": ["E-001"],
        "timeline_event_ids": ["T-001"],
    }
    payload.update(overrides)
    return AnalysisClaim.model_validate(payload)


def _provider_response(
    *claims: AnalysisClaim,
    associations: list[MitreAssociation] | None = None,
) -> ProviderCaseAnalysis:
    return ProviderCaseAnalysis(
        version="analysis_trace_v1",
        answer="Safe grounded answer.",
        claims=list(claims),
        mitre_associations=associations or [],
    )


def _association(**overrides: object) -> MitreAssociation:
    payload: dict[str, object] = {
        "association_id": "MA-01",
        "technique_id": "T1078",
        "claim_ids": ["A-01"],
        "reason": "The behavior concerns use of a valid credential.",
        "status": "candidate_only",
        "support_role": "external_technical_context",
    }
    payload.update(overrides)
    return MitreAssociation.model_validate(payload)


def _mitre_table() -> list[dict[str, object]]:
    return [
        {
            "technique_id": "T1078",
            "name": "Valid Accounts",
            "entity_type": "Technique",
        },
        {
            "technique_id": "T1059.001",
            "name": "PowerShell",
            "entity_type": "Subtechnique",
        },
    ]


def _http_response(payload: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "content": [{"type": "text", "text": json.dumps(payload)}],
            "stop_reason": "end_turn",
        },
    )


class AnalysisTraceValidationTests(unittest.TestCase):
    def test_contract_uses_native_references_without_fact_or_mitre_claim_ids(self) -> None:
        properties = AnalysisClaim.model_json_schema()["properties"]

        self.assertIn("entity_ids", properties)
        self.assertIn("relationship_ids", properties)
        self.assertNotIn("fact_ids", properties)
        self.assertNotIn("mitre_technique_ids", properties)

    def test_mitre_association_contract_has_no_incident_refs_or_scores(self) -> None:
        properties = MitreAssociation.model_json_schema()["properties"]

        self.assertNotIn("entity_ids", properties)
        self.assertNotIn("relationship_ids", properties)
        self.assertNotIn("evidence_ids", properties)
        self.assertNotIn("timeline_event_ids", properties)
        self.assertNotIn("confidence", properties)
        self.assertNotIn("score", properties)

    def test_reported_claim_type_is_independent_from_not_established_status(self) -> None:
        trace = validate_analysis_trace(
            _provider_response(_claim()),
            case_state_json=_case_state(),
            mitre_table=[],
            analysis_mode="case_overview",
        )

        self.assertEqual(trace.claims[0].claim_type, "reported")
        self.assertEqual(trace.claims[0].epistemic_status, "not_established")
        self.assertEqual(trace.reference_membership, "validated")
        self.assertEqual(
            trace.semantic_entailment,
            "not_deterministically_established",
        )

    def test_entity_membership_never_marks_semantic_support(self) -> None:
        trace = validate_analysis_trace(
            _provider_response(
                _claim(
                    relationship_ids=[],
                    evidence_ids=[],
                    timeline_event_ids=[],
                    epistemic_status="unknown",
                )
            ),
            case_state_json=_case_state(),
            mitre_table=[],
            analysis_mode="question_answer",
        )

        self.assertEqual(trace.reference_membership, "validated")
        self.assertNotIn("claim_supported", trace.model_dump(mode="json"))

    def test_each_missing_native_reference_fails_membership(self) -> None:
        cases = (
            ("entity_ids", ["ENT-999"], "analysis_trace_entity_reference_invalid"),
            (
                "relationship_ids",
                ["REL-999"],
                "analysis_trace_relationship_reference_invalid",
            ),
            ("evidence_ids", ["E-999"], "analysis_trace_evidence_reference_invalid"),
            (
                "timeline_event_ids",
                ["T-999"],
                "analysis_trace_timeline_reference_invalid",
            ),
        )
        for field, value, code in cases:
            with self.subTest(field=field), self.assertRaises(
                AnalysisTraceProvenanceError
            ) as raised:
                validate_analysis_trace(
                    _provider_response(_claim(**{field: value})),
                    case_state_json=_case_state(),
                    mitre_table=[],
                    analysis_mode="case_overview",
                )
            self.assertEqual(raised.exception.code, code)

    def test_relationship_status_cannot_be_strengthened(self) -> None:
        with self.assertRaises(AnalysisTraceProvenanceError) as raised:
            validate_analysis_trace(
                _provider_response(_claim(epistemic_status="reported")),
                case_state_json=_case_state(),
                mitre_table=[],
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_relationship_status_changed",
        )

    def test_claim_cannot_merge_relationships_with_different_statuses(self) -> None:
        case_state = _case_state()
        case_state["relationships"] = [
            *case_state["relationships"],
            {
                "relationship_id": "REL-002",
                "subject_entity_id": "ENT-001",
                "object_entity_id": "ENT-002",
                "status": "reported",
            },
        ]
        with self.assertRaises(AnalysisTraceProvenanceError) as raised:
            validate_analysis_trace(
                _provider_response(
                    _claim(
                        relationship_ids=["REL-001", "REL-002"],
                    )
                ),
                case_state_json=case_state,
                mitre_table=[],
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_relationship_status_changed",
        )

    def test_duplicate_claim_ids_are_harmless_structure_failure(self) -> None:
        with self.assertRaises(AnalysisTraceStructureError) as raised:
            validate_analysis_trace(
                _provider_response(_claim(), _claim()),
                case_state_json=_case_state(),
                mitre_table=[],
                analysis_mode="case_overview",
            )

        self.assertEqual(raised.exception.code, "analysis_trace_duplicate_claim_id")

    def test_admitted_candidate_links_to_claim_without_changing_epistemic_status(self) -> None:
        trace = validate_analysis_trace(
            _provider_response(
                _claim(),
                associations=[_association()],
            ),
            case_state_json=_case_state(),
            mitre_table=_mitre_table(),
            analysis_mode="case_overview",
        )

        association = trace.mitre_associations[0]
        self.assertEqual(association.technique_id, "T1078")
        self.assertEqual(association.claim_ids, ["A-01"])
        self.assertEqual(association.status, "candidate_only")
        self.assertEqual(association.support_role, "external_technical_context")
        self.assertEqual(trace.claims[0].epistemic_status, "not_established")

    def test_non_admitted_technique_fails_provenance(self) -> None:
        with self.assertRaises(AnalysisTraceProvenanceError) as raised:
            validate_analysis_trace(
                _provider_response(
                    _claim(),
                    associations=[_association(technique_id="T9999")],
                ),
                case_state_json=_case_state(),
                mitre_table=_mitre_table(),
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_mitre_technique_not_admitted",
        )

    def test_non_technique_mitre_row_is_not_admitted(self) -> None:
        with self.assertRaises(AnalysisTraceProvenanceError) as raised:
            validate_analysis_trace(
                _provider_response(
                    _claim(),
                    associations=[_association()],
                ),
                case_state_json=_case_state(),
                mitre_table=[
                    {
                        "technique_id": "T1078",
                        "name": "Not a technique row",
                        "entity_type": "Group",
                    }
                ],
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_mitre_technique_not_admitted",
        )

    def test_association_requires_an_existing_claim(self) -> None:
        with self.assertRaises(AnalysisTraceProvenanceError) as raised:
            validate_analysis_trace(
                _provider_response(
                    _claim(),
                    associations=[_association(claim_ids=["A-99"])],
                ),
                case_state_json=_case_state(),
                mitre_table=_mitre_table(),
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_mitre_claim_reference_invalid",
        )

    def test_duplicate_association_ids_are_harmless_structure_failure(self) -> None:
        with self.assertRaises(AnalysisTraceStructureError) as raised:
            validate_analysis_trace(
                _provider_response(
                    _claim(),
                    associations=[_association(), _association()],
                ),
                case_state_json=_case_state(),
                mitre_table=_mitre_table(),
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_duplicate_association_id",
        )


class AnalysisTraceFailurePolicyTests(unittest.TestCase):
    def test_structured_response_accepts_bound_candidate_association(self) -> None:
        payload = {
            "version": "analysis_trace_v1",
            "answer": "The behavior is a candidate interpretation only.",
            "claims": [_claim().model_dump(mode="json")],
            "mitre_associations": [_association().model_dump(mode="json")],
        }

        result = MainCaseAnalysisService._parse_response(
            _http_response(payload),
            case_state_json=_case_state(),
            analysis_context={"mitre_table": _mitre_table()},
            analysis_mode="case_overview",
        )

        self.assertEqual(result.trace.mitre_associations[0].technique_id, "T1078")

    def test_unsupported_version_keeps_safe_prose_and_discards_trace(self) -> None:
        result = MainCaseAnalysisService._parse_response(
            _http_response(
                {
                    "version": "analysis_trace_v2",
                    "answer": "Safe prose remains available.",
                    "claims": [],
                    "mitre_associations": [],
                }
            ),
            case_state_json=_case_state(),
            analysis_context={"mitre_table": []},
            analysis_mode="case_overview",
        )

        self.assertEqual(result.answer, "Safe prose remains available.")
        self.assertIsNone(result.trace)
        self.assertEqual(
            result.trace_failure.failure_code,
            "analysis_trace_version_unsupported",
        )

    def test_claim_level_mitre_reference_fails_entire_result(self) -> None:
        with self.assertRaises(CaseAnalysisFailure) as raised:
            MainCaseAnalysisService._parse_response(
                _http_response(
                    {
                        "version": "analysis_trace_v1",
                        "answer": "Unsafe prose must not be shown.",
                        "claims": [
                            {
                                "claim_id": "A-01",
                                "claim_type": "reported",
                                "text": "T1078 occurred.",
                                "epistemic_status": "reported",
                                "entity_ids": [],
                                "relationship_ids": [],
                                "evidence_ids": [],
                                "timeline_event_ids": [],
                                "mitre_technique_ids": ["T1078"],
                            }
                        ],
                        "mitre_associations": [],
                    }
                ),
                case_state_json=_case_state(),
                analysis_context={"mitre_table": []},
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_claim_mitre_reference_forbidden",
        )

    def test_non_candidate_association_fails_entire_result(self) -> None:
        payload = {
            "version": "analysis_trace_v1",
            "answer": "Unsafe confirmed mapping must not be shown.",
            "claims": [],
            "mitre_associations": [
                {
                    "association_id": "MA-01",
                    "technique_id": "T1078",
                    "claim_ids": ["A-01"],
                    "reason": "Invalid certainty.",
                    "status": "confirmed",
                    "support_role": "external_technical_context",
                }
            ],
        }

        with self.assertRaises(CaseAnalysisFailure) as raised:
            MainCaseAnalysisService._parse_response(
                _http_response(payload),
                case_state_json=_case_state(),
                analysis_context={"mitre_table": _mitre_table()},
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_mitre_status_invalid",
        )

    def test_unbound_technique_fails_entire_result(self) -> None:
        payload = {
            "version": "analysis_trace_v1",
            "answer": "Unsupported mapping must not be shown.",
            "claims": [_claim().model_dump(mode="json")],
            "mitre_associations": [
                _association(technique_id="T9999").model_dump(mode="json")
            ],
        }

        with self.assertRaises(CaseAnalysisFailure) as raised:
            MainCaseAnalysisService._parse_response(
                _http_response(payload),
                case_state_json=_case_state(),
                analysis_context={"mitre_table": _mitre_table()},
                analysis_mode="case_overview",
            )

        self.assertEqual(
            raised.exception.code,
            "analysis_trace_mitre_technique_not_admitted",
        )


if __name__ == "__main__":
    unittest.main()
