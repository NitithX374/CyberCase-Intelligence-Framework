import { hasThai } from "@/lib/language";
import { Icon } from "@/components/icons";
import type { FindingTraceabilityData } from "./findingTraceabilityData";

const SEMANTIC_LABELS = {
  english: {
    supported: "NLI: Source passages support this finding",
    not_supported:
      "Source check: the cited Source did not clearly support this finding. Check it before relying on it.",
    unassessed: "Meaning support not assessed",
  },
  thai: {
    supported: "NLI: ข้อความ Source รองรับ Finding",
    not_supported:
      "ตัวตรวจอัตโนมัติ: Source ที่อ้างไม่ชัดว่ารองรับ Finding นี้ ควรตรวจกับต้นฉบับก่อนใช้",
    unassessed: "ยังไม่ได้ตรวจการรองรับทางความหมาย",
  },
};

const SEMANTIC_REASONS = {
  english: {
    lr_supported: "Selected Source passages scored above the cutoff of the B1-LR support check.",
    lr_not_supported:
      "Selected Source passages scored below the cutoff of the B1-LR support check. This is a screening signal, not proof that the finding is wrong.",
    verifier_unavailable:
      "The support check could not run for this analysis, so this finding was neither confirmed nor flagged.",
    entailed: "The cited Source passages passed the NLI entailment threshold for this finding.",
    neutral: "The NLI model did not find that the cited Source passages entail this finding.",
    contradiction:
      "The NLI model found a contradiction between the cited Source passages and this finding.",
    low_entailment: "The NLI entailment score was below the admission threshold.",
    no_resolved_source: "There are no resolved supporting Source passages to assess.",
    unresolved_source_reference: "Some supporting Source references could not be resolved.",
    conflicting_source: "The finding has conflicting Source citations and was withheld.",
    claim_uncertain: "The finding has an uncertain or contradicted status and was withheld.",
    input_too_long: "The complete Source passages and finding exceed the NLI input limit.",
  },
  thai: {
    lr_supported: "ข้อความ Source ที่เลือกได้คะแนนสูงกว่าเกณฑ์ของตัวตรวจ B1-LR",
    lr_not_supported:
      "ข้อความ Source ที่เลือกได้คะแนนต่ำกว่าเกณฑ์ของตัวตรวจ B1-LR เป็นเพียงสัญญาณคัดกรอง ไม่ใช่การยืนยันว่า Finding ผิด",
    verifier_unavailable:
      "ตัวตรวจไม่พร้อมใช้งานในการวิเคราะห์นี้ จึงไม่ได้ยืนยันหรือติดป้าย Finding นี้",
    entailed: "ข้อความ Source ที่อ้างผ่านเกณฑ์การรองรับ Finding ของ NLI",
    neutral: "NLI ไม่พบว่าข้อความ Source ที่อ้างรองรับเนื้อหา Finding",
    contradiction: "NLI พบว่าข้อความ Source ที่อ้างขัดแย้งกับ Finding",
    low_entailment: "คะแนนการรองรับจาก NLI ต่ำกว่าเกณฑ์ที่ใช้ส่งเข้า Judgement",
    no_resolved_source: "ไม่มีข้อความ Source สนับสนุนที่เชื่อมตำแหน่งได้ให้ตรวจ",
    unresolved_source_reference: "การอ้างอิง Source สนับสนุนบางรายการยังเชื่อมตำแหน่งไม่ได้",
    conflicting_source: "Finding มีการอ้าง Source ที่ขัดแย้ง จึงไม่ส่งเข้า Judgement",
    claim_uncertain: "Finding มีสถานะน่าสงสัยหรือขัดแย้ง จึงไม่ส่งเข้า Judgement",
    input_too_long: "ข้อความ Source และ Finding รวมกันยาวเกินขีดจำกัดของ NLI",
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
              ? "การเชื่อม Source ระบุตำแหน่งข้อความอ้างอิง ผลวิเคราะห์นี้ยังไม่มีการตรวจว่าข้อความเหล่านั้นรองรับเนื้อหาของ Finding ครบหรือไม่"
              : "Source linkage locates cited text. This analysis has no recorded check that the cited passages support the complete finding."
        }
      >
        {isSupported && <Icon name="check" className="mt-0.5 h-4 w-4 shrink-0" />}
        {traceability.semanticSupport === "unassessed" && traceability.semanticReason
          ? traceability.semanticReason === "verifier_unavailable"
            ? thai
              ? "ตัวตรวจ Source ไม่พร้อมใช้งาน — ยังไม่ได้ประเมิน"
              : "Source check unavailable — not assessed"
            : thai
              ? "ตรวจการรองรับไม่ได้ — ไม่ส่งเข้า Judgement"
              : "Support could not be assessed — withheld from Judgement"
          : SEMANTIC_LABELS[language][traceability.semanticSupport]}
      </p>
    </div>
  );
}
