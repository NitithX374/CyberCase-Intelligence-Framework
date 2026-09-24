from types import SimpleNamespace
from uuid import uuid4

from app.schemas.rag import LegalReferenceResult
from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.analysis.mitre_gate.llm import MitreApplicabilityRecord
from app.services.analysis.steps.technical_context import CaseRagContextPayload
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem


def _fixtures():
    source_id = str(uuid4())
    text = "พบการใช้ PowerShell.exe เชื่อมต่อไปยัง 198.51.100.23"
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The evidence reports PowerShell network activity.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=text)],
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=claim.text,
        claims=[claim],
    )
    source_bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=text),),
    )
    applicability = MitreApplicabilityRecord(
        decision="RETRIEVE",
        source_message_ids=[source_id],
        trigger_text=[text],
    )
    context = CaseRagContextPayload(
        retrieval_context_id="retrieval-case-1",
        context="PowerShell execution is external technical context.",
        mitre_table=(
            {
                "technique_id": "T1059.001",
                "name": "PowerShell",
                "description": "Command and scripting interpreter.",
            },
            {
                "technique_id": "S0096",
                "name": "Systeminfo",
                "entity_type": "Software",
                "description": "System information utility.",
            },
        ),
        legal_relevance=LegalReferenceResult(
            provider="thanoy",
            query_sent="PowerShell execution",
        ),
    )
    return source_id, trace, source_bundle, applicability, context


def _gate(record):
    async def evaluate(**kwargs):
        return record

    return evaluate


def _response(context):
    return SimpleNamespace(
        retrieval_context_id=context.retrieval_context_id,
        context=context.context,
        mitre_table=list(context.mitre_table),
        legal_reference=context.legal_relevance,
    )
