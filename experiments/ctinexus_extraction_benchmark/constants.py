from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = PROJECT_ROOT.parent / "ctinexus" / "ctinexus" / "data" / "test"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "tmp" / "ctinexus_extraction_only"

EXPERIMENT_VERSION = "ctinexus_extraction_only_v1"
DATASET_SPLIT = "committed_test"
NORMALIZATION_VERSION = "deterministic_surface_nfkc_v1"
PRODUCTION_MODEL = "openai/gpt-5.6-luna"
PRODUCTION_PROMPT_VERSION = "baseline_extraction_prompt_v6"
PRODUCTION_SCHEMA_VERSION = "baseline_extraction_v2"
GLINER_MODEL = "fastino/gliner2-base-v1"
GLINER_THRESHOLD = 0.5
GLINER_SCHEMA_VERSION = "ctinexus_entity_types_and_generic_relation_spans_v1"

CTINEXUS_ENTITY_TYPES = (
    "Account",
    "Attacker",
    "Credential",
    "Event",
    "Exploit Target",
    "Indicator",
    "Indicator:Domain",
    "Indicator:Email",
    "Indicator:File",
    "Indicator:SSL Certificate",
    "Indicator:URL",
    "Information",
    "Infrastructure",
    "Location",
    "Malware",
    "Malware Characteristic:Behavior",
    "Malware Characteristic:Capability",
    "Malware Characteristic:Feature",
    "Malware Characteristic:Payload",
    "Malware Characteristic:Variants",
    "Organization",
    "This entity cannot be classified into any of the existing types",
    "Time",
    "Tool",
    "Vulnerability",
)

GLINER_RELATION_SCHEMA = {
    "ctinexus_relation": [
        {
            "name": "subject",
            "dtype": "str",
            "description": "Exact source span for the directed relation subject entity.",
        },
        {
            "name": "relation",
            "dtype": "str",
            "description": "Exact source span for the explicit relation phrase.",
        },
        {
            "name": "object",
            "dtype": "str",
            "description": "Exact source span for the directed relation object entity.",
        },
    ]
}
