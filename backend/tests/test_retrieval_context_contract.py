import asyncio
from types import SimpleNamespace

import pytest
from case_chat_support import seeded_case
from case_mitre_test_support import _fixtures
from isolated_database import isolated_database
from pydantic import ValidationError

from app.schemas.rag import LegalReferenceResult, QueryResponse
from app.services.analysis.clarification import Proceed
from app.services.analysis.pipeline import AnalysisAdvance, AnalysisArtifacts
from app.services.analysis.steps.technical_context import CaseMitreAugmentation
from app.services.analysis.technical_context_contracts import skipped_mitre_applicability
from app.services.workflow.analysis_storage import external_context, retrieval_context_row
from app.services.workflow.run_analysis import reusable_context, run_case_analysis
from app.trace.claims import CaseAssessmentTrace
from app.trace.trace import CaseMitreAssociation

KEY = {"source_revision": 1, "followup_answers": 0}
STARTED = SimpleNamespace(source_revision=1, followup_history=())


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


def artifacts_for(status: str, *, matched: bool = False) -> tuple[AnalysisArtifacts, object]:
    _, trace, _, applicability, context = _fixtures()
    if matched:
        trace = trace.model_copy(
            update={
                "mitre_associations": [
                    CaseMitreAssociation(
                        association_id="MA-01",
                        technique_id="T1059.001",
                        claim_ids=["A-01"],
                        reason="PowerShell execution appears in the source.",
                        status="candidate_only",
                        support_role="external_technical_context",
                    )
                ],
                "retrieval_context_id": context.retrieval_context_id,
            }
        )
    augmentation = CaseMitreAugmentation(
        status=status,
        applicability=skipped_mitre_applicability()
        if status == "not_applicable"
        else applicability,
        context=context if status in {"retrieved_from_rag", "insufficient_context"} else None,
        failure_code="rag_timeout" if status == "failed" else None,
    )
    return AnalysisArtifacts(trace=trace, augmentation=augmentation), context


@pytest.mark.parametrize(
    ("status", "matched", "stored_status", "legal_written"),
    [
        ("not_applicable", False, "not_applicable", False),
        ("insufficient_context", False, "insufficient_context", False),
        ("failed", False, "failed", False),
        ("retrieved_from_rag", False, "retrieved_from_rag", True),
        ("retrieved_from_rag", True, "retrieved_with_matches", True),
    ],
)
def test_legal_relevance_is_written_once_at_the_top_of_the_external_context(
    status, matched, stored_status, legal_written
):
    artifacts, context = artifacts_for(status, matched=matched)

    external = external_context(artifacts)
    row = retrieval_context_row(artifacts, STARTED)

    assert external["technical_augmentation"]["status"] == stored_status
    assert "legal_relevance" not in external["technical_augmentation"]
    if legal_written:
        assert external["legal_relevance"] == context.legal_relevance.model_dump(mode="json")
        assert row == {"context_key": KEY, "context": context.context}
    else:
        assert "legal_relevance" not in external
        assert row is None


def test_the_augmentation_record_keeps_the_fields_the_reader_reads():
    artifacts, context = artifacts_for("retrieved_from_rag", matched=True)

    stored = external_context(artifacts)["technical_augmentation"]

    assert stored["version"] == "case_mitre_augmentation_v1"
    assert stored["retrieval_context_id"] == context.retrieval_context_id
    assert stored["mitre_table"] == list(context.mitre_table)
    assert stored["association_ids"] == ["MA-01"]
    assert stored["failure_code"] is None
    assert stored["retrieval_context_reused"] is False


def stored_row(artifacts: AnalysisArtifacts):
    return SimpleNamespace(
        retrieval_context_json=retrieval_context_row(artifacts, STARTED),
        external_context_json=external_context(artifacts),
    )


def test_a_reused_context_yields_the_legal_relevance_it_was_stored_with():
    artifacts, context = artifacts_for("retrieved_from_rag", matched=True)
    written = stored_row(artifacts)

    restored = asyncio.run(reusable_context(_Database(written), "case-id", KEY))

    assert restored.retrieval_context_id == context.retrieval_context_id
    assert restored.context == context.context
    assert list(restored.mitre_table) == list(context.mitre_table)
    assert restored.legal_relevance == context.legal_relevance
    reused = AnalysisArtifacts(
        trace=artifacts.trace,
        augmentation=CaseMitreAugmentation(
            "retrieved_from_rag", artifacts.augmentation.applicability, restored, reused=True
        ),
    )
    assert (
        external_context(reused)["legal_relevance"]
        == written.external_context_json["legal_relevance"]
    )


def test_a_row_written_before_the_reduction_is_still_reused_with_its_legal_relevance():
    legal = LegalReferenceResult(
        provider="thanoy",
        query_sent="incident query",
        degraded="provider unavailable",
    ).model_dump(mode="json")
    artifacts, context = artifacts_for("retrieved_from_rag")
    augmentation = external_context(artifacts)["technical_augmentation"]
    del augmentation["failure_code"]
    row = SimpleNamespace(
        retrieval_context_json={
            "context_key": KEY,
            "retrieval_context_id": context.retrieval_context_id,
            "context": context.context,
            "mitre_table": list(context.mitre_table),
            "legal_relevance": legal,
        },
        external_context_json={"legal_relevance": legal, "technical_augmentation": augmentation},
    )

    restored = asyncio.run(reusable_context(_Database(row), "case-id", KEY))

    assert restored.legal_relevance.model_dump(mode="json") == legal
    assert restored.retrieval_context_id == context.retrieval_context_id


@pytest.mark.parametrize(
    "damage",
    [
        lambda row: row.external_context_json.pop("legal_relevance"),
        lambda row: row.external_context_json.pop("technical_augmentation"),
        lambda row: row.retrieval_context_json.update(context=""),
        lambda row: row.retrieval_context_json.update(context_key={**KEY, "followup_answers": 1}),
    ],
)
def test_a_row_that_cannot_rebuild_the_context_is_not_reused(damage):
    artifacts, _ = artifacts_for("retrieved_from_rag")
    row = stored_row(artifacts)
    damage(row)

    assert asyncio.run(reusable_context(_Database(row), "case-id", KEY)) is None


def test_the_latest_analysis_that_retrieved_nothing_is_not_reused():
    row = SimpleNamespace(retrieval_context_json=None, external_context_json={})

    assert asyncio.run(reusable_context(_Database(row), "case-id", KEY)) is None


def test_a_second_analysis_reuses_the_stored_retrieval_and_its_legal_relevance():
    async def exercise():
        async with isolated_database() as session_factory:
            case_id, user_id, _ = await seeded_case(session_factory, trace=None)
            _, trace, _, applicability, context = _fixtures()
            received = []

            async def pipeline(data):
                received.append(data.reused_context)
                augmentation = CaseMitreAugmentation(
                    "retrieved_from_rag",
                    applicability,
                    data.reused_context or context,
                    reused=data.reused_context is not None,
                )
                return AnalysisAdvance(
                    CaseAssessmentTrace(gaps=[]),
                    Proceed("no_eligible_gap"),
                    AnalysisArtifacts(trace=trace, augmentation=augmentation),
                )

            first = await run_case_analysis(
                case_id=case_id,
                user_id=user_id,
                session_factory=session_factory,
                pipeline=pipeline,
            )
            second = await run_case_analysis(
                case_id=case_id,
                user_id=user_id,
                session_factory=session_factory,
                pipeline=pipeline,
            )

            assert received[0] is None
            assert received[1].legal_relevance == context.legal_relevance
            assert received[1].mitre_table == context.mitre_table
            assert first.result.retrieval_context_json == {
                "context_key": KEY,
                "context": context.context,
            }
            legal = context.legal_relevance.model_dump(mode="json")
            assert first.result.external_context_json["legal_relevance"] == legal
            assert second.result.external_context_json["legal_relevance"] == legal
            augmentation = second.result.external_context_json["technical_augmentation"]
            assert augmentation["retrieval_context_reused"] is True

    asyncio.run(exercise())


class _Database:
    def __init__(self, row):
        self.row = row

    async def scalar(self, _statement):
        return self.row
