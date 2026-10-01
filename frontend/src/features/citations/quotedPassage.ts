import type { QuoteContext } from "./types";

const OCR_MARKUP =
  /<page_number>[^<]*<\/page_number>|<\/?(?:table|thead|tbody|tfoot|tr|th|td|caption|br)\b[^<>]*>/gi;

export interface QuotedPassage {
  before: string;
  quote: string;
  after: string;
}

export function readable(text: string): string {
  return text.replace(OCR_MARKUP, " ").replace(/\s+/g, " ");
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
