from __future__ import annotations

from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT
from app.analysis.write import judgement_request
from app.llm.request import request_stage
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.claims import CaseAnalysisClaim
from app.trace.evidence_binding import direct_citation
from app.trace.trace import CaseProviderJudgement, CaseProviderReading

from research.attribution_benchmark.propagation_data import ResponseCluster


def row_claim(claim_id: str, row: dict) -> CaseAnalysisClaim:
    sources = [
        CaseSourceItem(
            source_id=f"R-{row['id']}-ref-{index:02d}",
            source_kind="benchmark_reference",
            text=reference,
        )
        for index, reference in enumerate(row["references"], 1)
    ]
    if any(not source.text for source in sources):
        raise ValueError(f"Empty reference text cannot be represented: {row['id']}")
    citations = [
        direct_citation(unit, source) for source in sources for unit in evidence_units(source)
    ]
    claim = CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text=row["claim"],
        epistemic_status="reported",
        supporting_source_ids=[source.source_id for source in sources],
        supporting_citations=citations,
    )
    if len(row["claim"]) > 4_000:
        raise ValueError("Original claim exceeds native schema limit")
    claim = claim.model_copy(update={"text": row["claim"]})
    for source in sources:
        bound = [
            citation
            for citation in claim.supporting_citations
            if citation.source_id == source.source_id
        ]
        if "".join(citation.exact_quote for citation in bound) != source.text:
            raise ValueError(f"Native evidence conversion changed original reference: {row['id']}")
        if any(
            citation.exact_quote != source.text[citation.start : citation.end] for citation in bound
        ):
            raise ValueError("Native evidence offsets differ from original reference")
    if len(claim.supporting_citations) != len(citations):
        raise ValueError("Native schema dropped evidence citations")
    return claim


def prepare_payload(cluster: ResponseCluster, accepted: set[str]) -> dict:
    known = {claim_id for claim_id, _ in cluster.assigned_rows}
    if not accepted <= known:
        raise ValueError("Admission contains unknown claim IDs")
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[
            row_claim(claim_id, row)
            for claim_id, row in cluster.assigned_rows
            if claim_id in accepted
        ],
    )
    return judgement_request(reading, "en", (), None)


async def judge(
    payload: dict, config: AnalysisPipelineConfig, calls: list
) -> CaseProviderJudgement:
    if not payload["reading"]["claims"]:
        raise ValueError("Do not call Judgement with no accepted claims")
    return await request_stage(
        config=config,
        stage="case_judgement",
        system=CASE_JUDGEMENT_SYSTEM_PROMPT,
        content=payload,
        schema=CaseProviderJudgement,
        calls=calls,
        temperature=0,
    )
