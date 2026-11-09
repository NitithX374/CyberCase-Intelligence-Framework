"use client";

import { useState } from "react";
import type { SourceMessageRef } from "@/features/citations/types";

const CONTEXT_CHARS = 140;
const SHOWN = 2;

interface Passage {
  key: string;
  quote: string;
  before: string;
  after: string;
  label: string;
  pages: number[];
}

function passagesOf(sources: SourceMessageRef[]): Passage[] {
  return sources.flatMap((source, sourceIndex) => {
    const cited = source.passages?.length
      ? source.passages.map((passage) => ({ quote: passage.quote, context: passage.context }))
      : source.exactQuote
        ? [{ quote: source.exactQuote, context: source.quoteContext }]
        : [];
    return cited.map((passage, index) => {
      const before = passage.context?.before ?? "";
      const after = passage.context?.after ?? "";
      return {
        key: `${sourceIndex}-${source.id}-${index}`,
        quote: passage.quote,
        before:
          before.length > CONTEXT_CHARS || passage.context?.cutBefore
            ? `…${before.slice(-CONTEXT_CHARS)}`
            : before,
        after:
          after.length > CONTEXT_CHARS || passage.context?.cutAfter
            ? `${after.slice(0, CONTEXT_CHARS)}…`
            : after,
        label: source.label,
        pages: source.pageNumbers,
      };
    });
  });
}

export function CitedPassages({
  sources,
  conflicting = false,
}: {
  sources: SourceMessageRef[];
  conflicting?: boolean;
}) {
  const [withContext, setWithContext] = useState(false);
  const passages = passagesOf(sources);
  if (passages.length === 0) return null;
  const shown = passages.slice(0, SHOWN);
  const hasContext = shown.some((passage) => passage.before || passage.after);

  return (
    <div className="flex flex-col gap-2">
      {shown.map((passage) => (
        <figure
          key={passage.key}
          className="relative m-0 rounded-lg bg-surface-nested py-3 pr-4 pl-9 before:absolute before:top-0.5 before:left-2.5 before:font-serif before:text-3xl before:text-primary/50 before:content-['\201C']"
        >
          <figcaption className="text-xs text-ink-muted">
            {conflicting ? "Words in the conflicting source" : "Words in the source"}
            {passage.pages.length > 0 && `, page ${passage.pages.join(", ")}`}
          </figcaption>
          <blockquote className="m-0 mt-1 text-sm text-ink-secondary [overflow-wrap:anywhere]">
            {withContext && passage.before}
            <span className="text-ink underline decoration-primary/70 decoration-1 underline-offset-4">
              {passage.quote}
            </span>
            {withContext && passage.after}
          </blockquote>
        </figure>
      ))}
      {hasContext && (
        <button
          type="button"
          aria-expanded={withContext}
          onClick={() => setWithContext((open) => !open)}
          className="self-start text-xs font-semibold text-primary underline underline-offset-3"
        >
          {withContext ? "Hide surrounding text" : "Show surrounding text"}
        </button>
      )}
      {passages.length > SHOWN && (
        <p className="text-xs text-ink-secondary">
          {passages.length - SHOWN} more cited{" "}
          {passages.length - SHOWN === 1 ? "passage" : "passages"} in the source
        </p>
      )}
    </div>
  );
}
