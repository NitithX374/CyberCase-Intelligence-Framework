"use client";

import { useEffect, useId, useRef } from "react";
import type { SourceMessageRef } from "./types";
import { SourcePassages } from "./SourcePassages";
import { Icon } from "@/components/icons";
import { Markdown } from "@/components/Markdown";

export function SourceDrawer({
  sourceRef,
  anchorElement,
  citationRole,
  onClose,
}: {
  sourceRef: SourceMessageRef;
  anchorElement: HTMLElement;
  citationRole?: "supporting" | "conflicting";
  onClose: () => void;
}) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const sourceTitle = sourceRef.filename ?? sourceRef.label;

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    dialog.showModal();
    return () => {
      dialog.close();
      if (anchorElement.isConnected) anchorElement.focus();
    };
  }, [anchorElement]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={titleId}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClick={(event) => {
        if (event.target !== event.currentTarget) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        if (
          event.clientX < bounds.left ||
          event.clientX > bounds.right ||
          event.clientY < bounds.top ||
          event.clientY > bounds.bottom
        )
          onClose();
      }}
      className="fixed inset-y-0 right-0 left-auto m-0 h-dvh max-h-dvh w-full max-w-full overflow-hidden border-l border-line bg-surface p-0 text-ink shadow-2xl shadow-black/10 backdrop:bg-ink/20 sm:w-[400px]"
    >
      <div className="flex h-full min-h-0 flex-col">
        <header className="flex items-start justify-between gap-4 px-5 pt-5 pb-4 sm:px-6">
          <div className="min-w-0 space-y-1">
            {citationRole === "conflicting" && (
              <p className="text-xs font-medium text-critical">Conflicting source</p>
            )}
            <h2
              id={titleId}
              className="text-[15px] font-semibold leading-6 [overflow-wrap:anywhere]"
            >
              <span className="sr-only">Source: </span>
              {sourceTitle}
            </h2>
            {sourceRef.label !== sourceTitle && (
              <p className="text-[13px] text-ink-muted">{sourceRef.label}</p>
            )}
          </div>
          <button type="button" onClick={onClose} aria-label="Close source" className="icon-btn">
            <Icon name="close" className="h-5 w-5" />
          </button>
        </header>
        <div
          className="min-h-0 flex-1 overflow-y-auto px-5 pb-6 sm:px-6"
          tabIndex={0}
          aria-label="Source text"
        >
          <SourcePassages sourceRef={sourceRef} />
          <SourceContent sourceRef={sourceRef} />
        </div>
      </div>
    </dialog>
  );
}

const MARK_OPEN =
  '<mark class="bg-amber-200/60 dark:bg-amber-400/30 text-ink px-1 py-0.5 rounded font-medium">';
const MARK_CLOSE = "</mark>";
const TR_HIGHLIGHT = 'class="bg-amber-100/50 dark:bg-amber-400/15"';

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlightSnippet(snippet: string): string {
  if (/<[^>]+>/.test(snippet)) {
    const parts = snippet.split(/(<[^>]+>)/g);
    return parts
      .map((part) => {
        if (part.startsWith("<") && part.endsWith(">")) {
          if (/^<tr\b/i.test(part)) {
            if (/class=/i.test(part)) {
              return part.replace(
                /class=["']([^"']*)["']/i,
                (_, cls) => `class="${cls} bg-amber-100/50 dark:bg-amber-400/15"`,
              );
            }
            return part.replace(/^<tr/i, `<tr ${TR_HIGHLIGHT}`);
          }
          return part;
        }
        if (!part.trim()) return part;
        const leading = part.match(/^\s*/)?.[0] ?? "";
        const trailing = part.match(/\s*$/)?.[0] ?? "";
        const trimmed = part.slice(leading.length, part.length - trailing.length);
        return `${leading}${MARK_OPEN}${trimmed}${MARK_CLOSE}${trailing}`;
      })
      .join("");
  }

  if (snippet.trim().startsWith("|") && snippet.trim().endsWith("|")) {
    const cells = snippet.split("|");
    return cells
      .map((cell, idx) => {
        if (idx === 0 || idx === cells.length - 1) return cell;
        if (!cell.trim()) return cell;
        const leading = cell.match(/^\s*/)?.[0] ?? "";
        const trailing = cell.match(/\s*$/)?.[0] ?? "";
        const trimmed = cell.slice(leading.length, cell.length - trailing.length);
        return `${leading}${MARK_OPEN}${trimmed}${MARK_CLOSE}${trailing}`;
      })
      .join("|");
  }

  return `${MARK_OPEN}${snippet}${MARK_CLOSE}`;
}

function highlightSingleQuote(text: string, quote: string): string {
  const target = quote.trim();
  if (!target) return text;

  if (text.includes(target)) {
    return text.split(target).join(highlightSnippet(target));
  }

  const lowerText = text.toLowerCase();
  const lowerTarget = target.toLowerCase();
  const index = lowerText.indexOf(lowerTarget);
  if (index !== -1) {
    const matched = text.slice(index, index + target.length);
    const before = text.slice(0, index);
    const after = text.slice(index + target.length);
    return `${before}${highlightSnippet(matched)}${after}`;
  }

  const chunks = target
    .replace(/<[^>]+>/g, "\n")
    .split(/[\n|]+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

  if (chunks.length > 1) {
    const pattern = chunks.map(escapeRegex).join("(?:\\s*|<[^>]+>)+");
    try {
      const regex = new RegExp(pattern, "i");
      const match = regex.exec(text);
      if (match) {
        const matched = match[0];
        const before = text.slice(0, match.index);
        const after = text.slice(match.index + matched.length);
        return `${before}${highlightSnippet(matched)}${after}`;
      }
    } catch {
      // Fall through if regex fails
    }
  } else if (chunks.length === 1 && chunks[0].length > 1) {
    const chunk = chunks[0];
    const chunkIndex = lowerText.indexOf(chunk.toLowerCase());
    if (chunkIndex !== -1) {
      const matched = text.slice(chunkIndex, chunkIndex + chunk.length);
      const before = text.slice(0, chunkIndex);
      const after = text.slice(chunkIndex + chunk.length);
      return `${before}${highlightSnippet(matched)}${after}`;
    }
  }

  return text;
}

export function highlightQuote(text: string, quoteOrQuotes: string | string[] | null): string {
  if (!quoteOrQuotes) return text;
  const quotes = (Array.isArray(quoteOrQuotes) ? quoteOrQuotes : [quoteOrQuotes])
    .map((q) => q?.trim())
    .filter((q): q is string => Boolean(q));

  let result = text;
  for (const q of quotes) {
    result = highlightSingleQuote(result, q);
  }
  return result;
}

function SourceContent({ sourceRef }: { sourceRef: SourceMessageRef }) {
  const pages = sourceRef.sourcePages;
  const content = sourceRef.displayContent || sourceRef.excerpt;
  const quotes = sourceRef.passages?.length
    ? sourceRef.passages.map((p) => p.quote)
    : sourceRef.exactQuote;

  if (sourceRef.question) {
    return (
      <dl className="space-y-6">
        <div>
          <dt className="mb-2 text-xs font-medium text-ink-muted">Question</dt>
          <dd className="select-text whitespace-pre-wrap text-[15px] leading-7 text-ink-secondary [overflow-wrap:anywhere]">
            {sourceRef.question}
          </dd>
        </div>
        <div>
          <dt className="mb-2 text-xs font-medium text-ink-muted">Answer</dt>
          <dd className="select-text text-[15px] leading-7 text-ink [overflow-wrap:anywhere]">
            {content ? (
              <Markdown content={highlightQuote(content, quotes)} allowHtml />
            ) : (
              "(No text content)"
            )}
          </dd>
        </div>
      </dl>
    );
  }

  return (
    <div className="space-y-6">
      {pages.length > 0 ? (
        pages.map((page) => (
          <section key={page.pageNumber}>
            <h3 className="mb-2 text-xs font-medium text-ink-muted">Page {page.pageNumber}</h3>
            {page.text ? (
              <div className="select-text [overflow-wrap:anywhere]">
                <Markdown content={highlightQuote(page.text, quotes)} allowHtml />
              </div>
            ) : (
              <p className="select-text whitespace-pre-wrap text-[15px] leading-7 text-ink-muted [overflow-wrap:anywhere]">
                (No text content)
              </p>
            )}
          </section>
        ))
      ) : (
        <section>
          {sourceRef.exactQuote && (
            <h3 className="mb-2 text-xs font-medium text-ink-muted">Source text</h3>
          )}
          {content ? (
            <div className="select-text [overflow-wrap:anywhere]">
              <Markdown content={highlightQuote(content, quotes)} allowHtml />
            </div>
          ) : (
            <p className="select-text whitespace-pre-wrap text-[15px] leading-7 text-ink-muted [overflow-wrap:anywhere]">
              (No text content)
            </p>
          )}
        </section>
      )}
    </div>
  );
}
