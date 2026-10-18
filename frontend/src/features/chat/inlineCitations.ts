const INLINE_CITATION_RE =
  /\s*\[\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+)(?:\s*[,;]\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+))*\s*\]/gi;

export function stripInlineCitations(text: string): string {
  if (!text) return "";
  return text
    .replace(INLINE_CITATION_RE, "")
    .replace(/ +/g, " ")
    .replace(/ ([.,;:!?])/g, "$1")
    .trim();
}
