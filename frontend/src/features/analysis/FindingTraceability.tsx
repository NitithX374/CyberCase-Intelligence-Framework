import { hasThai } from "@/lib/language";
import type { FindingTraceabilityData } from "./findingTraceabilityData";

const SEMANTIC_LABELS = {
  english: {
    supported: "Supported by its cited text",
    not_supported: "Check against the source",
    unassessed: "Not checked",
    unavailable: "Check unavailable",
    withheld: "Not checked, not used in the summary",
  },
  thai: {
    supported: "ข้อความที่อ้างรองรับ",
    not_supported: "ควรตรวจกับต้นฉบับ",
    unassessed: "ยังไม่ได้ตรวจ",
    unavailable: "ตัวตรวจไม่พร้อมใช้งาน",
    withheld: "ยังไม่ได้ตรวจ ไม่ได้ใช้ในการสรุป",
  },
};

const STATUS_CLASS = {
  supported: "font-medium text-established",
  not_supported: "font-medium text-unresolved",
  unassessed: "text-ink-muted",
};

const SEMANTIC_REASONS = {
  english: {
    lr_supported: "Selected Source passages scored above the cutoff of the automatic check.",
    lr_not_supported:
      "Selected Source passages scored below the cutoff of the automatic check. This is a screening signal, not proof that the finding is wrong.",
    verifier_unavailable:
      "The support check could not run for this analysis, so this finding was neither confirmed nor flagged.",
    entailed: "The source check found that the cited Source passages support this finding.",
    neutral: "The source check did not find that the cited Source passages support this finding.",
    contradiction: "The source check found that the cited Source passages contradict this finding.",
    low_entailment: "The support score was below the cutoff of the source check.",
    no_resolved_source: "There are no resolved supporting Source passages to assess.",
    unresolved_source_reference: "Some supporting Source references could not be resolved.",
    conflicting_source:
      "The finding has conflicting Source citations and was not used in the summary.",
    claim_uncertain:
      "The finding has an uncertain or contradicted status and was not used in the summary.",
    input_too_long:
      "The complete Source passages and finding exceed the input limit of the source check.",
  },
  thai: {
    lr_supported: "ข้อความใน Source ที่เลือกได้คะแนนสูงกว่าเกณฑ์ของตัวตรวจอัตโนมัติ",
    lr_not_supported:
      "ข้อความใน Source ที่เลือกได้คะแนนต่ำกว่าเกณฑ์ของตัวตรวจอัตโนมัติ เป็นเพียงสัญญาณคัดกรอง ไม่ใช่การยืนยันว่าข้อค้นพบนี้ผิด",
    verifier_unavailable:
      "ตัวตรวจอัตโนมัติไม่พร้อมใช้งานในการวิเคราะห์นี้ จึงยังไม่ได้ตรวจข้อค้นพบนี้",
    entailed: "ตัวตรวจอัตโนมัติพบว่าข้อความใน Source ที่อ้างรองรับข้อค้นพบนี้",
    neutral: "ตัวตรวจอัตโนมัติไม่พบว่าข้อความใน Source ที่อ้างรองรับข้อค้นพบนี้",
    contradiction: "ตัวตรวจอัตโนมัติพบว่าข้อความใน Source ที่อ้างขัดแย้งกับข้อค้นพบนี้",
    low_entailment: "คะแนนการรองรับต่ำกว่าเกณฑ์ที่ตัวตรวจอัตโนมัติใช้",
    no_resolved_source: "ไม่มีข้อความ Source สนับสนุนที่เชื่อมตำแหน่งได้ให้ตรวจ",
    unresolved_source_reference: "การอ้างอิง Source สนับสนุนบางรายการยังเชื่อมตำแหน่งไม่ได้",
    conflicting_source: "ข้อค้นพบนี้อ้าง Source ที่ขัดแย้งกัน จึงไม่ได้นำไปใช้ในการสรุป",
    claim_uncertain: "ข้อค้นพบนี้มีสถานะไม่แน่ชัดหรือขัดแย้ง จึงไม่ได้นำไปใช้ในการสรุป",
    input_too_long: "ข้อความใน Source และข้อค้นพบรวมกันยาวเกินขีดจำกัดของตัวตรวจอัตโนมัติ",
  },
};

export function FindingTraceability({
  traceability,
  text,
}: {
  traceability: FindingTraceabilityData;
  text: string;
}) {
  const language = hasThai(text) ? "thai" : "english";
  const labels = SEMANTIC_LABELS[language];
  const support = traceability.semanticSupport;
  const reason = traceability.semanticReason;
  const label =
    support !== "unassessed" || !reason
      ? labels[support]
      : reason === "verifier_unavailable"
        ? labels.unavailable
        : labels.withheld;
  return (
    <span
      aria-label="Finding traceability"
      className={`text-xs leading-5 ${STATUS_CLASS[support]}`}
      title={
        reason
          ? SEMANTIC_REASONS[language][reason]
          : language === "thai"
            ? "การเชื่อม Source ระบุตำแหน่งข้อความอ้างอิง ผลวิเคราะห์นี้ยังไม่มีการตรวจว่าข้อความเหล่านั้นรองรับเนื้อหาของข้อค้นพบครบหรือไม่"
            : "Source linkage locates cited text. This analysis has no recorded check that the cited passages support the complete finding."
      }
    >
      {label}
    </span>
  );
}
