import type { SourceMessageRef } from "@/lib/case-overview";
import { HighlightedEvidenceText } from "./HighlightedEvidenceText";

export function SourceEvidenceContent({ sourceRef }: { sourceRef: SourceMessageRef }) {
  const pages = sourceRef.evidencePages;
  const content = sourceRef.displayContent || sourceRef.excerpt;
  const hasHighlight = pages.length > 0
    ? pages.some((page) => page.exactQuote !== null && page.text.includes(page.exactQuote))
    : sourceRef.exactQuote !== null && content.includes(sourceRef.exactQuote);

  return (
    <div className="space-y-4">
      {pages.length > 0 ? pages.map((page) => (
        <section key={page.pageNumber} className="space-y-3">
          <h3 className="border-b border-line pb-2 text-xs font-semibold text-ink-secondary">Page {page.pageNumber}</h3>
          <p className="select-text whitespace-pre-wrap text-sm leading-7 text-ink [overflow-wrap:anywhere]">
            <HighlightedEvidenceText content={page.text || "(No text content)"} exactQuote={page.exactQuote} />
          </p>
        </section>
      )) : (
        <p className="select-text whitespace-pre-wrap text-sm leading-7 text-ink [overflow-wrap:anywhere]">
          <HighlightedEvidenceText content={content || "(No text content)"} exactQuote={sourceRef.exactQuote} />
        </p>
      )}
      {sourceRef.exactQuote && !hasHighlight && (
        <p className="text-xs leading-relaxed text-ink-muted">
          The cited passage could not be highlighted in the available source text.
        </p>
      )}
    </div>
  );
}
