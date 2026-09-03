import type { PersistedChatMessage } from "@/lib/api";
import { getCaseEvidencePresentation } from "@/lib/case-evidence";
import type {
  AnalysisEvidenceCitation,
  EvidencePage,
  SourceMessageRef,
} from "@/lib/case-overview-contracts";
import { sha256Hex } from "@/lib/sha256";

interface PageSpan {
  pageNumber: number;
  start: number;
  end: number;
}

export function mapSourceMessageIds(
  sourceIds: string[],
  messages: PersistedChatMessage[],
  citations: AnalysisEvidenceCitation[] = [],
): SourceMessageRef[] {
  const messageMap = new Map(messages.map((message) => [message.id, message]));
  const citationsBySource = new Map<string, AnalysisEvidenceCitation[]>();
  for (const citation of citations) {
    const matches = citationsBySource.get(citation.sourceMessageId) ?? [];
    matches.push(citation);
    citationsBySource.set(citation.sourceMessageId, matches);
  }

  const refs = sourceIds.flatMap((id) => {
    const message = messageMap.get(id);
    if (!message || !getCaseEvidencePresentation(message)) return [];
    const matches = citationsBySource.get(id) ?? [null];
    return matches.map((citation) => buildSourceMessageRef(message, citation));
  });
  const unique = new Map<string, SourceMessageRef>();
  for (const ref of refs) {
    const key = [ref.id, ref.exactQuote ?? "", ref.pageNumbers.join(",")].join(":");
    if (!unique.has(key)) unique.set(key, ref);
  }
  return [...unique.values()];
}

export function parseEvidenceCitations(value: unknown): AnalysisEvidenceCitation[] {
  return asArray(value).flatMap((item) => {
    const citation = asRecord(item);
    if (!citation) return [];
    const sourceMessageId = asString(citation.source_message_id);
    const exactQuote = asString(citation.exact_quote);
    if (!sourceMessageId || !exactQuote) return [];
    const rawPages = asArray(citation.page_numbers);
    const pageNumbers = rawPages.every(isPositiveInteger) && rawPages.length <= 8
      ? rawPages as number[]
      : [];
    return [{
      sourceMessageId,
      exactQuote,
      documentId: asString(citation.document_id) || null,
      filename: asString(citation.filename) || null,
      pageNumbers,
    }];
  });
}

export function formatPageReference(pageNumbers: number[]): string {
  if (pageNumbers.length === 1) return `p. ${pageNumbers[0]}`;
  return `pp. ${formatPageList(pageNumbers)}`;
}

export function formatEvidenceCitationText(
  sourceRef: Pick<SourceMessageRef, "label" | "pageNumbers" | "sourceType">,
): string {
  if (sourceRef.pageNumbers.length > 0) return formatPageReference(sourceRef.pageNumbers);
  if (sourceRef.sourceType === "case_description") return "Case narrative";
  if (sourceRef.sourceType === "clarification_response") return "Clarification";
  if (sourceRef.sourceType === "additional_info") return "Added information";
  return sourceRef.label;
}

function buildSourceMessageRef(
  message: PersistedChatMessage,
  citation: AnalysisEvidenceCitation | null,
): SourceMessageRef {
  const presentation = getCaseEvidencePresentation(message);
  if (!presentation) throw new Error("Source message is not authoritative case evidence");
  const usableCitation = citation && message.content.includes(citation.exactQuote)
    ? citation
    : null;
  const evidencePages = usableCitation
    ? resolvePageCitation(message, usableCitation)
    : null;
  const pageLabel = evidencePages && usableCitation
    ? `${usableCitation.filename} · ${formatPageReference(usableCitation.pageNumbers)}`
    : null;
  const hasDocumentSource = asArray(message.metadata_json.document_sources).length > 0;
  const narrativeLabel = hasDocumentSource
    ? "Reviewed case narrative"
    : presentation.kind === "initial_case_narrative"
      ? "Case narrative"
      : presentation.overviewSourceLabel;

  return {
    id: message.id,
    ordinal: message.ordinal,
    label: pageLabel ?? narrativeLabel,
    excerpt: message.content.length > 120
      ? `${message.content.slice(0, 120)}…`
      : message.content,
    sourceType: presentation.sourceType,
    sourceTypeLabel: pageLabel
      ? `${pageLabel} · Document location`
      : hasDocumentSource
        ? "Reviewed case narrative · ข้อความจากเอกสารที่ผู้ใช้ตรวจทาน"
        : presentation.sourceTypeLabel,
    fullContent: message.content,
    displayContent: evidencePages
      ? evidencePages.map((page) => page.text).join("\n\n")
      : contextualExcerpt(message.content, usableCitation?.exactQuote),
    exactQuote: usableCitation?.exactQuote ?? null,
    documentId: evidencePages ? usableCitation?.documentId ?? null : null,
    filename: evidencePages ? usableCitation?.filename ?? null : null,
    pageNumbers: evidencePages ? usableCitation?.pageNumbers ?? [] : [],
    evidencePages: evidencePages ?? [],
  };
}

function resolvePageCitation(
  message: PersistedChatMessage,
  citation: AnalysisEvidenceCitation,
): EvidencePage[] | null {
  if (!citation.documentId || !citation.filename || citation.pageNumbers.length === 0) {
    return null;
  }
  if (!isSortedUnique(citation.pageNumbers)) return null;
  const document = asArray(message.metadata_json.document_sources)
    .map(asRecord)
    .find((value) => (
      asString(value?.document_id) === citation.documentId &&
      asString(value?.filename) === citation.filename
    ));
  if (!document) return null;
  const spans = validPageSpans(document, message.content);
  const occurrences = quoteOccurrences(message.content, citation.exactQuote);
  if (occurrences.length === 0) return null;
  const occurrencePages = occurrences.map((start) => spans
    .filter((span) => span.start < start + citation.exactQuote.length && span.end > start)
    .map((span) => span.pageNumber));
  const occurrenceHasCompleteBounds = occurrences.every((start) => {
    const end = start + citation.exactQuote.length;
    return spans.some((span) => span.start <= start && start < span.end) &&
      spans.some((span) => span.start < end && end <= span.end);
  });
  if (!occurrenceHasCompleteBounds || occurrencePages.some((pages) => pages.length === 0)) return null;
  const uniqueOccurrencePages = new Set(occurrencePages.map((pages) => pages.join(",")));
  if (uniqueOccurrencePages.size !== 1 || !sameNumbers(occurrencePages[0], citation.pageNumbers)) {
    return null;
  }
  const quoteStart = occurrences[0];
  const quoteEnd = quoteStart + citation.exactQuote.length;
  const pages = citation.pageNumbers.map((pageNumber) => spans.find(
    (span) => span.pageNumber === pageNumber,
  ));
  if (pages.some((page) => page === undefined)) return null;
  return pages.map((span) => {
    const page = span as PageSpan;
    const highlightStart = Math.max(page.start, quoteStart);
    const highlightEnd = Math.min(page.end, quoteEnd);
    return {
      pageNumber: page.pageNumber,
      text: message.content.slice(page.start, page.end),
      exactQuote: highlightStart < highlightEnd
        ? message.content.slice(highlightStart, highlightEnd)
        : null,
    };
  });
}

function validPageSpans(document: Record<string, unknown>, content: string): PageSpan[] {
  const spans: PageSpan[] = [];
  const seenPages = new Set<number>();
  let previousEnd = 0;
  for (const item of asArray(document.page_spans)) {
    const span = asRecord(item);
    if (!span) break;
    const pageNumber = span.page_number;
    const start = span.start_offset;
    const end = span.end_offset;
    const expectedHash = asString(span.text_sha256).toLowerCase();
    if (!isPositiveInteger(pageNumber) || !isInteger(start) || !isInteger(end)) break;
    if (start < 0 || end > content.length || start >= end || seenPages.has(pageNumber)) break;
    if (start < previousEnd || !/^[0-9a-f]{64}$/.test(expectedHash)) break;
    if (sha256Hex(content.slice(start, end)) !== expectedHash) break;
    seenPages.add(pageNumber);
    previousEnd = end;
    spans.push({ pageNumber, start, end });
  }
  return spans;
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
  const quoteStart = content.indexOf(exactQuote);
  if (quoteStart < 0) return content.length > 640 ? `${content.slice(0, 640)}…` : content;
  const start = Math.max(0, quoteStart - 220);
  const end = Math.min(content.length, quoteStart + exactQuote.length + 220);
  return `${start > 0 ? "…" : ""}${content.slice(start, end)}${end < content.length ? "…" : ""}`;
}

function formatPageList(pageNumbers: number[]): string {
  const consecutive = pageNumbers.every(
    (page, index) => index === 0 || page === pageNumbers[index - 1] + 1,
  );
  return consecutive
    ? `${pageNumbers[0]}–${pageNumbers[pageNumbers.length - 1]}`
    : pageNumbers.join(", ");
}

function sameNumbers(left: number[], right: number[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function isSortedUnique(values: number[]): boolean {
  return values.length > 0 && values.every(
    (value, index) => index === 0 || value > values[index - 1],
  );
}

function isInteger(value: unknown): value is number {
  return Number.isInteger(value);
}

function isPositiveInteger(value: unknown): value is number {
  return isInteger(value) && value > 0;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null;
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}
