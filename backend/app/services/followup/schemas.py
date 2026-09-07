"""Strict contracts shared by gap analysis and follow-up policy."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


from app.services.followup.claim_transport import (
    GAP_ANALYSIS_CLAIM_LIMIT as GAP_ANALYSIS_CLAIM_LIMIT,
    GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS as GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS,
    GapAnalysisClaim as GapAnalysisClaim,
    build_gap_analysis_claim_transport as build_gap_analysis_claim_transport,
)

GapStatus = Literal[
    "NOT_PROVIDED",
    "EXPLICITLY_UNKNOWN",
    "AMBIGUOUS",
    "CONFLICTING",
]
GapPriority = Literal["high", "medium", "low"]

FollowUpReasonCode = Literal[
    "sufficient_case_context",
    "unresolved_gaps_recorded",
    "material_incident_fact_missing",
    "material_incident_fact_ambiguous",
    "material_incident_fact_conflicting",
]

_COMPOUND_QUESTION_RE = re.compile(
    r"\b(?:and|or|but)\s+"
    r"(?:what|which|when|where|who|whom|why|how|"
    r"did|does|do|is|are|was|were|can|could|has|have|had)\b",
    re.IGNORECASE,
)


class GapItem(BaseModel):
    """One incident-specific information gap found in the current analysis."""

    model_config = ConfigDict(extra="ignore")

    topic: str
    status: GapStatus
    description: str
    affects: str
    reason: str
    priority: GapPriority
    askable: bool

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip().upper().replace(" ", "_").replace("-", "_")
        mapping = {
            "NOT_PROVIDED": "NOT_PROVIDED",
            "MISSING": "NOT_PROVIDED",
            "NOTPROVIDED": "NOT_PROVIDED",
            "NOT_SPECIFIED": "NOT_PROVIDED",
            "EXPLICITLY_UNKNOWN": "EXPLICITLY_UNKNOWN",
            "UNKNOWN": "EXPLICITLY_UNKNOWN",
            "UNAVAILABLE": "EXPLICITLY_UNKNOWN",
            "EXPLICITLYUNKNOWN": "EXPLICITLY_UNKNOWN",
            "AMBIGUOUS": "AMBIGUOUS",
            "UNCLEAR": "AMBIGUOUS",
            "CONFLICTING": "CONFLICTING",
            "INCONSISTENT": "CONFLICTING",
        }
        return mapping.get(normalized, normalized)

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip().lower()
        if normalized in ("high", "medium", "low"):
            return normalized
        if normalized in ("critical", "urgent", "highest"):
            return "high"
        if normalized in ("moderate", "normal"):
            return "medium"
        if normalized in ("info", "minor", "lowest"):
            return "low"
        return normalized

    @field_validator("topic", "description", "affects", "reason")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Gap text fields must not be blank")
        if len(value) > 1_000:
            raise ValueError("Gap text fields are too long")
        return value

    @model_validator(mode="after")
    def explicitly_unknown_is_not_askable(self) -> "GapItem":
        if self.status == "EXPLICITLY_UNKNOWN":
            self.askable = False
        return self


class GapAnalysis(BaseModel):
    """All relevant gaps detected for one completed Main Case Analysis."""

    model_config = ConfigDict(extra="ignore")

    gaps: list[GapItem] = Field(default_factory=list, max_length=32)


@dataclass(frozen=True)
class GapAnalysisResult:
    """Gap output plus provider telemetry; never an evidence mutation."""

    analysis: GapAnalysis
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    provider: str | None = None
    model: str | None = None


class FollowUpDecision(BaseModel):
    """One bounded decision made from an already-computed Gap Analysis."""

    model_config = ConfigDict(extra="ignore")

    decision: Literal["ask_followup", "proceed"]
    selected_gap: str | None = None
    question: str = ""
    # Kept only as an in-process compatibility field for legacy custom policies.
    # The provider schema in prompts.py deliberately does not expose it.
    reason_code: FollowUpReasonCode | None = None

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

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_action_shape(cls, value: object) -> object:
        if not isinstance(value, Mapping):
            return value
        normalized = dict(value)
        if "decision" not in normalized and "action" in normalized:
            normalized["decision"] = normalized.pop("action")
        if (
            normalized.get("decision") == "ask_followup"
            and not normalized.get("selected_gap")
            and normalized.get("reason_code") is not None
        ):
            # Old injected policies had no gap key. Keep them callable while the
            # production path requires a validated topic from Gap Analysis.
            normalized["selected_gap"] = "legacy_gap"
        return normalized

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
            if self.reason_code not in (
                None,
                "sufficient_case_context",
                "unresolved_gaps_recorded",
            ):
                raise ValueError("Proceed decisions have an invalid legacy reason code")
            return self

        if self.selected_gap is None:
            raise ValueError("Follow-up decisions require a selected gap")
        if self.reason_code == "sufficient_case_context":
            raise ValueError(
                "Follow-up decisions require a material missing or unclear fact"
            )
        if (
            not self.question
            or len(self.question) > 300
            or any(character in self.question for character in "\r\n\u2028\u2029")
            or sum(self.question.count(mark) for mark in ("?", "？", "؟")) > 1
            or _COMPOUND_QUESTION_RE.search(self.question) is not None
        ):
            raise ValueError("Follow-up must be one concise question")
        return self

    @property
    def action(self) -> Literal["ask_followup", "proceed"]:
        """Legacy name retained for existing in-process callers."""

        return self.decision


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
    evidence_sha256: str | None = None
    question_message_id: str | None = None
    answer_message_id: str | None = None


class GapAnalyzer(Protocol):
    async def analyze(
        self,
        *,
        original_user_content: str,
        clarification_exchanges: Sequence[ClarificationExchange],
        raw_evidence: str | None = None,
        analysis_answer: str | None = None,
        analysis_context: Mapping[str, object] | None = None,
        analysis_claims: Sequence[Mapping[str, object]] | None = None,
    ) -> GapAnalysisResult: ...


class FollowUpPolicy(Protocol):
    async def decide(
        self,
        *,
        original_user_content: str,
        clarification_exchanges: Sequence[ClarificationExchange],
        gap_analysis: GapAnalysis,
        raw_evidence: str | None = None,
        analysis_answer: str | None = None,
        analysis_context: Mapping[str, object] | None = None,
    ) -> FollowUpDecision: ...


__all__ = [
    "ClarificationExchange",
    "FollowUpDecision",
    "FollowUpPolicy",
    "FollowUpPolicyResult",
    "FollowUpReasonCode",
    "GAP_ANALYSIS_CLAIM_LIMIT",
    "GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS",
    "GapAnalysis",
    "GapAnalysisClaim",
    "GapAnalysisResult",
    "GapAnalyzer",
    "GapItem",
    "GapPriority",
    "GapStatus",
    "build_gap_analysis_claim_transport",
]
