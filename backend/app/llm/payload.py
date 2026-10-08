from __future__ import annotations

import json
from functools import lru_cache

import tiktoken
from pydantic import BaseModel

from app.llm.schema import structured_system_prompt
from app.llm.settings import AnalysisPipelineConfig


@lru_cache(maxsize=1)
def encoding():
    return tiktoken.get_encoding("o200k_base")


def token_count(value: object) -> int:
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return len(encoding().encode(serialized, disallowed_special=()))


def input_budget(config: AnalysisPipelineConfig) -> int:
    return min(
        config.input_tokens, config.context_tokens - config.max_tokens - config.safety_tokens
    )


def thinking_option(config: AnalysisPipelineConfig) -> dict[str, object]:
    if config.thinking_tokens == 0:
        return {"type": "disabled"}
    return {"type": "enabled", "budget_tokens": config.thinking_tokens}


def stage_payload(
    config: AnalysisPipelineConfig,
    system: str,
    content: dict[str, object] | str,
    schema: type[BaseModel],
    *,
    temperature: float | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": config.model,
        "max_tokens": config.max_tokens,
        "thinking": thinking_option(config),
        "system": structured_system_prompt(system, schema),
        "messages": [
            {
                "role": "user",
                "content": content
                if isinstance(content, str)
                else json.dumps(content, ensure_ascii=False, separators=(",", ":")),
            }
        ],
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if config.providers:
        payload["provider"] = {"order": list(config.providers), "allow_fallbacks": False}
    return payload
