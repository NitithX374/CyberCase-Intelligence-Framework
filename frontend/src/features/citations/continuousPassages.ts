import { citedSourcePassages } from "./groupSourceRefs";
import type { CitedSourcePassage, SourceMessageRef } from "./types";

function located(passage: CitedSourcePassage): boolean {
  return (
    passage.start !== null &&
    passage.end !== null &&
    passage.end - passage.start === Array.from(passage.quote).length
  );
}

export function continuousPassages(source: SourceMessageRef): CitedSourcePassage[] {
  const passages = [...citedSourcePassages(source)];
  if (passages.every(located)) passages.sort((a, b) => a.start! - b.start!);
  const result: CitedSourcePassage[] = [];
  for (const passage of passages) {
    const previous = result.at(-1);
    if (
      previous &&
      located(previous) &&
      located(passage) &&
      previous.end === passage.start &&
      previous.pointerState === passage.pointerState
    ) {
      result[result.length - 1] = {
        ...previous,
        quote: previous.quote + passage.quote,
        end: passage.end,
        context: {
          before: previous.context?.before ?? "",
          cutBefore: previous.context?.cutBefore ?? false,
          after: passage.context?.after ?? "",
          cutAfter: passage.context?.cutAfter ?? false,
        },
        notes: [...new Set([...previous.notes, ...passage.notes])],
      };
    } else {
      result.push(passage);
    }
  }
  return result;
}
