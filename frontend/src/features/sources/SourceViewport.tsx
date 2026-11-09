"use client";

import { plural } from "@/lib/format";
import { isTurnedOff, itemTitle, type RailItem } from "./SourceRail";
import { FileSourcePreview, TextSourcePreview, ViewportMessage } from "./SourcePreviews";
import { documentPages, fileKind, readByOcr } from "./sourcePresentation";

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
  const turnedOff = item !== null && item.kind !== "followup_answer" && isTurnedOff(item.source);
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
      className="sheet flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden"
    >
      <header className="card-head">
        <div className="flex min-w-0 flex-1 basis-56 items-baseline gap-2.5">
          <h2 className="truncate text-lg font-semibold text-ink">
            {item ? itemTitle(item) : "Select a source"}
          </h2>
          {subtitle && <p className="shrink-0 text-xs text-ink-muted">{subtitle}</p>}
        </div>

        {item?.kind === "file" && (
          <div
            role="group"
            aria-label="Source representation"
            className="flex items-center gap-0.5 rounded-[9px] bg-surface-hover p-[3px]"
          >
            {PREVIEW_MODES.map(([value, label]) => (
              <PreviewTab key={value} selected={mode === value} onClick={() => onModeChange(value)}>
                {value === "ocr" && readByOcr(item.source) ? "Machine-read text" : label}
              </PreviewTab>
            ))}
          </div>
        )}
      </header>

      {turnedOff && (
        <p className="border-b border-line bg-primary-wash px-6 py-2.5 text-sm text-ink-secondary">
          This source is turned off. The next analysis will not read it.
        </p>
      )}

      <div className="min-h-0 flex-1 bg-surface">
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
            onRetry={
              onRetryDocument && !turnedOff ? () => onRetryDocument(item.documentId) : undefined
            }
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
      aria-pressed={selected}
      onClick={onClick}
      className={`min-h-9 rounded-[7px] px-3.5 text-sm transition-colors ${
        selected
          ? "bg-surface font-semibold text-primary shadow-[0_2px_6px_rgba(24,24,28,0.08)]"
          : "text-ink-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}
