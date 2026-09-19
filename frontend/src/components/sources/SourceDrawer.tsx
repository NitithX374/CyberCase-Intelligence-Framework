"use client";

import { Fragment, useEffect, useId, useRef } from "react";
import type { SourceMessageRef } from "@/lib/caseOverview/types";
import { formatSourceCitationText } from "@/lib/caseOverview/source";
import { Icon } from "@/components/common/icons";

export function SourceDrawer({
  sourceRef,
  anchorElement,
  citationRole,
  onClose,
  onNavigateToSource,
}: {
  sourceRef: SourceMessageRef;
  anchorElement: HTMLElement;
  citationRole?: "supporting" | "conflicting";
  onClose: () => void;
  onNavigateToSource?: (id: string) => void;
}) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const citation = formatSourceCitationText(sourceRef);
  const sourceTitle =
    sourceRef.filename ??
    (sourceRef.sourceType === "case_description" ? citation : `${citation} #${sourceRef.ordinal}`);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    dialog.showModal();
    const passage = dialog.querySelector("mark");
    const scroller = textRef.current;
    if (passage && scroller) {
      scroller.scrollTop +=
        passage.getBoundingClientRect().top -
        scroller.getBoundingClientRect().top -
        scroller.clientHeight / 2;
    }
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
      className="fixed inset-y-0 right-0 left-auto m-0 h-dvh max-h-dvh w-full max-w-full overflow-hidden border-l border-line bg-surface p-0 text-ink shadow-xl backdrop:bg-ink/20 sm:w-[360px]"
    >
      <div className="flex h-full min-h-0 flex-col">
        <header className="flex items-start justify-between gap-4 border-b border-line p-5 sm:p-6">
          <div className="min-w-0 space-y-2">
            <p className="text-[11px] font-semibold tracking-[0.04em] text-ink-secondary">
              {citationRole === "conflicting" ? "Conflicting source" : "Supporting source"}
            </p>
            <h2 id={titleId} className="text-base font-semibold [overflow-wrap:anywhere]">
              <span className="sr-only">Source: </span>
              {sourceTitle}
            </h2>
            {sourceRef.filename && <p className="text-xs text-ink-muted">{citation}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close source"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-primary"
          >
            <Icon name="close" className="h-4 w-4" />
          </button>
        </header>
        <div
          ref={textRef}
          className="min-h-0 flex-1 overflow-y-auto p-5 sm:p-6"
          tabIndex={0}
          aria-label="Source text"
        >
          <SourceContent sourceRef={sourceRef} />
        </div>
        {onNavigateToSource && (
          <footer className="border-t border-line px-5 py-3 sm:px-6">
            <button
              type="button"
              onClick={() => {
                onClose();
                onNavigateToSource(sourceRef.id);
              }}
              className="min-h-9 text-xs font-semibold text-source underline underline-offset-4 hover:text-accent-strong focus-visible:ring-2 focus-visible:ring-primary"
            >
              View in Materials <span aria-hidden="true">↗</span>
            </button>
          </footer>
        )}
      </div>
    </dialog>
  );
}

function SourceContent({ sourceRef }: { sourceRef: SourceMessageRef }) {
  const pages = sourceRef.sourcePages;
  const content = sourceRef.displayContent || sourceRef.excerpt;
  const hasHighlight =
    pages.length > 0
      ? pages.some((page) => page.exactQuote !== null && page.text.includes(page.exactQuote))
      : sourceRef.exactQuote !== null && content.includes(sourceRef.exactQuote);

  return (
    <div className="space-y-4">
      {pages.length > 0 ? (
        pages.map((page) => (
          <section key={page.pageNumber} className="space-y-3">
            <h3 className="border-b border-line pb-2 text-xs font-semibold text-ink-secondary">
              Page {page.pageNumber}
            </h3>
            <p className="select-text whitespace-pre-wrap text-sm leading-7 text-ink [overflow-wrap:anywhere]">
              <HighlightedText
                content={page.text || "(No text content)"}
                exactQuote={page.exactQuote}
              />
            </p>
          </section>
        ))
      ) : (
        <p className="select-text whitespace-pre-wrap text-sm leading-7 text-ink [overflow-wrap:anywhere]">
          <HighlightedText
            content={content || "(No text content)"}
            exactQuote={sourceRef.exactQuote}
          />
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

function HighlightedText({ content, exactQuote }: { content: string; exactQuote: string | null }) {
  if (!exactQuote) return <>{content}</>;
  const segments = content.split(exactQuote);
  if (segments.length === 1) return <>{content}</>;
  return (
    <>
      {segments.map((segment, index) => (
        <Fragment key={index}>
          {segment}
          {index < segments.length - 1 && (
            <mark className="rounded-sm bg-[#F4D58D]/75 px-0.5 text-inherit ring-1 ring-[#B98218]/20">
              {exactQuote}
            </mark>
          )}
        </Fragment>
      ))}
    </>
  );
}
