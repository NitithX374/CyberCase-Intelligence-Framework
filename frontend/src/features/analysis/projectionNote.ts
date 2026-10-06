import type { CaseProjectionGrounding } from "@/lib/api/types";
import { hasThai } from "@/lib/language";
import { supportNote, type SupportStatus } from "./supportNote";

const NOTES = {
  english: {
    not_supported: "The linked findings do not support this description.",
    unassessed: "Support for this description has not been assessed.",
  },
  thai: {
    not_supported: "ข้อสังเกตที่เชื่อมไว้ไม่สนับสนุนข้อมูลนี้",
    unassessed: "ยังไม่ได้ประเมินว่าข้อสังเกตที่เชื่อมไว้สนับสนุนข้อมูลนี้หรือไม่",
  },
};

export function projectionNote(
  support: SupportStatus | null | undefined,
  grounding: CaseProjectionGrounding | null | undefined,
  writtenText: string,
): string | null {
  const binding = supportNote(support, writtenText);
  if (!grounding || grounding.verdict === "supported") return binding;
  const semantic = NOTES[hasThai(writtenText) ? "thai" : "english"][grounding.verdict];
  return [binding, semantic].filter(Boolean).join(" ");
}
