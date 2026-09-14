import type { EvidenceSourceRead } from "@/lib/api";
import { asArray, asRecord, asString } from "@/lib/case-overview-parsing";
import type { EvidencePage, SourceMessageRef } from "@/lib/case-overview-contracts";
import { formatPageReference } from "@/lib/evidence-citation";

export interface CaseSnapshotSource {
  id: string;
  kind: string;
  revision: number;
  text: string;
  provenance: Record<string, unknown>;
  documentId: string | null;
  filename: string | null;
}

export interface CaseCitation {
  sourceId: string;
  sourceRevision: number;
  exactQuote: string;
  documentId: string | null;
  filename: string | null;
  pageNumbers: number[];
}

interface CasePageBinding {
  pages: EvidencePage[];
  pageNumbers: number[];
}

export function parseCaseSnapshot(snapshot: unknown): CaseSnapshotSource[] {
  if (Array.isArray(snapshot)) {
    return snapshot.map((item) => parseEvidenceSource(item as EvidenceSourceRead));
  }
  const record = asRecord(snapshot);
  const manifest = asArray(record?.manifest_json);
  if (manifest.length > 0) {
    const sources = manifest.map(parseSnapshotSource);
    if (new Set(sources.map((source) => source.id)).size !== sources.length) throw new Error("Evidence snapshot has duplicate source IDs.");
    return sources;
  }
  if (Array.isArray(record?.sources)) {
    return record.sources.map(parseSnapshotSource);
  }
  return [];
}

export function parseEvidenceSource(source: EvidenceSourceRead): CaseSnapshotSource {
  const document = (source as unknown as { document?: { filename?: string | null } }).document;
  return {
    id: source.id,
    kind: source.source_kind,
    revision: 1,
    text: source.exact_text || "",
    provenance: (source.provenance_json as Record<string, unknown>) || {},
    documentId: source.document_id || null,
    filename: document?.filename || null,
  };
}

function parseSnapshotSource(value: unknown): CaseSnapshotSource {
  const entry = asRecord(value);
  const id = asString(entry?.source_id ?? entry?.id);
  const kind = asString(entry?.source_kind ?? entry?.kind);
  const revision = typeof entry?.revision === "number" ? entry.revision : 1;
  const text = typeof entry?.exact_text === "string" ? entry.exact_text : (typeof entry?.text === "string" ? entry.text : "");
  const provenance = asRecord(entry?.provenance ?? entry?.provenance_json) ?? {};
  if (!id || !kind || !text) {
    throw new Error("Evidence snapshot source binding is incomplete.");
  }
  return {
    id,
    kind,
    revision,
    text,
    provenance,
    documentId: asString(entry?.document_id ?? entry?.documentId) || null,
    filename: asString(entry?.filename) || null,
  };
}

export function parseCaseCitations(
  value: unknown,
  sourceIds: string[],
  sources: CaseSnapshotSource[],
): CaseCitation[] {
  return asArray(value).map((item) => {
    const citation = asRecord(item);
    const rawPages = asArray(citation?.page_numbers);
    if (!rawPages.every(isPositiveInteger) || rawPages.length > 8 || new Set(rawPages).size !== rawPages.length) {
      throw new Error("Analysis citation pages are invalid.");
    }
    const parsed = {
      sourceId: asString(citation?.source_id),
      sourceRevision: typeof citation?.source_revision === "number" ? citation.source_revision : 1,
      exactQuote: typeof citation?.exact_quote === "string" ? citation.exact_quote : "",
      documentId: asString(citation?.document_id) || null,
      filename: asString(citation?.filename) || null,
      pageNumbers: rawPages,
    };
    if (!sourceIds.includes(parsed.sourceId) || !parsed.exactQuote || parsed.exactQuote.trim() !== parsed.exactQuote) {
      throw new Error("Analysis citation is invalid.");
    }
    const source = sources.find((candidate) => candidate.id === parsed.sourceId);
    const occurrences = source ? quoteOccurrences(source.text, parsed.exactQuote) : [];
    if (!source || occurrences.length === 0) {
      throw new Error("Analysis citation is not bound to the snapshot.");
    }
    const citationObj = { ...parsed, sourceRevision: parsed.sourceRevision as number };
    if (occurrences.length > 1 && (!parsed.pageNumbers.length || !resolvePageBinding(source, citationObj))) {
      throw new Error("Analysis citation is ambiguous in the snapshot.");
    }
    const hasLocator = parsed.documentId !== null || parsed.filename !== null || parsed.pageNumbers.length > 0;
    if (hasLocator && (!parsed.documentId || !parsed.filename || !parsed.pageNumbers.length)) {
      throw new Error("Analysis document citation is incomplete.");
    }
    return citationObj;
  });
}

export function sourceRefs(
  ids: string[],
  citations: CaseCitation[],
  sources: CaseSnapshotSource[],
): SourceMessageRef[] {
  return ids.flatMap((id) => {
    const source = sources.find((candidate) => candidate.id === id);
    if (!source) throw new Error("Analysis source reference is missing from the snapshot.");
    const matches = citations.filter((citation) => citation.sourceId === id);
    return matches.length ? matches.map((citation) => buildSourceRef(source, citation)) : [buildSourceRef(source, null)];
  });
}

function buildSourceRef(source: CaseSnapshotSource, citation: CaseCitation | null): SourceMessageRef {
  const pageBinding = citation ? resolvePageBinding(source, citation) : null;
  const sourceType = sourceTypeFor(source.kind);
  const documentLabel = source.filename ? `${source.filename} · ` : "";
  const label = pageBinding ? `${documentLabel}${formatPageReference(pageBinding.pageNumbers)}` : `${documentLabel}Source ${source.id} · revision ${source.revision}`;
  return {
    id: source.id,
    ordinal: source.revision,
    label,
    excerpt: source.text.length > 120 ? `${source.text.slice(0, 120)}…` : source.text,
    sourceType,
    sourceTypeLabel: `${sourceTypeLabel(sourceType)} · Source ${source.id} · revision ${source.revision}`,
    fullContent: source.text,
    displayContent: pageBinding ? pageBinding.pages.map((page) => page.text).join("\n\n") : contextualExcerpt(source.text, citation?.exactQuote),
    exactQuote: citation?.exactQuote ?? null,
    documentId: source.documentId,
    filename: source.filename,
    pageNumbers: pageBinding?.pageNumbers ?? [],
    evidencePages: pageBinding?.pages ?? [],
    isNativeEvidence: true,
  };
}

function resolvePageBinding(source: CaseSnapshotSource, citation: CaseCitation): CasePageBinding | null {
  if (!citation.documentId || !citation.filename || citation.pageNumbers.length === 0) return null;
  if (source.documentId !== citation.documentId || source.filename !== citation.filename) return null;
  const spans = asArray(source.provenance.pages).flatMap((value, index, values) => {
    const span = asRecord(value);
    const pageNumber = span?.page_number;
    const start = span?.start_offset;
    const end = span?.end_offset;
    const previous = index > 0 ? asRecord(values[index - 1]) : null;
    const previousEnd = previous?.end_offset;
    const valid = isInteger(pageNumber) && isInteger(start) && isInteger(end) && end > start && start >= 0 && end <= source.text.length && (!isInteger(previousEnd) || start >= previousEnd);
    return valid ? [{ pageNumber, start, end }] : [];
  });
  const occurrences = quoteOccurrences(source.text, citation.exactQuote);
  const pageSets = occurrences.map((start) => spans.filter((span) => span.start < start + citation.exactQuote.length && span.end > start).map((span) => span.pageNumber));
  if (!pageSets.every((pages) => pages.length > 0 && sameNumbers(pages, citation.pageNumbers)) || new Set(pageSets.map((pages) => pages.join(","))).size !== 1) return null;
  const start = occurrences[0];
  const end = start + citation.exactQuote.length;
  if (!spans.some((span) => span.start <= start && start < span.end) || !spans.some((span) => span.start < end && end <= span.end)) return null;
  const pages = citation.pageNumbers.map((pageNumber) => spans.find((span) => span.pageNumber === pageNumber));
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
  if (kind === "clarification_answer" || kind === "followup_answer") return "clarification_response";
  if (kind === "explicit_chat_addition") return "additional_info";
  if (kind === "narrative" || kind === "reviewed_document") return "case_description";
  throw new Error("Unsupported native evidence source kind.");
}

function sourceTypeLabel(type: SourceMessageRef["sourceType"]): string {
  if (type === "clarification_response") return "Clarification response";
  if (type === "additional_info") return "Additional case information";
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

__all_exports: ;
