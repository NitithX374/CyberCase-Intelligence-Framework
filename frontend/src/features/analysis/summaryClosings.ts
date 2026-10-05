const CLAIM_IDS = /\[\s*(A-\d{2,}(?:\s*,\s*A-\d{2,})*)\s*\]/g;
const SEPARATORS = new Set(Array.from(" \t\r\n.,;:!?…。、！？；：，．"));
const PUNCTUATION = new Set(Array.from(".,;:!?…。、！？；：，．"));

function withoutLeading(text: string, characters: Set<string>): string {
  let at = 0;
  const all = Array.from(text);
  while (at < all.length && characters.has(all[at])) at += 1;
  return all.slice(at).join("");
}

function punctuation(run: string): string {
  return Array.from(run)
    .filter((character) => PUNCTUATION.has(character))
    .join("");
}

export function summaryClosings(summary: string): string[] {
  const closings: string[] = [];
  let start = 0;
  for (const match of summary.matchAll(CLAIM_IDS)) {
    const gap = summary.slice(start, match.index);
    const text = start ? withoutLeading(gap, SEPARATORS) : gap.trimStart();
    if (closings.length && start) {
      closings[closings.length - 1] = punctuation(gap.slice(0, gap.length - text.length));
    }
    start = match.index + match[0].length;
    if (text.trimEnd()) closings.push("");
    else if (closings.length) closings[closings.length - 1] = "";
  }
  if (!start) return summary.trim() ? [""] : [];
  const rest = summary.slice(start);
  const tail = withoutLeading(rest, SEPARATORS);
  if (closings.length) {
    closings[closings.length - 1] = punctuation(rest.slice(0, rest.length - tail.length));
  }
  if (tail.trimEnd()) closings.push("");
  return closings;
}

export function noteLetter(index: number): string {
  let letters = "";
  let rest = index + 1;
  while (rest) {
    const remainder = (rest - 1) % 26;
    letters = String.fromCharCode(97 + remainder) + letters;
    rest = Math.floor((rest - 1) / 26);
  }
  return letters;
}
