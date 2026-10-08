"use client";

import { plural } from "@/lib/format";
import { itemTitle, type RailItem } from "./SourceRail";
import { FileSourcePreview, TextSourcePreview, ViewportMessage } from "./SourcePreviews";
import { documentPages, fileKind } from "./sourcePresentation";

export type PreviewMode = "original" | "ocr" | "split";

const PREVIEW_MODES = [
  ["original", "Original"],
  ["ocr", "Text"],
  ["split", "Side by side"],
] as const;

interface SourceViewportProps {
  caseId: string;
  item: RailItem | null;
  mode: PreviewMode;
  onModeChange: (mode: PreviewMode) => void;
  onRetryDocument?: (documentId: string) => Promise<void>;
  isRetryingDocument?: boolean;
}

export function SourceViewport({
  caseId,
  item,
  mode,
  onModeChange,
  onRetryDocument,
  isRetryingDocument = false,
}: SourceViewportProps) {
  const subtitle = !item
    ? null
    : item.kind === "file"
      ? [fileKind(item.source), plural(documentPages(item.source).length, "page")].join(" · ")
      : item.kind === "followup_answer"
        ? "Follow-up answer"
        : "Case narrative";

  return (
    <section
      aria-label="Source preview"
      className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface"
    >
      <header className="flex min-h-12 flex-wrap items-center gap-x-4 gap-y-2 border-b border-line px-4 py-2 sm:px-5">
        <div className="flex min-w-0 flex-1 basis-56 items-baseline gap-2.5">
          <h2 className="truncate text-[14px] font-semibold text-ink">
            {item ? itemTitle(item) : "Select a source"}
          </h2>
          {subtitle && <p className="shrink-0 text-xs text-ink-muted">{subtitle}</p>}
        </div>

        {item?.kind === "file" && (
          <div
            role="tablist"
            aria-label="Source representation"
            className="flex h-8 items-center gap-0.5 rounded-lg bg-surface-nested p-0.5"
          >
            {PREVIEW_MODES.map(([value, label]) => (
              <PreviewTab key={value} selected={mode === value} onClick={() => onModeChange(value)}>
                {label}
              </PreviewTab>
            ))}
          </div>
        )}
      </header>

      <div className="min-h-0 flex-1 bg-canvas">
        {!item ? (
          <ViewportMessage title="Select a source to read it." />
        ) : item.kind === "followup_answer" ? (
          <TextSourcePreview question={item.followup.question} text={item.followup.answer} />
        ) : item.kind === "narrative" ? (
          <TextSourcePreview question={null} text={item.source.exact_text} />
        ) : (
          <FileSourcePreview
            caseId={caseId}
            item={item}
            mode={mode}
            onRetry={onRetryDocument ? () => onRetryDocument(item.documentId) : undefined}
            isRetrying={isRetryingDocument}
          />
        )}
      </div>
    </section>
  );
}

function PreviewTab({
  selected,
  onClick,
  children,
}: {
  selected: boolean;
  onClick: () => void;
  children: string;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={selected}
      tabIndex={selected ? 0 : -1}
      onClick={onClick}
      className={`h-7 rounded-md px-2.5 text-[13px] font-medium transition-colors ${
        selected ? "bg-surface text-ink shadow-xs" : "text-ink-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}
