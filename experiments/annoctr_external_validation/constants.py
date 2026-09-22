from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANNOCTR_ROOT = Path(
    os.environ.get("ANNOCTR_ROOT", r"F:\anno-ctr-lrec-coling-2024")
)
DEFAULT_CHECKPOINT = ROOT / "backend" / "xlmr_ladder_best" / "xlmr_ladder_best"
DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parent
LADDER_TEST = (
    ROOT
    / "experiments"
    / "LADDER"
    / "attack_pattern"
    / "data"
    / "sentence_classification"
    / "test.csv"
)
DECISION_THRESHOLD = 0.50
RANDOM_SEED = 20260923
SOURCE_SPLIT = "test"
TECHNIQUE_LINK_PREFIX = "https://attack.mitre.org/techniques/"
PREDICTION_COLUMNS = [
    "text",
    "document",
    "gold_label",
    "predicted_label",
    "p_relevant",
    "correct",
]
ERROR_COLUMNS = PREDICTION_COLUMNS + [
    "text_char_length",
    "token_length",
    "contains_attack_term",
    "contains_action_verb",
    "truncated",
]
