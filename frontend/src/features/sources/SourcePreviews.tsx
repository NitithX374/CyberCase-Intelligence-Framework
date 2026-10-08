"use client";

import { useMemo, type ReactNode } from "react";
import { Icon } from "@/components/icons";
import { Markdown } from "@/components/Markdown";
import { plural } from "@/lib/format";
import type { CaseSourceRead } from "@/lib/api/types";
import { useBlobUrl } from "@/lib/useBlobUrl";
import { fetchCaseDocumentContent } from "./api";
import type { RailItem } from "./SourceRail";
import type { PreviewMode } from "./SourceViewport";
import { documentPages } from "./sourcePresentation";

type FileItem = Extract<RailItem, { kind: "file" }>;

export function FileSourcePreview({
  caseId,
  item,
  mode,
  onRetry,
  isRetrying,
}: {
  caseId: string;
  item: FileItem;
  mode: PreviewMode;
  onRetry?: () => void;
  isRetrying: boolean;
}) {
  const original = <OriginalFilePreview caseId={caseId} item={item} />;
  const extracted = (
    <ExtractedTextPreview source={item.source} onRetry={onRetry} isRetrying={isRetrying} />
  );
  if (mode === "original") return original;
  if (mode === "ocr") return extracted;
  return (
    <div className="flex h-full min-h-0 flex-col divide-y divide-line lg:flex-row lg:divide-x lg:divide-y-0">
      <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">{original}</div>
      <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">{extracted}</div>
    </div>
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

export function TextSourcePreview({ question, text }: { question: string | null; text: string }) {
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
                <dd className="mt-1.5 break-words text-[15px] leading-8 text-ink">
                  <Markdown content={text} allowHtml />
                </dd>
              </div>
            </dl>
          ) : (
            <Markdown content={text} allowHtml />
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

const PAGE_JUMP_THRESHOLD = 4;

function ExtractedTextPreview({
  source,
  onRetry,
  isRetrying = false,
}: {
  source: CaseSourceRead;
  onRetry?: () => void;
  isRetrying?: boolean;
}) {
  const pages = useMemo(() => documentPages(source), [source]);
  const recorded = source.provenance_json?.warnings;
  const warningsList = Array.isArray(recorded) ? recorded.map(String) : [];
  const warnings = warningsList.length;

  return (
    <div role="tabpanel" aria-label="Extracted text" className="h-full overflow-auto p-4 sm:p-8">
      <div className="mx-auto max-w-3xl space-y-6">
        {(warnings > 0 || pages.length >= PAGE_JUMP_THRESHOLD || onRetry) && (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              {warnings > 0 && (
                <details className="group rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2 text-[13px] text-unresolved">
                  <summary className="flex cursor-pointer items-center gap-1.5 font-medium select-none">
                    <Icon name="alert" className="h-4 w-4 shrink-0" />
                    <span>{plural(warnings, "extraction warning")}</span>
                    <span className="text-xs text-ink-muted group-open:hidden">(view details)</span>
                  </summary>
                  <ul className="mt-2 space-y-1 pl-5 list-disc text-xs text-ink-secondary">
                    {warningsList.map((warning, index) => (
                      <li key={index} className="[overflow-wrap:anywhere]">
                        {warning}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
              {onRetry && (
                <button
                  type="button"
                  onClick={() => void onRetry()}
                  disabled={isRetrying}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink transition-colors hover:bg-surface-nested disabled:opacity-50"
                  aria-label="Retry extraction"
                >
                  <Icon name={isRetrying ? "spinner" : "refresh"} className="h-3.5 w-3.5" />
                  <span>{isRetrying ? "Retrying extraction..." : "Retry OCR extraction"}</span>
                </button>
              )}
            </div>

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

        {pages.map((page) => {
          const pageWarning = warningsList.find(
            (w) =>
              (w.startsWith(`Page ${page.pageNumber} [`) ||
                w.startsWith(`Page ${page.pageNumber}:`)) &&
              w.includes("["),
          );
          return (
            <div key={page.pageNumber} id={`ocr-page-${page.pageNumber}`} className="scroll-mt-4">
              <Paper label={`Page ${page.pageNumber}`}>
                {page.text.trim() ? (
                  <Markdown content={page.text} allowHtml />
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm text-ink-muted">No text on this page.</p>
                    {pageWarning && (
                      <p className="text-xs text-unresolved font-medium">{pageWarning}</p>
                    )}
                    {onRetry && (
                      <button
                        type="button"
                        onClick={() => void onRetry()}
                        disabled={isRetrying}
                        className="inline-flex items-center gap-1.5 rounded-md border border-line bg-surface px-2.5 py-1 text-xs font-medium text-ink transition-colors hover:bg-surface-nested disabled:opacity-50"
                      >
                        <Icon name={isRetrying ? "spinner" : "refresh"} className="h-3 w-3" />
                        <span>{isRetrying ? "Retrying..." : "Retry OCR"}</span>
                      </button>
                    )}
                  </div>
                )}
              </Paper>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function ViewportMessage({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex h-full min-h-[24rem] flex-col items-center justify-center p-8 text-center">
      <p className="text-sm text-ink-muted">{title}</p>
      {children}
    </div>
  );
}
