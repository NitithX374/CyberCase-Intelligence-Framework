"""Token budgeting, estimation, and context-window allocation for LLM prompts."""

from __future__ import annotations

import functools
import json
import logging
from dataclasses import asdict, dataclass
from typing import Any

from app.config import settings

logger = logging.getLogger("app.token_budget")


@functools.lru_cache(maxsize=4)
def _get_tiktoken_encoding(encoding_name: str = "cl100k_base"):
    try:
        import tiktoken

        return tiktoken.get_encoding(encoding_name)
    except Exception as exc:
        logger.debug(
            "tiktoken encoding %s not available (%s); using fallback heuristic",
            encoding_name,
            exc,
        )
        return None


def estimate_tokens(text: str | None, encoding_name: str = "cl100k_base") -> int:
    """Estimate token count for a string using tiktoken with conservative fallback."""
    if not text:
        return 0
    enc = _get_tiktoken_encoding(encoding_name)
    if enc is not None:
        try:
            return len(enc.encode(text))
        except Exception:
            pass
    # Fallback heuristic: conservative character-to-token ratio
    # For UTF-8 / Thai / Asian characters, 1 token ~ 2-3 bytes.
    utf8_len = len(text.encode("utf-8", errors="replace"))
    return max(1, (utf8_len + 2) // 3)


def estimate_json_tokens(data: Any, encoding_name: str = "cl100k_base") -> int:
    """Estimate token count for a JSON-serializable data structure."""
    if data is None:
        return 0
    serialized = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return estimate_tokens(serialized, encoding_name)


def get_safe_input_token_budget() -> int:
    """Return the safe input token budget for the active model context window.

    Formula:
      min(chat_max_input_tokens,
          chat_model_context_tokens - chat_reserved_output_tokens - chat_safety_margin_tokens)
    """
    context_limit = getattr(settings, "chat_model_context_tokens", 128_000)
    reserved_output = getattr(settings, "chat_reserved_output_tokens", 4_000)
    safety_margin = getattr(settings, "chat_safety_margin_tokens", 12_000)
    max_input = getattr(settings, "chat_max_input_tokens", 100_000)

    derived_budget = max(1_000, context_limit - reserved_output - safety_margin)
    return max(1_000, min(max_input, derived_budget))


@dataclass(frozen=True)
class ContextBudgetDiagnostics:
    estimated_input_tokens: int
    configured_input_token_budget: int
    raw_evidence_character_length: int
    raw_evidence_estimated_tokens: int
    external_context_estimated_tokens: int
    context_truncated: bool
    retained_evidence_ratio: float
    retained_external_context_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def log_context_budget_diagnostics(
    *,
    feature: str,
    estimated_input_tokens: int,
    configured_input_token_budget: int,
    raw_evidence: str | None = None,
    external_context: Any = None,
    context_truncated: bool = False,
    retained_evidence_ratio: float = 1.0,
    retained_external_context_ratio: float = 1.0,
) -> ContextBudgetDiagnostics:
    evidence_text = raw_evidence or ""
    diag = ContextBudgetDiagnostics(
        estimated_input_tokens=estimated_input_tokens,
        configured_input_token_budget=configured_input_token_budget,
        raw_evidence_character_length=len(evidence_text),
        raw_evidence_estimated_tokens=estimate_tokens(evidence_text),
        external_context_estimated_tokens=(
            estimate_json_tokens(external_context) if external_context else 0
        ),
        context_truncated=context_truncated,
        retained_evidence_ratio=retained_evidence_ratio,
        retained_external_context_ratio=retained_external_context_ratio,
    )
    logger.debug(
        "Context budget diagnostics [%s]: tokens=%d, budget=%d, evidence_chars=%d, "
        "evidence_tokens=%d, context_tokens=%d, truncated=%s, evidence_ratio=%.2f, "
        "context_ratio=%.2f",
        feature,
        diag.estimated_input_tokens,
        diag.configured_input_token_budget,
        diag.raw_evidence_character_length,
        diag.raw_evidence_estimated_tokens,
        diag.external_context_estimated_tokens,
        diag.context_truncated,
        diag.retained_evidence_ratio,
        diag.retained_external_context_ratio,
    )
    return diag


__all__ = [
    "ContextBudgetDiagnostics",
    "estimate_json_tokens",
    "estimate_tokens",
    "get_safe_input_token_budget",
    "log_context_budget_diagnostics",
]
