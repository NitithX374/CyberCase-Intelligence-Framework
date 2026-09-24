import type { CaseAnalysisResultRead } from "@/lib/api";
import { asArray, asRecord, asString } from "@/lib/parse";

export interface LegalProvision {
  citation: string;
  title: string;
  text: string;
  url: string;
}

export interface LegalReference {
  provisions: LegalProvision[];
  provider: string;
  querySent: string;
  degraded: string;
  disclaimer: string;
}

export const LEGAL_DISCLAIMER =
  "รายการอ้างอิงตัวบทที่อาจเกี่ยวข้อง จากบริการภายนอก " +
  "ไม่ใช่การเสนอข้อหาหรือความเห็นทางกฎหมาย " +
  "ผู้ใช้ต้องตรวจสอบตัวบทและความเกี่ยวข้องเองก่อนนำไปใช้";

export function readLegalReference(result: CaseAnalysisResultRead): LegalReference | null {
  const record = asRecord(result.external_context_json?.legal_relevance);
  if (!record) return null;
  return {
    provisions: asArray(record.provisions).flatMap(provision),
    provider: asString(record.provider),
    querySent: asString(record.query_sent),
    degraded: asString(record.degraded),
    disclaimer: asString(record.disclaimer) || LEGAL_DISCLAIMER,
  };
}

export function legalLookupSkipped(result: CaseAnalysisResultRead): boolean {
  const augmentation = asRecord(result.external_context_json?.technical_augmentation);
  return asString(augmentation?.status) === "not_applicable";
}

function provision(value: unknown): LegalProvision[] {
  const row = asRecord(value);
  const citation = asString(row?.citation);
  const text = asString(row?.text);
  if (!citation && !text) return [];
  const url = asString(row?.url);
  return [
    {
      citation,
      title: asString(row?.title),
      text,
      url: /^https?:\/\//i.test(url) ? url : "",
    },
  ];
}
