"""Configuration for the analysis-isolation evaluation pilot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = REPO_ROOT / "experiments" / "semantic_verification" / "data" / "semantic_verification.jsonl"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "evaluation" / "analysis_pilot"

# Analysis Model & Decoding Configurations
DEFAULT_ANALYSIS_MODEL = "openai/gpt-5.6-luna"
ANALYSIS_TEMPERATURE = 0.0
ANALYSIS_MAX_OUTPUT_TOKENS = 2048
ANALYSIS_TIMEOUT_SECONDS = 60.0

# Judge Model & Decoding Configurations
DEFAULT_JUDGE_MODEL = "qwen/qwen3.8-27b"
JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_OUTPUT_TOKENS = 2048
JUDGE_TIMEOUT_SECONDS = 45.0

# Scenarios & Language definitions for Stratified Deterministic Selection
SCENARIOS = (
    "email_execution",
    "forwarded_attachment",
    "mail_endpoint_review",
    "received_document",
)

LANGUAGES = ("en", "th")

# Metric Probe Types
EPISTEMIC_VIOLATION_TYPES = frozenset(
    {
        "certainty_strengthening",
        "causality_insertion",
        "attribution_insertion",
        "negation_flip",
    }
)

FACTUAL_ERROR_TYPES = frozenset(
    {
        "actor_swap",
        "target_swap",
        "predicate_swap",
        "timestamp_shift",
    }
)
