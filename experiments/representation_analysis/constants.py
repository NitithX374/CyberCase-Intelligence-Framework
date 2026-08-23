from __future__ import annotations

from pathlib import Path

from research.sevenllm_preflight.run_openrouter_b0 import GENERATION_CONFIG, MODEL


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "experiments" / "representation_analysis" / "outputs" / "pilot_28"
DEFAULT_B0_CACHE = PROJECT_ROOT / "tmp" / "context_refinement_run_20260823" / "predictions.jsonl"
DEFAULT_SBERT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_GLINER_MODEL = "fastino/gliner2-base-v1"
EXPERIMENT_VERSION = "representation_analysis_v1"
SEED = 42

CONDITIONS = ("B0", "B1", "B2")
REPRESENTATION_TYPES = {
    "B0": "raw",
    "B1": "existing_llm_case_state",
    "B2": "gliner2_events",
}
CONDITION_LABELS = {
    "B0": "Raw",
    "B1": "LLM Extraction → LLM",
    "B2": "GLiNER2 → LLM",
}
PAIRWISE_COMPARISONS = (
    ("B1", "B0"),
    ("B2", "B0"),
    ("B2", "B1"),
)
EVENT_FIELDS = (
    "actor",
    "action",
    "object",
    "target",
    "tool",
    "time",
    "location",
    "result",
)
EVENT_SCHEMA = {
    "cyber_event": [
        "actor::str::Explicit actor performing the event action",
        "action::str::Explicit action or behavior stated in the text",
        "object::str::Explicit object acted upon or produced",
        "target::str::Explicit system, organization, account, or person targeted",
        "tool::str::Explicit software, malware, command, utility, or technique used",
        "time::str::Explicit date, time, or temporal expression",
        "location::str::Explicit physical, network, or system location",
        "result::str::Explicit outcome or impact of the event",
    ]
}
DOWNSTREAM_MODEL = MODEL
DOWNSTREAM_GENERATION_CONFIG = GENERATION_CONFIG

