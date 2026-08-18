"""Data schemas for analysis outputs, extraction logs, probe evaluations, and metrics."""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

EpistemicStatus = Literal[
    "reported",
    "supported_inference",
    "uncertain",
    "not_established",
]

ProbeVerdict = Literal["PRESENT", "NOT_PRESENT"]


class Finding(BaseModel):
    """A distinct analytical finding with an associated epistemic status."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        min_length=1,
        description="A distinct analytical finding or statement derived from the supplied case information.",
    )
    epistemic_status: EpistemicStatus = Field(
        description=(
            "Epistemic status of the finding: 'reported' (explicitly stated fact), "
            "'supported_inference' (grounded interpretation), 'uncertain' (tentative/suspected/possible), "
            "or 'not_established' (explicitly negated/unverified)."
        ),
    )


class CaseAnalysisOutput(BaseModel):
    """Structured evaluation output schema for case analysis generation."""

    model_config = ConfigDict(extra="forbid")

    findings: list[Finding] = Field(
        min_length=1,
        description="List of key analytical findings covering facts, relationships, sequence, interpretations, and uncertainty.",
    )
    analysis_text: str = Field(
        min_length=1,
        description="Cohesive preliminary case analysis narrative synthesizing the findings, temporal sequence, interpretations, and analytical boundaries.",
    )


class JudgeResponse(BaseModel):
    """Structured output schema for the binary probe judge."""

    model_config = ConfigDict(extra="forbid")

    reasoning: str = Field(
        min_length=1,
        description="Concise step-by-step reasoning on whether the generated analysis semantically asserts or entails the claim.",
    )
    verdict: ProbeVerdict = Field(
        description="PRESENT if the analysis semantically asserts/entails the claim; NOT_PRESENT otherwise.",
    )


class GenerationRecord(BaseModel):
    """Full machine-readable log of an analysis generation call."""

    model_config = ConfigDict(extra="allow")

    case_id: str
    language: str
    scenario_id: str
    condition: Literal["RAW_DIRECT", "EXTRACTED_STATE"]
    input_used: str
    model: str
    prompt_version: str
    prompt_hash: str
    decoding_settings: dict[str, Any]
    output: CaseAnalysisOutput | None = None
    raw_response: str | None = None
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    failure_information: str | None = None


class ExtractionLogRecord(BaseModel):
    """Machine-readable record of production extraction step."""

    model_config = ConfigDict(extra="allow")

    case_id: str
    language: str
    scenario_id: str
    status: Literal["candidate", "failed"]
    raw_response: str | None
    canonical_case_state: dict[str, Any] | None = None
    failure_code: str | None = None
    failure_message: str | None = None
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None


class ProbeJudgmentRecord(BaseModel):
    """Machine-readable log of an individual probe evaluation."""

    model_config = ConfigDict(extra="allow")

    case_id: str
    language: str
    scenario_id: str
    condition: Literal["RAW_DIRECT", "EXTRACTED_STATE"]
    claim_id: str
    claim: str
    label: Literal["SUPPORTED", "UNSUPPORTED"]
    error_type: str
    source_fact_ids: list[str]
    judge_model: str
    reasoning: str
    verdict: ProbeVerdict
    is_correct_detection: bool  # For SUPPORTED: verdict==PRESENT; For UNSUPPORTED: verdict==NOT_PRESENT
    latency_ms: float
