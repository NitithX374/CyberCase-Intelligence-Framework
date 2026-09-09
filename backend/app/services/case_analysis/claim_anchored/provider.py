import asyncio
import json
import time
from collections.abc import Awaitable, Callable
from functools import lru_cache
from typing import TypeVar

import httpx
import tiktoken
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.case_analysis.case_analysis_response_utils import (
    _extract_visible_text,
)
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig
from app.services.case_analysis.response_decoder import validated_response_payload
from app.services.llm.core_llm import CoreLlmTarget, resolve_core_llm_target
from app.services.llm.structured_output import (
    structured_output_request_options,
    structured_output_schema,
)

Record = TypeVar("Record", bound=BaseModel)


@lru_cache(maxsize=1)
def encoding():
    return tiktoken.get_encoding("o200k_base")


def token_count(value: object) -> int:
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return len(encoding().encode(serialized, disallowed_special=()))


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
        "messages": [
            {"role": "user", "content": json.dumps(content, ensure_ascii=False)}
        ],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": structured_output_schema(schema, provider=config.provider),
            }
        },
    }


def input_budget(config: AnalysisPipelineConfig) -> int:
    return min(
        config.input_tokens,
        config.context_tokens - config.output_tokens - config.safety_tokens,
    )


def resolve_target(config: AnalysisPipelineConfig) -> CoreLlmTarget:
    configured = settings.model_copy(update={"core_llm_provider": config.provider})
    return resolve_core_llm_target(config.model, configured_settings=configured)


async def request_stage(
    *,
    client: httpx.AsyncClient,
    target: CoreLlmTarget,
    config: AnalysisPipelineConfig,
    stage: str,
    system: str,
    content: dict[str, object],
    schema: type[Record],
    calls: list[dict[str, object]],
    checkpoint: Callable[[], Awaitable[None]] | None = None,
) -> Record:
    payload = stage_payload(config, system, content, schema)
    estimated = await asyncio.to_thread(token_count, payload)
    if estimated > input_budget(config):
        raise ClaimAnchoredFailure(
            f"claim_{stage}_budget_exceeded", "Complete stage input exceeds budget"
        )
    receipt: dict[str, object] = {
        "stage": stage,
        "model": config.model,
        "provider": target.provider,
        "estimated_input_tokens": estimated,
        "token_estimator": config.encoding,
        "status": "started",
    }
    calls.append(receipt)
    if checkpoint is not None:
        await checkpoint()
    started = time.monotonic()
    try:
        response = await client.post(
            target.messages_url,
            headers=target.headers,
            json=payload,
            timeout=config.timeout_seconds,
        )
        try:
            raw_response = response.json()
        except ValueError:
            raw_response = None
        if isinstance(raw_response, dict):
            receipt["usage"] = raw_response.get("usage")
            receipt["returned_model"] = raw_response.get("model")
            receipt["request_id"] = raw_response.get("id")
        decoded = validated_response_payload(response)
        result = schema.model_validate_json(_extract_visible_text(decoded))
        receipt["status"] = "completed"
        return result
    except httpx.TimeoutException as error:
        raise ClaimAnchoredFailure(
            f"claim_{stage}_timeout", "Analysis stage timed out"
        ) from error
    except httpx.RequestError as error:
        raise ClaimAnchoredFailure(
            f"claim_{stage}_transport", "Analysis stage transport failed"
        ) from error
    except ValidationError as error:
        raise ClaimAnchoredFailure(
            f"claim_{stage}_invalid", "Analysis stage violated its schema"
        ) from error
    except CaseAnalysisFailure:
        raise
    finally:
        receipt["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        if receipt["status"] == "started":
            receipt["status"] = "failed"
        if checkpoint is not None:
            await checkpoint()
