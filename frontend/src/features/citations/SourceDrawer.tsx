"use client";

import { useEffect, useId, useRef } from "react";
import type { SourceMessageRef } from "./types";
import { Icon } from "@/components/icons";

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
          <SourceContent sourceRef={sourceRef} />
        </div>
      </div>
    </dialog>
  );
}

function SourceContent({ sourceRef }: { sourceRef: SourceMessageRef }) {
  const pages = sourceRef.sourcePages;
  const content = sourceRef.displayContent || sourceRef.excerpt;

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
          <dd className="select-text whitespace-pre-wrap text-[15px] leading-7 text-ink [overflow-wrap:anywhere]">
            {content || "(No text content)"}
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
            <p className="select-text whitespace-pre-wrap text-[15px] leading-7 text-ink [overflow-wrap:anywhere]">
              {page.text || "(No text content)"}
            </p>
          </section>
        ))
      ) : (
        <p className="select-text whitespace-pre-wrap text-[15px] leading-7 text-ink [overflow-wrap:anywhere]">
          {content || "(No text content)"}
        </p>
      )}
    </div>
  );
}
