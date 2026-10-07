import { hasThai } from "@/lib/language";
import type { FindingTraceabilityData } from "./findingTraceabilityData";

const SEMANTIC_LABELS = {
  english: {
    supported: "NLI: Source passages support this finding",
    not_supported: "NLI: Source support not established — withheld from Judgement",
    unassessed: "Meaning support not assessed",
  },
  thai: {
    supported: "NLI: ข้อความ Source รองรับ Finding",
    not_supported: "NLI: Source ไม่รองรับ Finding — ไม่ส่งเข้า Judgement",
    unassessed: "ยังไม่ได้ตรวจการรองรับทางความหมาย",
  },
};

const SEMANTIC_REASONS = {
  english: {
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
  const linked = traceability.direct + traceability.recovered + traceability.legacy;
  const descriptions = [
    {
      count: traceability.direct,
      label: thai
        ? `เชื่อม Source โดยตรง ${traceability.direct} ข้อความ`
        : `${traceability.direct} directly linked passage${traceability.direct === 1 ? "" : "s"}`,
    },
    {
      count: traceability.recovered,
      label: thai
        ? `ค้นคืนตำแหน่งใน Source ${traceability.recovered} ข้อความ`
        : `${traceability.recovered} recovered passage${traceability.recovered === 1 ? "" : "s"}`,
    },
    {
      count: traceability.legacy,
      label: thai
        ? `การอ้างอิงแบบเดิม ${traceability.legacy} ข้อความ`
        : `${traceability.legacy} legacy citation${traceability.legacy === 1 ? "" : "s"}`,
    },
    {
      count: traceability.unresolved,
      label: thai
        ? `เชื่อมตำแหน่งใน Source ไม่ได้ ${traceability.unresolved} รายการ`
        : `${traceability.unresolved} unresolved reference${traceability.unresolved === 1 ? "" : "s"}`,
    },
  ];
  return (
    <div className="mt-3 space-y-1 text-xs leading-5" aria-label="Finding traceability">
      <div className="flex flex-wrap gap-x-3 gap-y-1 text-ink-secondary">
        <span className="font-medium">{thai ? "การเชื่อม Source" : "Source linkage"}</span>
        {linked === 0 && (
          <span className="text-unresolved">
            {thai
              ? "ไม่มีข้อความ Source สนับสนุนที่เชื่อมไว้"
              : "No linked supporting Source passage"}
          </span>
        )}
        {descriptions
          .filter(({ count }) => count > 0)
          .map(({ label }) => (
            <span key={label}>{label}</span>
          ))}
      </div>
      <p
        className="text-ink-muted"
        title={
          traceability.semanticReason
            ? SEMANTIC_REASONS[language][traceability.semanticReason]
            : thai
              ? "การเชื่อม Source ระบุตำแหน่งข้อความอ้างอิง ผลวิเคราะห์นี้ยังไม่มีการตรวจว่าข้อความเหล่านั้นรองรับเนื้อหาของ Finding ครบหรือไม่"
              : "Source linkage locates cited text. This analysis has no recorded check that the cited passages support the complete finding."
        }
      >
        {traceability.semanticSupport === "unassessed" && traceability.semanticReason
          ? thai
            ? "ตรวจการรองรับไม่ได้ — ไม่ส่งเข้า Judgement"
            : "Support could not be assessed — withheld from Judgement"
          : SEMANTIC_LABELS[language][traceability.semanticSupport]}
      </p>
    </div>
  );
}
