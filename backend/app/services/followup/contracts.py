"""Strict contracts for deterministic follow-up."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.schemas.messageMetadata import MessageMetadata
from app.services.case_analysis.contracts import CaseAnalysisGap


_COMPOUND_QUESTION_RE = re.compile(
    r"\b(?:and|or|but)\s+"
    r"(?:what|which|when|where|who|whom|why|how|"
    r"did|does|do|is|are|was|were|can|could|has|have|had)\b",
    re.IGNORECASE,
)


class FollowUpDecision(BaseModel):
    """One bounded decision made from an already-selected case gap."""

    model_config = ConfigDict(extra="ignore")

    decision: Literal["ask_followup", "proceed"]
    selected_gap: str | None = None
    question: str = ""

    @field_validator("decision", mode="before")
    @classmethod
    def normalize_decision_mode(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        val = value.strip().lower().replace("-", "_").replace(" ", "_")
        if val in ("ask_followup", "ask_follow_up", "ask", "followup", "ask_question"):
            return "ask_followup"
        if val in ("proceed", "continue", "skip", "no_followup", "none"):
            return "proceed"
        return val

    @field_validator("selected_gap", mode="before")
    @classmethod
    def validate_selected_gap(cls, value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            return str(value)
        cleaned = value.strip()
        if not cleaned or cleaned.lower() in ("none", "null", "n/a"):
            return None
        if len(cleaned) > 240:
            return cleaned[:240]
        return cleaned

    @model_validator(mode="after")
    def validate_decision(self) -> "FollowUpDecision":
        self.question = self.question.strip()
        if self.decision == "proceed":
            self.selected_gap = None
            self.question = ""
            return self

        if self.selected_gap is None:
            raise ValueError("Follow-up decisions require a selected gap")
        if (
            not self.question
            or len(self.question) > 300
            or any(character in self.question for character in "\r\n\u2028\u2029")
            or sum(self.question.count(mark) for mark in ("?", "？", "؟")) > 1
            or _COMPOUND_QUESTION_RE.search(self.question) is not None
        ):
            raise ValueError("Follow-up must be one concise question")
        return self


@dataclass(frozen=True)
class FollowUpPolicyResult:
    """Decision plus safe provider metrics when the adapter supplies them."""

    decision: FollowUpDecision
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    provider: str | None = None
    model: str | None = None


@dataclass(frozen=True)
class ClarificationExchange:
    question: str
    answer: str
    gap_id: str | None = None
    gap_topic: str | None = None
    gap_key: str | None = None
    question_message_id: str | None = None
    answer_message_id: str | None = None


class FollowUpPolicy(Protocol):
    async def decide(
        self,
        *,
        selected_gap: CaseAnalysisGap,
    ) -> FollowUpDecision: ...

@dataclass(frozen=True)
class FollowUpResolution:
    """The gate result and the audit record carried into the final message."""

    question: str | None
    metadata_json: MessageMetadata


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
    "ClarificationExchange",
    "FollowUpDecision",
    "FollowUpPolicy",
    "FollowUpPolicyResult",
    "FollowUpResolution",
    "answer_indicates_unavailable",
]
