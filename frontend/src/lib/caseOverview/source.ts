import type { CaseSourceRead } from "@/lib/api";
import type { SourcePage, SourceMessageRef, CaseCitation, CaseSourceRef } from "./types";

export function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

export function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export function asString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

export function asStringArray(value: unknown): string[] {
  return asArray(value).map(asString).filter(Boolean);
}

export function formatPageReference(pageNumbers: number[]): string {
  if (pageNumbers.length === 1) return `p. ${pageNumbers[0]}`;
  return `pp. ${formatPageList(pageNumbers)}`;
}

export function formatSourceCitationText(
  sourceRef: Pick<SourceMessageRef, "label" | "pageNumbers" | "sourceType" | "isNativeSource">,
): string {
  if (sourceRef.isNativeSource) return sourceRef.label;
  if (sourceRef.pageNumbers.length > 0) return formatPageReference(sourceRef.pageNumbers);
  if (sourceRef.sourceType === "case_description") return "Case narrative";
  if (sourceRef.sourceType === "followup_response") return "Follow-up answer";
  return sourceRef.label;
}

export function parseCaseSources(rows: CaseSourceRead[]): CaseSourceRef[] {
  const refs = rows.map((row, index) => parseSourceRow(row, index + 1));
  if (new Set(refs.map((ref) => ref.id)).size !== refs.length) {
    throw new Error("The case has duplicate source IDs.");
  }
  return refs;
}

function parseSourceRow(source: CaseSourceRead, ordinal: number): CaseSourceRef {
  const metadata = asRecord(source.source_metadata_json) ?? {};
  const provenance = asRecord(source.provenance_json) ?? {};
  if (!source.id || !source.source_kind || !source.exact_text.trim()) {
    throw new Error("Case source binding is incomplete.");
  }
  return {
    id: source.id,
    kind: source.source_kind,
    ordinal,
    text: source.exact_text,
    provenance,
    documentId: source.document_id || asString(metadata.document_id) || null,
    filename: asString(metadata.filename) || asString(provenance.filename) || null,
  };
}

export function parseCaseCitations(
  value: unknown,
  sourceIds: string[],
  sources: CaseSourceRef[],
): CaseCitation[] {
  return asArray(value).flatMap((item) => {
    const citation = asRecord(item);
    const rawPages = asArray(citation?.page_numbers);
    const parsedPages =
      rawPages.every(isPositiveInteger) &&
      rawPages.length <= 8 &&
      new Set(rawPages).size === rawPages.length
        ? rawPages
        : [];
    const sourceId = asString(citation?.source_id);
    const exactQuote = typeof citation?.exact_quote === "string" ? citation.exact_quote : "";
    if (!sourceIds.includes(sourceId) || !exactQuote || exactQuote.trim() !== exactQuote) {
      return [];
    }
    const source = sources.find((candidate) => candidate.id === sourceId);
    if (!source) {
      return [];
    }
    const occurrences = quoteOccurrences(source.text, exactQuote);
    if (occurrences.length === 0) {
      return [];
    }
    const parsed: CaseCitation = {
      sourceId,
      exactQuote,
      documentId: asString(citation?.document_id) || null,
      filename: asString(citation?.filename) || null,
      pageNumbers: parsedPages,
    };
    if (
      occurrences.length > 1 &&
      (!parsed.pageNumbers.length || !resolvePageBinding(source, parsed))
    ) {
      return [
        {
          ...parsed,
          pageNumbers: [],
        },
      ];
    }
    return [parsed];
  });
}

export function sourceRefs(
  ids: string[],
  citations: CaseCitation[],
  sources: CaseSourceRef[],
): SourceMessageRef[] {
  return ids.flatMap((id) => {
    const source = sources.find((candidate) => candidate.id === id);
    if (!source) return [];
    const matches = citations.filter((citation) => citation.sourceId === id);
    return matches.length
      ? matches.map((citation) => buildSourceRef(source, citation))
      : [buildSourceRef(source, null)];
  });
}

function buildSourceRef(source: CaseSourceRef, citation: CaseCitation | null): SourceMessageRef {
  const pageBinding = citation ? resolvePageBinding(source, citation) : null;
  const sourceType = sourceTypeFor(source.kind);
  // What a reader can recognise: the file it came from, or where it sits in
  // the case. A source id is a UUID and says nothing to anyone.
  const identity = source.filename ?? `${sourceTypeLabel(sourceType)} #${source.ordinal}`;
  const label = pageBinding
    ? `${identity} · ${formatPageReference(pageBinding.pageNumbers)}`
    : identity;
  return {
    id: source.id,
    ordinal: source.ordinal,
    label,
    excerpt: source.text.length > 120 ? `${source.text.slice(0, 120)}…` : source.text,
    sourceType,
    sourceTypeLabel: identity,
    fullContent: source.text,
    displayContent: pageBinding
      ? pageBinding.pages.map((page) => page.text).join("\n\n")
      : contextualExcerpt(source.text, citation?.exactQuote),
    exactQuote: citation?.exactQuote ?? null,
    documentId: source.documentId,
    filename: source.filename,
    pageNumbers: pageBinding?.pageNumbers ?? [],
    sourcePages: pageBinding?.pages ?? [],
    isNativeSource: true,
  };
}

interface CasePageBinding {
  pages: SourcePage[];
  pageNumbers: number[];
}

function resolvePageBinding(source: CaseSourceRef, citation: CaseCitation): CasePageBinding | null {
  if (!citation.documentId || !citation.filename || citation.pageNumbers.length === 0) return null;
  if (source.documentId !== citation.documentId || source.filename !== citation.filename)
    return null;
  const spans = asArray(source.provenance.pages).flatMap((value, index, values) => {
    const span = asRecord(value);
    const pageNumber = span?.page_number;
    const start = span?.start_offset;
    const end = span?.end_offset;
    const previous = index > 0 ? asRecord(values[index - 1]) : null;
    const previousEnd = previous?.end_offset;
    const valid =
      isInteger(pageNumber) &&
      isInteger(start) &&
      isInteger(end) &&
      end > start &&
      start >= 0 &&
      end <= source.text.length &&
      (!isInteger(previousEnd) || start >= previousEnd);
    return valid ? [{ pageNumber, start, end }] : [];
  });
  const occurrences = quoteOccurrences(source.text, citation.exactQuote);
  const pageSets = occurrences.map((start) =>
    spans
      .filter((span) => span.start < start + citation.exactQuote.length && span.end > start)
      .map((span) => span.pageNumber),
  );
  if (
    !pageSets.every((pages) => pages.length > 0 && sameNumbers(pages, citation.pageNumbers)) ||
    new Set(pageSets.map((pages) => pages.join(","))).size !== 1
  )
    return null;
  const start = occurrences[0];
  const end = start + citation.exactQuote.length;
  if (
    !spans.some((span) => span.start <= start && start < span.end) ||
    !spans.some((span) => span.start < end && end <= span.end)
  )
    return null;
  const pages = citation.pageNumbers.map((pageNumber) =>
    spans.find((span) => span.pageNumber === pageNumber),
  );
  if (pages.some((page) => !page)) return null;
  return {
    pageNumbers: citation.pageNumbers,
    pages: pages.map((page) => ({
      pageNumber: page!.pageNumber,
      text: source.text.slice(page!.start, page!.end),
      exactQuote: source.text.slice(Math.max(page!.start, start), Math.min(page!.end, end)),
    })),
  };
}

function sourceTypeFor(kind: string): SourceMessageRef["sourceType"] {
  if (kind === "followup_answer") return "followup_response";
  if (kind === "narrative" || kind === "document") return "case_description";
  throw new Error("Unsupported native source kind.");
}

function sourceTypeLabel(type: SourceMessageRef["sourceType"]): string {
  if (type === "followup_response") return "Follow-up answer";
  return "Case narrative";
}

function quoteOccurrences(content: string, quote: string): number[] {
  const occurrences: number[] = [];
  let start = content.indexOf(quote);
  while (start >= 0) {
    occurrences.push(start);
    start = content.indexOf(quote, start + 1);
  }
  return occurrences;
}

function contextualExcerpt(content: string, exactQuote?: string): string {
  if (!exactQuote) return content.length > 640 ? `${content.slice(0, 640)}…` : content;
  const start = content.indexOf(exactQuote);
  if (start < 0) return content.length > 640 ? `${content.slice(0, 640)}…` : content;
  const lower = Math.max(0, start - 220);
  const upper = Math.min(content.length, start + exactQuote.length + 220);
  return `${lower > 0 ? "…" : ""}${content.slice(lower, upper)}${upper < content.length ? "…" : ""}`;
}

function sameNumbers(left: number[], right: number[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function isInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value);
}

function isPositiveInteger(value: unknown): value is number {
  return isInteger(value) && value > 0;
}

function formatPageList(pageNumbers: number[]): string {
  const consecutive = pageNumbers.every(
    (page, index) => index === 0 || page === pageNumbers[index - 1] + 1,
  );
  return consecutive
    ? `${pageNumbers[0]}–${pageNumbers[pageNumbers.length - 1]}`
    : pageNumbers.join(", ");
}
