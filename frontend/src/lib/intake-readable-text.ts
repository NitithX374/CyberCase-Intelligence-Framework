const entities: Record<string, string> = {
  amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ",
};

export function intakeReadableText(source: string): string {
  const decoded = source.replace(/&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi, (match, entity: string) => {
    if (!entity.startsWith("#")) return entities[entity.toLowerCase()] ?? match;
    const hex = entity[1].toLowerCase() === "x";
    const code = Number.parseInt(entity.slice(hex ? 2 : 1), hex ? 16 : 10);
    return code > 0 && code <= 0x10ffff && !(code >= 0xd800 && code <= 0xdfff)
      ? String.fromCodePoint(code)
      : match;
  });
  return decoded
    .replace(/<!--[^]*?-->/g, "")
    .replace(/<(script|style|iframe|object|template)\b[^>]*>[^]*?<\/\1\s*>/gi, "")
    .replace(/<\/(td|th)\s*>\s*<(td|th)\b[^>]*>/gi, " | ")
    .replace(/<\/tr\s*>\s*<tr\b[^>]*>/gi, "\n")
    .replace(/<\/?(?:table|thead|tbody|tfoot|tr|p|div|h[1-6]|ul|ol|li|blockquote)\b[^>]*>/gi, "\n")
    .replace(/<br\b[^>]*\/?\s*>/gi, "\n")
    .replace(/<\/?[a-z][^>]*>/gi, "")
    .replace(/\*\*([^]*?)\*\*/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
