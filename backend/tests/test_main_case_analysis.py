from copy import deepcopy
import json
import unittest
from typing import cast, get_args
from unittest.mock import patch

import httpx

from app.config import settings
from app.services.case_analysis import (
    AnalysisMode,
    CaseAnalysisFailure,
    MainCaseAnalysisService,
    ResponseLanguage,
    build_case_analysis_prompt,
    resolve_response_language,
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


def _case_inputs() -> tuple[dict[str, object], dict[str, object]]:
    return (
        {
            "case_summary": "reported host-7 activity",
            "entities": [
                {
                    "entity_id": "host-7",
                    "attributes": {"roles": ["affected", "source"]},
                }
            ],
        },
        {
            "answer": "The grounded analysis identified host-7.",
            "retrieval_context_id": "retrieval-1",
            "mitre_table": [
                {
                    "technique_id": "T1059",
                    "metadata": {"confidence": "supported"},
                }
            ],
        },
    )


def _structured_text(answer: str) -> str:
    return json.dumps(
        {
            "version": "analysis_trace_v1",
            "answer": answer,
            "claims": [],
            "mitre_associations": [],
        }
    )


class MainCaseAnalysisServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_does_not_mutate_nested_inputs(self) -> None:
        case_state, analysis_context = _case_inputs()
        expected_case_state = deepcopy(case_state)
        expected_analysis_context = deepcopy(analysis_context)

        def respond(request: httpx.Request) -> httpx.Response:
            request_payload = json.loads(request.content)
            system_prompt = request_payload["system"]
            claim_schema = request_payload["output_config"]["format"]["schema"][
                "$defs"
            ]["AnalysisClaim"]
            self.assertNotIn("fact_ids", claim_schema["properties"])
            self.assertNotIn("mitre_technique_ids", claim_schema["properties"])
            self.assertIn(
                "mitre_associations",
                request_payload["output_config"]["format"]["schema"]["properties"],
            )
            self.assertIn("candidate_only", system_prompt)
            self.assertIn("external_technical_context", system_prompt)
            self.assertIn("TRUST HIERARCHY", system_prompt)
            self.assertIn("Do not retrieve new information", system_prompt)
            self.assertIn("ANALYSIS MODE: question_answer", system_prompt)
            self.assertIn("Answer the question directly", system_prompt)
            self.assertIn("proportional to the question", system_prompt)
            self.assertIn("RESPONSE LANGUAGE AND VOICE", system_prompt)
            self.assertIn("natural, professional English", system_prompt)
            self.assertIn(
                '"response_language":"english"',
                request_payload["messages"][0]["content"],
            )
            self.assertIn(
                "Which host should be investigated next?",
                request_payload["messages"][0]["content"],
            )
            return httpx.Response(
                200,
                json={
                    "content": [
                        {"type": "text", "text": _structured_text("Investigate host-7 next.")}
                    ],
                    "stop_reason": "end_turn",
                },
            )

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(respond)
        ) as client:
            with patch(
                "app.services.case_analysis.service.resolve_core_llm_target",
                return_value=_target(),
            ):
                answer = await MainCaseAnalysisService(client=client).analyze(
                    mode="question_answer",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question="Which host should be investigated next?",
                    user_message="Which host should be investigated next?",
                )

        self.assertEqual(answer.answer, "Investigate host-7 next.")
        self.assertEqual(answer.trace.analysis_mode, "question_answer")
        self.assertEqual(case_state, expected_case_state)
        self.assertEqual(analysis_context, expected_analysis_context)

    def test_response_language_uses_thai_script_before_english_terms(self) -> None:
        self.assertEqual(
            resolve_response_language("ช่วยวิเคราะห์ PowerShell และ T1059 ให้หน่อย"),
            "thai",
        )
        self.assertEqual(
            resolve_response_language("Please analyze the PowerShell activity."),
            "english",
        )

    def test_response_language_rejects_nonlinguistic_message(self) -> None:
        with self.assertRaises(ValueError):
            resolve_response_language("198.51.100.23 -> 10.0.0.5")

        case_state, analysis_context = _case_inputs()
        with self.assertRaises(CaseAnalysisFailure) as raised:
            build_case_analysis_prompt(
                mode="case_overview",
                case_state_json=case_state,
                analysis_context=analysis_context,
                question=None,
                response_language=cast(ResponseLanguage, "spanish"),
            )
        self.assertEqual(
            raised.exception.code,
            "analysis_response_language_unsupported",
        )

    async def test_thai_user_message_selects_natural_thai_response_profile(self) -> None:
        case_state, analysis_context = _case_inputs()

        def respond(request: httpx.Request) -> httpx.Response:
            request_payload = json.loads(request.content)
            system_prompt = request_payload["system"]
            user_prompt = request_payload["messages"][0]["content"]
            self.assertIn("natural, contemporary, professional Thai", system_prompt)
            self.assertIn('"response_language":"thai"', user_prompt)
            return httpx.Response(
                200,
                json={
                    "content": [
                        {
                            "type": "text",
                            "text": _structured_text("ขณะนี้ข้อมูลระบุเพียงกิจกรรมที่ถูกรายงาน"),
                        }
                    ],
                    "stop_reason": "end_turn",
                },
            )

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(respond)
        ) as client:
            with patch(
                "app.services.case_analysis.service.resolve_core_llm_target",
                return_value=_target(),
            ):
                result = await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question=None,
                    user_message="ช่วยวิเคราะห์เหตุการณ์นี้ให้หน่อยครับ",
                )

        self.assertEqual(
            result.answer,
            "ขณะนี้ข้อมูลระบุเพียงกิจกรรมที่ถูกรายงาน",
        )

    async def test_unsupported_user_message_language_fails_before_provider(self) -> None:
        case_state, analysis_context = _case_inputs()
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: self.fail("Provider must not be called")
            )
        ) as client:
            with self.assertRaises(CaseAnalysisFailure) as raised:
                await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question=None,
                    user_message="198.51.100.23 -> 10.0.0.5",
                )

        self.assertEqual(
            raised.exception.code,
            "analysis_response_language_unsupported",
        )

    async def test_provider_failure_does_not_mutate_nested_inputs(self) -> None:
        case_state, analysis_context = _case_inputs()
        expected_case_state = deepcopy(case_state)
        expected_analysis_context = deepcopy(analysis_context)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(503, json={"error": "unavailable"})
            )
        ) as client:
            with (
                patch(
                    "app.services.case_analysis.service.resolve_core_llm_target",
                    return_value=_target(),
                ),
                self.assertRaises(CaseAnalysisFailure) as raised,
            ):
                await MainCaseAnalysisService(client=client).analyze(
                    mode="question_answer",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question="What does the current analysis support?",
                    user_message="What does the current analysis support?",
                )

        self.assertEqual(raised.exception.code, "analysis_provider_error")
        self.assertEqual(case_state, expected_case_state)
        self.assertEqual(analysis_context, expected_analysis_context)

    async def test_case_overview_uses_deterministic_overview_task(self) -> None:
        case_state, analysis_context = _case_inputs()

        def respond(request: httpx.Request) -> httpx.Response:
            request_payload = json.loads(request.content)
            prompt = request_payload["messages"][0]["content"]
            system_prompt = request_payload["system"]
            self.assertIn("TRUST HIERARCHY", system_prompt)
            self.assertIn("Do not retrieve new information", system_prompt)
            self.assertIn("ANALYSIS MODE: case_overview", system_prompt)
            self.assertIn("five sections in this order", system_prompt)
            self.assertIn(
                "copy its exact status into epistemic_status",
                system_prompt,
            )
            self.assertIn(
                '"not_established" and "not_confirmed" are distinct values',
                system_prompt,
            )
            self.assertIn(
                "Split claims when referenced relationship statuses differ",
                system_prompt,
            )
            self.assertIn('"analysis_mode":"case_overview"', prompt)
            self.assertIn('"question":null', prompt)
            return httpx.Response(
                200,
                json={
                    "content": [
                        {"type": "text", "text": _structured_text("Bounded main case analysis.")}
                    ],
                    "stop_reason": "end_turn",
                },
            )

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(respond)
        ) as client:
            with patch(
                "app.services.case_analysis.service.resolve_core_llm_target",
                return_value=_target(),
            ):
                answer = await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question=None,
                    user_message="Please analyze this case.",
                )

        self.assertEqual(answer.answer, "Bounded main case analysis.")
        self.assertEqual(answer.trace.analysis_mode, "case_overview")

    async def test_openrouter_output_text_block_is_accepted(self) -> None:
        case_state, analysis_context = _case_inputs()

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "content": [
                            {"type": "redacted_thinking", "data": "omitted"},
                            {"type": "output_text", "text": _structured_text("Output-text analysis.")},
                        ],
                        "stop_reason": "end_turn",
                    },
                )
            )
        ) as client:
            with patch(
                "app.services.case_analysis.service.resolve_core_llm_target",
                return_value=_target(),
            ):
                answer = await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question=None,
                    user_message="Please analyze this case.",
                )

        self.assertEqual(answer.answer, "Output-text analysis.")

    async def test_openai_choices_envelope_is_accepted(self) -> None:
        case_state, analysis_context = _case_inputs()

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "choices": [
                            {
                                "message": {
                                    "role": "assistant",
                                    "content": _structured_text("Choices-envelope analysis."),
                                },
                                "finish_reason": "stop",
                            }
                        ]
                    },
                )
            )
        ) as client:
            with patch(
                "app.services.case_analysis.service.resolve_core_llm_target",
                return_value=_target(),
            ):
                answer = await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question=None,
                    user_message="Please analyze this case.",
                )

        self.assertEqual(answer.answer, "Choices-envelope analysis.")

    async def test_success_error_envelope_is_classified_as_provider_error(self) -> None:
        case_state, analysis_context = _case_inputs()

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "type": "error",
                        "error": {
                            "type": "api_error",
                            "error_type": "provider_overloaded",
                        },
                    },
                )
            )
        ) as client:
            with (
                patch(
                    "app.services.case_analysis.service.resolve_core_llm_target",
                    return_value=_target(),
                ),
                self.assertRaises(CaseAnalysisFailure) as raised,
            ):
                await MainCaseAnalysisService(client=client).analyze(
                    mode="case_overview",
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question=None,
                    user_message="Please analyze this case.",
                )

        self.assertEqual(raised.exception.code, "analysis_provider_error")

    def test_analysis_mode_literal_is_exported(self) -> None:
        self.assertEqual(
            get_args(AnalysisMode),
            ("case_overview", "question_answer"),
        )

    def test_invalid_mode_and_question_combinations_fail_stably(self) -> None:
        case_state, analysis_context = _case_inputs()
        invalid_requests = (
            ("unsupported", None),
            ("question_answer", None),
            ("question_answer", "   "),
            ("case_overview", "Do not accept this question"),
        )

        for mode, question in invalid_requests:
            with (
                self.subTest(mode=mode, question=question),
                self.assertRaises(CaseAnalysisFailure) as raised,
            ):
                build_case_analysis_prompt(
                    mode=mode,  # type: ignore[arg-type]
                    case_state_json=case_state,
                    analysis_context=analysis_context,
                    question=question,
                    response_language="english",
                )
            self.assertEqual(raised.exception.code, "analysis_invalid_request")

    def test_oversized_question_answer_retains_exact_mode_and_question(self) -> None:
        exact_question = "  Which exact host is supported by this case?  "
        with patch.object(settings, "chat_ask_max_input_chars", 480):
            prompt = build_case_analysis_prompt(
                mode="question_answer",
                case_state_json={"case_summary": "case " * 1_000},
                analysis_context={"retrieved_context": "context " * 1_000},
                question=exact_question,
                response_language="english",
            )

        serialized = prompt.split("<case_context_json>\n", 1)[1].split(
            "\n</case_context_json>",
            1,
        )[0]
        payload = json.loads(serialized)
        self.assertLessEqual(len(prompt), 480)
        self.assertEqual(payload["analysis_mode"], "question_answer")
        self.assertEqual(payload["response_language"], "english")
        self.assertEqual(payload["question"], exact_question)
        self.assertTrue(payload["context_truncated"])
        self.assertTrue(payload["case_narrative"]["truncated"])
        self.assertTrue(payload["analysis_context"]["truncated"])

    def test_oversized_case_state_preserves_relationship_status_contract(self) -> None:
        case_state = {
            "case_summary": "case " * 1_000,
            "relationships": [
                {
                    "relationship_id": "REL-001",
                    "status": "not_established",
                }
            ],
        }
        with patch.object(settings, "chat_ask_max_input_chars", 900):
            prompt = build_case_analysis_prompt(
                mode="question_answer",
                case_state_json=case_state,
                analysis_context={"retrieved_context": "context " * 1_000},
                question="Which relationship remains unresolved?",
                response_language="english",
            )

        serialized = prompt.split("<case_context_json>\n", 1)[1].split(
            "\n</case_context_json>",
            1,
        )[0]
        payload = json.loads(serialized)
        self.assertLessEqual(len(prompt), 900)
        self.assertTrue(payload["context_truncated"])
        self.assertEqual(
            payload["relationship_status_contract"],
            [{"relationship_id": "REL-001", "status": "not_established"}],
        )


if __name__ == "__main__":
    unittest.main()
