"use client";

import { useEffect, useId, useRef } from "react";
import type { SourceMessageRef } from "@/lib/case-overview";
import { formatEvidenceCitationText } from "@/lib/evidence-citation";
import { SourceEvidenceContent } from "@/components/evidence/SourceEvidenceContent";
import { Icon } from "@/components/common/icons";

export function SourceEvidenceDrawer({ sourceRef, anchorElement, citationRole, onClose, onNavigateToSource }: {
  sourceRef: SourceMessageRef;
  anchorElement: HTMLElement;
  citationRole?: "supporting" | "conflicting";
  onClose: () => void;
  onNavigateToSource?: (id: string) => void;
}) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const citation = formatEvidenceCitationText(sourceRef);
  const sourceTitle = sourceRef.filename ?? (sourceRef.sourceType === "case_description"
    ? citation : `${citation} #${sourceRef.ordinal}`);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    dialog.showModal();
    const passage = dialog.querySelector("mark");
    const scroller = textRef.current;
    if (passage && scroller) {
      scroller.scrollTop += passage.getBoundingClientRect().top - scroller.getBoundingClientRect().top - scroller.clientHeight / 2;
    }
    return () => {
      dialog.close();
      if (anchorElement.isConnected) anchorElement.focus();
    };
  }, [anchorElement]);

  return (
    <dialog
      ref={dialogRef} aria-labelledby={titleId}
      onCancel={(event) => { event.preventDefault(); onClose(); }}
      onClick={(event) => {
        if (event.target !== event.currentTarget) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) onClose();
      }}
      className="fixed inset-y-0 right-0 left-auto m-0 h-dvh max-h-dvh w-full max-w-full overflow-hidden border-l border-line bg-surface p-0 text-ink shadow-xl backdrop:bg-ink/20 sm:w-[30rem]"
    >
      <div className="flex h-full min-h-0 flex-col">
        <header className="flex items-start justify-between gap-4 border-b border-line p-5 sm:p-6">
          <div className="min-w-0 space-y-2">
            <p className="text-xs text-ink-secondary">{citationRole === "conflicting" ? "Conflicting source" : "Source evidence"}</p>
            <h2 id={titleId} className="text-base font-semibold [overflow-wrap:anywhere]">
              <span className="sr-only">Source Evidence: </span>{sourceTitle}
            </h2>
            {sourceRef.filename && <p className="text-xs text-ink-muted">{citation}</p>}
          </div>
          <button type="button" onClick={onClose} aria-label="Close source evidence"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-primary">
            <Icon name="close" className="h-4 w-4" />
          </button>
        </header>
        <div ref={textRef} className="min-h-0 flex-1 overflow-y-auto p-5 sm:p-6" tabIndex={0} aria-label="Source text">
          <SourceEvidenceContent sourceRef={sourceRef} />
        </div>
        {onNavigateToSource && (
          <footer className="border-t border-line px-5 py-3 sm:px-6">
            <button type="button" onClick={() => { onClose(); onNavigateToSource(sourceRef.id); }}
              className="min-h-9 text-xs font-semibold underline underline-offset-4 focus-visible:ring-2 focus-visible:ring-primary">
              View in Chat <span aria-hidden="true">↗</span>
            </button>
          </footer>
        )}
      </div>
    </dialog>
  );
}
