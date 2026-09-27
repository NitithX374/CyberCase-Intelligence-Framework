"use client";

import { useMemo, type ReactNode } from "react";
import { Icon } from "@/components/icons";
import { plural } from "@/lib/format";
import { fetchCaseDocumentContent } from "./api";
import type { CaseSourceRead } from "@/lib/api/types";
import { useBlobUrl } from "@/lib/useBlobUrl";
import { itemTitle, type RailItem } from "./SourceRail";

export type PreviewMode = "original" | "ocr" | "split";

type FileItem = Extract<RailItem, { kind: "file" }>;

interface SourceViewportProps {
  caseId: string;
  item: RailItem | null;
  mode: PreviewMode;
  onModeChange: (mode: PreviewMode) => void;
}

export function SourceViewport({ caseId, item, mode, onModeChange }: SourceViewportProps) {
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
            <PreviewTab selected={mode === "original"} onClick={() => onModeChange("original")}>
              Original
            </PreviewTab>
            <PreviewTab selected={mode === "ocr"} onClick={() => onModeChange("ocr")}>
              Text
            </PreviewTab>
            <PreviewTab selected={mode === "split"} onClick={() => onModeChange("split")}>
              Side by side
            </PreviewTab>
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
        ) : mode === "original" ? (
          <OriginalFilePreview caseId={caseId} item={item} />
        ) : mode === "ocr" ? (
          <ExtractedTextPreview source={item.source} />
        ) : (
          <div className="flex h-full min-h-0 flex-col divide-y divide-line lg:flex-row lg:divide-x lg:divide-y-0">
            <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">
              <OriginalFilePreview caseId={caseId} item={item} />
            </div>
            <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">
              <ExtractedTextPreview source={item.source} />
            </div>
          </div>
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

function Paper({ label, children }: { label?: string; children: ReactNode }) {
  return (
    <section className="scroll-mt-4">
      {label && <h3 className="mb-2 px-1 text-xs font-medium text-ink-muted">{label}</h3>}
      <div className="rounded-xl border border-line bg-surface px-6 py-6 shadow-xs sm:px-10 sm:py-9">
        {children}
      </div>
    </section>
  );
}

function TextSourcePreview({ question, text }: { question: string | null; text: string }) {
  return (
    <div className="h-full overflow-auto p-4 sm:p-8">
      <div className="mx-auto max-w-3xl">
        <Paper>
          {question ? (
            <dl className="space-y-6">
              <div>
                <dt className="text-xs font-medium text-ink-muted">Question</dt>
                <dd className="mt-1.5 whitespace-pre-wrap break-words text-[15px] leading-8 text-ink-secondary">
                  {question}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-ink-muted">Answer</dt>
                <dd className="mt-1.5 whitespace-pre-wrap break-words text-[15px] leading-8 text-ink">
                  {text}
                </dd>
              </div>
            </dl>
          ) : (
            <p className="whitespace-pre-wrap break-words text-[15px] leading-8 text-ink">{text}</p>
          )}
        </Paper>
      </div>
    </div>
  );
}

function OriginalFilePreview({ caseId, item }: { caseId: string; item: FileItem }) {
  const { documentId } = item;
  const filename = item.source.filename ?? "";
  const mimeType = item.source.mime_type ?? "";
  const { blob, attach, isLoading, error, refetch } = useBlobUrl(
    ["case-document-content", caseId, documentId],
    (signal) => fetchCaseDocumentContent(caseId, documentId, signal),
  );

  if (isLoading) {
    return (
      <div
        role="status"
        aria-label="Loading original file"
        className="flex h-full min-h-[24rem] items-center justify-center text-ink-muted"
      >
        <Icon name="spinner" className="h-6 w-6" />
      </div>
    );
  }
  if (error || !blob) {
    return (
      <ViewportMessage title="The original file could not be loaded.">
        <button
          type="button"
          onClick={() => void refetch()}
          className="btn-secondary mt-4 h-8 px-3"
        >
          Try again
        </button>
      </ViewportMessage>
    );
  }

  const canEmbed = mimeType === "application/pdf" || mimeType.startsWith("image/");
  if (!canEmbed) {
    return (
      <ViewportMessage title="This file type has no preview.">
        <a ref={attach} download={filename} className="btn-primary mt-4">
          <Icon name="download" className="h-4 w-4" />
          Download file
        </a>
      </ViewportMessage>
    );
  }

  return (
    <iframe
      ref={attach}
      title={`Original file: ${filename}`}
      className="h-full min-h-[28rem] w-full border-0 bg-surface"
    />
  );
}

interface ExtractionPageItem {
  page_number?: number;
  text?: string;
  merged_text?: string;
  text_method?: string;
  verification_status?: string;
}

interface ExtractionPage {
  pageNumber: number;
  text: string;
  method?: string;
}

function documentPages(source: CaseSourceRead): ExtractionPage[] {
  const provenance = source.provenance_json as Record<string, unknown> | undefined;
  const rawPages = Array.isArray(provenance?.pages)
    ? (provenance.pages as ExtractionPageItem[])
    : [];

  if (rawPages.length === 0) {
    return [{ pageNumber: 1, text: source.exact_text }];
  }

  return rawPages.map((page, index) => ({
    pageNumber: typeof page.page_number === "number" ? page.page_number : index + 1,
    text:
      typeof page.text === "string"
        ? page.text
        : typeof page.merged_text === "string"
          ? page.merged_text
          : "",
    method: typeof page.text_method === "string" ? page.text_method : undefined,
  }));
}

const PAGE_JUMP_THRESHOLD = 4;

function ExtractedTextPreview({ source }: { source: CaseSourceRead }) {
  const pages = useMemo(() => documentPages(source), [source]);
  const recorded = source.provenance_json?.warnings;
  const warnings = Array.isArray(recorded) ? recorded.length : 0;

  return (
    <div role="tabpanel" aria-label="Extracted text" className="h-full overflow-auto p-4 sm:p-8">
      <div className="mx-auto max-w-3xl space-y-6">
        {(warnings > 0 || pages.length >= PAGE_JUMP_THRESHOLD) && (
          <div className="flex flex-wrap items-center justify-between gap-3">
            {warnings > 0 ? (
              <p className="flex items-center gap-1.5 text-[13px] text-unresolved">
                <Icon name="alert" className="h-4 w-4" />
                {plural(warnings, "extraction warning")}
              </p>
            ) : (
              <span />
            )}
            {pages.length >= PAGE_JUMP_THRESHOLD && (
              <nav aria-label="Page navigation" className="flex flex-wrap items-center gap-0.5">
                {pages.map((page) => (
                  <button
                    key={page.pageNumber}
                    type="button"
                    aria-label={`Go to page ${page.pageNumber}`}
                    onClick={() => {
                      document
                        .getElementById(`ocr-page-${page.pageNumber}`)
                        ?.scrollIntoView({ behavior: "smooth", block: "start" });
                    }}
                    className="h-7 min-w-7 rounded-md px-1.5 text-xs font-medium text-ink-muted transition-colors hover:bg-surface hover:text-ink"
                  >
                    {page.pageNumber}
                  </button>
                ))}
              </nav>
            )}
          </div>
        )}

        {pages.map((page) => (
          <div key={page.pageNumber} id={`ocr-page-${page.pageNumber}`} className="scroll-mt-4">
            <Paper label={`Page ${page.pageNumber}`}>
              {page.text.trim() ? (
                <p className="whitespace-pre-wrap break-words text-[15px] leading-8 text-ink">
                  {page.text}
                </p>
              ) : (
                <p className="text-sm text-ink-muted">No text on this page.</p>
              )}
            </Paper>
          </div>
        ))}
      </div>
    </div>
  );
}

function ViewportMessage({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex h-full min-h-[24rem] flex-col items-center justify-center p-8 text-center">
      <p className="text-sm text-ink-muted">{title}</p>
      {children}
    </div>
  );
}

function fileKind(source: CaseSourceRead): string {
  const extension = source.filename?.split(".").pop()?.toUpperCase();
  const mimeType = source.mime_type ?? "";
  if (mimeType === "application/pdf") return "PDF";
  if (mimeType.startsWith("image/")) return extension ?? "Image";
  return extension ?? "File";
}
