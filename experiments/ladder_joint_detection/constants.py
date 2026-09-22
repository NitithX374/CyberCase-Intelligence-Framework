from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LADDER_DATA_ROOT = ROOT / "experiments" / "LADDER" / "attack_pattern" / "data"
CLASSIFICATION_ROOT = LADDER_DATA_ROOT / "sentence_classification"
ENTITY_ROOT = LADDER_DATA_ROOT / "entity_extraction"
DEFAULT_OUTPUT_ROOT = ROOT / "experiments" / "ladder_joint_detection"
OUTPUT_ROOT = Path(os.environ.get("LADDER_JOINT_OUTPUT") or DEFAULT_OUTPUT_ROOT).resolve()

SPLITS = ("train", "dev", "test")
RELEVANT_LABEL = 1
IRRELEVANT_LABEL = 0
ENTITY_LABELS = frozenset({"ATK", "O"})
ATTACK_LABEL = "ATK"
SOURCE_NAME = "LADDER"
DECISIONS = frozenset({"SAFE", "PARTIALLY_SAFE", "UNSAFE"})
