import type { CaseEvidenceSnapshotRead } from "@/lib/api";
import { asArray, asRecord, asString } from "@/lib/case-overview-parsing";
import type { EvidencePage, SourceMessageRef } from "@/lib/case-overview-contracts";
import { formatPageReference } from "@/lib/evidence-citation";
import { sha256Hex } from "@/lib/sha256";

export interface NativeSnapshotSource {
  id: string;
  kind: string;
  revision: number;
  text: string;
  textSha256: string;
  provenance: Record<string, unknown>;
  documentId: string | null;
  filename: string | null;
}

export interface NativeCitation {
  sourceId: string;
  sourceRevision: number;
  exactQuote: string;
  documentId: string | null;
  filename: string | null;
  pageNumbers: number[];
}

interface NativePageBinding {
  pages: EvidencePage[];
  pageNumbers: number[];
}

export function parseNativeSnapshot(snapshot: CaseEvidenceSnapshotRead): NativeSnapshotSource[] {
  if (snapshot.format_version !== "case_evidence_snapshot_v1") throw new Error("Unsupported evidence snapshot format.");
  if (sha256Hex(snapshot.input_text) !== snapshot.text_sha256) throw new Error("Evidence snapshot text hash does not match.");
  if (!matchesManifestHash(snapshot.manifest_json, snapshot.manifest_sha256)) throw new Error("Evidence snapshot manifest hash does not match.");
  const sources = snapshot.manifest_json.map(parseSnapshotSource);
  if (!sources.length) throw new Error("Evidence snapshot has no admitted sources.");
  if (new Set(sources.map((source) => source.id)).size !== sources.length) throw new Error("Evidence snapshot has duplicate source IDs.");
  return sources;
}

function parseSnapshotSource(value: unknown): NativeSnapshotSource {
  const entry = asRecord(value);
  const id = asString(entry?.source_id);
  const kind = asString(entry?.source_kind);
  const revision = entry?.revision;
  const text = typeof entry?.exact_text === "string" ? entry.exact_text : "";
  const textSha256 = asString(entry?.text_sha256);
  const provenance = asRecord(entry?.provenance);
  if (!id || !kind || typeof revision !== "number" || !Number.isInteger(revision) || revision < 1 || !text || !/^[0-9a-f]{64}$/.test(textSha256) || !provenance) {
    throw new Error("Evidence snapshot source binding is incomplete.");
  }
  if (sha256Hex(text) !== textSha256) throw new Error("Evidence snapshot source hash does not match.");
  return {
    id,
    kind,
    revision,
    text,
    textSha256,
    provenance,
    documentId: asString(entry?.document_id) || null,
    filename: asString(entry?.filename) || null,
  };
}

export function parseNativeCitations(
  value: unknown,
  sourceIds: string[],
  sources: NativeSnapshotSource[],
): NativeCitation[] {
  return asArray(value).map((item) => {
    const citation = asRecord(item);
    const rawPages = asArray(citation?.page_numbers);
    if (!rawPages.every(isPositiveInteger) || rawPages.length > 8 || new Set(rawPages).size !== rawPages.length) {
      throw new Error("Analysis citation pages are invalid.");
    }
    const parsed = {
      sourceId: asString(citation?.source_id),
      sourceRevision: citation?.source_revision,
      exactQuote: typeof citation?.exact_quote === "string" ? citation.exact_quote : "",
      documentId: asString(citation?.document_id) || null,
      filename: asString(citation?.filename) || null,
      pageNumbers: rawPages,
    };
    if (!sourceIds.includes(parsed.sourceId) || !Number.isInteger(parsed.sourceRevision) || !parsed.exactQuote || parsed.exactQuote.trim() !== parsed.exactQuote) {
      throw new Error("Analysis citation is invalid.");
    }
    const source = sources.find((candidate) => candidate.id === parsed.sourceId);
    const occurrences = source ? quoteOccurrences(source.text, parsed.exactQuote) : [];
    if (!source || source.revision !== parsed.sourceRevision || occurrences.length === 0) {
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
  citations: NativeCitation[],
  sources: NativeSnapshotSource[],
): SourceMessageRef[] {
  return ids.flatMap((id) => {
    const source = sources.find((candidate) => candidate.id === id);
    if (!source) throw new Error("Analysis source reference is missing from the snapshot.");
    const matches = citations.filter((citation) => citation.sourceId === id);
    return matches.length ? matches.map((citation) => buildSourceRef(source, citation)) : [buildSourceRef(source, null)];
  });
}

function buildSourceRef(source: NativeSnapshotSource, citation: NativeCitation | null): SourceMessageRef {
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

function resolvePageBinding(source: NativeSnapshotSource, citation: NativeCitation): NativePageBinding | null {
  if (!citation.documentId || !citation.filename || citation.pageNumbers.length === 0) return null;
  if (source.documentId !== citation.documentId || source.filename !== citation.filename) return null;
  const spans = asArray(source.provenance.pages).flatMap((value, index, values) => {
    const span = asRecord(value);
    const pageNumber = span?.page_number;
    const start = span?.start_offset;
    const end = span?.end_offset;
    const hash = asString(span?.text_sha256);
    const previous = index > 0 ? asRecord(values[index - 1]) : null;
    const previousEnd = previous?.end_offset;
    const valid = isInteger(pageNumber) && isInteger(start) && isInteger(end) && end > start && start >= 0 && end <= source.text.length && (!isInteger(previousEnd) || start >= previousEnd) && /^[0-9a-f]{64}$/.test(hash) && sha256Hex(source.text.slice(start, end)) === hash;
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
  if (kind === "clarification_answer") return "clarification_response";
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

function matchesManifestHash(manifestJson: unknown, expectedHash: string): boolean {
  if (!/^[0-9a-f]{64}$/.test(expectedHash)) return false;
  return sha256Hex(canonicalJson(manifestJson, false)) === expectedHash || sha256Hex(canonicalJson(manifestJson, true)) === expectedHash;
}

function canonicalJson(value: unknown, formatFloatBbox = false, parentKey = ""): string {
  if (Array.isArray(value)) return `[${value.map((item) => canonicalJson(item, formatFloatBbox, parentKey)).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(record[key], formatFloatBbox, key)}`).join(",")}}`;
  }
  if (typeof value === "number") {
    if (formatFloatBbox && Number.isInteger(value) && (parentKey === "x0" || parentKey === "y0" || parentKey === "x1" || parentKey === "y1")) {
      return value.toFixed(1);
    }
    return JSON.stringify(value);
  }
  const serialized = JSON.stringify(value);
  if (serialized === undefined) throw new Error("Evidence snapshot contains an unsupported value.");
  return serialized;
}

