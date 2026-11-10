import { hasThai } from "@/lib/language";
import type { FindingTraceabilityData } from "./findingTraceabilityData";

const SEMANTIC_LABELS = {
  english: {
    not_supported:
      "Source check: the cited Source did not clearly support this finding. Check it before relying on it.",
    unassessed: "Support not checked",
  },
  thai: {
    not_supported:
      "ตัวตรวจอัตโนมัติ: Source ที่อ้างไม่ชัดว่ารองรับข้อค้นพบนี้ ควรตรวจกับต้นฉบับก่อนใช้",
    unassessed: "ยังไม่ได้ตรวจว่า Source รองรับข้อค้นพบนี้หรือไม่",
  },
};

const SEMANTIC_REASONS: Record<
  "english" | "thai",
  Partial<Record<NonNullable<FindingTraceabilityData["semanticReason"]>, string>>
> = {
  english: {
    lr_not_supported:
      "The automatic check scored the cited words low. It is a prompt to look, not proof the finding is wrong.",
    verifier_unavailable:
      "The support check could not run for this analysis, so this finding was neither confirmed nor flagged.",
    no_resolved_source: "No cited passage could be found to check.",
    unresolved_source_reference: "Some cited passages could not be found.",
    conflicting_source:
      "The finding has conflicting Source citations and was not used in the summary.",
    claim_uncertain:
      "The finding has an uncertain or contradicted status and was not used in the summary.",
  },
  thai: {
    lr_not_supported:
      "ข้อความใน Source ที่เลือกได้คะแนนต่ำกว่าเกณฑ์ของตัวตรวจอัตโนมัติ เป็นเพียงสัญญาณคัดกรอง ไม่ใช่การยืนยันว่าข้อค้นพบนี้ผิด",
    verifier_unavailable:
      "ตัวตรวจอัตโนมัติไม่พร้อมใช้งานในการวิเคราะห์นี้ จึงยังไม่ได้ตรวจข้อค้นพบนี้",
    no_resolved_source: "ไม่มีข้อความ Source สนับสนุนที่เชื่อมตำแหน่งได้ให้ตรวจ",
    unresolved_source_reference: "การอ้างอิง Source สนับสนุนบางรายการยังเชื่อมตำแหน่งไม่ได้",
    conflicting_source: "ข้อค้นพบนี้อ้าง Source ที่ขัดแย้งกัน จึงไม่ได้นำไปใช้ในการสรุป",
    claim_uncertain: "ข้อค้นพบนี้มีสถานะไม่แน่ชัดหรือขัดแย้ง จึงไม่ได้นำไปใช้ในการสรุป",
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
  if (traceability.semanticSupport === "supported") return null;
  return (
    <div className="mt-2 text-xs leading-5" aria-label="Finding traceability">
      <p
        className={
          traceability.semanticSupport === "not_supported"
            ? "font-medium text-unresolved"
            : "text-ink-muted"
        }
        title={
          traceability.semanticReason
            ? SEMANTIC_REASONS[language][traceability.semanticReason]
            : thai
              ? "การเชื่อม Source ระบุตำแหน่งข้อความอ้างอิง ผลวิเคราะห์นี้ยังไม่มีการตรวจว่าข้อความเหล่านั้นรองรับเนื้อหาของข้อค้นพบครบหรือไม่"
              : "The link shows where the words are. Whether they support the whole finding was not checked in this analysis."
        }
      >
        {traceability.semanticSupport === "unassessed" && traceability.semanticReason
          ? traceability.semanticReason === "verifier_unavailable"
            ? thai
              ? "ตัวตรวจอัตโนมัติไม่พร้อมใช้งาน ยังไม่ได้ตรวจ"
              : "Source check unavailable. Not assessed."
            : thai
              ? "ตรวจการรองรับไม่ได้ จึงไม่ได้นำไปใช้ในการสรุป"
              : "Support could not be assessed, so it was left out of the summary."
          : SEMANTIC_LABELS[language][traceability.semanticSupport]}
      </p>
    </div>
  );
}
