from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .constants import CTINEXUS_ENTITY_TYPES
from .dataset import CTINexusCase
from .schemas import ExtractorPrediction
from .type_mapping import map_production_entity_type

from backend.experiments.ctinexus.metrics import compute_counts_and_f1
from backend.experiments.ctinexus.normalize import normalize_entity_name, normalize_relation, normalize_triplet


def _mapped_type(condition: str, value: str) -> str | None:
    if condition == "E1":
        return map_production_entity_type(value)
    return value if value in CTINEXUS_ENTITY_TYPES else None


def _sets_for_entity_type(case: CTINexusCase, prediction: ExtractorPrediction, condition: str):
    gold = {(normalize_entity_name(item.text), item.entity_type) for item in case.gold_entities}
    predicted: set[tuple[str, str]] = set()
    unmappable = 0
    for item in prediction.typed_entities:
        mapped = _mapped_type(condition, item.entity_type)
        if mapped is None:
            unmappable += 1
            continue
        normalized = normalize_entity_name(item.text)
        if normalized:
            predicted.add((normalized, mapped))
    return gold, predicted, unmappable


def entity_type_metrics(
    cases: Iterable[CTINexusCase],
    predictions: dict[str, ExtractorPrediction],
    condition: str,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "support": 0})
    unmappable = 0
    wrong_type = 0
    for case in cases:
        prediction = predictions[case.document.doc_id]
        gold, predicted, rejected = _sets_for_entity_type(case, prediction, condition)
        unmappable += rejected
        for entity_type in {item[1] for item in gold | predicted}:
            gold_values = {item for item in gold if item[1] == entity_type}
            predicted_values = {item for item in predicted if item[1] == entity_type}
            counts[entity_type]["tp"] += len(gold_values & predicted_values)
            counts[entity_type]["fp"] += len(predicted_values - gold_values)
            counts[entity_type]["fn"] += len(gold_values - predicted_values)
            counts[entity_type]["support"] += len(gold_values)
        gold_names = defaultdict(set)
        for name, entity_type in gold:
            gold_names[name].add(entity_type)
        for name, entity_type in predicted:
            if name in gold_names and entity_type not in gold_names[name]:
                wrong_type += 1
    rows = []
    for entity_type in sorted(counts):
        values = counts[entity_type]
        metric = compute_counts_and_f1(values["tp"], values["fp"], values["fn"])
        rows.append({"type": entity_type, "support": values["support"], **metric.model_dump(mode="json")})
    return rows, {"unmappable_predictions": unmappable, "correct_name_wrong_type": wrong_type}


def relation_type_metrics(
    cases: Iterable[CTINexusCase],
    predictions: dict[str, ExtractorPrediction],
) -> list[dict[str, object]]:
    counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "support": 0})
    for case in cases:
        prediction = predictions[case.document.doc_id]
        gold = {normalize_triplet(item.subject, item.relation, item.object) for item in case.gold_relations}
        predicted = {normalize_triplet(item[0], item[1], item[2]) for item in prediction.graph.triplets}
        relations = {item[1] for item in gold | predicted}
        for relation in relations:
            gold_values = {item for item in gold if item[1] == relation}
            predicted_values = {item for item in predicted if item[1] == relation}
            counts[relation]["tp"] += len(gold_values & predicted_values)
            counts[relation]["fp"] += len(predicted_values - gold_values)
            counts[relation]["fn"] += len(gold_values - predicted_values)
            counts[relation]["support"] += len(gold_values)
    rows = []
    for relation in sorted(counts):
        values = counts[relation]
        metric = compute_counts_and_f1(values["tp"], values["fp"], values["fn"])
        rows.append({"relation": relation, "support": values["support"], **metric.model_dump(mode="json")})
    return rows
