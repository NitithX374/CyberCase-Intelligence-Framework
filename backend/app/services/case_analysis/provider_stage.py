from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Awaitable, Callable
from functools import lru_cache
from typing import TypeVar

import httpx
import tiktoken
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.services.case_analysis.case_analysis_response_parser import (
    extract_visible_text,
    validate_response_payload,
)
from app.services.case_analysis.contracts import CaseAnalysisFailure
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig
from app.services.llm.core_llm import CoreLlmTarget, resolve_core_llm_target
from app.services.llm.structured_output import (
    structured_output_request_options,
    structured_output_schema,
)

ProviderResult = TypeVar("ProviderResult", bound=BaseModel)


@lru_cache(maxsize=1)
def encoding():
    return tiktoken.get_encoding("o200k_base")


def token_count(value: object) -> int:
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return len(encoding().encode(serialized, disallowed_special=()))


def input_budget(config: AnalysisPipelineConfig) -> int:
    return min(
        config.input_tokens,
        config.context_tokens - config.output_tokens - config.safety_tokens,
    )


def resolve_target(config: AnalysisPipelineConfig) -> CoreLlmTarget:
    configured = settings.model_copy(update={"core_llm_provider": config.provider})
    return resolve_core_llm_target(config.model, configured_settings=configured)


def stage_payload(
    config: AnalysisPipelineConfig,
    system: str,
    content: dict[str, object],
    schema: type[BaseModel],
) -> dict[str, object]:
    return {
        "model": config.model,
        **structured_output_request_options(
            provider=config.provider,
            feature="case_analysis",
            configured_max_tokens=config.output_tokens,
        ),
        "system": system,
        "messages": [{"role": "user", "content": json.dumps(content, ensure_ascii=False)}],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": structured_output_schema(schema, provider=config.provider),
            }
        },
    }


async def request_stage(
    *,
    client: httpx.AsyncClient | None,
    target: CoreLlmTarget,
    config: AnalysisPipelineConfig,
    stage: str,
    system: str,
    content: dict[str, object],
    schema: type[ProviderResult],
    calls: list[dict[str, object]],
    checkpoint: Callable[[], Awaitable[None]] | None = None,
) -> ProviderResult:
    payload = stage_payload(config, system, content, schema)
    estimated = await asyncio.to_thread(token_count, payload)
    if estimated > input_budget(config):
        raise CaseAnalysisFailure(f"{stage}_budget_exceeded", "Stage input exceeds budget")
    receipt: dict[str, object] = {
        "stage": stage,
        "model": config.model,
        "provider": target.provider,
        "estimated_input_tokens": estimated,
        "status": "started",
    }
    calls.append(receipt)
    if checkpoint is not None:
        await checkpoint()
    started = time.monotonic()
    try:
        if client is not None:
            response = await client.post(
                target.messages_url,
                headers=target.headers,
                json=payload,
                timeout=config.timeout_seconds,
            )
            decoded = validate_response_payload(response)
            result = schema.model_validate_json(extract_visible_text(decoded))
        else:
            model = build_chat_model(config, target)
            structured_model = model.with_structured_output(schema)
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system),
                    MessagesPlaceholder("conversation_history"),
                    ("human", "{content}"),
                ]
            )
            history = conversation_messages(content.get("conversation_history"))
            chain = prompt | structured_model
            async with asyncio.timeout(config.timeout_seconds):
                result = await chain.ainvoke(
                    {
                        "conversation_history": history,
                        "content": json.dumps(content, ensure_ascii=False),
                    }
                )
            result = schema.model_validate(result)
        receipt["status"] = "completed"
        return result
    except (asyncio.TimeoutError, httpx.TimeoutException) as error:
        raise CaseAnalysisFailure(f"{stage}_timeout", "Analysis stage timed out") from error
    except ValidationError as error:
        raise CaseAnalysisFailure(f"{stage}_invalid", "Analysis stage violated its schema") from error
    except httpx.RequestError as error:
        raise CaseAnalysisFailure(f"{stage}_transport", "Analysis stage transport failed") from error
    except Exception as error:
        raise CaseAnalysisFailure(f"{stage}_provider", "Analysis stage provider failed") from error
    finally:
        receipt["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        if receipt["status"] == "started":
            receipt["status"] = "failed"
        if checkpoint is not None:
            await checkpoint()


def build_chat_model(
    config: AnalysisPipelineConfig,
    target: CoreLlmTarget,
) -> ChatOpenAI | ChatAnthropic:
    common = {
        "model": target.model,
        "api_key": target.api_key,
        "timeout": config.timeout_seconds,
        "max_retries": 0,
        "temperature": 0,
        "max_tokens": config.output_tokens,
    }
    if target.provider == "openrouter":
        return ChatOpenAI(base_url=target.base_url, **common)
    return ChatAnthropic(base_url=target.base_url, **common)


def conversation_messages(value: object) -> list[HumanMessage | AIMessage]:
    if not isinstance(value, list):
        return []
    messages: list[HumanMessage | AIMessage] = []
    for item in value[-12:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


__all__ = [
    "build_chat_model",
    "conversation_messages",
    "input_budget",
    "request_stage",
    "resolve_target",
    "stage_payload",
    "token_count",
]
