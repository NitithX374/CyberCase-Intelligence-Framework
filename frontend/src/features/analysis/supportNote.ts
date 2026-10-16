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

export function supportNote(
  support: SupportStatus | null | undefined,
  writtenText: string,
): string | null {
  if (!support || support === "bound") return null;
  return NOTES[hasThai(writtenText) ? "thai" : "english"][support];
}
