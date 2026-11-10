import { hasThai } from "@/lib/language";

type SupportStatus = "bound" | "mixed" | "unbound" | "no_claim";

type Note = Exclude<SupportStatus, "bound">;

const NOTES: Record<"english" | "thai", Record<Note, string>> = {
  english: {
    unbound: "None of the findings behind this sentence has a located passage.",
    mixed: "Only some findings behind this sentence have a located passage.",
    no_claim: "Not linked to any finding.",
  },
  thai: {
    unbound: "ยังระบุตำแหน่งข้อความอ้างอิงใน Source ของข้อค้นพบที่เชื่อมไว้ไม่ได้",
    mixed: "ระบุตำแหน่งข้อความอ้างอิงใน Source ได้สำหรับข้อค้นพบที่เชื่อมไว้บางข้อ",
    no_claim: "ไม่ได้เชื่อมกับข้อค้นพบใด",
  },
};

const FLAGGED_NOTE = {
  english:
    "A finding behind this sentence was not clearly supported by its cited Source. Check it before relying on the sentence.",
  thai: "Source ที่อ้างไม่ชัดว่ารองรับข้อค้นพบอย่างน้อยหนึ่งข้อที่ประโยคนี้อิงอยู่ ควรตรวจกับต้นฉบับก่อนใช้",
};

export function supportNote(
  support: SupportStatus | null | undefined,
  writtenText: string,
  flagged = false,
): string | null {
  const language = hasThai(writtenText) ? "thai" : "english";
  const notes = [
    support && support !== "bound" ? NOTES[language][support] : null,
    flagged ? FLAGGED_NOTE[language] : null,
  ].filter((note) => note !== null);
  return notes.length > 0 ? notes.join(" ") : null;
}
