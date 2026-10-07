import type { CaseProjectionGrounding } from "@/lib/api/types";
import { hasThai } from "@/lib/language";

export type SupportStatus = "bound" | "mixed" | "unbound" | "no_claim";

type Note = Exclude<SupportStatus, "bound">;

const NOTES: Record<"english" | "thai", Record<Note, string>> = {
  english: {
    unbound: "None of the linked claims has a resolved source citation.",
    mixed: "Only some linked claims have resolved source citations.",
    no_claim: "Not linked to any claim.",
  },
  thai: {
    unbound: "ยังระบุตำแหน่งข้อความอ้างอิงใน Source ของข้อค้นพบที่เชื่อมไว้ไม่ได้",
    mixed: "ระบุตำแหน่งข้อความอ้างอิงใน Source ได้สำหรับข้อค้นพบที่เชื่อมไว้บางข้อ",
    no_claim: "ไม่ได้เชื่อมกับข้อสังเกตใด",
  },
};

const PROJECTION_GROUNDING_NOTES = {
  english: {
    not_supported: "The linked findings do not support this description.",
    unassessed: "Support for this description has not been assessed.",
  },
  thai: {
    not_supported: "ข้อสังเกตที่เชื่อมไว้ไม่สนับสนุนข้อมูลนี้",
    unassessed: "ยังไม่ได้ประเมินว่าข้อสังเกตที่เชื่อมไว้สนับสนุนข้อมูลนี้หรือไม่",
  },
};

export function supportNote(
  support: SupportStatus | null | undefined,
  writtenText: string,
): string | null {
  if (!support || support === "bound") return null;
  return NOTES[hasThai(writtenText) ? "thai" : "english"][support];
}

export function projectionNote(
  support: SupportStatus | null | undefined,
  grounding: CaseProjectionGrounding | null | undefined,
  writtenText: string,
): string | null {
  const binding = supportNote(support, writtenText);
  if (!grounding || grounding.verdict === "supported") return binding;
  const semantic = PROJECTION_GROUNDING_NOTES[hasThai(writtenText) ? "thai" : "english"][grounding.verdict];
  return [binding, semantic].filter(Boolean).join(" ");
}
