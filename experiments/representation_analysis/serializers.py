from __future__ import annotations

import json
import re
from typing import Any

from .constants import EVENT_FIELDS


def serialize_case_state(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def serialize_events(events: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for number, event in enumerate(events, start=1):
        lines = [f"EVENT {number}"]
        lines.extend(f"{field.title()}: {event[field]['text']}" for field in EVENT_FIELDS if field in event)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def estimate_tokens(text: str) -> int:
    return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))
