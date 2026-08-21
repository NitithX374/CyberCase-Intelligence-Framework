"""Tests for experimental analysis input mode switch (RAW_DIRECT vs CASE_STATE)."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import httpx
from pydantic import ValidationError

from app.config import Settings, settings
from app.models.case_state import CaseStateVersion
from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.schemas.rag import QueryResponse
from app.services.case_analysis import (
    AnalysisClaim,
    AnalysisTraceDraft,
    CaseAnalysisResult,
    AnalysisInputMode,
    AnalysisMode,
    CASE_ANALYSIS_PROMPT_VERSION,
    CaseAnalysisFailure,
    DEFAULT_ANALYSIS_INPUT_MODE,
    MainCaseAnalysisService,
    VALID_ANALYSIS_INPUT_MODES,
    build_analysis_prompt,
    build_case_analysis_prompt,
    request_case_analysis,
    resolve_analysis_case_evidence,
    resolve_analysis_case_narrative,
)
from app.services.case_state import (
    extract_raw_case_evidence_segments,
    format_raw_case_evidence_segments,
    resolve_raw_case_evidence_history,
)
from app.services.followup import FollowUpResolution
from app.services.workflow import (
    AssistantOutcome,
    ChatRunWorker,
    ClaimedChatRun,
    RagContextPayload,
    map_case_analysis_response,
    map_case_state_mutation_response,
    map_initial_case_analysis_response,
    process_chat_run,
)
from app.services.llm.core_llm import CoreLlmTarget


def _target() -> CoreLlmTarget:
    return CoreLlmTarget(
        provider="anthropic",
        model="test-model",
        api_key="test-key",
        base_url="https://provider.test",
        messages_url="https://provider.test/v1/messages",
        headers={"x-api-key": "test-key"},
    )


def _case_state_fixture(source_msg_id: UUID | None = None) -> dict[str, object]:
    msg_id = str(source_msg_id or uuid4())
    return {
        "version": "baseline_extraction_v1",
        "mode": "single_pass_llm",
        "status": "candidate",
        "case_summary": "Intrusion into internal host-Alpha via SSH.",
        "entities": [
            {
                "entity_id": "ent_perpetrator_program",
                "name": "mimikatz.exe",
                "entity_type": "tool",
                "reported_role": "credential_dumping",
                "confidence": "high",
                "source_message_ids": [msg_id],
            },
            {
                "entity_id": "ent_c2_server",
                "name": "198.51.100.23",
                "entity_type": "ip_address",
                "reported_role": "c2_destination",
                "confidence": "high",
                "source_message_ids": [msg_id],
            },
        ],
        "relationships": [
            {
                "relationship_id": "rel_attacker_ssh",
                "subject_entity_id": "ent_c2_server",
                "predicate": "downloads",
                "object_entity_id": "ent_perpetrator_program",
                "statement": "C2 server downloaded perpetrator program.",
                "status": "reported",
                "confidence": "high",
                "source_message_ids": [msg_id],
            },
            {
                "relationship_id": "rel_exfiltration_channel",
                "subject_entity_id": "ent_perpetrator_program",
                "predicate": "exfiltrates_to",
                "object_entity_id": "ent_c2_server",
                "statement": "Perpetrator program exfiltrates data to C2 server.",
                "status": "suspected",
                "confidence": "medium",
                "source_message_ids": [msg_id],
            },
        ],
        "evidence": [],
        "timeline": [],
        "missing_information": [],
        "warnings": [],
    }


def _analysis_context_fixture() -> dict[str, object]:
    return {
        "retrieved_context": "MITRE ATT&CK T1059: Command and Scripting Interpreter.",
        "retrieval_context_id": "retrieval-ctx-99",
        "mitre_table": [
            {
                "technique_id": "T1059",
                "name": "Command and Scripting Interpreter",
                "confidence": "high",
            }
        ],
        "previous_analysis": None,
    }


class _SessionContext:
    def __init__(self, session: object) -> None:
        self._session = session

    async def __aenter__(self) -> object:
        return self._session

    async def __aexit__(self, *_: object) -> None:
        pass


class AnalysisInputModeTests(unittest.IsolatedAsyncioTestCase):
    def test_mode_configuration_and_aliases(self) -> None:
        self.assertIn("case_state", VALID_ANALYSIS_INPUT_MODES)
        self.assertIn("raw_direct", VALID_ANALYSIS_INPUT_MODES)
        self.assertIn(settings.analysis_input_mode, VALID_ANALYSIS_INPUT_MODES)

    def test_invalid_mode_configuration_fails_clearly(self) -> None:
        with self.assertRaises(CaseAnalysisFailure) as raised:
            resolve_analysis_case_narrative(mode="unsupported_mode")
        self.assertEqual(raised.exception.code, "analysis_invalid_mode")

        with self.assertRaises(CaseAnalysisFailure) as raised_prompt:
            build_case_analysis_prompt(
                mode="case_overview",
                analysis_input_mode="invalid_mode",
                analysis_context=_analysis_context_fixture(),
                question=None,
                response_language="english",
            )
        self.assertEqual(raised_prompt.exception.code, "analysis_invalid_mode")

        # Pydantic Settings strict validation on invalid values
        with self.assertRaises(ValidationError):
            Settings(analysis_input_mode="invalid_value")  # type: ignore[arg-type]

    def test_missing_evidence_in_selected_mode_fails_cleanly(self) -> None:
        # CASE_STATE mode requires case_state_json dict
        with self.assertRaises(CaseAnalysisFailure) as raised_state:
            resolve_analysis_case_narrative(
                mode="case_state",
                case_state_json=None,
            )
        self.assertEqual(raised_state.exception.code, "analysis_context_missing")

        # RAW_DIRECT mode requires raw_case_narrative str
        with self.assertRaises(CaseAnalysisFailure) as raised_raw:
            resolve_analysis_case_narrative(
                mode="raw_direct",
                raw_case_narrative="",
            )
        self.assertEqual(raised_raw.exception.code, "analysis_context_missing")

        with self.assertRaises(CaseAnalysisFailure) as raised_whitespace:
            resolve_analysis_case_narrative(
                mode="raw_direct",
                raw_case_narrative="   ",
            )
        self.assertEqual(raised_whitespace.exception.code, "analysis_context_missing")

    def test_case_state_mode_passes_case_state_evidence(self) -> None:
        case_state = _case_state_fixture()
        analysis_context = _analysis_context_fixture()

        prompt = build_case_analysis_prompt(
            mode="case_overview",
            case_state_json=case_state,
            raw_case_narrative="Raw narrative that should not be used in CASE_STATE mode.",
            analysis_input_mode="case_state",
            analysis_context=analysis_context,
            question=None,
            response_language="english",
        )

        serialized = prompt.split("<case_context_json>\n", 1)[1].split(
            "\n</case_context_json>", 1
        )[0]
        payload = json.loads(serialized)

        self.assertEqual(payload["analysis_mode"], "case_overview")
        self.assertIsInstance(payload["case_narrative"], dict)
        self.assertEqual(
            payload["case_narrative"]["case_summary"],
            case_state["case_summary"],
        )
        self.assertEqual(
            payload["relationship_status_contract"],
            [
                {"relationship_id": "rel_attacker_ssh", "status": "reported"},
                {
                    "relationship_id": "rel_exfiltration_channel",
                    "status": "suspected",
                },
            ],
        )
        self.assertIn("ent_perpetrator_program", prompt)
        self.assertIn("rel_attacker_ssh", prompt)
        self.assertNotIn("Raw narrative that should not be used", prompt)

    def test_raw_direct_mode_passes_raw_narrative(self) -> None:
        case_state = _case_state_fixture()
        raw_narrative = (
            "On 2026-08-10, host workstation-4 executed powershell.exe connecting "
            "to 198.51.100.23 port 443."
        )
        analysis_context = _analysis_context_fixture()

        prompt = build_case_analysis_prompt(
            mode="case_overview",
            case_state_json=case_state,
            raw_case_narrative=raw_narrative,
            analysis_input_mode="raw_direct",
            analysis_context=analysis_context,
            question=None,
            response_language="english",
        )

        serialized = prompt.split("<case_context_json>\n", 1)[1].split(
            "\n</case_context_json>", 1
        )[0]
        payload = json.loads(serialized)

        self.assertEqual(payload["analysis_mode"], "case_overview")
        self.assertEqual(payload["case_narrative"], raw_narrative)
        self.assertIn(raw_narrative, prompt)

    def test_raw_direct_does_not_expose_case_state_entities_or_relationships(self) -> None:
        case_state = _case_state_fixture()
        raw_narrative = (
            "On 2026-08-10, host workstation-4 executed powershell.exe connecting "
            "to 198.51.100.23."
        )
        analysis_context = _analysis_context_fixture()

        prompt = build_case_analysis_prompt(
            mode="case_overview",
            case_state_json=case_state,
            raw_case_narrative=raw_narrative,
            analysis_input_mode="raw_direct",
            analysis_context=analysis_context,
            question=None,
            response_language="english",
        )

        # Assert Case State internal identifiers and entity structures do NOT appear in prompt
        self.assertNotIn("ent_perpetrator_program", prompt)
        self.assertNotIn("rel_attacker_ssh", prompt)
        self.assertNotIn("ent_c2_server", prompt)
        self.assertNotIn("rel_exfiltration_channel", prompt)
        self.assertNotIn("baseline_extraction_v1", prompt)
        self.assertNotIn("single_pass_llm", prompt)
        self.assertNotIn("epistemic_status", prompt)

        # Raw narrative and external retrieved context must be present
        self.assertIn(raw_narrative, prompt)
        self.assertIn("MITRE ATT&CK T1059", prompt)
        self.assertIn("retrieval-ctx-99", prompt)

    async def test_both_modes_receive_equivalent_normalized_instructions(self) -> None:
        case_state = _case_state_fixture()
        raw_narrative = "Observed suspicious PowerShell execution on endpoint."
        analysis_context = _analysis_context_fixture()

        system_prompts: dict[str, str] = {}

        def make_responder(captured_key: str):
            def respond(request: httpx.Request) -> httpx.Response:
                payload = json.loads(request.content)
                system_prompts[captured_key] = payload["system"]
                return httpx.Response(
                    200,
                    json={
                        "content": [{
                            "type": "text",
                            "text": json.dumps({
                                "version": "analysis_trace_v1",
                                "answer": "Analysis answer.",
                                "claims": [],
                                "mitre_associations": [],
                            }),
                        }],
                        "stop_reason": "end_turn",
                    },
                )
            return respond

        with patch(
            "app.services.case_analysis.service.resolve_core_llm_target",
            return_value=_target(),
        ):
            # Test CASE_STATE mode
            async with httpx.AsyncClient(
                transport=httpx.MockTransport(make_responder("case_state"))
            ) as client:
                await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    raw_case_narrative=raw_narrative,
                    analysis_input_mode="case_state",
                    analysis_context=analysis_context,
                    question=None,
                    user_message=raw_narrative,
                )

            # Test RAW_DIRECT mode
            async with httpx.AsyncClient(
                transport=httpx.MockTransport(make_responder("raw_direct"))
            ) as client:
                await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    raw_case_narrative=raw_narrative,
                    analysis_input_mode="raw_direct",
                    analysis_context=analysis_context,
                    question=None,
                    user_message=raw_narrative,
                )

        # Both modes must receive identical normalized system instructions
        self.assertEqual(
            system_prompts["case_state"],
            system_prompts["raw_direct"],
        )
        self.assertIn("CASE NARRATIVE", system_prompts["case_state"])
        self.assertIn(
            "CASE NARRATIVE is the authoritative source of facts about this incident.",
            system_prompts["case_state"],
        )
        self.assertIn(
            "External reference knowledge, including MITRE ATT&CK or retrieved cybersecurity",
            system_prompts["case_state"],
        )
        self.assertIn(
            "Do not introduce case-specific facts that are unsupported by CASE NARRATIVE.",
            system_prompts["case_state"],
        )
        self.assertNotIn("The Case State is authoritative", system_prompts["case_state"])

    def test_raw_direct_oversized_payload_truncates_evidence_cleanly(self) -> None:
        oversized_narrative = "Suspicious network activity detected. " * 1_000
        exact_question = "Which system was compromised?"

        with patch.object(settings, "chat_ask_max_input_chars", 500):
            prompt = build_case_analysis_prompt(
                mode="question_answer",
                raw_case_narrative=oversized_narrative,
                analysis_input_mode="raw_direct",
                analysis_context={"retrieved_context": "context " * 500},
                question=exact_question,
                response_language="english",
            )

        serialized = prompt.split("<case_context_json>\n", 1)[1].split(
            "\n</case_context_json>", 1
        )[0]
        payload = json.loads(serialized)

        self.assertLessEqual(len(prompt), 500)
        self.assertEqual(payload["analysis_mode"], "question_answer")
        self.assertEqual(payload["question"], exact_question)
        self.assertTrue(payload["context_truncated"])
        self.assertTrue(payload["case_narrative"]["truncated"])

    async def test_chat_worker_initial_flow_in_raw_direct_mode_preserves_case_state_creation(self) -> None:
        raw_narrative = "On 2026-08-10, host workstation-4 executed powershell.exe."
        case_state = _case_state_fixture()
        extraction_metadata = {"status": "candidate", "validation_status": "validated"}
        analysis_calls: list[dict[str, object]] = []

        claimed = ClaimedChatRun(
            id=uuid4(),
            operation="query",
            input_rag_session_id=None,
            content=raw_narrative,
            rag_query=raw_narrative,
            original_user_content=raw_narrative,
            raw_case_narrative=raw_narrative,
            clarification_exchanges=(),
            followup_root_ordinal=1,
            extraction_input=Mock(),
        )

        worker = Mock()
        worker.claim_run = AsyncMock(return_value=claimed)
        worker.complete_run = AsyncMock(return_value=True)

        rag_call = AsyncMock(
            return_value=QueryResponse(
                status="completed",
                retrieval_context_id="retrieval-1",
                context="bounded MITRE context",
            )
        )

        async def capture_analysis(**kwargs: object) -> str:
            analysis_calls.append(kwargs)
            return "Grounded initial analysis in raw_direct mode."

        with (
            patch.object(settings, "analysis_input_mode", "raw_direct"),
            patch(
                "app.services.workflow.pipeline.async_session",
                return_value=_SessionContext(Mock()),
            ),
            patch(
                "app.services.workflow.pipeline.ChatRunWorker",
                return_value=worker,
            ),
            patch(
                "app.services.workflow.pipeline.evaluate_followup_outcome",
                new=AsyncMock(
                    return_value=FollowUpResolution(
                        outcome=None,
                        metadata_json={},
                    )
                ),
            ),
            patch(
                "app.services.workflow.pipeline.run_validated_case_state_extraction",
                new=AsyncMock(return_value=(case_state, extraction_metadata)),
            ) as extraction_mock,
        ):
            await process_chat_run(
                claimed.id,
                rag_call=rag_call,
                ask_call=capture_analysis,
            )

        # 1. Case State extraction was executed normally
        extraction_mock.assert_awaited_once()

        # 2. Analysis received raw_case_narrative
        self.assertEqual(len(analysis_calls), 1)
        self.assertEqual(analysis_calls[0]["raw_case_narrative"], raw_narrative)
        self.assertEqual(analysis_calls[0]["case_state_json"], case_state)

        # 3. Persistence outcome contains validated Case State (NOT deleted, NOT bypassed)
        outcome: AssistantOutcome = worker.complete_run.await_args.args[2]
        self.assertEqual(outcome.content, "Grounded initial analysis in raw_direct mode.")
        self.assertIsNotNone(outcome.validated_case_state_json)
        self.assertEqual(outcome.validated_case_state_json, case_state)
        self.assertIsNotNone(outcome.rag_context_payload)
        self.assertEqual(outcome.metadata_json["analysis_input_mode"], "raw_direct")
        self.assertEqual(
            outcome.metadata_json["chat_action"]["analysis_input_mode"],
            "raw_direct",
        )

    async def test_chat_worker_ask_flow_in_raw_direct_mode(self) -> None:
        case_state = _case_state_fixture()
        raw_narrative = "On 2026-08-10, host workstation-4 executed powershell.exe."
        analyst_question = "What MITRE techniques were identified?"
        analysis_calls: list[dict[str, object]] = []

        claimed = ClaimedChatRun(
            id=uuid4(),
            operation="query",
            input_rag_session_id=None,
            content=analyst_question,
            rag_query=analyst_question,
            original_user_content=raw_narrative,
            raw_case_narrative=raw_narrative,
            clarification_exchanges=(),
            followup_root_ordinal=1,
            post_answer_action="ask",
            case_state_json=case_state,
            analysis_context=_analysis_context_fixture(),
        )

        worker = Mock()
        worker.claim_run = AsyncMock(return_value=claimed)
        worker.complete_run = AsyncMock(return_value=True)

        async def capture_analysis(**kwargs: object) -> CaseAnalysisResult:
            analysis_calls.append(kwargs)
            return CaseAnalysisResult(
                answer="Answer to analyst question in raw_direct mode.",
                trace=AnalysisTraceDraft(
                    analysis_mode="question_answer",
                    claims=[
                        AnalysisClaim(
                            claim_id="A-01",
                            claim_type="unknown",
                            text="The requested conclusion remains unknown.",
                            epistemic_status="unknown",
                            entity_ids=[],
                            relationship_ids=[],
                            evidence_ids=[],
                            timeline_event_ids=[],
                        )
                    ],
                ),
            )

        with (
            patch.object(settings, "analysis_input_mode", "raw_direct"),
            patch(
                "app.services.workflow.pipeline.async_session",
                return_value=_SessionContext(Mock()),
            ),
            patch(
                "app.services.workflow.pipeline.ChatRunWorker",
                return_value=worker,
            ),
        ):
            await process_chat_run(
                claimed.id,
                ask_call=capture_analysis,
            )

        self.assertEqual(len(analysis_calls), 1)
        self.assertEqual(analysis_calls[0]["mode"], "question_answer")
        self.assertEqual(analysis_calls[0]["raw_case_narrative"], raw_narrative)
        self.assertEqual(analysis_calls[0]["question"], analyst_question)

        outcome: AssistantOutcome = worker.complete_run.await_args.args[2]
        self.assertEqual(outcome.content, "Answer to analyst question in raw_direct mode.")
        self.assertEqual(outcome.analysis_trace_draft.analysis_mode, "question_answer")
        self.assertEqual(outcome.metadata_json["analysis_input_mode"], "raw_direct")
        self.assertEqual(
            outcome.metadata_json["chat_action"]["analysis_input_mode"],
            "raw_direct",
        )

    def test_outcome_mappers_record_analysis_input_mode_metadata(self) -> None:
        case_state = _case_state_fixture()
        rag_payload = RagContextPayload(
            retrieval_context_id="ret-1",
            context="context text",
            mitre_table=(),
        )

        # 1. Initial analysis outcome
        initial_outcome = map_initial_case_analysis_response(
            "Initial answer",
            rag_context_payload=rag_payload,
            validated_case_state_json=case_state,
            extraction_metadata={"status": "candidate"},
            followup_metadata_json={},
            analysis_input_mode="raw_direct",
        )
        self.assertEqual(
            initial_outcome.metadata_json["analysis_input_mode"],
            "raw_direct",
        )
        self.assertEqual(
            initial_outcome.metadata_json["chat_action"]["analysis_input_mode"],
            "raw_direct",
        )

        # 2. Ask outcome
        ask_outcome = map_case_analysis_response(
            "Ask answer",
            analysis_context={"retrieval_context_id": "ret-1", "mitre_table": []},
            analysis_input_mode="case_state",
        )
        self.assertEqual(
            ask_outcome.metadata_json["analysis_input_mode"],
            "case_state",
        )
        self.assertEqual(
            ask_outcome.metadata_json["chat_action"]["analysis_input_mode"],
            "case_state",
        )

        # 3. Mutation outcome
        mutation_outcome = map_case_state_mutation_response(
            "Mutation answer",
            rag_context_payload=rag_payload,
            merged_case_state_json=case_state,
            delta_json={},
            expected_parent_case_state_version_id=uuid4(),
            mutation_metadata={},
            analysis_input_mode="raw_direct",
        )
        self.assertEqual(
            mutation_outcome.metadata_json["analysis_input_mode"],
            "raw_direct",
        )
        self.assertEqual(
            mutation_outcome.metadata_json["chat_action"]["analysis_input_mode"],
            "raw_direct",
        )


    async def test_claim_run_resolves_intake_narrative_for_ask_round_zero(self) -> None:
        thread_id = uuid4()
        run_id = uuid4()
        case_state = _case_state_fixture()
        state_version_id = uuid4()
        analyst_question = "Is the attacker program the same as the workstation program?"
        intake_narrative = "The attacker used Application Shimming and placed malware on employee machines."

        run = ChatRun(
            id=run_id,
            thread_id=thread_id,
            request_message_id=uuid4(),
            operation="query",
            status="queued",
            input_rag_session_id=None,
            idempotency_key="ask-claim-test",
            request_fingerprint="f" * 64,
            request_payload={
                "action": "ask",
                "content": analyst_question,
                "rag_query": analyst_question,
                "followup_round": 0,
                "case_state_version_id": str(state_version_id),
                "followup_root_ordinal": 3,
            },
            attempt_count=0,
        )

        mock_state = Mock()
        mock_state.id = state_version_id
        mock_state.state_json = case_state

        mock_rag_context = Mock()
        mock_rag_context.retrieval_context_id = "ret-1"
        mock_rag_context.context = "MITRE context"
        mock_rag_context.mitre_table = []

        def _result(val: object) -> Mock:
            res = Mock()
            res.scalar_one_or_none.return_value = val
            return res

        db = Mock()
        db.begin.return_value = _SessionContext(db)
        db.execute = AsyncMock(
            side_effect=[
                _result(run),
                _result(state_version_id),
                _result(mock_state),
                _result(mock_rag_context),
                _result(intake_narrative),  # Intake message query
            ]
        )
        db.flush = AsyncMock()

        claimed = await ChatRunWorker(db).claim_run(run_id, "worker-test")

        self.assertIsNotNone(claimed)
        assert claimed is not None
        self.assertEqual(claimed.content, analyst_question)
        self.assertEqual(claimed.raw_case_narrative, intake_narrative)
        self.assertNotEqual(claimed.raw_case_narrative, analyst_question)

    def test_extract_and_format_raw_case_evidence_segments(self) -> None:
        msg1_id = uuid4()
        msg2_id = uuid4()
        msg3_id = uuid4()

        # TEST 1: Single initial segment -> returns verbatim
        segments_1 = extract_raw_case_evidence_segments([
            (msg1_id, 1, "Initial case narrative", None),
        ])
        self.assertEqual(segments_1, ("Initial case narrative",))
        self.assertEqual(format_raw_case_evidence_segments(segments_1), "Initial case narrative")

        # TEST 2 & 4: Multiple adds in chronological order
        segments_multi = extract_raw_case_evidence_segments([
            (msg1_id, 1, "Narrative A", None),
            (msg2_id, 3, "Info B", {"action": "add_case_info"}),
            (msg3_id, 5, "Info C", {"action": "add_case_info"}),
        ])
        self.assertEqual(segments_multi, ("Narrative A", "Info B", "Info C"))
        formatted = format_raw_case_evidence_segments(segments_multi)
        self.assertIn("[INITIAL CASE NARRATIVE]\nNarrative A", formatted)
        self.assertIn("[ADDED CASE INFORMATION #1]\nInfo B", formatted)
        self.assertIn("[ADDED CASE INFORMATION #2]\nInfo C", formatted)
        self.assertTrue(formatted.index("Narrative A") < formatted.index("Info B") < formatted.index("Info C"))

        # TEST 5: Ask does not contaminate evidence
        ask1_id = uuid4()
        ask2_id = uuid4()
        segments_filtered = extract_raw_case_evidence_segments([
            (msg1_id, 1, "Narrative A", None),
            (ask1_id, 3, "Question Q1", {"action": "ask"}),
            (msg2_id, 5, "Info B", {"action": "add_case_info"}),
            (ask2_id, 7, "Question Q2", {"action": "ask"}),
        ])
        self.assertEqual(segments_filtered, ("Narrative A", "Info B"))
        formatted_filtered = format_raw_case_evidence_segments(segments_filtered)
        self.assertNotIn("Question Q1", formatted_filtered)
        self.assertNotIn("Question Q2", formatted_filtered)
        self.assertIn("Narrative A", formatted_filtered)
        self.assertIn("Info B", formatted_filtered)

        # TEST 6: Correction remains raw (both preserved)
        correction_id = uuid4()
        segments_correction = extract_raw_case_evidence_segments([
            (msg1_id, 1, "คนร้ายชื่อนาย A", None),
            (correction_id, 3, "แก้ไข คนร้ายไม่ใช่นาย A แต่เป็นนาย B", {"action": "add_case_info"}),
        ])
        self.assertEqual(
            segments_correction,
            ("คนร้ายชื่อนาย A", "แก้ไข คนร้ายไม่ใช่นาย A แต่เป็นนาย B"),
        )
        formatted_corr = format_raw_case_evidence_segments(segments_correction)
        self.assertIn("คนร้ายชื่อนาย A", formatted_corr)
        self.assertIn("แก้ไข คนร้ายไม่ใช่นาย A แต่เป็นนาย B", formatted_corr)
        self.assertTrue(formatted_corr.index("คนร้ายชื่อนาย A") < formatted_corr.index("แก้ไข คนร้ายไม่ใช่นาย A แต่เป็นนาย B"))

    async def test_chat_worker_add_case_info_in_raw_direct_mode_receives_accumulated_evidence(self) -> None:
        initial_narrative = "เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่ง..."
        added_info = "คนร้ายชื่อนาย A"
        accumulated_narrative = (
            f"[INITIAL CASE NARRATIVE]\n{initial_narrative}\n\n"
            f"[ADDED CASE INFORMATION #1]\n{added_info}"
        )
        case_state = _case_state_fixture()
        analysis_calls: list[dict[str, object]] = []

        claimed = ClaimedChatRun(
            id=uuid4(),
            operation="query",
            input_rag_session_id=None,
            content=added_info,
            rag_query=added_info,
            original_user_content=added_info,
            raw_case_narrative=accumulated_narrative,
            clarification_exchanges=(),
            followup_root_ordinal=3,
            request_message_id=uuid4(),
            post_answer_action="add_case_info",
            case_state_version_id=uuid4(),
            case_state_json=case_state,
            analysis_context=_analysis_context_fixture(),
        )

        worker = Mock()
        worker.claim_run = AsyncMock(return_value=claimed)
        worker.complete_run = AsyncMock(return_value=True)

        async def capture_analysis(**kwargs: object) -> str:
            analysis_calls.append(kwargs)
            return "Updated case overview in raw_direct mode."

        delta_mock = Mock()
        delta_mock.changes = [{"target_type": "evidence"}]
        delta_mock.model_dump.return_value = {}

        with (
            patch.object(settings, "analysis_input_mode", "raw_direct"),
            patch(
                "app.services.workflow.pipeline.async_session",
                return_value=_SessionContext(Mock()),
            ),
            patch(
                "app.services.workflow.pipeline.ChatRunWorker",
                return_value=worker,
            ),
            patch(
                "app.services.workflow.pipeline.run_case_state_delta_extraction",
                new=AsyncMock(return_value=(delta_mock, {"status": "candidate"})),
            ),
            patch(
                "app.services.workflow.pipeline.apply_case_state_delta",
                return_value=case_state,
            ),
            patch(
                "app.services.workflow.pipeline.request_rag",
                new=AsyncMock(
                    return_value=QueryResponse(
                        status="completed",
                        retrieval_context_id="ret-1",
                        context="MITRE context",
                    )
                ),
            ),
            patch(
                "app.services.workflow.pipeline.evaluate_followup_outcome",
                new=AsyncMock(
                    return_value=FollowUpResolution(
                        outcome=None,
                        metadata_json={},
                    )
                ),
            ),
        ):
            await process_chat_run(
                claimed.id,
                ask_call=capture_analysis,
            )

        self.assertEqual(len(analysis_calls), 1)
        self.assertEqual(analysis_calls[0]["mode"], "case_overview")
        self.assertEqual(analysis_calls[0]["raw_case_narrative"], accumulated_narrative)
        self.assertIn(initial_narrative, analysis_calls[0]["raw_case_narrative"])
        self.assertIn(added_info, analysis_calls[0]["raw_case_narrative"])
        self.assertIsNone(analysis_calls[0]["question"])

    async def test_chat_worker_ask_after_add_in_raw_direct_mode_does_not_contain_question_in_evidence(self) -> None:
        initial_narrative = "เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่ง..."
        added_info = "คนร้ายชื่อนาย A"
        accumulated_narrative = (
            f"[INITIAL CASE NARRATIVE]\n{initial_narrative}\n\n"
            f"[ADDED CASE INFORMATION #1]\n{added_info}"
        )
        analyst_question = "คนร้ายชื่ออะไร?"
        case_state = _case_state_fixture()
        analysis_calls: list[dict[str, object]] = []

        claimed = ClaimedChatRun(
            id=uuid4(),
            operation="query",
            input_rag_session_id=None,
            content=analyst_question,
            rag_query=analyst_question,
            original_user_content=analyst_question,
            raw_case_narrative=accumulated_narrative,
            clarification_exchanges=(),
            followup_root_ordinal=5,
            request_message_id=uuid4(),
            post_answer_action="ask",
            case_state_json=case_state,
            analysis_context=_analysis_context_fixture(),
        )

        worker = Mock()
        worker.claim_run = AsyncMock(return_value=claimed)
        worker.complete_run = AsyncMock(return_value=True)

        async def capture_analysis(**kwargs: object) -> str:
            analysis_calls.append(kwargs)
            return "Answer to question in raw_direct mode."

        with (
            patch.object(settings, "analysis_input_mode", "raw_direct"),
            patch(
                "app.services.workflow.pipeline.async_session",
                return_value=_SessionContext(Mock()),
            ),
            patch(
                "app.services.workflow.pipeline.ChatRunWorker",
                return_value=worker,
            ),
        ):
            await process_chat_run(
                claimed.id,
                ask_call=capture_analysis,
            )

        self.assertEqual(len(analysis_calls), 1)
        self.assertEqual(analysis_calls[0]["mode"], "question_answer")
        self.assertEqual(analysis_calls[0]["raw_case_narrative"], accumulated_narrative)
        self.assertEqual(analysis_calls[0]["question"], analyst_question)
        self.assertNotIn(analyst_question, analysis_calls[0]["raw_case_narrative"])

    async def test_ask_missing_raw_evidence_in_raw_direct_mode_fails_explicitly(self) -> None:
        case_state = _case_state_fixture()
        analyst_question = "เหตุการณ์เกิดตอนไหน"

        claimed = ClaimedChatRun(
            id=uuid4(),
            operation="query",
            input_rag_session_id=None,
            content=analyst_question,
            rag_query=analyst_question,
            original_user_content=analyst_question,
            raw_case_narrative=None,  # Missing raw evidence
            clarification_exchanges=(),
            followup_root_ordinal=3,
            request_message_id=uuid4(),
            post_answer_action="ask",
            case_state_json=case_state,
            analysis_context=_analysis_context_fixture(),
        )

        worker = Mock()
        worker.claim_run = AsyncMock(return_value=claimed)
        worker.fail_run = AsyncMock(return_value=True)

        with (
            patch.object(settings, "analysis_input_mode", "raw_direct"),
            patch(
                "app.services.workflow.pipeline.async_session",
                return_value=_SessionContext(Mock()),
            ),
            patch(
                "app.services.workflow.pipeline.ChatRunWorker",
                return_value=worker,
            ),
        ):
            await process_chat_run(claimed.id)

        # Worker recorded failure with analysis_context_missing
        worker.fail_run.assert_awaited_once()
        self.assertEqual(
            worker.fail_run.await_args.args[2],
            "analysis_context_missing",
        )

    async def test_resolve_raw_case_evidence_history_db_multi_turn(self) -> None:
        thread_id = uuid4()
        msg1_id = uuid4()
        msg2_id = uuid4()
        msg3_id = uuid4()
        msg4_id = uuid4()
        msg5_id = uuid4()

        class MockRow:
            def __init__(self, msg_id: UUID, ordinal: int, content: str, payload: dict[str, object] | None):
                self._mapping = {
                    "id": msg_id,
                    "ordinal": ordinal,
                    "content": content,
                    "request_payload": payload,
                }
                self.id = msg_id
                self.ordinal = ordinal
                self.content = content
                self.request_payload = payload

        mock_rows = [
            MockRow(msg1_id, 1, "Initial Case Narrative A", {"followup_round": 0}),
            MockRow(msg2_id, 3, "Analyst Question Q1", {"action": "ask"}),
            MockRow(msg3_id, 5, "Added Evidence B", {"action": "add_case_info"}),
            MockRow(msg4_id, 7, "Added Evidence C", {"action": "add_case_info"}),
            MockRow(msg5_id, 9, "Analyst Question Q2", {"action": "ask"}),
        ]

        def _make_db():
            db = Mock()
            res = Mock()
            res.all.return_value = mock_rows
            db.execute = AsyncMock(return_value=res)
            return db

        # Test resolving at Message 5 (Added Evidence B)
        evidence_b = await resolve_raw_case_evidence_history(
            _make_db(),
            thread_id=thread_id,
            current_request_message_id=msg3_id,
            current_request_payload={"action": "add_case_info", "content": "Added Evidence B"},
        )
        self.assertIsNotNone(evidence_b)
        self.assertIn("Initial Case Narrative A", evidence_b)
        self.assertIn("Added Evidence B", evidence_b)
        self.assertNotIn("Analyst Question Q1", evidence_b)
        self.assertNotIn("Added Evidence C", evidence_b)

        # Test resolving at Message 9 (Analyst Question Q2)
        evidence_q2 = await resolve_raw_case_evidence_history(
            _make_db(),
            thread_id=thread_id,
            current_request_message_id=msg5_id,
            current_request_payload={"action": "ask", "content": "Analyst Question Q2"},
        )
        self.assertIsNotNone(evidence_q2)
        self.assertIn("Initial Case Narrative A", evidence_q2)
        self.assertIn("Added Evidence B", evidence_q2)
        self.assertIn("Added Evidence C", evidence_q2)
        self.assertNotIn("Analyst Question Q1", evidence_q2)
        self.assertNotIn("Analyst Question Q2", evidence_q2)

    async def test_acceptance_scenario_nonthaburi_multi_turn_raw_direct(self) -> None:
        initial_narrative = (
            "เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบรับส่งไฟล์ผ่านเว็บของบริษัท"
            "ถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของเว็บเซิร์ฟเวอร์พบว่าคนร้ายส่งคำสั่งฐานข้อมูลแทรกเข้าไป"
            "ทางช่องกรอกข้อมูลบนหน้าเว็บที่เปิดให้บริการต่อสาธารณะ จนสามารถวางไฟล์สคริปต์สำหรับสั่งการระยะไกลไว้บนเซิร์ฟเวอร์ได้"
        )
        added_info = "คนร้ายชื่อนาย A"
        ask_question = "เหตุการณ์เกิดขึ้นเมื่อวันที่เท่าไร และคนร้ายชื่ออะไร?"

        msg1_id = uuid4()
        msg2_id = uuid4()
        msg3_id = uuid4()

        # Turn 1: Initial analysis
        segments_turn1 = extract_raw_case_evidence_segments([
            (msg1_id, 1, initial_narrative, None),
        ])
        formatted_turn1 = format_raw_case_evidence_segments(segments_turn1)
        self.assertEqual(formatted_turn1, initial_narrative)

        prompt_turn1 = build_case_analysis_prompt(
            mode="case_overview",
            raw_case_narrative=formatted_turn1,
            analysis_input_mode="raw_direct",
            analysis_context=_analysis_context_fixture(),
            question=None,
            response_language="english",
        )
        self.assertIn(initial_narrative, prompt_turn1)
        self.assertNotIn("นาย A", prompt_turn1)

        # Turn 2: add_case_info ("คนร้ายชื่อนาย A")
        segments_turn2 = extract_raw_case_evidence_segments([
            (msg1_id, 1, initial_narrative, None),
            (msg2_id, 3, added_info, {"action": "add_case_info"}),
        ])
        formatted_turn2 = format_raw_case_evidence_segments(segments_turn2)
        self.assertIn("[INITIAL CASE NARRATIVE]", formatted_turn2)
        self.assertIn(initial_narrative, formatted_turn2)
        self.assertIn("[ADDED CASE INFORMATION #1]", formatted_turn2)
        self.assertIn("คนร้ายชื่อนาย A", formatted_turn2)
        self.assertTrue(formatted_turn2.index(initial_narrative) < formatted_turn2.index("คนร้ายชื่อนาย A"))

        prompt_turn2 = build_case_analysis_prompt(
            mode="case_overview",
            raw_case_narrative=formatted_turn2,
            analysis_input_mode="raw_direct",
            analysis_context=_analysis_context_fixture(),
            question=None,
            response_language="thai",
        )
        self.assertIn(initial_narrative, prompt_turn2)
        self.assertIn("คนร้ายชื่อนาย A", prompt_turn2)

        # Turn 3: ask ("เหตุการณ์เกิดขึ้นเมื่อวันที่เท่าไร และคนร้ายชื่ออะไร?")
        segments_turn3 = extract_raw_case_evidence_segments([
            (msg1_id, 1, initial_narrative, None),
            (msg2_id, 3, added_info, {"action": "add_case_info"}),
            (msg3_id, 5, ask_question, {"action": "ask"}),
        ])
        formatted_turn3 = format_raw_case_evidence_segments(segments_turn3)
        # Evidence must contain Turn 1 and Turn 2, NOT Turn 3 ask question
        self.assertEqual(formatted_turn3, formatted_turn2)
        self.assertNotIn(ask_question, formatted_turn3)

        prompt_turn3 = build_case_analysis_prompt(
            mode="question_answer",
            raw_case_narrative=formatted_turn3,
            analysis_input_mode="raw_direct",
            analysis_context=_analysis_context_fixture(),
            question=ask_question,
            response_language="thai",
        )
        self.assertIn(initial_narrative, prompt_turn3)
        self.assertIn("คนร้ายชื่อนาย A", prompt_turn3)
        self.assertIn(ask_question, prompt_turn3)

        payload_turn3 = json.loads(
            prompt_turn3.split("<case_context_json>\n", 1)[1].split("\n</case_context_json>", 1)[0]
        )
        self.assertEqual(payload_turn3["analysis_mode"], "question_answer")
        self.assertEqual(payload_turn3["question"], ask_question)
        self.assertIn("12 พฤษภาคม 2566", payload_turn3["case_narrative"])
        self.assertIn("คนร้ายชื่อนาย A", payload_turn3["case_narrative"])
        self.assertNotIn(ask_question, payload_turn3["case_narrative"])


if __name__ == "__main__":
    unittest.main()
