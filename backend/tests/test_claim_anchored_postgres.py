import asyncio
import json
from datetime import datetime, timedelta, timezone

import httpx
from app.config import settings
from app.models import ChatMessage, ChatRun, ChatThread
from app.schemas.chat import ChatMessageCreate
from app.services.case_analysis.case_analysis_executor import request_case_analysis
from app.services.chat.chat_run_creation import create_message_and_run
from app.services.followup.decision import evaluate_followup_outcome
from app.services.workflow.analysis_execution_receipt import persist_analysis_receipt
from app.services.workflow.chat_run_claim import claim_run
from app.services.workflow.chat_run_store import ChatRunWorker
from app.services.workflow.pipeline_execution import (
    PipelineDependencies,
    process_chat_run,
)
from app.services.workflow.run_recovery import recover_expired_runs
from run_recovery_support import create_request, isolated_database
from sqlalchemy import select
from test_claim_anchored_binding import extraction
from test_claim_anchored_pipeline import envelope
from test_stateful_clarification_pipeline import Analyzer, Policy, gap


async def forbidden(*args, **kwargs):
    raise AssertionError("Technical path must not execute")


def transport(request, *, invalid=False):
    payload = json.loads(request.content)
    content = json.loads(payload["messages"][0]["content"])
    if "sources" in content:
        claims = [
            extraction(
                "absent quotation" if invalid else source["content"],
                source["source_message_id"],
            ).model_dump(mode="json")["claims"][0]
            for source in content["sources"]
        ]
        result = {"claims": claims}
    else:
        result = {
            "units": [
                {"text": claim["text"], "claim_ids": [claim["claim_id"]]}
                for claim in content["selected_claims"]
            ]
        }
    return httpx.Response(200, json=envelope(result))


async def execute(factory, run_id, *, invalid=False, ask_followup=False):
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda request: transport(request, invalid=invalid)
        )
    ) as client:

        async def analyze(**kwargs):
            return await request_case_analysis(**kwargs, client=client)

        dependencies = PipelineDependencies(
            session_factory=factory,
            worker_type=ChatRunWorker,
            rag_request=forbidden,
            analysis_request=analyze,
            followup_evaluator=evaluate_followup_outcome,
        )
        await process_chat_run(
            run_id,
            dependencies=dependencies,
            applicability_call=forbidden,
            gap_analyzer=Analyzer([gap("Identity")] if ask_followup else []),
            policy=Policy("Identity", "Who saw the bicycle?"),
        )


def configure(monkeypatch):
    monkeypatch.setattr(settings, "case_analysis_pipeline", "claim_anchored")
    monkeypatch.setattr(settings, "core_llm_provider", "openrouter")
    monkeypatch.setattr(settings, "chat_ask_model", "openai/gpt-5.6-luna")
    monkeypatch.setattr(settings, "openrouter_cybercase", "test")


def test_interrupted_run_keeps_pinned_method_and_stage_receipt(monkeypatch):
    configure(monkeypatch)

    async def exercise():
        async with isolated_database() as factory:
            thread_id, message, run, request = await create_request(factory)
            async with factory() as db:
                await claim_run(db, run.id, "interrupted-owner")
            await persist_analysis_receipt(
                factory,
                run.id,
                "interrupted-owner",
                {
                    "calls": [
                        {"stage": "extraction", "status": "started", "usage": None}
                    ],
                },
            )
            async with factory() as db, db.begin():
                saved = await db.get(ChatRun, run.id)
                saved.lease_expires_at = datetime.now(timezone.utc) - timedelta(
                    seconds=1
                )
            assert await recover_expired_runs(factory) == 1
            monkeypatch.setattr(settings, "case_analysis_pipeline", "raw_direct")
            monkeypatch.setattr(settings, "chat_ask_model", "openai/gpt-4o")
            async with factory() as db:
                retry_message, retry_run = await create_message_and_run(
                    db, thread_id, request
                )
            assert retry_run.id == run.id and retry_message.id == message.id
            await execute(factory, run.id)
            await execute(factory, run.id)
            async with factory() as db:
                saved = await db.get(ChatRun, run.id)
                assert saved.status == "completed" and saved.attempt_count == 2
                assert (
                    saved.request_payload["analysis_pipeline"]["model"]
                    == "openai/gpt-5.6-luna"
                )
                assert (
                    saved.request_payload["analysis_previous_attempts"][0][
                        "run_attempt"
                    ]
                    == 1
                )
                results = list(
                    (
                        await db.scalars(
                            select(ChatMessage).where(
                                ChatMessage.thread_id == thread_id
                            )
                        )
                    ).all()
                )
                assert len(results) == 2
                assistant = next(item for item in results if item.role == "assistant")
                assert (
                    assistant.metadata_json["analysis_execution"][
                        "semantic_verification"
                    ]
                    == "not_performed"
                )
                assert (
                    assistant.metadata_json["analysis_trace"]["version"]
                    == "analysis_trace_v3"
                )
                assert len(assistant.metadata_json["analysis_execution"]["calls"]) == 2

    asyncio.run(exercise())


def test_provider_failure_survives_heartbeat_exception_group(monkeypatch):
    configure(monkeypatch)

    async def exercise():
        async with isolated_database() as factory:
            thread_id, _, run, _ = await create_request(factory)
            await execute(factory, run.id, invalid=True)
            async with factory() as db:
                saved = await db.get(ChatRun, run.id)
                assert saved.status == "failed"
                assert saved.error_code == "claim_quote_absent"
                receipt = saved.request_payload["analysis_execution"]
                assert receipt["calls"][0]["status"] == "completed"
                assert (
                    saved.request_payload["analysis_failed_attempts"][0]["attempt"] == 1
                )
                assistant = await db.scalar(
                    select(ChatMessage).where(
                        ChatMessage.thread_id == thread_id,
                        ChatMessage.role == "assistant",
                    )
                )
                assert assistant is None

    asyncio.run(exercise())


def test_clarification_inherits_pinned_root_after_setting_changes(monkeypatch):
    configure(monkeypatch)

    async def exercise():
        async with isolated_database() as factory:
            thread_id, _, run, _ = await create_request(factory)
            await execute(factory, run.id, ask_followup=True)
            async with factory() as db:
                thread = await db.get(ChatThread, thread_id)
                assert thread.status == "awaiting_followup"
            monkeypatch.setattr(settings, "case_analysis_pipeline", "raw_direct")
            async with factory() as db:
                _, continuation = await create_message_and_run(
                    db,
                    thread_id,
                    ChatMessageCreate(
                        content="The witness was Somchai.",
                        idempotency_key="clarification-answer",
                    ),
                )
            assert (
                continuation.request_payload["analysis_pipeline"]
                == run.request_payload["analysis_pipeline"]
            )
            await execute(factory, continuation.id)
            async with factory() as db:
                saved = await db.get(ChatRun, continuation.id)
                assert saved.status == "completed"
                messages = list(
                    (
                        await db.scalars(
                            select(ChatMessage)
                            .where(
                                ChatMessage.thread_id == thread_id,
                                ChatMessage.role == "assistant",
                            )
                            .order_by(ChatMessage.ordinal)
                        )
                    ).all()
                )
                assert len(messages) == 2
                assert all(
                    item.metadata_json["analysis_pipeline"]["pipeline"]
                    == "claim_anchored"
                    for item in messages
                )
                assert len(messages[-1].metadata_json["analysis_trace"]["claims"]) == 2

    asyncio.run(exercise())
