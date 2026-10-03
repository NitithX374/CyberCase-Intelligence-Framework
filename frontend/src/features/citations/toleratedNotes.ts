import { hasThai } from "@/lib/language";

export interface ToleratedDifference {
  written: string;
  source: string;
}

const ENGLISH_LEAD = "Found in the source when formatting is ignored.";
const THAI_LEAD = "พบในเอกสารเมื่อไม่นับรูปแบบ";

function englishNote({ written, source }: ToleratedDifference): string {
  if (written && source) {
    return `${ENGLISH_LEAD} The analysis wrote «${written}»; the source says «${source}».`;
  }
  if (written) return `${ENGLISH_LEAD} The analysis adds «${written}».`;
  return `${ENGLISH_LEAD} The source has «${source}», which the analysis leaves out.`;
}

function thaiNote({ written, source }: ToleratedDifference): string {
  if (written && source) {
    return `${THAI_LEAD} — ข้อความวิเคราะห์เขียน «${written}» เอกสารเขียน «${source}»`;
  }
  if (written) return `${THAI_LEAD} — ข้อความวิเคราะห์เติม «${written}»`;
  return `${THAI_LEAD} — เอกสารมี «${source}» ที่ข้อความวิเคราะห์ตัดออก`;
}

export function toleratedNotes(
  differences: ToleratedDifference[] | undefined,
  writtenText: string,
): string[] {
  const note = hasThai(writtenText) ? thaiNote : englishNote;
  return (differences ?? []).map(note);
}
