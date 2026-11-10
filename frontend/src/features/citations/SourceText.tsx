"use client";

import { useEffect, useRef } from "react";
import type { CitedSourcePassage, SourceMessageRef } from "./types";
import { citedSourcePassages } from "./groupSourceRefs";
import { Markdown } from "@/components/Markdown";
import { hasThai } from "@/lib/language";

const MARK_OPEN =
  '<mark class="rounded-sm bg-primary-soft px-0.5 text-ink [box-decoration-break:clone]">';
const MARK_CLOSE = "</mark>";
const ROW_HIGHLIGHT = "bg-primary-wash";

const UNRESOLVED_NOTE = {
  thai: "บางข้อความที่อ้างไว้หาตำแหน่งใน Source ไม่พบ",
  english: "Some quoted words could not be located in this source.",
};

interface Segment {
  pageNumber: number | null;
  text: string;
  start: number | null;
}

export function SourceText({ sourceRef }: { sourceRef: SourceMessageRef }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const passages = citedPassages(sourceRef);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const mark = containerRef.current?.querySelector("mark");
      let scroller = mark?.parentElement ?? null;
      while (scroller && !/auto|scroll/.test(getComputedStyle(scroller).overflowY)) {
        scroller = scroller.parentElement;
      }
      if (!mark || !scroller) return;
      const offset = mark.getBoundingClientRect().top - scroller.getBoundingClientRect().top;
      scroller.scrollTop += offset - scroller.clientHeight / 3;
    });
    return () => window.cancelAnimationFrame(frame);
  }, [sourceRef]);

  if (sourceRef.question) {
    const content = sourceRef.sourceText ?? sourceRef.displayContent;
    return (
      <dl className="space-y-6">
        <div>
          <dt className="mb-2 text-xs font-medium text-ink-muted">Question</dt>
          <dd className="select-text whitespace-pre-wrap text-base leading-7 text-ink-secondary [overflow-wrap:anywhere]">
            {sourceRef.question}
          </dd>
        </div>
        <div>
          <dt className="mb-2 text-xs font-medium text-ink-muted">Answer</dt>
          <dd className="select-text text-base leading-7 text-ink [overflow-wrap:anywhere]">
            {content ? (
              <Markdown
                content={highlightQuotes(
                  content,
                  passages.map((passage) => passage.quote),
                )}
                allowHtml
              />
            ) : (
              "(No text content)"
            )}
          </dd>
        </div>
      </dl>
    );
  }

  const segments = sourceSegments(sourceRef);
  const unresolved = passages.some((passage) => passage.pointerState === "unresolved");
  const thai = hasThai(sourceRef.exactQuote ?? sourceRef.displayContent);

  return (
    <div ref={containerRef} className="space-y-6">
      {unresolved && (
        <p className="text-sm text-ink-muted">
          {thai ? UNRESOLVED_NOTE.thai : UNRESOLVED_NOTE.english}
        </p>
      )}
      {segments.map((segment, index) => (
        <section key={segment.pageNumber ?? index}>
          {segment.pageNumber !== null && segments.length > 1 && (
            <h3 className="mb-2 text-xs font-medium text-ink-muted">Page {segment.pageNumber}</h3>
          )}
          {segment.text ? (
            <div className="select-text [overflow-wrap:anywhere]">
              <Markdown content={markSegment(segment, passages)} allowHtml />
            </div>
          ) : (
            <p className="text-base leading-7 text-ink-muted">(No text content)</p>
          )}
        </section>
      ))}
    </div>
  );
}

function citedPassages(sourceRef: SourceMessageRef): CitedSourcePassage[] {
  const passages = citedSourcePassages(sourceRef);
  if (passages.length || !sourceRef.exactQuote) return passages;
  return [
    {
      quote: sourceRef.exactQuote,
      context: sourceRef.quoteContext,
      pointerState: "recovered",
      start: null,
      end: null,
    },
  ];
}

function sourceSegments(sourceRef: SourceMessageRef): Segment[] {
  const pages = sourceRef.allPages?.length ? sourceRef.allPages : sourceRef.sourcePages;
  if (pages.length) {
    return pages.map((page) => ({
      pageNumber: page.pageNumber,
      text: page.text,
      start: page.start ?? null,
    }));
  }
  if (sourceRef.sourceText !== undefined) {
    return [{ pageNumber: null, text: sourceRef.sourceText, start: 0 }];
  }
  return [{ pageNumber: null, text: sourceRef.displayContent, start: null }];
}

function markSegment(segment: Segment, passages: CitedSourcePassage[]): string {
  const characters = Array.from(segment.text);
  const placed: [number, number][] = [];
  const loose: string[] = [];
  for (const passage of passages) {
    if (segment.start !== null && passage.start !== null && passage.end !== null) {
      const from = passage.start - segment.start;
      const to = passage.end - segment.start;
      if (from >= characters.length || to <= 0) continue;
      if (from >= 0 && to <= characters.length) {
        if (characters.slice(from, to).join("") === passage.quote) {
          placed.push([from, to]);
          continue;
        }
      }
    }
    loose.push(passage.quote);
  }

  placed.sort((a, b) => a[0] - b[0]);
  let marked = "";
  let cursor = 0;
  for (const [from, to] of placed) {
    if (from < cursor) continue;
    marked += characters.slice(cursor, from).join("");
    marked += highlightSnippet(characters.slice(from, to).join(""));
    cursor = to;
  }
  marked += characters.slice(cursor).join("");
  return highlightQuotes(marked, loose);
}

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlightSnippet(snippet: string): string {
  if (/<[^>]+>/.test(snippet)) {
    return snippet
      .split(/(<[^>]+>)/g)
      .map((part) => {
        if (part.startsWith("<") && part.endsWith(">")) {
          if (/^<tr\b/i.test(part)) {
            if (/class=/i.test(part)) {
              return part.replace(
                /class=["']([^"']*)["']/i,
                (_, cls) => `class="${cls} ${ROW_HIGHLIGHT}"`,
              );
            }
            return part.replace(/^<tr/i, `<tr class="${ROW_HIGHLIGHT}"`);
          }
          return part;
        }
        return wrapTrimmed(part);
      })
      .join("");
  }

  if (snippet.trim().startsWith("|") && snippet.trim().endsWith("|")) {
    const cells = snippet.split("|");
    return cells
      .map((cell, index) => (index === 0 || index === cells.length - 1 ? cell : wrapTrimmed(cell)))
      .join("|");
  }

  return wrapTrimmed(snippet);
}

function wrapTrimmed(part: string): string {
  if (!part.trim()) return part;
  const leading = part.match(/^\s*/)?.[0] ?? "";
  const trailing = part.match(/\s*$/)?.[0] ?? "";
  const trimmed = part.slice(leading.length, part.length - trailing.length);
  return `${leading}${MARK_OPEN}${trimmed}${MARK_CLOSE}${trailing}`;
}

function highlightSingleQuote(text: string, quote: string): string {
  const target = quote.trim();
  if (!target) return text;

  if (text.includes(target)) {
    return text.split(target).join(highlightSnippet(target));
  }

  const index = text.toLowerCase().indexOf(target.toLowerCase());
  if (index !== -1) {
    return `${text.slice(0, index)}${highlightSnippet(text.slice(index, index + target.length))}${text.slice(index + target.length)}`;
  }

  const chunks = target
    .replace(/<[^>]+>/g, "\n")
    .split(/[\n|]+/)
    .map((chunk) => chunk.trim())
    .filter((chunk) => chunk.length > 0);

  if (chunks.length > 1) {
    try {
      const match = new RegExp(chunks.map(escapeRegex).join("(?:\\s*|<[^>]+>)+"), "i").exec(text);
      if (match) {
        return `${text.slice(0, match.index)}${highlightSnippet(match[0])}${text.slice(match.index + match[0].length)}`;
      }
    } catch {
      return text;
    }
  } else if (chunks.length === 1 && chunks[0].length > 1) {
    const chunkIndex = text.toLowerCase().indexOf(chunks[0].toLowerCase());
    if (chunkIndex !== -1) {
      const end = chunkIndex + chunks[0].length;
      return `${text.slice(0, chunkIndex)}${highlightSnippet(text.slice(chunkIndex, end))}${text.slice(end)}`;
    }
  }

  return text;
}

function highlightQuotes(text: string, quotes: string[]): string {
  return quotes
    .map((quote) => quote?.trim())
    .filter((quote): quote is string => Boolean(quote))
    .reduce((result, quote) => highlightSingleQuote(result, quote), text);
}
