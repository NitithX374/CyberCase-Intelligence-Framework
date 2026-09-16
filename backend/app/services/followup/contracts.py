"""Contracts for deterministic Case follow-up and policy evaluation."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal, Protocol, runtime_checkable
import unicodedata

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.message_metadata import MessageMetadata
from app.services.case_analysis.contracts import CaseAnalysisGap


@dataclass(frozen=True)
class FollowUpExchange:
    question: str
    answer: str
    disposition: Literal["answered", "unavailable", "skipped"] = "answered"
    gap_id: str | None = None
    gap_topic: str | None = None
    gap_key: str | None = None
    question_message_id: str | None = None
    answer_message_id: str | None = None
    round_number: int = 1




@dataclass(frozen=True)
class FollowUpResolution:
    """The gate result and the audit record carried into the final message."""

    question: str | None
    metadata_json: MessageMetadata


class FollowUpDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["ask_followup", "proceed"]
    selected_gap: str | None = None
    question: str = Field(default="")


@dataclass(frozen=True)
class FollowUpPolicyResult:
    decision: FollowUpDecision
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    provider: str | None = None
    model: str | None = None


@runtime_checkable
class FollowUpPolicy(Protocol):
    async def decide(
        self,
        *,
        selected_gap: CaseAnalysisGap,
        client: object | None = None,
    ) -> FollowUpDecision: ...

    async def decide_with_metadata(
        self,
        *,
        selected_gap: CaseAnalysisGap,
        client: object | None = None,
    ) -> FollowUpPolicyResult: ...


_UNAVAILABLE_ANSWER_PHRASES = (
    "unknown",
    "unavailable",
    "not available",
    "not provided",
    "not known",
    "no information",
    "cannot be obtained",
    "can't be obtained",
    "could not be obtained",
    "couldn't be obtained",
    "cannot be determined",
    "can't be determined",
    "could not be determined",
    "couldn't be determined",
    "don't know",
    "dont know",
    "do not know",
    "i don't know",
    "i do not know",
    "we don't know",
    "we do not know",
    "not sure",
    "unsure",
    "no idea",
    "idk",
    "absent",
    "missing",
    "n/a",
    "ไม่ทราบ",
    "ยังไม่ทราบ",
    "ไม่รู้",
    "ยังไม่รู้",
    "ไม่มีข้อมูล",
    "ไม่มีรายละเอียด",
    "ไม่แน่ใจ",
    "จำไม่ได้",
    "ไม่สามารถระบุได้",
    "ไม่สามารถยืนยันได้",
    "หาไม่ได้",
    "หาไม่เจอ",
    "ไม่พบข้อมูล",
    "ไม่พร้อมใช้งาน",
    "ไม่ระบุ",
    "ไม่ชัดเจน",
)


def answer_indicates_unavailable(answer: str) -> bool:
    normalized = unicodedata.normalize("NFKC", answer)
    normalized = " ".join(normalized.split()).casefold()
    if not normalized:
        return False
    normalized = normalized.strip(" .,!?:;()[]{}")
    if normalized in {
        "none",
        "not known",
        "not available",
        "unavailable",
        "ไม่มี",
        "ไม่มีครับ",
        "ไม่มีค่ะ",
        "ไม่มีเลย",
    }:
        return True
    if re.search(r"\bnot\s+unavailable\b", normalized):
        return False
    for phrase in _UNAVAILABLE_ANSWER_PHRASES:
        if any(ord(character) > 127 for character in phrase):
            if phrase in normalized:
                return True
        elif re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalized):
            return True
    return False


__all__ = [
    "FollowUpDecision",
    "FollowUpExchange",
    "FollowUpPolicy",
    "FollowUpPolicyResult",
    "FollowUpResolution",
    "answer_indicates_unavailable",
]
