from __future__ import annotations

from collections.abc import Callable

from app.analysis.technical_context.contracts import CaseTechnicalAugmentation
from app.reports.schemas import ReportTechnique
from app.trace.trace import CaseAnalysisTrace

UNREACHABLE_SERVICE_CODES = {"rag_service_error", "rag_service_unavailable"}
NOTES_BY_STATUS = {
    "not_applicable": (
        "ไม่พบเงื่อนไขที่จำเป็นต้องใช้ MITRE ATT&CK กับคดีนี้",
        "ระบบข้ามการค้นหา MITRE ตามเกณฑ์ความเกี่ยวข้องของคดี",
    ),
    "insufficient_context": (
        "มีการร้องขอ MITRE ATT&CK แต่ข้อมูลทางเทคนิคภายนอกไม่เพียงพอ",
        "ยังไม่มีบริบททางเทคนิคเพียงพอสำหรับการให้เหตุผลของ mapping",
    ),
}


def report_techniques(
    augmentation: CaseTechnicalAugmentation | None,
    trace: CaseAnalysisTrace,
    ordinals: dict[str, int],
    references: Callable[[list[str]], list[str]],
) -> tuple[list[ReportTechnique], bool]:
    if augmentation is None:
        return [], False
    rows = {
        str(row["technique_id"]): row for row in augmentation.mitre_table if row.get("technique_id")
    }
    if augmentation.status == "retrieved_with_matches":
        return [
            ReportTechnique(
                technique_id=association.technique_id,
                name=row_text(rows.get(association.technique_id), "name"),
                tactic=row_text(rows.get(association.technique_id), "tactic"),
                meaning=association.plain_meaning.strip(),
                reason=association.reason,
                findings=sorted(
                    {
                        ordinals[claim_id]
                        for claim_id in association.claim_ids
                        if claim_id in ordinals
                    }
                ),
                references=references(association.claim_ids),
            )
            for association in trace.mitre_associations
        ], True
    if augmentation.status == "retrieved_from_rag":
        return [
            ReportTechnique(
                technique_id=str(row.get("technique_id") or row.get("name") or "-"),
                name=row_text(row, "name"),
                tactic=row_text(row, "tactic"),
                meaning="",
                reason="",
            )
            for row in augmentation.mitre_table
        ], False
    return [], False


def row_text(row: dict[str, object] | None, key: str) -> str:
    value = (row or {}).get(key)
    return value.strip() if isinstance(value, str) else ""


def failure_detail(augmentation: CaseTechnicalAugmentation) -> str:
    if augmentation.failure_code in UNREACHABLE_SERVICE_CODES:
        return "ไม่สามารถเชื่อมต่อกับบริการภายนอกได้ในขณะนี้"
    return f"ระบบภายนอกขัดข้อง ({augmentation.failure_code})"


def augmentation_notes(
    augmentation: CaseTechnicalAugmentation | None,
) -> tuple[str | None, str | None]:
    if augmentation is None:
        return (
            "ไม่มีผลการเสริมข้อมูล MITRE ที่บันทึกไว้สำหรับผลวิเคราะห์นี้",
            "ไม่มีผลการเสริมข้อมูล MITRE ที่บันทึกไว้ จึงไม่มีการอนุมาน mapping จาก metadata",
        )
    if augmentation.status == "failed":
        detail = failure_detail(augmentation)
        return (
            f"การเสริมข้อมูล MITRE ATT&CK ไม่สำเร็จ: {detail} จึงไม่แสดง mapping เป็นข้อสรุปของคดี",
            f"ยังไม่สามารถอธิบาย mapping ได้ ({detail})",
        )
    return NOTES_BY_STATUS.get(augmentation.status, (None, None))
