import type { CitedSourcePassage, SourceMessageRef } from "./types";

export function citedSourcePassages(source: SourceMessageRef): CitedSourcePassage[] {
  if (source.passages) return source.passages;
  if (!source.exactQuote) return [];
  return [
    {
      quote: source.exactQuote,
      context: source.quoteContext,
      pointerState: source.pointerState ?? "legacy",
      start: source.start ?? null,
      end: source.end ?? null,
      notes: [...(source.toleratedNotes ?? []), ...(source.reviewNotes ?? [])],
    },
  ];
}

export function groupSourceRefs(sources: SourceMessageRef[]): SourceMessageRef[] {
  const groups = new Map<
    string,
    { source: SourceMessageRef; passages: Map<string, CitedSourcePassage> }
  >();
  for (const source of sources) {
    const key = JSON.stringify([source.id, source.pageNumbers, source.label]);
    const group = groups.get(key) ?? { source, passages: new Map<string, CitedSourcePassage>() };
    for (const passage of citedSourcePassages(source)) {
      const location = JSON.stringify([passage.start, passage.end, passage.quote]);
      const previous = group.passages.get(location);
      group.passages.set(
        location,
        previous
          ? { ...previous, notes: [...new Set([...previous.notes, ...passage.notes])] }
          : passage,
      );
    }
    groups.set(key, group);
  }
  return Array.from(groups.values(), ({ source, passages }) => ({
    ...source,
    passages: [...passages.values()],
  }));
}
