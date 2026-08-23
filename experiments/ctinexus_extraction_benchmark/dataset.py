from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .runtime import prepare_runtime

prepare_runtime()

from backend.experiments.ctinexus.dataset import load_ctinexus_test_dataset
from backend.experiments.ctinexus.schemas import CTINexusDocument


@dataclass(frozen=True)
class GoldEntity:
    text: str
    entity_type: str


@dataclass(frozen=True)
class GoldRelation:
    subject: str
    relation: str
    object: str


@dataclass(frozen=True)
class CTINexusCase:
    document: CTINexusDocument
    gold_entities: tuple[GoldEntity, ...]
    gold_relations: tuple[GoldRelation, ...]
    narrative_sha256: str


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _raw_entities(raw: dict[str, Any]) -> list[GoldEntity]:
    entities: list[GoldEntity] = []
    for item in raw.get("entities", []):
        if not isinstance(item, dict):
            continue
        text = str(item.get("entity_name") or item.get("name") or item.get("entity") or "").strip()
        entity_type = str(item.get("entity_type") or item.get("type") or "").strip()
        if text and entity_type:
            entities.append(GoldEntity(text=text, entity_type=entity_type))
    return list(dict.fromkeys(entities))


def _raw_relations(raw: dict[str, Any]) -> list[GoldRelation]:
    relations: list[GoldRelation] = []
    for item in raw.get("explicit_triplets", []):
        if isinstance(item, dict):
            subject = str(item.get("subject") or item.get("head") or item.get("source") or "").strip()
            relation = str(item.get("relation") or item.get("predicate") or item.get("type") or "").strip()
            target = str(item.get("object") or item.get("tail") or item.get("target") or "").strip()
        elif isinstance(item, (list, tuple)) and len(item) >= 3:
            subject, relation, target = (str(value).strip() for value in item[:3])
        else:
            continue
        if subject and relation and target:
            relations.append(GoldRelation(subject=subject, relation=relation, object=target))
    return list(dict.fromkeys(relations))


def _load_raw_document(path: Path) -> dict[str, Any]:
    content = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise ValueError(f"Expected one CTINexus object in {path}")
    return content


def load_ctinexus_cases(dataset_dir: str | Path) -> list[CTINexusCase]:
    documents = load_ctinexus_test_dataset(dataset_dir)
    cases: list[CTINexusCase] = []
    for document in documents:
        path = Path(document.file_path)
        raw = _load_raw_document(path)
        cases.append(
            CTINexusCase(
                document=document,
                gold_entities=tuple(_raw_entities(raw)),
                gold_relations=tuple(_raw_relations(raw)),
                narrative_sha256=sha256_text(document.text),
            )
        )
    return cases


def dataset_manifest(cases: list[CTINexusCase], dataset_dir: str | Path) -> dict[str, Any]:
    rows = []
    for case in cases:
        rows.append(
            {
                "doc_id": case.document.doc_id,
                "file": case.document.file_path,
                "file_sha256": hashlib.sha256(Path(case.document.file_path).read_bytes()).hexdigest(),
                "narrative_sha256": case.narrative_sha256,
                "characters": len(case.document.text),
                "gold_entity_count": len(case.document.gold_entities),
                "gold_relation_count": len(case.document.gold_explicit_triplets),
                "gold_entity_types": sorted({item.entity_type for item in case.gold_entities}),
                "gold_relation_types": sorted({item.relation for item in case.gold_relations}),
            }
        )
    return {
        "dataset": "CTINexus",
        "split": "committed_test",
        "language": "English",
        "language_field_present": False,
        "dataset_dir": str(Path(dataset_dir).resolve()),
        "documents": len(rows),
        "gold_entities": sum(row["gold_entity_count"] for row in rows),
        "gold_relations": sum(row["gold_relation_count"] for row in rows),
        "files": rows,
    }
