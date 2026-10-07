import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from config import DATA_DIR, LABEL_MAPPING_BINARY

@dataclass
class WiCEExample:
    example_id: str
    claim_id: str
    claim: str
    evidence_units: list[str]
    gold_label_3class: str
    gold_label_binary: int
    gold_evidence_indices: list[int]
    meta: dict[str, Any] = field(default_factory=dict)

def load_wice_split(split: str, data_dir: Path | None = None) -> list[WiCEExample]:
    """
    Loads WiCE oracle_chunks claim-level examples for a given split ('train', 'dev', 'test').
    
    Fields per row in WiCE oracle_chunks/claim:
    - 'claim': str
    - 'evidence': list[str] (candidate sentence-level EvidenceUnits)
    - 'label': str ('supported', 'partially_supported', 'not_supported')
    - 'meta': dict with 'id', 'chunk_idx', and optionally 'oracle_idx'
    
    Gold evidence indices within evidence_units:
    Sentences where chunk_idx[i] is in oracle_idx.
    """
    if data_dir is None:
        data_dir = DATA_DIR / "wice"
    
    file_path = data_dir / f"{split}.jsonl"
    if not file_path.exists():
        raise FileNotFoundError(f"WiCE data file not found at: {file_path}")

    examples: list[WiCEExample] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            data = json.loads(line)
            
            raw_label = data["label"]
            binary_label = LABEL_MAPPING_BINARY[raw_label]
            meta = data.get("meta", {})
            claim_id = meta.get("id", f"{split}_{idx}")
            example_id = f"{claim_id}_chunk_{idx}"
            
            evidence_units = [str(sent).strip() for sent in data.get("evidence", []) if str(sent).strip()]
            chunk_idx = meta.get("chunk_idx", [])
            oracle_idx = set(meta.get("oracle_idx", []))
            
            # Identify indices in evidence_units that match oracle_idx
            gold_indices: list[int] = []
            for sent_pos, orig_idx in enumerate(chunk_idx):
                if orig_idx in oracle_idx and sent_pos < len(evidence_units):
                    gold_indices.append(sent_pos)

            examples.append(
                WiCEExample(
                    example_id=example_id,
                    claim_id=claim_id,
                    claim=data["claim"].strip(),
                    evidence_units=evidence_units,
                    gold_label_3class=raw_label,
                    gold_label_binary=binary_label,
                    gold_evidence_indices=gold_indices,
                    meta=meta,
                )
            )

    return examples
