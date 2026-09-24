import asyncio
from types import SimpleNamespace

import pytest
from case_mitre_test_support import _fixtures
from pydantic import ValidationError

from app.schemas.rag import LegalReferenceResult, QueryResponse
from app.services.analysis.pipeline import AnalysisArtifacts
from app.services.analysis.steps.technical_context import CaseMitreAugmentation
from app.services.workflow.analysis_storage import external_context, retrieval_context_row
from app.services.workflow.run_analysis import reusable_context


def test_rag_response_requires_legal_reference():
    with pytest.raises(ValidationError):
        QueryResponse.model_validate(
            {
                "status": "completed",
                "retrieval_context_id": "retrieval-1",
                "context": "technical context",
                "mitre_table": [],
            }
        )


def test_retrieved_legal_relevance_is_persisted_in_both_analysis_json_fields():
    _, trace, _, applicability, context = _fixtures()
    metadata = CaseMitreAugmentation(
        status="retrieved_from_rag",
        applicability=applicability,
        context=context,
        associations=(),
    ).to_metadata()
    artifacts = AnalysisArtifacts(
        trace=trace,
        technical_context={
            "context": context.context,
            "mitre_table": list(context.mitre_table),
        },
        retrieval_context_id=context.retrieval_context_id,
        receipt={"technical_augmentation": metadata},
    )
    started = SimpleNamespace(source_revision=1, followup_history=())

    external = external_context(artifacts)
    reusable = retrieval_context_row(artifacts, started)

    assert "mitre_table" not in external
    assert external["legal_relevance"] == metadata["legal_relevance"]
    assert external["technical_augmentation"]["mitre_table"] == list(context.mitre_table)
    assert reusable["mitre_table"] == list(context.mitre_table)
    assert reusable["legal_relevance"] == metadata["legal_relevance"]


def test_old_retrieval_snapshot_without_legal_relevance_is_not_reused():
    row = SimpleNamespace(
        retrieval_context_json={
            "context_key": {"source_revision": 1, "followup_answers": 0},
            "retrieval_context_id": "retrieval-old",
            "context": "old technical context",
            "mitre_table": [],
        }
    )

    result = asyncio.run(
        reusable_context(
            _Database(row),
            "case-id",
            row.retrieval_context_json["context_key"],
        )
    )
    assert result is None


def test_retrieval_snapshot_reuse_restores_legal_relevance():
    legal = LegalReferenceResult(
        provider="thanoy",
        query_sent="incident query",
        degraded="provider unavailable",
    ).model_dump(mode="json")
    snapshot = {
        "context_key": {"source_revision": 1, "followup_answers": 0},
        "retrieval_context_id": "retrieval-current",
        "context": "technical context",
        "mitre_table": [],
        "legal_relevance": legal,
    }
    row = SimpleNamespace(retrieval_context_json=snapshot)

    restored = asyncio.run(reusable_context(_Database(row), "case-id", snapshot["context_key"]))

    assert restored.retrieval_context_id == "retrieval-current"
    assert restored.legal_relevance.model_dump(mode="json") == legal


def test_analysis_without_retrieval_has_no_reusable_or_legal_context():
    _, trace, _, _, _ = _fixtures()
    artifacts = AnalysisArtifacts(
        trace=trace,
        receipt={"technical_augmentation": {"status": "not_applicable"}},
    )

    external = external_context(artifacts)
    reusable = retrieval_context_row(
        artifacts,
        SimpleNamespace(source_revision=1, followup_history=()),
    )

    assert reusable is None
    assert "legal_relevance" not in external
    assert "mitre_table" not in external


class _Database:
    def __init__(self, row):
        self.row = row

    async def scalar(self, _statement):
        return self.row
