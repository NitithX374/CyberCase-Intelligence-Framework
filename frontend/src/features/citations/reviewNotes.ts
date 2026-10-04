import { hasThai } from "@/lib/language";

export interface ReviewFlag {
  kind: string;
  verdict: string;
  detail: string;
}

type Place = "edge" | "ignored";

const NOTES: Record<"english" | "thai", Record<Place, (marks: string) => string>> = {
  english: {
    edge: (marks) =>
      `Check: the source has the mark ${marks} next to the quote, which the quote leaves out.`,
    ignored: (marks) =>
      `Check: the quote and the source differ at the mark ${marks}, which may change the meaning.`,
  },
  thai: {
    edge: (marks) => `ตรวจ: ต้นฉบับมีเครื่องหมาย ${marks} ที่ quote ไม่ได้รวมไว้`,
    ignored: (marks) =>
      `ตรวจ: ต้นฉบับกับ quote ต่างกันที่เครื่องหมาย ${marks} ซึ่งอาจเปลี่ยนความหมาย`,
  },
};

export function reviewNotes(flags: ReviewFlag[] | undefined, writtenText: string): string[] {
  const notes = NOTES[hasThai(writtenText) ? "thai" : "english"];
  return (flags ?? []).flatMap((flag) => {
    const words = flag.detail.trim().split(/\s+/);
    const place = words[words.length - 1];
    if (flag.kind !== "meaning_mark" || words.length < 2) return [];
    if (place !== "edge" && place !== "ignored") return [];
    return [notes[place](words.slice(0, -1).join(" "))];
  });
}
