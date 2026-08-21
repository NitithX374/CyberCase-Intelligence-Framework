from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

from app.config import settings
from app.services.followup.schemas import ClarificationExchange, GapAnalysis


def build_bounded_context(
    *,
    original_user_content: str,
    clarification_exchanges: Sequence[ClarificationExchange],
    case_state: Mapping[str, object] | None = None,
    analysis_answer: str | None = None,
    analysis_context: Mapping[str, object] | None = None,
    gap_analysis: GapAnalysis | Mapping[str, object] | None = None,
) -> dict[str, object]:
    original = _bounded(
        original_user_content,
        settings.chat_followup_policy_max_user_chars,
    )
    exchanges = [
        {
            "question": _bounded(
                exchange.question,
                settings.chat_followup_question_max_chars,
            ),
            "answer": _bounded(
                exchange.answer,
                settings.chat_followup_policy_max_user_chars,
            ),
        }
        for exchange in clarification_exchanges
    ]

    def content_size() -> int:
        return len(original) + sum(
            len(str(exchange["question"])) + len(str(exchange["answer"]))
            for exchange in exchanges
        )

    maximum = max(1, settings.chat_followup_combined_query_max_chars)
    gap_analysis_reserve = (
        min(4_096, max(1, maximum // 3))
        if gap_analysis is not None
        else 0
    )
    base_maximum = max(1, maximum - gap_analysis_reserve)
    exchanges = [
        exchange
        for exchange in exchanges
        if exchange["question"] or exchange["answer"]
    ]
    while content_size() > base_maximum and len(exchanges) > 1:
        overflow = content_size() - base_maximum
        exchange = exchanges[0]
        exchange_answer = str(exchange["answer"])
        shortened_answer = exchange_answer[
            : max(0, len(exchange_answer) - overflow)
        ]
        if not shortened_answer:
            exchanges.pop(0)
            continue
        exchange["answer"] = shortened_answer

    if exchanges:
        overflow = content_size() - base_maximum
        if overflow > 0:
            newest_question = str(exchanges[-1]["question"])
            exchanges[-1]["question"] = newest_question[
                : max(0, len(newest_question) - overflow)
            ]

    overflow = content_size() - base_maximum
    if overflow > 0:
        removable = max(0, len(original) - 1)
        remove_count = min(overflow, removable)
        original = original[: len(original) - remove_count]

    if exchanges:
        overflow = content_size() - base_maximum
        if overflow > 0:
            newest_answer = str(exchanges[-1]["answer"])
            removable = max(0, len(newest_answer) - 1)
            remove_count = min(overflow, removable)
            exchanges[-1]["answer"] = newest_answer[
                : len(newest_answer) - remove_count
            ]

    exchanges = [
        exchange
        for exchange in exchanges
        if exchange["question"] or exchange["answer"]
    ]
    payload: dict[str, object] = {
        "original_user_content": original,
        "clarification_exchanges": exchanges,
    }

    if isinstance(gap_analysis, GapAnalysis):
        gap_analysis = gap_analysis.model_dump(mode="json")

    optional_values: list[tuple[str, object | None]] = [
        ("gap_analysis", gap_analysis),
        ("case_state", case_state),
        ("main_case_analysis", analysis_answer),
        ("retrieved_mitre_context", analysis_context),
    ]
    present_count = sum(value is not None for _, value in optional_values)
    maximum = max(1, settings.chat_followup_combined_query_max_chars)
    for key, value in optional_values:
        if value is None:
            continue
        current_size = len(json.dumps(payload, ensure_ascii=False, default=str))
        remaining = max(1, maximum - current_size)
        if key == "gap_analysis":
            budget = min(4_096, remaining)
        else:
            budget = max(1, remaining // max(1, present_count))
        if isinstance(value, Mapping):
            payload[key] = _bounded_mapping(value, budget)
        else:
            payload[key] = _bounded(str(value), budget)
        present_count -= 1
    return payload


def _bounded(value: str, limit: int) -> str:
    return value[: max(0, limit)]


def _bounded_mapping(
    value: Mapping[str, object],
    limit: int,
) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, item in value.items():
        if isinstance(item, str):
            output[str(key)] = _bounded(item, max(1, limit // 4))
        elif isinstance(item, Mapping):
            output[str(key)] = _bounded_mapping(item, max(1, limit // 2))
        elif isinstance(item, list):
            output[str(key)] = [
                _bounded_mapping(entry, max(1, limit // 4))
                if isinstance(entry, Mapping)
                else (
                    _bounded(entry, max(1, limit // 4))
                    if isinstance(entry, str)
                    else entry
                )
                for entry in item[:32]
            ]
        else:
            output[str(key)] = item

    serialized = json.dumps(output, ensure_ascii=False, default=str)
    if len(serialized) <= limit:
        return output
    return {
        "truncated": True,
        "serialized_context": serialized[: max(1, limit - 32)],
    }


__all__ = ["build_bounded_context"]
