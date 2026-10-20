import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config import BASE_DIR

@dataclass
class AttributionBenchExample:
    example_id: str
    claim: str
    evidence_units: list[str]
    gold_label_binary: int  # 1 = attributable, 0 = not attributable
    src_dataset: str
    meta: dict[str, Any] = field(default_factory=dict)

def split_reference_into_sentences(text: str) -> list[str]:
    """
    Splits reference text into clean sentence-level EvidenceUnits.
    """
    if not text or not text.strip():
        return []
    # Split by newlines and standard sentence punctuation
    raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    sentences: list[str] = []
    for p in raw_paragraphs:
        parts = re.split(r'(?<=[.!?])\s+', p)
        for s in parts:
            s_clean = s.strip()
            if len(s_clean) > 3:  # skip empty or tiny artifact tokens
                sentences.append(s_clean)
    return sentences if sentences else [text.strip()]

def load_attributionbench_split(
    split_type: str = "id",  # "id" (in-domain) or "ood" (out-of-domain)
    data_dir: Path | None = None,
) -> list[AttributionBenchExample]:
    if data_dir is None:
        data_dir = BASE_DIR.parent / "research" / "attribution_benchmark" / "data"
    
    if split_type == "id":
        file_path = data_dir / "test_all_subset_balanced.jsonl"
    elif split_type == "ood":
        file_path = data_dir / "test_ood_all_subset_balanced.jsonl"
    else:
        raise ValueError(f"Unknown split_type: {split_type}. Must be 'id' or 'ood'.")

    if not file_path.exists():
        raise FileNotFoundError(f"AttributionBench file not found at: {file_path}")

    examples: list[AttributionBenchExample] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            data = json.loads(line)
            
            raw_label = data.get("attribution_label", "").strip().lower()
            binary_label = 1 if raw_label == "attributable" else 0
            
            claim = data.get("claim", "").strip()
            if not claim:
                claim = data.get("response", "").strip()

            raw_refs = data.get("references", [])
            evidence_units: list[str] = []
            if isinstance(raw_refs, list):
                for ref in raw_refs:
                    evidence_units.extend(split_reference_into_sentences(str(ref)))
            elif isinstance(raw_refs, str):
                evidence_units.extend(split_reference_into_sentences(raw_refs))

            ex_id = data.get("id", f"{split_type}_{idx}")
            src_dataset = data.get("src_dataset", "unknown")

            examples.append(
                AttributionBenchExample(
                    example_id=ex_id,
                    claim=claim,
                    evidence_units=evidence_units,
                    gold_label_binary=binary_label,
                    src_dataset=src_dataset,
                    meta={"question": data.get("question"), "raw_label": raw_label},
                )
            )

    return examples
