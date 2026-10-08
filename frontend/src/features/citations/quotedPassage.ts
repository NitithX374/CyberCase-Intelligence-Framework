import type { QuoteContext } from "./types";

const OCR_MARKUP =
  /<page_number>[^<]*<\/page_number>|<\/?(?:table|thead|tbody|tfoot|tr|th|td|caption|br)\b[^<>]*>/gi;
const CELL_BOUNDARY = /<\/(?:td|th)\s*>\s*<(?:td|th)\b[^<>]*>/gi;
const ROW_BOUNDARY = /<\/tr\s*>|<br\b[^<>]*>/gi;

export interface QuotedPassage {
  before: string;
  quote: string;
  after: string;
}

export function readable(text: string): string {
  return text
    .replace(CELL_BOUNDARY, " | ")
    .replace(ROW_BOUNDARY, "\n")
    .replace(OCR_MARKUP, "")
    .replace(/[^\S\r\n]+/g, " ")
    .replace(/ *\r?\n */g, "\n")
    .replace(/\n{3,}/g, "\n\n");
}

export function quotedPassage(quote: string, context: QuoteContext | null): QuotedPassage {
  const shown = readable(quote).trim();
  const before = readable(context?.before ?? "").trimStart();
  const after = readable(context?.after ?? "").trimEnd();
  if (!before && !after) return { before: "", quote: shown, after: "" };
  return {
    before: `${context?.cutBefore ? "… " : ""}${before}`,
    quote: shown,
    after: `${after}${context?.cutAfter ? " …" : ""}`,
  };
}
