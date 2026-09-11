import hashlib
import unittest
from unittest.mock import patch

import pytest

from app.services.case_analysis.caseAnalysis import executeRawDirectPipeline
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseProviderAnalysis,
    CaseTimelineItem,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_analysis.validation import validate_case_trace


def test_case_overview_models_construct_and_normalize_claim_ids() -> None:
    party = CaseInvolvedParty(
        name="Alice Corp",
        role="Victim Organization",
        claim_ids=["claim-1", "A-02"],
    )
    assert party.name == "Alice Corp"
    assert party.role == "Victim Organization"
    assert party.claim_ids == ["A-01", "A-02"]

    timeline_item = CaseTimelineItem(
        time="2026-03-01 10:00:00 UTC",
        event="Unauthorized access detected",
        claim_ids=["c-2"],
    )
    assert timeline_item.time == "2026-03-01 10:00:00 UTC"
    assert timeline_item.event == "Unauthorized access detected"
    assert timeline_item.claim_ids == ["A-02"]

    impact = CaseImpactItem(
        description="Customer database exfiltrated",
        claim_ids=["A-03"],
    )
    assert impact.description == "Customer database exfiltrated"
    assert impact.claim_ids == ["A-03"]


def test_validate_case_trace_accepts_valid_parties_timeline_and_impacts() -> None:
    source = CaseAdmittedSource(
        source_id="s1",
        revision=1,
        content="Server breached on Monday.",
        content_sha256=hashlib.sha256(b"Server breached on Monday.").hexdigest(),
    )
    citation = CaseEvidenceCitation(
        source_id="s1",
        source_revision=1,
        exact_quote="Server breached on Monday.",
    )
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="Server breached on Monday.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
        supporting_citations=[citation],
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Breach occurred.",
        involved_parties=[
            CaseInvolvedParty(name="Victim Org", role="Target", claim_ids=["A-01"])
        ],
        timeline=[
            CaseTimelineItem(time="Monday", event="Breach", claim_ids=["A-01"])
        ],
        claims=[claim],
        impacts=[
            CaseImpactItem(description="Server compromise", claim_ids=["A-01"])
        ],
        evidence_sha256="0" * 64,
    )
    validated = validate_case_trace(trace, (source,), [])
    assert len(validated.involved_parties) == 1
    assert len(validated.timeline) == 1
    assert len(validated.impacts) == 1


def test_validate_case_trace_rejects_unknown_claim_in_involved_parties() -> None:
    source = CaseAdmittedSource(
        source_id="s1",
        revision=1,
        content="Server breached.",
        content_sha256=hashlib.sha256(b"Server breached.").hexdigest(),
    )
    citation = CaseEvidenceCitation(
        source_id="s1",
        source_revision=1,
        exact_quote="Server breached.",
    )
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="Server breached.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
        supporting_citations=[citation],
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Breach occurred.",
        involved_parties=[
            CaseInvolvedParty(name="Unknown Actor", role="Attacker", claim_ids=["A-99"])
        ],
        claims=[claim],
        evidence_sha256="0" * 64,
    )
    with pytest.raises(CaseAnalysisFailure) as exc_info:
        validate_case_trace(trace, (source,), [])
    assert exc_info.value.code == "case_trace_party_unknown_claim"


def test_validate_case_trace_rejects_unknown_claim_in_timeline() -> None:
    source = CaseAdmittedSource(
        source_id="s1",
        revision=1,
        content="Server breached.",
        content_sha256=hashlib.sha256(b"Server breached.").hexdigest(),
    )
    citation = CaseEvidenceCitation(
        source_id="s1",
        source_revision=1,
        exact_quote="Server breached.",
    )
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="Server breached.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
        supporting_citations=[citation],
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Breach occurred.",
        timeline=[
            CaseTimelineItem(time="Tuesday", event="Lateral movement", claim_ids=["A-05"])
        ],
        claims=[claim],
        evidence_sha256="0" * 64,
    )
    with pytest.raises(CaseAnalysisFailure) as exc_info:
        validate_case_trace(trace, (source,), [])
    assert exc_info.value.code == "case_trace_timeline_unknown_claim"


def test_validate_case_trace_rejects_unknown_claim_in_impacts() -> None:
    source = CaseAdmittedSource(
        source_id="s1",
        revision=1,
        content="Server breached.",
        content_sha256=hashlib.sha256(b"Server breached.").hexdigest(),
    )
    citation = CaseEvidenceCitation(
        source_id="s1",
        source_revision=1,
        exact_quote="Server breached.",
    )
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="Server breached.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
        supporting_citations=[citation],
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Breach occurred.",
        impacts=[
            CaseImpactItem(description="Financial loss", claim_ids=["A-99"])
        ],
        claims=[claim],
        evidence_sha256="0" * 64,
    )
    with pytest.raises(CaseAnalysisFailure) as exc_info:
        validate_case_trace(trace, (source,), [])
    assert exc_info.value.code == "case_trace_impact_unknown_claim"


class DirectAnalysisStructuralOverviewTests(unittest.IsolatedAsyncioTestCase):
    async def test_direct_pipeline_populates_parties_timeline_and_impacts(self) -> None:
        raw_text = "On Monday, company ACME was targeted by unauthorized access."
        source = CaseAdmittedSource(
            source_id="s1",
            revision=1,
            content=raw_text,
            content_sha256=hashlib.sha256(raw_text.encode()).hexdigest(),
        )
        citation = CaseEvidenceCitation(
            source_id="s1",
            source_revision=1,
            exact_quote=raw_text,
        )
        claim = CaseAnalysisClaim(
            claim_id="A-01",
            claim_type="reported",
            text="Company ACME was targeted by unauthorized access on Monday.",
            epistemic_status="reported",
            supporting_source_ids=["s1"],
            supporting_citations=[citation],
        )
        provider_output = CaseProviderAnalysis(
            version="case_analysis_trace_v1",
            answer="Summary answer",
            summary="Case overview summary",
            involved_parties=[
                CaseInvolvedParty(name="ACME", role="Victim", claim_ids=["A-01"])
            ],
            timeline=[
                CaseTimelineItem(time="Monday", event="Unauthorized access", claim_ids=["A-01"])
            ],
            claims=[claim],
            impacts=[
                CaseImpactItem(description="Unauthorized access to systems", claim_ids=["A-01"])
            ],
        )

        async def fake_request_stage(*args, **kwargs):
            return provider_output

        raw_evidence = f"[SOURCE s1 · REVISION 1]\n{raw_text}"
        digest = hashlib.sha256(raw_evidence.encode()).hexdigest()
        with patch(
            "app.services.case_analysis.caseAnalysis.requestAnalysisStage",
            new=fake_request_stage,
        ):
            result = await executeRawDirectPipeline(
                raw_evidence,
                {"document_source_context": []},
                "english",
                AnalysisPipelineConfig(),
                (source,),
                None,  # client
                digest,
                {"calls": []},
                "case_overview",
                None,
            )

        assert result.trace is not None
        assert isinstance(result.trace, CaseAnalysisTrace)
        assert len(result.trace.involved_parties) == 1
        assert result.trace.involved_parties[0].name == "ACME"
        assert result.trace.involved_parties[0].claim_ids == ["A-01"]
        assert len(result.trace.timeline) == 1
        assert result.trace.timeline[0].event == "Unauthorized access"
        assert len(result.trace.impacts) == 1
        assert result.trace.impacts[0].description == "Unauthorized access to systems"
