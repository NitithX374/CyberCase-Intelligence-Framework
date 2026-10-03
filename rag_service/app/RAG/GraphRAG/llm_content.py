"""Safe extraction of visible text from LangChain message responses."""

from typing import Any

from langchain_core.messages import BaseMessage

# A model can answer with no visible text at all — the default OpenRouter
# model did on about one answer call in ten when it was measured. Asking
# again costs one call; not asking fails the whole request.
EMPTY_REPLY_ATTEMPTS = 3


class LlmContentError(ValueError):
    """Raised when an LLM response has no usable visible text."""


def require_message_text(message: BaseMessage, *, operation: str) -> str:
    """Return canonical visible message text or fail without exposing content."""
    try:
        text = getattr(message, "text", None)
    except Exception:
        text = None

    if isinstance(text, str) and text.strip():
        return text

    # Fallback: inspect content if it is a list of dicts (e.g. thinking + text blocks)
    content = getattr(message, "content", None)
    if isinstance(content, list):
        extracted_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                extracted_parts.append(block.get("text") or "")
            elif isinstance(block, str):
                extracted_parts.append(block)
        joined = "".join(extracted_parts).strip()
        if joined:
            return joined
    elif isinstance(content, str) and content.strip():
        return content.strip()

    raise LlmContentError(f"{operation} returned no usable text")


def invoke_for_text(llm: Any, messages: list, *, operation: str) -> str:
    """Invoke ``llm`` and return its visible text, asking again on an empty reply.

    Only an empty reply is retried. Anything ``invoke`` raises propagates from
    the attempt that raised it.
    """
    for attempt in range(1, EMPTY_REPLY_ATTEMPTS + 1):
        response = llm.invoke(messages)
        try:
            return require_message_text(response, operation=operation)
        except LlmContentError:
            if attempt == EMPTY_REPLY_ATTEMPTS:
                raise
            print(
                f"[LLM] {operation} returned no usable text — asking again "
                f"({attempt + 1}/{EMPTY_REPLY_ATTEMPTS})"
            )
    raise AssertionError("unreachable")
