"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import {
  downloadChatReportPdf,
  type ChatReportRead,
} from "@/lib/api";

interface PersistedReportCardProps {
  report: ChatReportRead;
  threadId: string;
  threadTitle: string;
  isDownloading: boolean;
  onDownloadPdf: () => void;
}

export function PersistedReportCard({
  report,
  threadId,
  threadTitle,
  isDownloading,
  onDownloadPdf,
}: PersistedReportCardProps) {
  return (
    <article
      aria-label="Persisted report"
      className="space-y-4"
    >
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-line pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
              Version {report.version_number} · Saved
            </span>
            <span className="text-[10px] font-semibold text-ink-muted">
              {report.persistence_status === "completed"
                ? "Provisional"
                : "Generation failed"}
            </span>
          </div>
          <h2 className="mt-1 text-lg font-bold tracking-tight text-ink sm:text-xl">
            {report.report?.title ?? threadTitle}
          </h2>
        </div>

        {report.persistence_status === "completed" && report.report && (
          <button
            type="button"
            onClick={onDownloadPdf}
            disabled={isDownloading}
            className="inline-flex items-center gap-1.5 rounded bg-primary px-3.5 py-1.5 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
          >
            {isDownloading ? "Preparing PDF..." : "Download PDF"}
          </button>
        )}
      </header>

      {report.persistence_status === "failed" || !report.report ? (
        <ReportFailure report={report} />
      ) : (
        <ReportPdfViewer
          threadId={threadId}
          reportId={report.report_id}
          title={report.report.title ?? threadTitle}
        />
      )}
    </article>
  );
}

function ReportPdfViewer({
  threadId,
  reportId,
  title,
}: {
  threadId: string;
  reportId: string;
  title: string;
}) {
  const {
    data: pdfBlob,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["report-pdf-blob", threadId, reportId],
    queryFn: () => downloadChatReportPdf(threadId, reportId),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const pdfUrl = useMemo(() => {
    if (
      !pdfBlob ||
      typeof window === "undefined" ||
      typeof window.URL?.createObjectURL !== "function"
    ) {
      return null;
    }
    return window.URL.createObjectURL(pdfBlob);
  }, [pdfBlob]);

  useEffect(() => {
    return () => {
      if (
        pdfUrl &&
        typeof window !== "undefined" &&
        typeof window.URL?.revokeObjectURL === "function"
      ) {
        window.URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  if (isLoading) {
    return (
      <div
        aria-label="Loading PDF preview"
        className="flex h-[750px] w-full flex-col items-center justify-center rounded-lg border border-dashed border-line bg-surface p-6 text-center text-ink-secondary"
      >
        <div
          className="h-6 w-6 animate-spin rounded-full border-2 border-primary/30 border-t-primary"
          aria-hidden="true"
        />
        <p className="mt-3 text-xs font-bold text-ink">Loading PDF report...</p>
        <p className="mt-0.5 text-[11px] text-ink-muted">
          Retrieving formatted case analysis document.
        </p>
      </div>
    );
  }

  if (error || !pdfUrl) {
    const errorMessage =
      error instanceof Error ? error.message : "Unable to display PDF preview.";
    return (
      <div className="rounded border border-accent/30 bg-accent-soft p-4 text-xs text-accent">
        <p className="font-bold">Failed to load PDF preview</p>
        <p className="mt-0.5">{errorMessage}</p>
      </div>
    );
  }

  return (
    <div
      aria-label="PDF Document Viewer"
      className="overflow-hidden rounded-lg border border-line bg-surface shadow-xs"
    >
      <iframe
        src={`${pdfUrl}#toolbar=1&navpanes=0`}
        title={`PDF Report: ${title}`}
        className="h-[800px] w-full border-0 bg-canvas sm:h-[850px]"
      />
    </div>
  );
}

function ReportFailure({ report }: { report: ChatReportRead }) {
  return (
    <div className="rounded border border-accent/30 bg-accent-soft p-4 text-xs text-accent space-y-2">
      <h3 className="text-sm font-bold">
        Report generation failed
      </h3>
      <p className="text-ink-secondary">
        {report.failure_message ?? "The backend did not produce a validated report."}
      </p>
      {report.failure_code && (
        <p className="font-mono text-[10px] font-bold uppercase">
          Failure code: {report.failure_code}
        </p>
      )}
      {report.validation_errors.length > 0 && (
        <ul className="list-disc space-y-0.5 pl-4 text-ink-secondary">
          {report.validation_errors.map((error, index) => (
            <li key={`validation-error-${index}`}>{error}</li>
          ))}
        </ul>
      )}
      <p className="text-ink-muted pt-1">
        You may generate another version once case issues are resolved.
      </p>
    </div>
  );
}
