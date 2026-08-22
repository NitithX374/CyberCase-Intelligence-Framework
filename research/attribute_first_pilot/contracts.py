"""Domain contracts, schemas, and enums for the Attribute-First Reasoning Pilot."""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class AnswerabilityEnum(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    CONFLICTING = "CONFLICTING"


class QuestionTypeEnum(str, Enum):
    MEANS = "MEANS"
    PROGRESSION = "PROGRESSION"
    CORRELATION = "CORRELATION"
    IMPACT = "IMPACT"
    OBJECTIVE = "OBJECTIVE"
    OTHER = "OTHER"


class EpistemicStateEnum(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNESTABLISHED = "UNESTABLISHED"
    CONTRADICTED = "CONTRADICTED"


class ConditionEnum(str, Enum):
    ORIGINAL = "ORIGINAL"
    REMOVED = "REMOVED"
    CONTRADICTION = "CONTRADICTION"
    DISTRACTOR = "DISTRACTOR"
    REORDER = "REORDER"


class SentenceEvidence(BaseModel):
    """A numbered sentence unit in the cybersecurity case context."""
    id: str = Field(..., description="Sentence/Evidence identifier, e.g., S1, S2")
    text: str = Field(..., description="The textual statement of the evidence fact")


class AttributeContract(BaseModel):
    """The concise intermediate context-analysis attribute representation."""
    answerability: AnswerabilityEnum = Field(
        ...,
        description="Whether the supplied context contains enough, insufficient, or conflicting evidence.",
    )
    question_type: QuestionTypeEnum = Field(
        ...,
        description="The cybersecurity analytical question category.",
    )
    relevant_evidence_ids: list[str] = Field(
        default_factory=list,
        description="List of sentence IDs (e.g. ['S1', 'S2']) directly relevant to the question.",
    )
    epistemic_state: EpistemicStateEnum = Field(
        ...,
        description="Epistemic status of the requested conclusion: SUPPORTED, UNESTABLISHED, or CONTRADICTED.",
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Short description of facts absent from the context required to establish the conclusion.",
    )


class EvaluationNotes(BaseModel):
    """Ground truth analytical notes for manual or deterministic verification."""
    expected_behavior: str = Field(..., description="Brief description of the expected analytical outcome.")
    required_points: list[str] = Field(default_factory=list, description="Key points that must be recognized.")
    forbidden_points: list[str] = Field(default_factory=list, description="Unsupported assumptions or hallucinations.")


class BenchmarkItem(BaseModel):
    """Single benchmark instance."""
    id: str = Field(..., description="Unique benchmark instance ID, e.g. case_01_original")
    base_case_id: str = Field(..., description="Identifier of the base scenario, e.g. case_01")
    condition: ConditionEnum = Field(..., description="Context perturbation condition")
    context_sentences: list[SentenceEvidence] = Field(..., description="Segmented evidence sentences")
    question: str = Field(..., description="The analytical cybersecurity question")
    gold_attributes: AttributeContract = Field(..., description="Manually designed gold attribute representation")
    evaluation_notes: EvaluationNotes = Field(..., description="Evaluation notes and criteria")

    def formatted_context(self) -> str:
        """Format sentences with bracketed sentence IDs."""
        return "\n".join(f"[{s.id}] {s.text}" for s in self.context_sentences)


class BenchmarkSuite(BaseModel):
    """Full benchmark suite containing all instances."""
    version: str = "1.0.0"
    description: str = "CyberCase Attribute-First Reasoning Pilot Benchmark"
    items: list[BenchmarkItem]


class ModelCallUsage(BaseModel):
    """Token usage metadata for a single LLM invocation."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class GenerationResult(BaseModel):
    """Result of an answer generation call."""
    answer: str
    latency_ms: float
    usage: ModelCallUsage
    model: str
    error: str | None = None
    raw_response: str | None = None


class AttributePredictionResult(BaseModel):
    """Result of an attribute prediction call."""
    attributes: AttributeContract | None = None
    latency_ms: float
    usage: ModelCallUsage
    model: str
    error: str | None = None
    raw_response: str | None = None


class ItemRunResult(BaseModel):
    """Full experimental execution records for a single benchmark item across all 3 conditions."""
    benchmark_id: str
    base_case_id: str
    condition: str
    question: str
    gold_attributes: AttributeContract
    direct: GenerationResult  # B0
    predicted_attributes: AttributePredictionResult  # A1 Step 1
    attribute_first: GenerationResult  # A1 Step 2
    oracle_attribute: GenerationResult  # A2


class PilotRunOutput(BaseModel):
    """Complete serialized experiment run output."""
    timestamp: str
    model: str
    temperature: float
    total_items: int
    results: list[ItemRunResult]
