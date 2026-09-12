import asyncio
import json
from functools import partial
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import func, select

from app.models import Case, CaseRun, CaseAnalysisResult, ChatMessage
from app.models.chat import ChatThread
from app.models.caseMaterials import EvidenceSource
from app.schemas.chat import ChatMessageCreate
from app.services.chat.caseChat import createCaseChatMessageAndRun
from app.services.chat import caseAnswer
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.workflow.caseRunExecution import executeCaseRun
from run_recovery_support import isolated_database
from test_case_chat_postgres import _case_with_source, _complete_initial
from test_mitre_applicability_provider import target


@pytest.mark.parametrize("outcome", ["answer", "unknown", "invalid_claim", "transport_failure"])
def test_chat_uses_pinned_analysis_without_reanalysis(monkeypatch, outcome):
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            await _complete_initial(factory, case_id, source_id, followup=False)
            async with factory() as db, db.begin():
                db.add(ChatThread(id=case_id, title="Case Chat"))
            async with factory() as db, db.begin():
                question, run = await createCaseChatMessageAndRun(
                    db, case_id=case_id, user_id=None,
                    request=ChatMessageCreate(content="What vehicle?", idempotency_key="ask-test"),
                )
                result_id = question.analysis_result_id
            captured = []

            def handler(request):
                payload = json.loads(request.content)
                captured.append(payload)
                if outcome == "transport_failure":
                    raise httpx.ConnectError("test unavailable", request=request)
                response = {
                    "insufficient_context": outcome == "unknown",
                    "units": [] if outcome == "unknown" else [{
                        "text": "The witness reported a blue vehicle.",
                        "claim_ids": ["A-99" if outcome == "invalid_claim" else "A-01"],
                    }],
                }
                return httpx.Response(200, json={"output_text": json.dumps(response)})

            async def forbidden(**kwargs):
                raise AssertionError("Chat must not invoke Case analysis or augmentation")

            monkeypatch.setattr(caseAnswer, "resolve_target", lambda config: target())
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                await executeCaseRun(
                    run.id, session_factory=factory,
                    analysis_request=forbidden, applicability_gate=forbidden,
                    rag_request=forbidden, mapping_request=forbidden,
                    answer_request=partial(caseAnswer.generateCaseAnswer, client=client),
                )
            assert len(captured) == 1
            content = json.loads(captured[0]["messages"][0]["content"])
            assert content["question"] == question.content
            assert content["claims"][0]["supporting_citations"][0]["source_id"] == str(source_id)
            assert "raw_case_evidence" not in content
            assert "NativeProviderCaseAnalysis" not in json.dumps(captured[0])
            async with factory() as db:
                saved = await db.get(CaseRun, run.id)
                case = await db.get(Case, case_id)
                assert case.latest_analysis_result_id == result_id
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 1
                assert await db.scalar(select(func.count()).select_from(EvidenceSource)) == 1
                messages = list((await db.scalars(select(ChatMessage).order_by(ChatMessage.ordinal))).all())
                if outcome in {"invalid_claim", "transport_failure"}:
                    assert saved.status == "failed"
                    assert len(messages) == 1
                    return
                assert saved.status == "completed"
                assert len(messages) == 2
                answer = messages[-1]
                assert answer.analysis_result_id == result_id
                assert answer.metadata_json["answer_receipt"]["prompt_version"] == "case_chat_answer_v1"
                assert answer.metadata_json["context_analysis_result_id"] == str(result_id)
                claims = answer.metadata_json["analysis_trace"]["claims"]
                if outcome == "unknown":
                    assert claims == []
                    assert "enough information" in answer.content
                else:
                    assert claims[0]["supporting_citations"] == content["claims"][0]["supporting_citations"]

    asyncio.run(exercise())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("context_analysis_result_id", None),
        ("trace_json", None),
        ("trace_json", {"analysis_mode": "case_overview"}),
        ("provider_metadata_json", []),
    ],
)
def test_chat_rejects_corrupt_pinned_context_without_provider_calls(field, value):
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            await _complete_initial(factory, case_id, source_id, followup=False)
            async with factory() as db, db.begin():
                db.add(ChatThread(id=case_id, title="Case Chat"))
            async with factory() as db, db.begin():
                question, run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=ChatMessageCreate(content="What vehicle?", idempotency_key=f"corrupt-{field}"),
                )
                result = await db.get(CaseAnalysisResult, question.analysis_result_id)
                if field == "context_analysis_result_id":
                    question.analysis_result_id = value
                else:
                    setattr(result, field, value)

            async def forbidden(**kwargs):
                raise AssertionError("Corrupt Chat context must not reach a provider")

            await executeCaseRun(
                run.id,
                session_factory=factory,
                analysis_request=forbidden,
                answer_request=forbidden,
                applicability_gate=forbidden,
                rag_request=forbidden,
                mapping_request=forbidden,
            )
            async with factory() as db:
                saved = await db.get(CaseRun, run.id)
                messages = list((await db.scalars(select(ChatMessage).order_by(ChatMessage.ordinal))).all())
                assert saved.status == "failed"
                assert saved.error_code == "case_ask_context_invalid"
                assert len(messages) == 1

    asyncio.run(exercise())


def test_chat_rejects_cross_case_pinned_result_without_provider_calls():
    async def exercise():
        async with isolated_database() as factory:
            case_a, source_a = await _case_with_source(factory)
            await _complete_initial(factory, case_a, source_a, followup=False)
            case_b, source_b = await _case_with_source(factory)
            await _complete_initial(factory, case_b, source_b, followup=False)
            async with factory() as db, db.begin():
                db.add(ChatThread(id=case_a, title="Case Chat A"))
            async with factory() as db, db.begin():
                question, run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_a,
                    user_id=None,
                    request=ChatMessageCreate(content="What vehicle?", idempotency_key="cross-case"),
                )
                result_b = await db.scalar(
                    select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_b)
                )
                question.analysis_result_id = result_b.id

            async def forbidden(**kwargs):
                raise AssertionError("Cross-case Chat context must not reach a provider")

            await executeCaseRun(
                run.id,
                session_factory=factory,
                analysis_request=forbidden,
                answer_request=forbidden,
                applicability_gate=forbidden,
                rag_request=forbidden,
                mapping_request=forbidden,
            )
            async with factory() as db:
                saved = await db.get(CaseRun, run.id)
                assert saved.status == "failed"
                assert saved.error_code == "case_ask_context_invalid"

    asyncio.run(exercise())


def test_chat_answer_history_is_preceding_same_result_context_only(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            await _complete_initial(factory, case_id, source_id, followup=False)
            async with factory() as db, db.begin():
                db.add(ChatThread(id=case_id, title="Case Chat"))
            async with factory() as db, db.begin():
                case = await db.get(Case, case_id)
                result_id = case.latest_analysis_result_id
                thread = await db.get(ChatThread, case_id)
                for index in range(1, 14):
                    db.add(
                        ChatMessage(
                            thread_id=case_id,
                            ordinal=thread.next_message_ordinal,
                            role="user" if index % 2 else "assistant",
                            content=f"history-{index}",
                            message_kind="conversation",
                            analysis_result_id=result_id,
                            metadata_json=serialize_message_metadata(
                                {"context_analysis_result_id": str(result_id)}
                            ),
                        )
                    )
                    thread.next_message_ordinal += 1
                db.add(
                    ChatMessage(
                        thread_id=case_id,
                        ordinal=thread.next_message_ordinal,
                        role="assistant",
                        content="other-context",
                        message_kind="conversation",
                        metadata_json=serialize_message_metadata(
                            {"context_analysis_result_id": str(uuid4())}
                        ),
                    )
                )
                thread.next_message_ordinal += 1

            async with factory() as db, db.begin():
                _, run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=ChatMessageCreate(content="What vehicle?", idempotency_key="history"),
                )
                thread = await db.get(ChatThread, case_id)
                db.add(
                    ChatMessage(
                        thread_id=case_id,
                        ordinal=thread.next_message_ordinal,
                        role="assistant",
                        content="later-context",
                        message_kind="conversation",
                        metadata_json=serialize_message_metadata(
                            {"context_analysis_result_id": str(result_id)}
                        ),
                    )
                )
                thread.next_message_ordinal += 1
            captured = []

            def handler(request):
                captured.append(json.loads(request.content))
                response = {
                    "insufficient_context": False,
                    "units": [{"text": "The witness reported a blue vehicle.", "claim_ids": ["A-01"]}],
                }
                return httpx.Response(200, json={"output_text": json.dumps(response)})

            async def forbidden(**kwargs):
                raise AssertionError("Chat must not invoke Case analysis or augmentation")

            monkeypatch.setattr(caseAnswer, "resolve_target", lambda config: target())
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                await executeCaseRun(
                    run.id,
                    session_factory=factory,
                    analysis_request=forbidden,
                    applicability_gate=forbidden,
                    rag_request=forbidden,
                    mapping_request=forbidden,
                    answer_request=partial(caseAnswer.generateCaseAnswer, client=client),
                )
            content = json.loads(captured[0]["messages"][0]["content"])
            history = content["conversation_history"]
            assert [item["content"] for item in history] == [f"history-{index}" for index in range(2, 14)]
            assert all(item["content"] not in {"other-context", "later-context"} for item in history)

    asyncio.run(exercise())
