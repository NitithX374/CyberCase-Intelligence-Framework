from app.services.case_materials.materialService import (
    AssembledCaseEvidence,
    CaseMaterialsError,
    CaseMaterialsService,
    assembleCaseEvidence,
    buildCaseEvidenceSnapshot,
)
from app.services.case_materials.documentContent import getOwnedDocumentContent
import json


def canonicalJson(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


__all__ = [
    "AssembledCaseEvidence",
    "CaseMaterialsError",
    "CaseMaterialsService",
    "assembleCaseEvidence",
    "buildCaseEvidenceSnapshot",
    "canonicalJson",
    "getOwnedDocumentContent",
]
