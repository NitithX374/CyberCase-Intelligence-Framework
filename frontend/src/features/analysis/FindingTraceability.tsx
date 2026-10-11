import { hasThai } from "@/lib/language";
import { Icon } from "@/components/icons";
import type { FindingTraceabilityData } from "./findingTraceabilityData";

const SEMANTIC_LABELS = {
  english: {
    supported: "Source check: the cited Source passages support this finding",
    not_supported:
      "Source check: the cited Source did not clearly support this finding. Check it before relying on it.",
    unassessed: "Meaning support not assessed",
  },
  thai: {
    supported: "ตัวตรวจอัตโนมัติ: ข้อความใน Source ที่อ้างรองรับข้อค้นพบนี้",
    not_supported:
      "ตัวตรวจอัตโนมัติ: Source ที่อ้างไม่ชัดว่ารองรับข้อค้นพบนี้ ควรตรวจกับต้นฉบับก่อนใช้",
    unassessed: "ยังไม่ได้ตรวจว่า Source รองรับข้อค้นพบนี้หรือไม่",
  },
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
  const thai = hasThai(text);
  const language = thai ? "thai" : "english";
  const isSupported = traceability.semanticSupport === "supported";
  return (
    <div className="mt-2 text-xs leading-5" aria-label="Finding traceability">
      <p
        className={
          isSupported
            ? "inline-flex items-start gap-1.5 rounded-md bg-established/10 px-2.5 py-1 font-semibold text-established"
            : traceability.semanticSupport === "not_supported"
              ? "font-medium text-unresolved"
              : "text-ink-muted"
        }
        title={
          traceability.semanticReason
            ? SEMANTIC_REASONS[language][traceability.semanticReason]
            : thai
              ? "การเชื่อม Source ระบุตำแหน่งข้อความอ้างอิง ผลวิเคราะห์นี้ยังไม่มีการตรวจว่าข้อความเหล่านั้นรองรับเนื้อหาของข้อค้นพบครบหรือไม่"
              : "Source linkage locates cited text. This analysis has no recorded check that the cited passages support the complete finding."
        }
      >
        {isSupported && <Icon name="check" className="mt-0.5 h-4 w-4 shrink-0" />}
        {traceability.semanticSupport === "unassessed" && traceability.semanticReason
          ? traceability.semanticReason === "verifier_unavailable"
            ? thai
              ? "ตัวตรวจอัตโนมัติไม่พร้อมใช้งาน — ยังไม่ได้ตรวจ"
              : "Source check unavailable — not assessed"
            : thai
              ? "ตรวจการรองรับไม่ได้ — ไม่ได้นำไปใช้ในการสรุป"
              : "Support could not be assessed — not used in the summary"
          : SEMANTIC_LABELS[language][traceability.semanticSupport]}
      </p>
    </div>
  );
}
