from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langgraph.types import interrupt
from langchain_core.runnables import RunnableLambda

from app.services.gap_clarification import graph
from app.services.gap_clarification.contracts import (
    ClarificationResumeAnswer,
    GapAnswerInterpretation,
    GapNextStep,
)
from app.services.case_analysis.contracts import CaseQuestionAnswerResponse
from app.services.case_analysis.pipeline_config import configured_pipeline
from app.services.case_analysis import provider_stage
from app.services.llm.core_llm import CoreLlmTarget


def initial_state() -> dict[str, object]:
    return {
        "case_id": str(uuid4()),
        "source_analysis_id": str(uuid4()),
        "source_evidence_revision": 1,
        "response_language": "english",
        "gap_id": "G-01",
        "attempt_count": 0,
        "resolution_status": "unresolved",
    }


def test_gap_contract_rejects_question_without_target() -> None:
    with pytest.raises(ValueError):
        GapNextStep(action="ask", question="What time?")


def test_adaptive_graph_interrupts_and_resumes_with_a_different_question(monkeypatch) -> None:
    async def select_question(state, config):
        if state.get("attempt_count"):
            return {
                "attempt_count": 2,
                "pending_question_message_id": "q-2",
                "resolution_status": "unresolved",
            }
        return {
            "attempt_count": 1,
            "pending_question_message_id": "q-1",
            "resolution_status": "unresolved",
        }

    questions = {
        "q-1": "Do you know the exact time?",
        "q-2": "What record shows the time?",
    }

    async def ask_user(state, config):
        answer = interrupt(
            {
                "question_message_id": state["pending_question_message_id"],
                "question": questions[state["pending_question_message_id"]],
            }
        )
        return {"latest_answer": dict(answer)}

    async def interpret_answer(state, config):
        content = state["latest_answer"]["content"]
        if content == "No":
            value = GapAnswerInterpretation(
                response_type="scope_clarification",
                gap_resolution="partially_resolved",
            )
        else:
            value = GapAnswerInterpretation(
                response_type="case_fact",
                normalized_fact=content,
                gap_resolution="resolved",
            )
        return {"latest_interpretation": value.model_dump(mode="json")}

    async def commit_answer(state, config):
        return {}

    monkeypatch.setattr(graph, "select_question", select_question)
    monkeypatch.setattr(graph, "ask_user", ask_user)
    monkeypatch.setattr(graph, "interpret_answer", interpret_answer)
    monkeypatch.setattr(graph, "commit_answer", commit_answer)

    async def exercise() -> None:
        state = initial_state()
        config = {"configurable": {"thread_id": str(uuid4())}}
        compiled = graph.build_gap_clarification_graph(MemorySaver())
        first = await compiled.ainvoke(state, config=config)
        assert "pending_question" not in first
        assert "pending_target_information" not in first
        assert first["__interrupt__"][0].value["question"] == "Do you know the exact time?"

        second = await compiled.ainvoke(
            Command(
                resume={
                    "content": "No",
                    "disposition": "answered",
                    "request_key": "answer-1",
                    "question_message_id": first["pending_question_message_id"],
                }
            ),
            config=config,
        )
        assert second["__interrupt__"][0].value["question"] == "What record shows the time?"

        final = await compiled.ainvoke(
            Command(
                resume={
                    "content": "transaction at 22:31",
                    "disposition": "answered",
                    "request_key": "answer-2",
                    "question_message_id": second["pending_question_message_id"],
                }
            ),
            config=config,
        )
        assert final["resolution_status"] == "resolved"
        assert "__interrupt__" not in final

    asyncio.run(exercise())


def test_duplicate_question_terminates_instead_of_looping(monkeypatch) -> None:
    async def select_question(state, config):
        if state.get("attempt_count"):
            return {"pending_question_message_id": None, "resolution_status": "not_productive"}
        return {
            "attempt_count": 1,
            "pending_question_message_id": "q-1",
            "resolution_status": "unresolved",
        }

    async def ask_user(state, config):
        answer = interrupt(
            {
                "question_message_id": state["pending_question_message_id"],
                "question": "What time?",
            }
        )
        return {"latest_answer": dict(answer)}

    async def interpret_answer(state, config):
        return {
            "latest_interpretation": GapAnswerInterpretation(
                response_type="scope_clarification",
                gap_resolution="partially_resolved",
            ).model_dump(mode="json")
        }

    async def commit_answer(state, config):
        return {}

    monkeypatch.setattr(graph, "select_question", select_question)
    monkeypatch.setattr(graph, "ask_user", ask_user)
    monkeypatch.setattr(graph, "interpret_answer", interpret_answer)
    monkeypatch.setattr(graph, "commit_answer", commit_answer)

    async def exercise() -> None:
        state = initial_state()
        config = {"configurable": {"thread_id": str(uuid4())}}
        compiled = graph.build_gap_clarification_graph(MemorySaver())
        first = await compiled.ainvoke(state, config=config)
        final = await compiled.ainvoke(
            Command(
                resume={
                    "content": "No",
                    "disposition": "answered",
                    "request_key": "answer-loop",
                    "question_message_id": first["pending_question_message_id"],
                }
            ),
            config=config,
        )
        assert final["resolution_status"] == "not_productive"

    asyncio.run(exercise())


def test_request_stage_uses_langchain_structured_output(monkeypatch) -> None:
    class FakeModel:
        def with_structured_output(self, schema):
            return RunnableLambda(lambda _: schema(answer="grounded", cited_source_ids=[]))

    monkeypatch.setattr(provider_stage, "build_chat_model", lambda config, target: FakeModel())

    async def exercise() -> None:
        calls: list[dict[str, object]] = []
        result = await provider_stage.request_stage(
            client=None,
            target=CoreLlmTarget(
                provider="openrouter",
                model="openai/test",
                api_key="test-key",
                base_url="https://provider.test/v1",
                messages_url="https://provider.test/v1/messages",
                headers={},
            ),
            config=configured_pipeline(),
            stage="question_answer",
            system="Return structured output.",
            content={"case_sources": [], "conversation_history": []},
            schema=CaseQuestionAnswerResponse,
            calls=calls,
        )
        assert isinstance(result, CaseQuestionAnswerResponse)
        assert result.answer == "grounded"
        assert calls[0]["status"] == "completed"

    asyncio.run(exercise())


def test_unavailable_and_skipped_answers_terminate_without_model_interpretation() -> None:
    from app.services.gap_clarification.nodes import evaluate_gap, interpret_answer

    async def exercise() -> None:
        for disposition, content, status in (
            ("answered", "I don't know", "explicitly_unknown"),
            ("skipped", "", "skipped"),
        ):
            state = initial_state()
            state.update(
                {
                    "pending_question_message_id": str(uuid4()),
                    "latest_answer": {
                        "content": content,
                        "disposition": disposition,
                        "request_key": str(uuid4()),
                    },
                }
            )
            interpretation = await interpret_answer(
                state,
                {"configurable": {"thread_id": str(uuid4())}},
            )
            state.update(interpretation)
            assert evaluate_gap(state)["resolution_status"] == status

    asyncio.run(exercise())


def test_gap_next_step_rejects_contradictory_non_ask_payloads() -> None:
    # ask requires question and target_information
    with pytest.raises(ValueError, match="ask decisions require a question"):
        GapNextStep(action="ask", question="   ", target_information="time")
    with pytest.raises(ValueError, match="ask decisions require target_information"):
        GapNextStep(action="ask", question="What time?", target_information=None)

    # non-ask must not include question or target_information
    with pytest.raises(ValueError, match="resolved decisions cannot include"):
        GapNextStep(action="resolved", question="What time?")
    with pytest.raises(ValueError, match="explicitly_unknown decisions cannot include"):
        GapNextStep(action="explicitly_unknown", target_information="time")

    # non-ask with None values is valid and preserves fields
    step = GapNextStep(action="resolved", question=None, target_information=None, rationale_summary="  done  ")
    assert step.action == "resolved"
    assert step.question is None
    assert step.target_information is None
    assert step.rationale_summary == "done"


def test_gap_answer_interpretation_does_not_mutate_resolution() -> None:
    # case_fact requires normalized_fact
    with pytest.raises(ValueError, match="case_fact responses require normalized_fact"):
        GapAnswerInterpretation(
            response_type="case_fact",
            normalized_fact="   ",
            gap_resolution="resolved",
        )

    # gap_resolution is NOT mutated inside Pydantic
    interp = GapAnswerInterpretation(
        response_type="skip",
        gap_resolution="resolved",
    )
    assert interp.gap_resolution == "resolved"

    # normalization trims fields
    fact = GapAnswerInterpretation(
        response_type="case_fact",
        normalized_fact="  evidence text  ",
        resolved_information="  info  ",
        gap_resolution="resolved",
    )
    assert fact.normalized_fact == "evidence text"
    assert fact.resolved_information == "info"


def test_clarification_resume_answer_rejects_non_answered_content_and_does_not_synthesize() -> None:
    # answered requires content
    with pytest.raises(ValueError, match="answered clarification requires content"):
        ClarificationResumeAnswer(
            content="   ",
            disposition="answered",
            request_key="req-1",
            question_message_id="q-1",
        )

    # non-answered cannot include content
    with pytest.raises(ValueError, match="skipped clarification cannot include content"):
        ClarificationResumeAnswer(
            content="some answer",
            disposition="skipped",
            request_key="req-2",
            question_message_id="q-1",
        )

    # non-answered with empty content does NOT mutate content to disposition
    resume = ClarificationResumeAnswer(
        content="",
        disposition="skipped",
        request_key="  req-3  ",
        question_message_id="q-1",
    )
    assert resume.content == ""
    assert resume.disposition == "skipped"
    assert resume.request_key == "req-3"
