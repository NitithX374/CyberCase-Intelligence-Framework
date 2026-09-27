import type { CaseAnalysisClaim, CaseSourceCitation, CaseSourceRead } from "@/lib/api/types";
import { asArray } from "@/lib/parse";
import type { CaseSourceRef, FollowupAnswer, SourceMessageRef, SourcePage } from "./types";

interface ProvenancePage {
  page_number: number;
  start_offset: number;
  end_offset: number;
}

export function formatPageReference(pageNumbers: number[]): string {
  if (pageNumbers.length === 1) return `p. ${pageNumbers[0]}`;
  return `pp. ${formatPageList(pageNumbers)}`;
}

export function parseCaseSources(
  rows: CaseSourceRead[],
  followups: FollowupAnswer[],
): CaseSourceRef[] {
  const counts = new Map<string, number>();
  const read = rows.map((row): CaseSourceRef => {
    const ordinal = (counts.get(row.source_kind) ?? 0) + 1;
    counts.set(row.source_kind, ordinal);
    return {
      id: row.id,
      kind: row.source_kind,
      ordinal,
      text: row.exact_text,
      pages: sourcePages(row),
      filename: row.filename ?? null,
      question: null,
    };
  });
  const answered = followups.map((followup, index): CaseSourceRef => ({
    id: followup.qaId,
    kind: "followup_answer",
    ordinal: index + 1,
    text: followup.answer,
    pages: [],
    filename: null,
    question: followup.question,
  }));
  return [...read, ...answered];
}

export function claimRefs(
  claim: Pick<
    CaseAnalysisClaim,
    | "supporting_source_ids"
    | "supporting_citations"
    | "contradicting_source_ids"
    | "contradicting_citations"
  >,
  sources: CaseSourceRef[],
): { supporting: SourceMessageRef[]; contradicting: SourceMessageRef[] } {
  return {
    supporting: refs(claim.supporting_source_ids, claim.supporting_citations, sources),
    contradicting: refs(claim.contradicting_source_ids, claim.contradicting_citations, sources),
  };
}

function refs(
  ids: string[] = [],
  citations: CaseSourceCitation[] = [],
  sources: CaseSourceRef[],
): SourceMessageRef[] {
  return ids.flatMap((id) => {
    const source = sources.find((candidate) => candidate.id === id);
    if (!source) return [];
    const cited = citations.filter((citation) => citation.source_id === id);
    return cited.length
      ? cited.map((citation) => sourceRef(source, citation))
      : [sourceRef(source, null)];
  });
}

function sourceRef(source: CaseSourceRef, citation: CaseSourceCitation | null): SourceMessageRef {
  const quote = citation?.exact_quote || null;
  const pages = (citation?.page_numbers ?? []).flatMap(
    (pageNumber) => source.pages.find((page) => page.pageNumber === pageNumber) ?? [],
  );
  const pageNumbers = pages.map((page) => page.pageNumber);
  const identity = sourceIdentity(source);
  return {
    id: source.id,
    label: pageNumbers.length ? `${identity} · ${formatPageReference(pageNumbers)}` : identity,
    excerpt: source.text.length > 120 ? `${source.text.slice(0, 120)}…` : source.text,
    displayContent: pages.length
      ? pages.map((page) => page.text).join("\n\n")
      : contextualExcerpt(source.text, quote),
    exactQuote: quote,
    filename: source.filename,
    pageNumbers,
    sourcePages: pages,
    question: source.question,
  };
}

function sourceIdentity(source: CaseSourceRef): string {
  if (source.filename) return source.filename;
  if (source.kind === "followup_answer") return `Follow-up answer ${source.id}`;
  return `Case narrative #${source.ordinal}`;
}

function sourcePages(row: CaseSourceRead): SourcePage[] {
  const spans = asArray(row.provenance_json?.pages) as ProvenancePage[];
  if (!spans.length) return [];
  const characters = Array.from(row.exact_text);
  return spans.map((span) => ({
    pageNumber: span.page_number,
    text: characters.slice(span.start_offset, span.end_offset).join(""),
  }));
}

function contextualExcerpt(content: string, exactQuote: string | null): string {
  const start = exactQuote ? content.indexOf(exactQuote) : -1;
  if (!exactQuote || start < 0) return content.length > 640 ? `${content.slice(0, 640)}…` : content;
  const lower = Math.max(0, start - 220);
  const upper = Math.min(content.length, start + exactQuote.length + 220);
  return `${lower > 0 ? "…" : ""}${content.slice(lower, upper)}${upper < content.length ? "…" : ""}`;
}

function formatPageList(pageNumbers: number[]): string {
  const consecutive = pageNumbers.every(
    (page, index) => index === 0 || page === pageNumbers[index - 1] + 1,
  );
  return consecutive
    ? `${pageNumbers[0]}–${pageNumbers[pageNumbers.length - 1]}`
    : pageNumbers.join(", ");
}
