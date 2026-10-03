import { hasThai } from "@/lib/language";

export type SupportStatus = "bound" | "mixed" | "unbound" | "no_claim";

type Note = Exclude<SupportStatus, "bound">;

const NOTES: Record<"english" | "thai", Record<Note, string>> = {
  english: {
    unbound: "No cited quotation was found in the sources.",
    mixed: "Some cited quotations were not found in the sources.",
    no_claim: "Not linked to any claim.",
  },
  thai: {
    unbound: "ไม่พบข้อความที่อ้างในเอกสาร",
    mixed: "ข้อความที่อ้างบางส่วนไม่พบในเอกสาร",
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
