import type { CaseProjectionGrounding } from "@/lib/api/types";

export type ProjectionCheckStatus = CaseProjectionGrounding["verdict"] | "not_recorded";

const REASONS = {
  english: {
    no_claim: "This description is not linked to a claim.",
    unknown_claim: "One or more linked claims could not be found.",
    unbound_claim: "A linked claim has no resolved source citation.",
    qualified_claim: "A linked claim is not recorded as reported information.",
    context_limit: "The linked claims and description exceed the verifier's input limit.",
    entailment: "The verifier found support for the complete description in the linked claims.",
    neutral: "The linked claims do not establish the complete description.",
    contradiction: "The verifier found a conflict with the linked claims.",
    low_entailment: "The verifier did not reach the required support threshold.",
  },
  thai: {
    no_claim: "รายการนี้ไม่ได้เชื่อมกับข้อค้นพบใด",
    unknown_claim: "ไม่พบข้อค้นพบที่เชื่อมไว้บางข้อ",
    unbound_claim: "ข้อค้นพบที่เชื่อมไว้บางข้อยังไม่มีข้อความอ้างอิงจาก Source ที่ระบุตำแหน่งได้",
    qualified_claim: "ข้อค้นพบที่เชื่อมไว้บางข้อไม่ได้มีสถานะเป็นข้อมูลที่รายงานไว้",
    context_limit: "ข้อค้นพบและรายการนี้ยาวเกินขีดจำกัดของตัวตรวจสอบ",
    entailment: "ตัวตรวจสอบพบว่าข้อค้นพบที่เชื่อมไว้สนับสนุนเนื้อหาทั้งหมดของรายการนี้",
    neutral: "ข้อค้นพบที่เชื่อมไว้ยังไม่รองรับเนื้อหาทั้งหมดของรายการนี้",
    contradiction: "ตัวตรวจสอบพบว่าเนื้อหาขัดกับข้อค้นพบที่เชื่อมไว้",
    low_entailment: "ผลตรวจยังไม่ถึงเกณฑ์ที่กำหนดสำหรับการสนับสนุน",
  },
};

export function projectionStatus(
  grounding: CaseProjectionGrounding | null | undefined,
): ProjectionCheckStatus {
  return grounding?.verdict ?? "not_recorded";
}

export function projectionReason(grounding: CaseProjectionGrounding, thai = false): string {
  const reason = grounding.reason;
  if (reason.startsWith("model_unavailable:")) {
    const detail = reason.slice("model_unavailable:".length);
    if (detail === "weights_missing") {
      return thai
        ? "ตัวตรวจสอบยังใช้งานไม่ได้ เพราะไม่มีไฟล์โมเดล"
        : "The support verifier is unavailable because its model files are missing.";
    }
    return thai
      ? `ตัวตรวจสอบยังใช้งานไม่ได้ (${detail})`
      : `The support verifier is unavailable (${detail}).`;
  }
  const reasons = REASONS[thai ? "thai" : "english"];
  return Object.hasOwn(reasons, reason)
    ? reasons[reason as keyof typeof reasons]
    : thai
      ? `เหตุผลที่บันทึกไว้: ${reason}`
      : `Recorded check reason: ${reason}`;
}

export const PROJECTION_LABELS: Record<ProjectionCheckStatus, string> = {
  supported: "Supported by linked claims",
  not_supported: "Not supported by linked claims",
  unassessed: "Not assessed",
  not_recorded: "Check not recorded",
};
