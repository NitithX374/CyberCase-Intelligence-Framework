"use client";

import { useMemo } from "react";
import { Icon } from "@/components/icons";
import { Markdown } from "@/components/Markdown";
import { plural } from "@/lib/format";
import type { CaseSourceRead } from "@/lib/api/types";
import { documentPages } from "./sourcePresentation";
import { Paper } from "./Paper";

const PAGE_JUMP_THRESHOLD = 4;

export function ExtractedTextPreview({
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
        {(warnings > 0 || pages.length >= PAGE_JUMP_THRESHOLD) && (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              {warnings > 0 && (
                <details className="group text-[13px] text-unresolved">
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
