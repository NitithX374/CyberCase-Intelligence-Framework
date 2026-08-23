from __future__ import annotations

from typing import Any, Iterable

from .runtime import prepare_runtime

prepare_runtime()

from backend.experiments.ctinexus.adapter import extraction_to_predicted_graph
from backend.experiments.ctinexus.schemas import CTINexusDocument, PredictedGraph

from .dataset import CTINexusCase
from .schemas import ExtractorPrediction, TypedEntityPrediction, TypedRelationPrediction


def _dedupe(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value.strip()))


def _prediction(
    *,
    condition: str,
    case: CTINexusCase,
    model: str,
    graph: PredictedGraph,
    typed_entities: list[TypedEntityPrediction],
    typed_relations: list[TypedRelationPrediction],
    diagnostics: dict[str, Any],
    contract: dict[str, Any],
) -> ExtractorPrediction:
    return ExtractorPrediction(
        condition=condition,
        doc_id=case.document.doc_id,
        narrative_sha256=case.narrative_sha256,
        model=model,
        status=graph.status,
        graph=graph,
        typed_entities=typed_entities,
        typed_relations=typed_relations,
        diagnostics=diagnostics,
        contract=contract,
    )


def production_prediction(
    case: CTINexusCase,
    extraction: Any,
    *,
    model: str,
    status: str,
    failure_code: str | None,
    failure_message: str | None,
    latency_ms: float,
    input_tokens: int | None,
    output_tokens: int | None,
    diagnostics: dict[str, Any],
    contract: dict[str, Any],
) -> ExtractorPrediction:
    if extraction is None:
        graph = PredictedGraph(
            doc_id=case.document.doc_id,
            status=status,
            failure_code=failure_code,
            failure_message=failure_message,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        typed_entities: list[TypedEntityPrediction] = []
        typed_relations: list[TypedRelationPrediction] = []
    else:
        graph = extraction_to_predicted_graph(
            case.document,
            extraction,
            status=status,
            failure_code=failure_code,
            failure_message=failure_message,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        typed_entities = [
            TypedEntityPrediction(
                text=item.name.strip(),
                entity_type=item.entity_type.strip(),
                confidence=None,
            )
            for item in extraction.entities
            if item.name.strip()
        ]
        typed_relations = [
            TypedRelationPrediction(
                subject=subject.name.strip(),
                relation=relationship.predicate.strip(),
                object=target.name.strip(),
            )
            for relationship in extraction.relationships
            for subject in extraction.entities
            if subject.entity_id == relationship.subject_entity_id
            for target in extraction.entities
            if target.entity_id == relationship.object_entity_id
        ]
    return _prediction(
        condition="E1",
        case=case,
        model=model,
        graph=graph,
        typed_entities=typed_entities,
        typed_relations=typed_relations,
        diagnostics=diagnostics,
        contract=contract,
    )


def gliner_prediction(
    case: CTINexusCase,
    *,
    model: str,
    entities: list[TypedEntityPrediction],
    relations: list[TypedRelationPrediction],
    latency_ms: float,
    diagnostics: dict[str, Any],
    contract: dict[str, Any],
) -> ExtractorPrediction:
    graph = PredictedGraph(
        doc_id=case.document.doc_id,
        entities=_dedupe(item.text for item in entities),
        triplets=_dedupe_triplets(relations),
        endpoint_edges=_dedupe_edges(relations),
        latency_ms=latency_ms,
    )
    return _prediction(
        condition="E2",
        case=case,
        model=model,
        graph=graph,
        typed_entities=entities,
        typed_relations=relations,
        diagnostics=diagnostics,
        contract=contract,
    )


def _dedupe_triplets(relations: list[TypedRelationPrediction]) -> list[tuple[str, str, str]]:
    return list(dict.fromkeys((item.subject, item.relation, item.object) for item in relations))


def _dedupe_edges(relations: list[TypedRelationPrediction]) -> list[tuple[str, str]]:
    return list(dict.fromkeys((item.subject, item.object) for item in relations))
