import asyncio
import hashlib
import unittest
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.services.case_analysis.caseAnalysis import executeRawDirectPipeline
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisClaim,
    CaseEvidenceCitation,
    CaseProviderAnalysis,
)
from app.services.case_analysis.pipelineConfig import AnalysisPipelineConfig
from app.services.case_materials import CaseMaterialsService, buildCaseEvidenceSnapshot
from app.services.workflow.caseRunExecution import _analysis_context
from app.services.workflow.caseRunService import ClaimedCaseRun
from run_recovery_support import isolated_database


def test_analysis_context_extracts_ocr_quality_metadata_from_manifest() -> None:
    manifest_entry = {
        "source_id": "s1",
        "source_kind": "reviewed_document",
        "revision_id": "r1",
        "revision": 1,
        "exact_text": "OCR transcribed text.",
        "text_sha256": hashlib.sha256(b"OCR transcribed text.").hexdigest(),
        "document_id": "DOC-OCR-001",
        "filename": "scan.pdf",
        "provenance": {
            "document_id": "DOC-OCR-001",
            "filename": "scan.pdf",
            "extraction_method": "document_recognition",
            "provider": "document_recognition",
            "verification_status": "machine_read",
            "confidence_status": "not_reported",
            "minimum_confidence": None,
            "warnings": ["Typhoon OCR did not report confidence."],
            "pages": [
                {
                    "page_number": 1,
                    "start_offset": 0,
                    "end_offset": 21,
                    "text_sha256": hashlib.sha256(b"OCR transcribed text.").hexdigest(),
                }
            ],
        },
    }
    claimed = ClaimedCaseRun(
        id=uuid4(),
        case_id=uuid4(),
        snapshot_id=uuid4(),
        attempt_count=0,
        operation="analysis",
        input_text="OCR transcribed text.",
        text_sha256=hashlib.sha256(b"OCR transcribed text.").hexdigest(),
        manifest=(manifest_entry,),
        source_ids=("s1",),
        source_text_by_id={"s1": "OCR transcribed text."},
        pipeline_config={},
        request_payload={},
    )
    context = _analysis_context(claimed)
    doc_context = context["document_source_context"]
    assert len(doc_context) == 1
    doc = doc_context[0]["documents"][0]
    assert doc["document_id"] == "DOC-OCR-001"
    assert doc["filename"] == "scan.pdf"
    assert doc["extraction_method"] == "document_recognition"
    assert doc["verification_status"] == "machine_read"
    assert doc["confidence_status"] == "not_reported"
    assert doc["minimum_confidence"] is None
    assert doc["warnings"] == ["Typhoon OCR did not report confidence."]


class DirectPipelineOcrQualityTests(unittest.IsolatedAsyncioTestCase):
    async def test_execute_raw_direct_passes_quality_context_to_request_stage(self) -> None:
        source_text = "Scanned statement text."
        source = CaseAdmittedSource(
            source_id="s1",
            revision=1,
            content=source_text,
            content_sha256=hashlib.sha256(source_text.encode()).hexdigest(),
        )
        citation = CaseEvidenceCitation(
            source_id="s1",
            source_revision=1,
            exact_quote=source_text,
        )
        claim = CaseAnalysisClaim(
            claim_id="A-01",
            claim_type="reported",
            text="Scanned statement text.",
            epistemic_status="reported",
            supporting_source_ids=["s1"],
            supporting_citations=[citation],
        )
        provider_output = CaseProviderAnalysis(
            version="case_analysis_trace_v1",
            answer="Answer",
            summary="Summary",
            claims=[claim],
        )

        captured_request_content: dict[str, object] = {}

        async def fake_request_stage(client, config, stage, system, content, schema, receipt):
            nonlocal captured_request_content
            captured_request_content = content
            return provider_output

        context = {
            "document_source_context": [
                {
                    "source_id": "s1",
                    "documents": [
                        {
                            "document_id": "DOC-OCR-001",
                            "filename": "scan.pdf",
                            "page_spans": [{"page_number": 1, "start_offset": 0, "end_offset": len(source_text)}],
                            "extraction_method": "document_recognition",
                            "provider": "document_recognition",
                            "verification_status": "machine_read",
                            "confidence_status": "not_reported",
                            "minimum_confidence": None,
                            "warnings": ["Typhoon OCR did not report confidence."],
                        }
                    ],
                }
            ]
        }

        raw_evidence = f"[DOCUMENT scan.pdf · SOURCE s1 · REVISION 1]\n{source_text}"
        digest = hashlib.sha256(raw_evidence.encode()).hexdigest()
        with patch(
            "app.services.case_analysis.caseAnalysis.requestAnalysisStage",
            new=fake_request_stage,
        ):
            await executeRawDirectPipeline(
                raw_evidence,
                context,
                "english",
                AnalysisPipelineConfig(),
                (source,),
                None,
                digest,
                {"calls": []},
                "case_overview",
                None,
            )

        assert "document_quality_context" in captured_request_content
        quality_list = captured_request_content["document_quality_context"]
        assert len(quality_list) == 1
        meta = quality_list[0]
        assert meta["extraction_method"] == "document_recognition"
        assert meta["verification_status"] == "machine_read"
        assert meta["confidence_status"] == "not_reported"
        assert meta["minimum_confidence"] is None
        assert meta["warnings"] == ["Typhoon OCR did not report confidence."]


def test_document_extraction_warnings_survive_admission_and_snapshot_postgres():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="OCR Quality Case"))
            async with factory() as db, db.begin():
                document = await CaseMaterialsService(db).addDocument(
                    case_id=case_id,
                    user_id=None,
                    filename="scanned_report.pdf",
                    mime_type="application/pdf",
                    content=b"%PDF-scanned",
                    extraction={
                        "provider": "document_recognition",
                        "config_json": {"mode": "unified"},
                        "extracted_text": "Scanned Thai text from document.",
                        "provenance_json": {
                            "document_id": "DOC-SCAN-1",
                            "media_type": "application/pdf",
                            "extraction_method": "document_recognition",
                            "mode": "unified",
                            "pages": [
                                {
                                    "page_number": 1,
                                    "merged_text": "Scanned Thai text from document.",
                                    "regions": [
                                        {
                                            "region_id": "DOC-SCAN-1-P001-R001",
                                            "page_number": 1,
                                            "region_type": "printed_text",
                                            "recognition_method": "ocr",
                                            "recognizer": "typhoon",
                                            "text": "Scanned Thai text from document.",
                                            "verification_status": "machine_read",
                                            "content_role": "transcribed_text",
                                            "recognition_confidence": None,
                                        }
                                    ],
                                }
                            ],
                        },
                        "warnings_json": ["Typhoon OCR does not provide calibrated confidence."],
                    },
                )
                source = await CaseMaterialsService(db).admitExtraction(
                    case_id=case_id,
                    user_id=None,
                    extraction_id=document.extractions[0].id,
                )
                revision = source.revisions[0]
                prov = revision.provenance_json
                assert prov["warnings"] == ["Typhoon OCR does not provide calibrated confidence."]
                assert prov["extraction_method"] == "document_recognition"
                assert prov["verification_status"] == "machine_read"
                assert prov["confidence_status"] == "not_reported"
                assert prov["minimum_confidence"] is None

            async with factory() as db, db.begin():
                snapshot = await buildCaseEvidenceSnapshot(db, case_id=case_id, user_id=None)
                manifest_entry = snapshot.manifest_json[0]
                snap_prov = manifest_entry["provenance"]
                assert snap_prov["warnings"] == ["Typhoon OCR does not provide calibrated confidence."]
                assert snap_prov["extraction_method"] == "document_recognition"
                assert snap_prov["confidence_status"] == "not_reported"

    asyncio.run(exercise())
