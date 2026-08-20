"""Comprehensive tests for expanded, report-ready, source-bounded CaseState."""

import json
import unittest
from copy import deepcopy
from uuid import UUID, uuid4

from pydantic import ValidationError

from app.models.case_state import CaseStateVersion
from app.services.case_state import (
    CaseStateDelta,
    CaseStateDeltaChange,
    CaseStateDeltaValue,
    CaseStateMutationFailure,
    apply_case_state_delta,
    project_case_state_to_retrieval_query,
)
from app.services.extraction import (
    BASELINE_EXTRACTION_PROMPT_VERSION,
    BASELINE_EXTRACTION_SYSTEM_PROMPT,
    CaseState,
    ExtractedEntity,
    ExtractedEvidence,
    ExtractedFact,
    ExtractedImpact,
    ExtractedMissingInformation,
    ExtractedRelationship,
    ExtractedTimelineEvent,
    ExtractionInput,
    ExtractionSourceMessage,
    ExtractionValidationError,
    LegacyBaselineExtractionV1,
    normalize_case_state,
    validate_baseline_extraction,
)
from app.services.reports import ReportInputSnapshot, ReportSourceMessage


class CaseStateFactualCompletenessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.msg1_id = uuid4()
        self.msg2_id = uuid4()
        self.input_packet = ExtractionInput(
            thread_id=uuid4(),
            messages=[
                ExtractionSourceMessage(
                    message_id=self.msg1_id,
                    ordinal=1,
                    source_type="user_case_statement",
                    content="User reported finding weird network traffic on accounting PC.",
                ),
                ExtractionSourceMessage(
                    message_id=self.msg2_id,
                    ordinal=2,
                    source_type="clarification_answer",
                    content="Finance department lost access to their billing portal.",
                ),
            ],
        )

    def test_1_narrative_detail_retained_in_facts_layer(self) -> None:
        """A narrative assertion that does not fit entity/relationship/evidence/timeline is retained in facts."""
        fact = ExtractedFact(
            fact_id="FACT-001",
            statement="User noted an unusual smell near the server rack before the incident.",
            category="observation",
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        state = CaseState(
            facts=[fact],
            entities=[],
            relationships=[],
            evidence=[],
            timeline=[],
            impacts=[],
            missing_information=[],
            warnings=[],
        )
        validated = validate_baseline_extraction(state, self.input_packet)
        self.assertEqual(len(validated.facts), 1)
        self.assertEqual(validated.facts[0].statement, fact.statement)
        self.assertEqual(validated.facts[0].category, "observation")

    def test_2_uncertain_statement_preserves_epistemic_status(self) -> None:
        """Uncertain statements preserve suspected/not_established status without being strengthened."""
        fact_suspected = ExtractedFact(
            fact_id="FACT-002",
            statement="Malware might have been downloaded via USB drive.",
            category="action",
            status="suspected",
            confidence="low",
            source_message_ids=[self.msg1_id],
        )
        fact_not_established = ExtractedFact(
            fact_id="FACT-003",
            statement="Attacker nationality is not established.",
            category="attribution",
            status="not_established",
            confidence="unknown",
            source_message_ids=[self.msg1_id],
        )
        state = CaseState(
            facts=[fact_suspected, fact_not_established],
            entities=[],
            relationships=[],
            evidence=[],
            timeline=[],
            impacts=[],
            missing_information=[],
            warnings=[],
        )
        validated = validate_baseline_extraction(state, self.input_packet)
        self.assertEqual(validated.facts[0].status, "suspected")
        self.assertEqual(validated.facts[1].status, "not_established")

    def test_3_explicit_impact_captured_in_impacts(self) -> None:
        """Explicitly reported impacts are captured in the impacts structure."""
        entity = ExtractedEntity(
            entity_id="ENT-001",
            name="Billing Portal",
            entity_type="application",
            confidence="high",
            source_message_ids=[self.msg2_id],
        )
        impact = ExtractedImpact(
            impact_id="IMP-001",
            description="Finance department lost access to the billing portal.",
            impact_type="service_disruption",
            affected_entity_ids=["ENT-001"],
            status="reported",
            confidence="high",
            source_message_ids=[self.msg2_id],
        )
        state = CaseState(
            facts=[],
            entities=[entity],
            relationships=[],
            evidence=[],
            timeline=[],
            impacts=[impact],
            missing_information=[],
            warnings=[],
        )
        validated = validate_baseline_extraction(state, self.input_packet)
        self.assertEqual(len(validated.impacts), 1)
        self.assertEqual(validated.impacts[0].impact_type, "service_disruption")
        self.assertEqual(validated.impacts[0].affected_entity_ids, ["ENT-001"])

    def test_4_unconfirmed_impact_not_strengthened(self) -> None:
        """Suspected or unconfirmed impact preserves its status."""
        impact = ExtractedImpact(
            impact_id="IMP-002",
            description="Data exfiltration was suspected but not confirmed.",
            impact_type="data_exposure",
            affected_entity_ids=[],
            status="suspected",
            confidence="low",
            source_message_ids=[self.msg1_id],
        )
        state = CaseState(
            facts=[],
            entities=[],
            relationships=[],
            evidence=[],
            timeline=[],
            impacts=[impact],
            missing_information=[],
            warnings=[],
        )
        validated = validate_baseline_extraction(state, self.input_packet)
        self.assertEqual(validated.impacts[0].status, "suspected")

    def test_5_explicit_unresolved_information_captured(self) -> None:
        """Explicitly stated uncertainties are captured in missing_information."""
        missing = ExtractedMissingInformation(
            missing_id="MISS-001",
            description="The exact IP address used by the remote attacker is unknown.",
            importance="material",
            source_message_ids=[self.msg1_id],
        )
        state = CaseState(
            facts=[],
            entities=[],
            relationships=[],
            evidence=[],
            timeline=[],
            impacts=[],
            missing_information=[missing],
            warnings=[],
        )
        validated = validate_baseline_extraction(state, self.input_packet)
        self.assertEqual(len(validated.missing_information), 1)
        self.assertEqual(validated.missing_information[0].importance, "material")

    def test_6_invalid_provenance_reference_rejected(self) -> None:
        """Factual records with unknown source_message_ids are strictly rejected."""
        unknown_id = uuid4()
        fact = ExtractedFact(
            fact_id="FACT-001",
            statement="Invented fact from external model knowledge.",
            category="technical",
            status="reported",
            confidence="high",
            source_message_ids=[unknown_id],
        )
        state = CaseState(facts=[fact])
        with self.assertRaises(ExtractionValidationError):
            validate_baseline_extraction(state, self.input_packet)

    def test_7_collection_scoped_id_uniqueness(self) -> None:
        """IDs must be unique within each collection, but can match across collections."""
        shared_id = "ITEM-001"
        fact = ExtractedFact(
            fact_id=shared_id,
            statement="User noted suspicious login.",
            category="observation",
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        entity = ExtractedEntity(
            entity_id=shared_id,
            name="Accounting PC",
            entity_type="device",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        evidence = ExtractedEvidence(
            evidence_id=shared_id,
            title="Log dump",
            description="System event log",
            artifact_type="log",
            status="reported",
            confidence="high",
            source_type="user_reported",
            source_message_ids=[self.msg1_id],
        )
        state = CaseState(
            facts=[fact],
            entities=[entity],
            relationships=[],
            evidence=[evidence],
        )
        # Sharing ID across collections is permitted
        validated = validate_baseline_extraction(state, self.input_packet)
        self.assertEqual(len(validated.facts), 1)
        self.assertEqual(len(validated.entities), 1)
        self.assertEqual(len(validated.evidence), 1)

        # Duplicate within the same collection is rejected
        duplicate_fact = ExtractedFact(
            fact_id=shared_id,
            statement="Second fact reusing same ID in facts collection.",
            category="action",
            status="reported",
            confidence="medium",
            source_message_ids=[self.msg1_id],
        )
        invalid_state = CaseState(facts=[fact, duplicate_fact], entities=[entity])
        with self.assertRaises(ExtractionValidationError):
            validate_baseline_extraction(invalid_state, self.input_packet)

    def test_8_impact_affected_entity_id_validation(self) -> None:
        """Impact affected_entity_ids must reference valid existing entities."""
        impact = ExtractedImpact(
            impact_id="IMP-001",
            description="Server crashed",
            impact_type="service_disruption",
            affected_entity_ids=["NON-EXISTENT-ENT"],
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        state = CaseState(entities=[], impacts=[impact])
        with self.assertRaises(ExtractionValidationError):
            validate_baseline_extraction(state, self.input_packet)

    def test_9_casestate_mutation_merges_new_fields(self) -> None:
        """CaseState mutation correctly merges facts, impacts, and missing_information additions."""
        parent_state = {
            "facts": [
                {
                    "fact_id": "F-001",
                    "statement": "Initial statement.",
                    "category": "observation",
                    "status": "reported",
                    "confidence": "high",
                    "source_message_ids": [str(self.msg1_id)],
                }
            ],
            "entities": [
                {
                    "entity_id": "ENT-001",
                    "name": "Accounting PC",
                    "entity_type": "device",
                    "confidence": "high",
                    "source_message_ids": [str(self.msg1_id)],
                }
            ],
            "relationships": [],
            "evidence": [],
            "timeline": [],
            "impacts": [],
            "missing_information": [],
            "warnings": [],
        }

        delta = CaseStateDelta(
            changes=[
                CaseStateDeltaChange(
                    target_type="fact",
                    target_id="F-002",
                    field=None,
                    old_value=None,
                    new_value=CaseStateDeltaValue(
                        fact_id="F-002",
                        statement="New fact revealed in clarification.",
                        category="technical",
                        status="reported",
                        confidence="medium",
                    ),
                ),
                CaseStateDeltaChange(
                    target_type="impact",
                    target_id="IMP-001",
                    field=None,
                    old_value=None,
                    new_value=CaseStateDeltaValue(
                        impact_id="IMP-001",
                        description="PC was encrypted by ransomware.",
                        impact_type="system_modification",
                        affected_entity_ids=["ENT-001"],
                        status="reported",
                        confidence="high",
                    ),
                ),
                CaseStateDeltaChange(
                    target_type="missing_information",
                    target_id="MISS-001",
                    field=None,
                    old_value=None,
                    new_value=CaseStateDeltaValue(
                        missing_id="MISS-001",
                        description="Ransom payment demand amount unknown.",
                        importance="material",
                    ),
                ),
            ]
        )

        merged = apply_case_state_delta(
            parent_state,
            delta,
            source_message_id=self.msg2_id,
        )

        self.assertEqual(len(merged["facts"]), 2)
        self.assertEqual(merged["facts"][1]["fact_id"], "F-002")
        self.assertEqual(merged["facts"][1]["source_message_ids"], [str(self.msg2_id)])
        self.assertEqual(len(merged["impacts"]), 1)
        self.assertEqual(merged["impacts"][0]["impact_id"], "IMP-001")
        self.assertEqual(len(merged["missing_information"]), 1)
        self.assertEqual(merged["missing_information"][0]["missing_id"], "MISS-001")

    def test_10_legacy_baseline_extraction_rows_remain_readable(self) -> None:
        """Historical state_json payloads without facts or impacts normalize cleanly."""
        legacy_data = {
            "entities": [
                {
                    "entity_id": "ENT-001",
                    "name": "Host-1",
                    "entity_type": "device",
                    "confidence": "high",
                    "source_message_ids": [str(self.msg1_id)],
                }
            ],
            "relationships": [],
            "evidence": [],
            "timeline": [],
            "warnings": [],
        }
        normalized = normalize_case_state(legacy_data)
        self.assertIsInstance(normalized, CaseState)
        self.assertEqual(normalized.facts, [])
        self.assertEqual(normalized.impacts, [])
        self.assertEqual(normalized.missing_information, [])
        self.assertEqual(len(normalized.entities), 1)

    def test_11_report_input_snapshot_accepts_expanded_casestate(self) -> None:
        """ReportInputSnapshot accepts expanded CaseState with facts, impacts, and missing_information."""
        fact = ExtractedFact(
            fact_id="F-001",
            statement="User opened invoice.pdf attachment.",
            category="action",
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        impact = ExtractedImpact(
            impact_id="IMP-001",
            description="Malware execution disrupted accounting services.",
            impact_type="service_disruption",
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        state = CaseState(
            facts=[fact],
            entities=[],
            relationships=[],
            evidence=[],
            timeline=[],
            impacts=[impact],
            missing_information=[],
            warnings=[],
        )

        snapshot = ReportInputSnapshot(
            thread_id=uuid4(),
            thread_title="Incident Report",
            extraction_id=uuid4(),
            extraction_version="baseline_extraction_v2",
            source_messages=[
                ReportSourceMessage(
                    message_id=self.msg1_id,
                    ordinal=1,
                    source_type="user_case_statement",
                    content="User opened invoice.pdf and accounting services crashed.",
                )
            ],
            extraction=state,
            mitre_rows=[],
        )

        self.assertEqual(len(snapshot.extraction.facts), 1)
        self.assertEqual(len(snapshot.extraction.impacts), 1)
        self.assertEqual(snapshot.extraction.facts[0].statement, fact.statement)

    def test_12_retrieval_query_projection_deduplicates_and_prioritizes_facts(self) -> None:
        """Retrieval query projection deduplicates repeated statements between facts, relationships, and timeline."""
        fact = ExtractedFact(
            fact_id="F-001",
            statement="Alice executed powershell script on host-1.",
            category="action",
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        entity1 = ExtractedEntity(
            entity_id="ENT-001",
            name="Alice",
            entity_type="person",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        entity2 = ExtractedEntity(
            entity_id="ENT-002",
            name="host-1",
            entity_type="device",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        rel_duplicate = ExtractedRelationship(
            relationship_id="REL-001",
            subject_entity_id="ENT-001",
            predicate="executed_script_on",
            object_entity_id="ENT-002",
            statement="Alice executed powershell script on host-1.",  # exact duplicate of fact
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        rel_unique = ExtractedRelationship(
            relationship_id="REL-002",
            subject_entity_id="ENT-001",
            predicate="logged_into",
            object_entity_id="ENT-002",
            statement="Alice logged into host-1 via SSH.",  # unique statement
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        timeline_duplicate = ExtractedTimelineEvent(
            event_id="T-001",
            event="Alice executed powershell script on host-1.",  # exact duplicate of fact
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )
        timeline_unique = ExtractedTimelineEvent(
            event_id="T-002",
            event="Network alerts fired 5 minutes later.",  # unique
            status="reported",
            confidence="high",
            source_message_ids=[self.msg1_id],
        )

        state = CaseState(
            facts=[fact],
            entities=[entity1, entity2],
            relationships=[rel_duplicate, rel_unique],
            evidence=[],
            timeline=[timeline_duplicate, timeline_unique],
            impacts=[],
            missing_information=[],
            warnings=[],
        )

        query = project_case_state_to_retrieval_query(state)
        self.assertIn("<case_state_retrieval_json>", query)
        payload_str = query.split("<case_state_retrieval_json>\n")[1].split("\n</case_state_retrieval_json>")[0]
        payload = json.loads(payload_str)

        # Facts has the statement
        self.assertEqual(len(payload["facts"]), 1)
        self.assertEqual(payload["facts"][0]["statement"], fact.statement)

        # Relationships only kept the non-duplicate one
        self.assertEqual(len(payload["relationships"]), 1)
        self.assertEqual(payload["relationships"][0]["relationship_id"], "REL-002")

        # Timeline only kept the non-duplicate one
        self.assertEqual(len(payload["timeline"]), 1)
        self.assertEqual(payload["timeline"][0]["event_id"], "T-002")


if __name__ == "__main__":
    unittest.main()
