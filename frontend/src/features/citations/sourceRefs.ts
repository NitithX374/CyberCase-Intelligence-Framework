import type { CaseAnalysisClaim, CaseSourceCitation, CaseSourceRead } from "@/lib/api/types";
import { asArray } from "@/lib/parse";
import { reviewNotes } from "./reviewNotes";
import { toleratedNotes } from "./toleratedNotes";
import type { CaseSourceRef, FollowupAnswer, SourceMessageRef, SourcePage } from "./types";

interface ProvenancePage {
  page_number: number;
  start_offset: number;
  end_offset: number;
}

function formatPageReference(pageNumbers: number[]): string {
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
  writtenText?: string,
): { supporting: SourceMessageRef[]; contradicting: SourceMessageRef[] } {
  return {
    supporting: refs(claim.supporting_source_ids, claim.supporting_citations, sources, writtenText),
    contradicting: refs(
      claim.contradicting_source_ids,
      claim.contradicting_citations,
      sources,
      writtenText,
    ),
  };
}

function refs(
  ids: string[] = [],
  citations: CaseSourceCitation[] = [],
  sources: CaseSourceRef[],
  writtenText?: string,
): SourceMessageRef[] {
  return ids.flatMap((id) => {
    const source = sources.find((candidate) => candidate.id === id);
    if (!source) return [];
    const cited = citations.filter((citation) => citation.source_id === id);
    return cited.length
      ? cited.map((citation) => sourceRef(source, citation, writtenText))
      : [sourceRef(source, null)];
  });
}

export function passageRef(
  sources: CaseSourceRef[],
  sourceId: string,
  passage: string,
  quoteLabel = "Nearest passage",
): SourceMessageRef | null {
  const source = sources.find((candidate) => candidate.id === sourceId);
  if (!source) return null;
  return {
    ...sourceRef(source, {
      source_id: sourceId,
      exact_quote: passage,
      pointer_state: "unresolved",
    }),
    quoteLabel,
  };
}

function sourceRef(
  source: CaseSourceRef,
  citation: CaseSourceCitation | null,
  writtenText?: string,
): SourceMessageRef {
  const quote = citation?.exact_quote || null;
  const context = quote ? citation?.context : null;
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
      : contextualExcerpt(source.text, quote, citation),
    exactQuote: quote,
    quoteContext: context
      ? {
          before: context.before,
          after: context.after,
          cutBefore: context.cut_before,
          cutAfter: context.cut_after,
        }
      : null,
    filename: source.filename,
    pageNumbers,
    sourcePages: pages,
    question: source.question,
    ...(quote && citation
      ? {
          pointerState: citation.pointer_state ?? "legacy",
          start: citation.start ?? null,
          end: citation.end ?? null,
        }
      : {}),
    ...(quote && writtenText !== undefined && citation?.tolerated_differences?.length
      ? { toleratedNotes: toleratedNotes(citation.tolerated_differences, writtenText) }
      : {}),
    ...(quote && writtenText !== undefined && citation?.review_flags?.length
      ? { reviewNotes: reviewNotes(citation.review_flags, writtenText) }
      : {}),
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

function contextualExcerpt(
  content: string,
  exactQuote: string | null,
  citation: CaseSourceCitation | null,
): string {
  if (citation?.pointer_state === "direct" && citation.start != null && citation.end != null) {
    const characters = Array.from(content);
    if (characters.slice(citation.start, citation.end).join("") === exactQuote) {
      const lower = Math.max(0, citation.start - 220);
      const upper = Math.min(characters.length, citation.end + 220);
      return `${lower > 0 ? "…" : ""}${characters.slice(lower, upper).join("")}${upper < characters.length ? "…" : ""}`;
    }
  }
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
